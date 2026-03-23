"""Module containing the main PyCardGolfApp Textual application."""

from __future__ import annotations

import queue
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.widgets import Footer, Static

from pycardgolf.core.actions import ActionSpace
from pycardgolf.core.observation import ObservationBuilder
from pycardgolf.core.phases import RoundPhase
from pycardgolf.exceptions import GameExitError
from pycardgolf.interfaces.tui.components.banner import SideIndicator
from pycardgolf.interfaces.tui.components.center_table import CenterTable
from pycardgolf.interfaces.tui.components.event_log import EventLogWidget
from pycardgolf.interfaces.tui.components.opponents import OpponentGrid
from pycardgolf.interfaces.tui.components.player_hand import PlayerHandWidget
from pycardgolf.interfaces.tui.components.status_bar import StatusBar
from pycardgolf.players.human import HumanPlayer

if TYPE_CHECKING:
    from textual.worker import Worker

    from pycardgolf.core.actions import Action
    from pycardgolf.core.game import Game
    from pycardgolf.core.hand import Hand
    from pycardgolf.core.observation import Observation
    from pycardgolf.interfaces.tui.tui_input import TUIInputHandler
    from pycardgolf.interfaces.tui.tui_renderer import TUIRenderer
    from pycardgolf.players.player import BasePlayer
    from pycardgolf.utils.types import CardID


class PyCardGolfApp(App[None]):
    """The main Textual application for PyCardGolf.

    Manages layout, reactive game state, dynamic hotkey bindings,
    and a background worker thread that runs the game engine loop.
    """

    CSS_PATH = str(Path(__file__).parent / "layout.tcss")

    TITLE = "PyCardGolf"

    # All possible bindings — check_action() filters by phase
    BINDINGS: ClassVar[list[Binding]] = [  # type: ignore[assignment]
        # Draw phase
        Binding("d", "draw_deck", "Draw from Deck", show=True),
        Binding("p", "pick_discard", "Pick from Discard", show=True),
        # Card selection (1-6): used in SETUP, ACTION/swap, FLIP
        # Using parameterized actions to avoid boilerplate methods
        Binding("1", "select(1)", "Card 1", show=True),
        Binding("2", "select(2)", "Card 2", show=True),
        Binding("3", "select(3)", "Card 3", show=True),
        Binding("4", "select(4)", "Card 4", show=True),
        Binding("5", "select(5)", "Card 5", show=True),
        Binding("6", "select(6)", "Card 6", show=True),
        # Action phase: discard drawn card
        Binding("x", "discard_drawn", "Discard Drawn", show=True),
        # Flip phase: pass
        Binding("n", "pass_flip", "Pass (No Flip)", show=True),
        # Round-end continue
        Binding("enter", "continue_round", "Continue", show=True),
        # Always available
        Binding("q", "quit_game", "Quit", show=True),
    ]

    # Map action names to their required phase and core game action
    _ACTION_DISPATCH: ClassVar[dict[str, tuple[str, Action]]] = {
        "draw_deck": ("DRAW", ActionSpace.DRAW_DECK),
        "pick_discard": ("DRAW", ActionSpace.DRAW_DISCARD),
        "discard_drawn": ("ACTION", ActionSpace.DISCARD_DRAWN),
        "pass_flip": ("FLIP", ActionSpace.PASS),
    }

    # --- Reactive State ---
    game_phase: reactive[str] = reactive("WAITING")
    current_player_name: reactive[str] = reactive("")
    can_discard: reactive[bool] = reactive(False)
    is_human_turn: reactive[bool] = reactive(False)
    game_over: reactive[bool] = reactive(False)
    waiting_for_continue: reactive[bool] = reactive(False)

    def __init__(
        self,
        game: Game,
        renderer: TUIRenderer,
        input_handler: TUIInputHandler,
    ) -> None:
        """Initialize with game engine, renderer, and input handler."""
        super().__init__()
        self._game = game
        self._renderer = renderer
        self._input_handler = input_handler
        self._current_observation: Observation | None = None
        self._game_worker: Worker[None] | None = None
        self._shutting_down = False
        # Queue for round-end "press Enter to continue"
        self._continue_queue: queue.Queue[bool] = queue.Queue()

    def compose(self) -> ComposeResult:
        """Build the TUI layout."""
        # Determine how many opponent slots we need (everyone except one player)
        num_opp_slots = min(len(self._game.players) - 1, 3)

        with Horizontal(id="main-container"):
            with Vertical(id="game-area"):
                yield OpponentGrid(num_opp_slots, id="opponents")
                yield CenterTable(id="center-table")
                with Horizontal(id="player-area"):
                    yield PlayerHandWidget(id="player-hand")
                    yield SideIndicator(id="final-turn-indicator")
            with Vertical(id="event-log-container"):
                yield Static(
                    "─── Event Log ───",
                    id="event-log-title",
                    classes="section-title",
                )
                yield EventLogWidget(id="event-log")
        yield StatusBar(id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        """Start the game engine in a background worker thread."""
        self._renderer.set_app(self)
        self._input_handler.set_app(self)
        self._game_worker = self.run_game_loop()

    # ------------------------------------------------------------------
    # check_action — dynamic binding visibility
    # ------------------------------------------------------------------

    def check_action(
        self,
        action: str,
        parameters: tuple[object, ...],
    ) -> bool | None:
        """Return False to dim/hide actions invalid for the current phase."""
        _ = parameters

        if action == "quit_game":
            return True

        # If game is terminal/paused, only allow continue if actively waiting for it
        if self.game_over or not self.is_human_turn or self.waiting_for_continue:
            return action == "continue_round" and self.waiting_for_continue

        if action == "select":
            return self.game_phase in ("SETUP", "ACTION", "FLIP")

        if action in self._ACTION_DISPATCH:
            required_phase, _ = self._ACTION_DISPATCH[action]
            is_valid = self.game_phase == required_phase
            return (
                (is_valid and self.can_discard)
                if action == "discard_drawn"
                else is_valid
            )

        return False

    # ------------------------------------------------------------------
    # Action handlers — push actions to the input queue
    # ------------------------------------------------------------------

    def _try_submit(self, action_name: str) -> None:
        """Look up and submit a phase-gated action from the dispatch table."""
        if not self.is_human_turn or self.waiting_for_continue:
            return

        entry = self._ACTION_DISPATCH.get(action_name)
        if not entry:
            return

        required_phase, action_value = entry
        if self.game_phase != required_phase:
            return

        # Extra guard for discard
        if action_name == "discard_drawn" and not self.can_discard:
            return

        self._input_handler.submit_action(action_value)

    def action_draw_deck(self) -> None:
        """Handle 'd' key."""
        self._try_submit("draw_deck")

    def action_pick_discard(self) -> None:
        """Handle 'p' key."""
        self._try_submit("pick_discard")

    def action_discard_drawn(self) -> None:
        """Handle 'x' key."""
        self._try_submit("discard_drawn")

    def action_pass_flip(self) -> None:
        """Handle 'n' key."""
        self._try_submit("pass_flip")

    def action_continue_round(self) -> None:
        """Handle Enter key: continue past round-end summary."""
        if self.waiting_for_continue:
            self._continue_queue.put_nowait(True)

    def action_select(self, index: int) -> None:
        """Handle card selection (1-6) via parameterized action."""
        self._handle_card_select(index - 1)

    def _handle_card_select(self, index: int) -> None:
        """Handle a numbered card selection (0-indexed)."""
        if not self.is_human_turn or self.waiting_for_continue:
            return

        phase = self.game_phase
        if phase in ("SETUP", "FLIP"):
            self._input_handler.submit_action(ActionSpace.FLIP[index])
        elif phase == "ACTION":
            self._input_handler.submit_action(ActionSpace.SWAP[index])

    def action_quit_game(self) -> None:
        """Handle 'q' key: exit the application cleanly."""
        self._shutting_down = True
        # Unblock any waiting queue.get() calls
        self._input_handler.shutdown()
        self._continue_queue.put_nowait(False)
        self.exit()

    # ------------------------------------------------------------------
    # Game worker — runs the tick loop in a background thread
    # ------------------------------------------------------------------

    @work(thread=True, exclusive=True)
    def run_game_loop(self) -> None:
        """Run the game engine loop in a background thread."""
        try:
            self._game.start()
            running = True
            while running and not self._shutting_down:
                running = self._game.tick()
        except GameExitError:
            self.call_from_thread(
                self.log_game_event, "[bold red]Game exited.[/bold red]"
            )
        except Exception as exc:  # noqa: BLE001
            if not self._shutting_down:
                self.call_from_thread(
                    self.log_game_event,
                    f"[bold red]Error: {exc}[/bold red]",
                )
        finally:
            if not self._shutting_down:
                self.call_from_thread(self.end_game)

    # ------------------------------------------------------------------
    # Methods called from the worker thread (via call_from_thread)
    # ------------------------------------------------------------------

    def _is_final_turn(self) -> bool:
        """Check if the current round is in its final turn sequence."""
        if not self._game.current_round:
            return False
        if self._game.current_round.phase == RoundPhase.FINISHED:
            return False
        return (
            getattr(self._game.current_round, "last_turn_player_idx", None) is not None
        )

    def set_final_turn_warning(self, is_final: bool) -> None:
        """Update the UI to show or hide the final turn warning."""
        # Update side indicator
        indicator = self.query_one("#final-turn-indicator", SideIndicator)
        indicator.message = "FINAL TURN" if is_final else ""

        # Update status bar phase name
        status_bar = self.query_one("#status-bar", StatusBar)
        if is_final:
            if "⚠️" not in status_bar.phase_name:
                status_bar.phase_name = (
                    f"{status_bar.phase_name} [bold red]⚠️  FINAL TURN[/bold red]"
                )
        elif "⚠️" in status_bar.phase_name:
            # Strip the warning tag
            status_bar.phase_name = status_bar.phase_name.split(" [")[0]

    def _get_phase_prompt(self, phase_name: str, can_discard: bool) -> str:
        """Return a human-readable prompt for the current game phase."""
        prompts = {
            "SETUP": "Select 2 cards to flip face-up (press 1-6)",
            "DRAW": (
                "Draw a card: [bold]d[/bold] from deck, [bold]p[/bold] from discard"
            ),
            "FLIP": ("Flip a card (press 1-6) or [bold]n[/bold] to pass"),
        }
        if phase_name == "ACTION":
            if can_discard:
                return (
                    "Swap drawn card with a hand card (1-6) "
                    "or [bold]x[/bold] to discard it"
                )
            return "Swap drawn card with a hand card (press 1-6)"
        return prompts.get(phase_name, "")

    def prepare_for_input(self, player: BasePlayer, observation: Observation) -> None:
        """Update UI and bind hotkeys for the current player's turn."""
        self._input_handler.clear_actions()
        self._current_observation = observation
        self.game_phase = observation.phase.name
        self.current_player_name = player.name
        self.is_human_turn = isinstance(player, HumanPlayer)
        self.can_discard = observation.can_discard_drawn

        # Check if it's the final turn
        is_final_turn = self._is_final_turn()

        # Update status bar
        status_bar = self.query_one("#status-bar", StatusBar)
        # Handle status bar phase name via helper to ensure consistency
        status_bar.phase_name = observation.phase.name
        status_bar.current_player = player.name
        self.set_final_turn_warning(is_final_turn)

        # Update player hand from observation
        hand_widget = self.query_one("#player-hand", PlayerHandWidget)
        hand_widget.player_label = f"{player.name}'s Hand"
        hand_widget.hand_cards = list(observation.my_hand)

        # Update drawn card display
        center = self.query_one("#center-table", CenterTable)
        center.drawn_card = observation.drawn_card_id
        center.deck_size = observation.deck_size

        if observation.discard_top is not None:
            center.discard_top = observation.discard_top

        # Log action prompt for human players
        if isinstance(player, HumanPlayer):
            prompt = self._get_phase_prompt(
                observation.phase.name, observation.can_discard_drawn
            )
            if prompt:
                if is_final_turn:
                    # Double space after ⚠️ to help with rendering properly
                    prompt = f"[bold red]⚠️  FINAL TURN ⚠️[/bold red]\n  {prompt}"
                self.log_game_event(f"[italic yellow]▸ {prompt}[/italic yellow]")

    def refresh_hands(self) -> None:
        """Manually refresh all player hands from the current game state."""
        current_round = self._game.current_round
        if current_round:
            current_player_idx = current_round.get_current_player_idx()
            # hands is a dict[int, Hand]
            hands = dict(enumerate(current_round.hands))
            self.update_hands_from_event(current_player_idx, hands)

    def update_hands_from_event(
        self,
        current_player_idx: int,
        hands: dict[int, Hand],
    ) -> None:
        """Update all hand displays from a TurnStartEvent."""
        players = self._game.players

        # Dynamic human selection for the bottom widget:
        # 1. If currently active player is human, focus on them.
        # 2. Otherwise, stick with the first human found.
        human_idx = -1
        # Try to find the active player if they are human
        if current_player_idx < len(players) and isinstance(
            players[current_player_idx], HumanPlayer
        ):
            human_idx = current_player_idx
        else:
            # Fallback to the first human
            for i, p in enumerate(players):
                if isinstance(p, HumanPlayer):
                    human_idx = i
                    break

        # Update bottom hand widget with human's hand
        if human_idx != -1 and human_idx in hands:
            my_hand = ObservationBuilder.sanitize_hand(hands[human_idx])
            hand_widget = self.query_one("#player-hand", PlayerHandWidget)
            hand_widget.player_label = f"{players[human_idx].name}'s Hand"
            hand_widget.hand_cards = my_hand

        # Update opponent grid with everyone else's hands
        opp_index = 0
        opponent_grid = self.query_one("#opponents", OpponentGrid)
        total_players = len(players)
        # Start looking at the next player after the focused human
        for offset in range(1, total_players):
            i = (human_idx + offset) % total_players
            if i not in hands:
                continue
            sanitized = ObservationBuilder.sanitize_hand(hands[i])
            color = self._get_player_color(i)
            opponent_grid.update_opponent(opp_index, players[i].name, sanitized, color)
            opp_index += 1
            if opp_index >= opponent_grid.MAX_OPPONENTS:
                break

        # Update banner in case it's a bot turn (prepare_for_input not called)
        self.set_final_turn_warning(self._is_final_turn())

        # Update status bar with current player
        status_bar = self.query_one("#status-bar", StatusBar)
        if current_player_idx < len(players):
            status_bar.current_player = players[current_player_idx].name
            self._apply_player_theme(current_player_idx)

    def _get_player_color(self, player_idx: int) -> str:
        """Get a distinct color for a given player index dynamically."""
        total_players = len(self._game.players) if hasattr(self, "_game") else 1
        num_colors = max(total_players, 1)
        # Distribute hues evenly across the 360-degree color wheel
        hue = int(360 * player_idx / num_colors)
        return f"hsl({hue},80%,45%)"

    def _apply_player_theme(self, player_idx: int) -> None:
        """Apply a dynamic color theme based on the current player index."""
        color = self._get_player_color(player_idx)

        try:
            status_bar = self.query_one("#status-bar", StatusBar)
            status_bar.styles.background = color
            status_bar.styles.color = "white"
        except NoMatches:
            pass

        try:
            player_area = self.query_one("#player-area")
            player_area.styles.border_top = ("thick", color)
        except NoMatches:
            pass

        try:
            event_log_title = self.query_one("#event-log-title")
            event_log_title.styles.color = color
        except NoMatches:
            pass

    def set_drawn_card(self, card_id: CardID) -> None:
        """Set the drawn card display."""
        center = self.query_one("#center-table", CenterTable)
        center.drawn_card = card_id

    def clear_drawn_card(self) -> None:
        """Clear the drawn card display after swap/discard."""
        center = self.query_one("#center-table", CenterTable)
        center.drawn_card = None

    def show_all_hands_face_up(
        self,
        hands_by_name: dict[str, list[CardID]],
        human_name: str,
    ) -> None:
        """Reveal all hands face-up in the main window for round-end recap.

        Shows the human's hand in the bottom panel (fully revealed),
        and all opponent hands in the opponent grid.
        """
        players = self._game.players

        # Update bottom hand widget with the human player's revealed hand
        if human_name in hands_by_name:
            hand_widget = self.query_one("#player-hand", PlayerHandWidget)
            hand_widget.player_label = f"{human_name}'s Hand (Final)"
            hand_widget.hand_cards = hands_by_name[human_name]

        # Update opponent grid with everyone else's revealed hand
        opp_index = 0
        opponent_grid = self.query_one("#opponents", OpponentGrid)
        total_players = len(players)

        # Find the human's index so we can start offsets from them
        human_idx = 0
        for i, p in enumerate(players):
            if p.name == human_name:
                human_idx = i
                break

        for offset in range(1, total_players):
            idx = (human_idx + offset) % total_players
            player = players[idx]
            if player.name in hands_by_name:
                color = self._get_player_color(idx)
                opponent_grid.update_opponent(
                    opp_index, player.name, hands_by_name[player.name], color
                )
                opp_index += 1
            if opp_index >= opponent_grid.MAX_OPPONENTS:
                break

    def set_next_player(self, next_player_name: str) -> None:
        """Highlight the next player in the opponent grid."""
        try:
            opponent_grid = self.query_one("#opponents", OpponentGrid)
            opponent_grid.mark_next_player(next_player_name)
        except NoMatches:
            pass

    def set_round_num(self, round_num: int) -> None:
        """Update the round number on the status bar."""
        status_bar = self.query_one("#status-bar", StatusBar)
        status_bar.round_num = round_num

    def log_game_event(self, message: str) -> None:
        """Append a message to the event log widget."""
        try:
            event_log = self.query_one("#event-log", EventLogWidget)
            event_log.log_event(message)
        except NoMatches:
            pass  # Widget may not be mounted yet

    def show_round_end_summary(self) -> None:
        """Enable the waiting-for-continue state for round-end."""
        self.waiting_for_continue = True

    def end_game(self) -> None:
        """Mark the game as over and update UI."""
        self.game_over = True
        self.game_phase = "FINISHED"
        self.is_human_turn = False

        status_bar = self.query_one("#status-bar", StatusBar)
        status_bar.phase_name = "GAME OVER"
        status_bar.current_player = ""

    def wait_for_continue(self) -> bool:
        """Block the worker thread until the user presses Enter.

        Returns True if the user pressed Enter (continue), or
        False if the app is shutting down.
        """
        try:
            return self._continue_queue.get(timeout=0.5)
        except queue.Empty:
            if self._shutting_down:
                return False
            # Keep waiting
            return self.wait_for_continue()

    def finish_continue(self) -> None:
        """Reset the waiting state after Enter is pressed."""
        self.waiting_for_continue = False

    # ------------------------------------------------------------------
    # Reactive watchers
    # ------------------------------------------------------------------

    def watch_game_phase(self) -> None:
        """Refresh bindings when game phase changes."""
        self.refresh_bindings()

    def watch_is_human_turn(self) -> None:
        """Refresh bindings when turn ownership changes."""
        self.refresh_bindings()

    def watch_can_discard(self) -> None:
        """Refresh bindings when discard eligibility changes."""
        self.refresh_bindings()

    def watch_game_over(self) -> None:
        """Refresh bindings when game ends."""
        self.refresh_bindings()

    def watch_waiting_for_continue(self) -> None:
        """Refresh bindings when waiting for continue changes."""
        self.refresh_bindings()
