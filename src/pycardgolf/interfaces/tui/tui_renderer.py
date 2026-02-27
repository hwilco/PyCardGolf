"""Module containing the TUIRenderer — a GameRenderer for the Textual TUI."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pycardgolf.interfaces.base import GameRenderer
from pycardgolf.utils.card import card_to_string

if TYPE_CHECKING:
    from pycardgolf.core.event_bus import EventBus
    from pycardgolf.core.events import (
        CardDiscardedEvent,
        CardDrawnDeckEvent,
        CardDrawnDiscardEvent,
        CardFlippedEvent,
        CardSwappedEvent,
        DeckReshuffledEvent,
        GameOverEvent,
        GameStatsEvent,
        IllegalActionEvent,
        RoundEndEvent,
        RoundStartEvent,
        ScoreBoardEvent,
        TurnStartEvent,
    )
    from pycardgolf.core.hand import Hand
    from pycardgolf.interfaces.tui.tui_app import PyCardGolfApp


class TUIRenderer(GameRenderer):
    """GameRenderer that forwards events to the Textual TUI app.

    Each display method calls ``self.app.call_from_thread()`` to safely
    post updates to the async UI thread. The app dispatches to the
    appropriate widgets and event log.
    """

    def __init__(self, event_bus: EventBus) -> None:
        """Initialize the renderer (app will be set before use)."""
        self._app: PyCardGolfApp | None = None
        super().__init__(event_bus)

    @property
    def app(self) -> PyCardGolfApp:
        """Return the Textual app reference."""
        if self._app is None:
            msg = "TUIRenderer.app not set. Call set_app() before use."
            raise RuntimeError(msg)
        return self._app

    def set_app(self, app: PyCardGolfApp) -> None:
        """Attach the Textual app instance (called at startup)."""
        self._app = app

    def _log(self, message: str) -> None:
        """Post a message to the event log, thread-safely."""
        self.app.call_from_thread(self.app.log_game_event, message)

    def _get_player_name(self, player_idx: int) -> str:
        """Get a player's name from their index."""
        if self.players and player_idx < len(self.players):
            return self.players[player_idx].name
        return f"Player {player_idx}"

    # ------------------------------------------------------------------
    # GameRenderer implementation
    # ------------------------------------------------------------------

    def display_round_start(self, event: RoundStartEvent) -> None:
        """Display the start of a round."""
        self._log(f"[bold cyan]─── Round {event.round_num} Start ───[/bold cyan]")
        self.app.call_from_thread(self.app.set_round_num, event.round_num)

    def display_turn_start(self, event: TurnStartEvent) -> None:
        """Display the start of a player's turn and update all hands."""
        from pycardgolf.players.human import HumanPlayer  # noqa: PLC0415

        player_name = self._get_player_name(event.player_idx)
        player = self.players[event.player_idx] if self.players else None
        is_bot = player is not None and not isinstance(player, HumanPlayer)
        is_human = not is_bot

        if is_bot:
            self._log(f"[dim]── {player_name} is thinking... ──[/dim]")
        else:
            self._log(f"[bold]── {player_name}'s turn ──[/bold]")

        self.app.call_from_thread(
            self.app.update_hands_from_event,
            event.player_idx,
            event.hands,
        )

        # Mark next player in opponent grid (bots show as "next" for the human)
        if is_human and self.players:
            # Find who acts after this human (next in player list)
            next_idx = (event.player_idx + 1) % len(self.players)
            next_name = self._get_player_name(next_idx)
            self.app.call_from_thread(self.app.set_next_player, next_name)
        elif is_bot:
            # Clear next indicators when a bot is acting
            self.app.call_from_thread(self.app.set_next_player, player_name)

    def display_drawn_card(self, event: CardDrawnDeckEvent) -> None:
        """Display the card drawn from the deck."""
        player_name = self._get_player_name(event.player_idx)
        card_str = card_to_string(event.card_id)
        self._log(f"{player_name} drew [bold]{card_str}[/bold] from deck")
        self.app.call_from_thread(self.app.set_drawn_card, event.card_id)

    def display_discard_draw(self, event: CardDrawnDiscardEvent) -> None:
        """Display the card drawn from the discard pile."""
        player_name = self._get_player_name(event.player_idx)
        card_str = card_to_string(event.card_id)
        self._log(
            f"{player_name} drew [bold]{card_str}[/bold] from discard (must swap)"
        )
        self.app.call_from_thread(self.app.set_drawn_card, event.card_id)

    def display_replace_action(self, event: CardSwappedEvent) -> None:
        """Display the action of replacing a card in hand."""
        player_name = self._get_player_name(event.player_idx)
        new_str = card_to_string(event.new_card_id)
        old_str = card_to_string(event.old_card_id)
        self._log(
            f"{player_name} replaced position {event.hand_index + 1} "
            f"with [bold]{new_str}[/bold] (discarded {old_str})"
        )
        self.app.call_from_thread(self.app.clear_drawn_card)
        self.app.call_from_thread(self.app.refresh_hands)

    def display_flip_action(self, event: CardFlippedEvent) -> None:
        """Display the action of flipping a card."""
        player_name = self._get_player_name(event.player_idx)
        card_str = card_to_string(event.card_id)
        self._log(
            f"{player_name} flipped position {event.hand_index + 1}: "
            f"[bold]{card_str}[/bold]"
        )
        self.app.call_from_thread(self.app.refresh_hands)

    def display_discard_action(self, event: CardDiscardedEvent) -> None:
        """Display the action of discarding a drawn card."""
        player_name = self._get_player_name(event.player_idx)
        card_str = card_to_string(event.card_id)
        self._log(f"{player_name} discarded [bold]{card_str}[/bold]")
        self.app.call_from_thread(self.app.clear_drawn_card)

    def display_round_end(self, event: RoundEndEvent) -> None:
        """Display round-end summary with all hands and scores, then wait for Enter."""
        from pycardgolf.players.human import HumanPlayer  # noqa: PLC0415
        from pycardgolf.utils.card import card_to_string as c2s  # noqa: PLC0415

        self._log(f"\n[bold cyan]═══ Round {event.round_num} Complete ═══[/bold cyan]")

        # Build face-up hand data for main window (card_id list per player name)
        hands_by_name: dict[str, list[int]] = {}
        for player, hand in event.hands.items():
            hands_by_name[player.name] = list(hand)

        # Determine the human player name (if any) for the bottom widget
        human_name = ""
        if self.players:
            for p in self.players:
                if isinstance(p, HumanPlayer):
                    human_name = p.name
                    break

        # Show all hands face-up in the main window
        self.app.call_from_thread(
            self.app.show_all_hands_face_up, hands_by_name, human_name
        )

        # Clear indicators for the recap screen
        self.app.call_from_thread(self.app.set_next_player, "")
        self.app.call_from_thread(self.app.set_final_turn_warning, False)

        # Log each player's revealed hand and score in the event log
        for player, score in event.scores.items():
            hand = event.hands.get(player)
            if hand is not None:
                cards_str = "  ".join(
                    f"[bold]{c2s(card_id)}[/bold]" for card_id in hand
                )
                self._log(f"  {player.name}: {cards_str}  →  [bold]{score}[/bold]")
            else:
                self._log(f"  {player.name}: [bold]{score}[/bold]")

        self._log(
            "[italic yellow]▸ Press [bold]Enter[/bold] to continue...[/italic yellow]"
        )

        # Enable the "Continue" binding and block the worker
        self.app.call_from_thread(self.app.show_round_end_summary)

        # Block the worker thread until Enter is pressed
        continued = self.app.wait_for_continue()

        # Reset the waiting state
        if continued:
            self.app.call_from_thread(self.app.finish_continue)

    def display_scoreboard(self, event: ScoreBoardEvent) -> None:
        """Display current scores."""
        self._log("[bold]Scores:[/bold]")
        for player, score in event.scores.items():
            self._log(f"  {player.name}: {score}")

    def display_game_over(self, event: GameOverEvent) -> None:
        """Display game over message."""
        self._log(
            f"[bold red]─── Game Over ───[/bold red]\n"
            f"[bold gold1]Winner: {event.winner.name} "
            f"({event.winning_score})![/bold gold1]"
        )
        self.app.call_from_thread(self.app.end_game)

    def display_game_stats(self, event: GameStatsEvent) -> None:
        """Display per-player game statistics."""
        self._log("\n[bold]═══ Final Game Statistics ═══[/bold]")
        for player, stats in event.stats.items():
            rounds_str = ", ".join(str(s) for s in stats.round_scores)
            self._log(
                f"  [bold]{player.name}[/bold]\n"
                f"    Rounds: {rounds_str}\n"
                f"    Total: [bold]{stats.total_score}[/bold]  "
                f"Best: {stats.best_score}  "
                f"Worst: {stats.worst_score}  "
                f"Avg: {stats.average_score:.1f}"
            )

    def display_deck_reshuffled(self, event: DeckReshuffledEvent) -> None:  # noqa: ARG002
        """Display a message when the discard pile is reshuffled into the deck."""
        self._log(
            "[bold yellow]The discard pile was reshuffled into the deck.[/bold yellow]"
        )

    def display_illegal_action(self, event: IllegalActionEvent) -> None:
        """Display an error message for an illegal action."""
        self._log(f"[bold red]Error: {event.message}[/bold red]")

    def display_hand(  # pragma: no cover
        self,
        hand: Hand,
        display_indices: bool = False,
    ) -> None:
        """No-op: the TUI always shows hands from reactive state."""
