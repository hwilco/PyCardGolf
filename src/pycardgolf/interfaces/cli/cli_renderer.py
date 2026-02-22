"""Module containing the CLI renderer implementation."""

from __future__ import annotations

import dataclasses
import sys
import time
from typing import TYPE_CHECKING, ClassVar

from color_contrast import ModulationMode, modulate
from rich.color import Color, ColorParseError
from rich.panel import Panel
from rich.style import Style
from rich.text import Text

from pycardgolf.exceptions import GameConfigError
from pycardgolf.interfaces.base import GameRenderer
from pycardgolf.utils.card import Card
from pycardgolf.utils.constants import HAND_SIZE

if TYPE_CHECKING:
    from rich.console import Console

    from pycardgolf.core.event_bus import EventBus
    from pycardgolf.core.events import (
        CardDiscardedEvent,
        CardDrawnDeckEvent,
        CardDrawnDiscardEvent,
        CardFlippedEvent,
        CardSwappedEvent,
        GameOverEvent,
        GameStatsEvent,
        RoundEndEvent,
        RoundStartEvent,
        ScoreBoardEvent,
        TurnStartEvent,
    )
    from pycardgolf.core.round import Round
    from pycardgolf.players import BasePlayer

try:
    import msvcrt
except ImportError:  # pragma: no cover
    msvcrt = None  # type: ignore[assignment]

try:
    import select
except ImportError:  # pragma: no cover
    select = None  # type: ignore[assignment]


class CLIRenderer(GameRenderer):
    """Renderer for the CLI interface."""

    CARD_DISPLAY_WIDTH: ClassVar[int] = 4
    FACE_BACKGROUND_COLOR: ClassVar[str] = "white"
    LUMINANCE_THRESHOLD: ClassVar[float] = 0.179
    MAX_OPPONENT_HANDS_TO_DISPLAY: ClassVar[int] = 3

    def __init__(
        self, event_bus: EventBus, console: Console, delay: float = 0.0
    ) -> None:
        super().__init__(event_bus)
        self.console = console
        self.delay = delay

    def wait_for_enter(self) -> None:
        """Wait for the configured delay. Key press skips delay."""
        if self.delay < 0:
            msg = f"Delay cannot be negative. Got {self.delay}"
            raise GameConfigError(msg)
        if self.delay == 0:
            return

        end_time = time.time() + self.delay

        if msvcrt:
            # Windows
            while time.time() < end_time:
                if msvcrt.kbhit():  # pragma: no cover
                    msvcrt.getch()  # pragma: no cover
                    break  # pragma: no cover
                time.sleep(0.05)

        elif select:  # pragma: no cover
            # Unix / Linux / macOS
            while time.time() < end_time:
                # Check for input availability (non-blocking)
                dr, _, _ = select.select([sys.stdin], [], [], 0)
                if dr:
                    # Input available, read line to consume (assuming Enter pressed)
                    sys.stdin.readline()
                    break
                time.sleep(0.05)

        else:  # pragma: no cover
            # Fallback
            time.sleep(self.delay)

    def get_card_string(self, card: Card | None) -> Text:
        """Get a rich Text object for a card with appropriate coloring."""
        text: str
        text_color: str
        background_color: str

        if card and card.face_up:
            text = str(card).center(self.CARD_DISPLAY_WIDTH)
            text_color = card.face_color
            background_color = self.FACE_BACKGROUND_COLOR
        else:
            text = "??".center(self.CARD_DISPLAY_WIDTH)
            text_color = "black"
            # Default back color if card is None (unseen deck card)
            background_color = card.back_color if card else "blue"
            text_color, background_color = (
                str(color)
                for color in modulate(
                    text_color, background_color, mode=ModulationMode.FOREGROUND
                )[:2]
            )
        try:
            style = Style(color=text_color, bgcolor=background_color, bold=True)
            return Text(text, style=style)
        except ColorParseError as e:
            msg = f"Invalid color '{text_color}' or '{background_color}': {e}"
            raise GameConfigError(msg) from e

    def display_round_end(self, event: RoundEndEvent) -> None:
        """Display the state of the game at the end of a round."""
        self.console.print(
            Panel(f"[bold cyan]--- Round {event.round_num} End ---[/bold cyan]")
        )

        for player, score in event.scores.items():
            self.console.print(f"Player: {player.name} (Round Score: {score})")
            self.display_hand(player, display_indices=False)

    def _display_discard_pile(self, game_round: Round) -> None:
        """Display the discard pile."""
        top_card = game_round.discard_pile.peek()
        card_text = self.get_card_string(top_card)

        discard_pile_text = "\nDiscard Pile Top Card: "
        line_len = len(discard_pile_text) + len(card_text)
        self.console.print(discard_pile_text, end="")
        self.console.print(card_text)
        self.console.print("-" * line_len)

    def display_hand(self, player: BasePlayer, display_indices: bool = False) -> None:
        """Display a player's hand."""
        # Display hand in 2 rows with position indicators
        cols = HAND_SIZE // 2

        # Prepare card strings
        row1_cards = player.hand[0:cols]
        row2_cards = player.hand[cols:HAND_SIZE]

        indices_str_2 = ""
        indices_str_1 = ""
        if display_indices:
            # Prepare indices strings
            indices_1 = [
                str(i).center(self.CARD_DISPLAY_WIDTH) for i in range(1, cols + 1)
            ]
            indices_2 = [
                str(i).center(self.CARD_DISPLAY_WIDTH)
                for i in range(cols + 1, HAND_SIZE + 1)
            ]

            indices_str_1 = " ".join(indices_1)
            indices_str_2 = " ".join(indices_2)

            # Print with indices aligned
            # Indent indices by 2 spaces to account for the box border "| "
            self.console.print("  " + indices_str_1)

        # Border around cards
        border = "+" + "-" * (len(row1_cards) * (self.CARD_DISPLAY_WIDTH + 1) + 1) + "+"
        self.console.print(border)

        # Row 1
        self.console.print("| ", end="")
        for i, card in enumerate(row1_cards):
            self.console.print(self.get_card_string(card), end="")
            if i < len(row1_cards) - 1:
                self.console.print(" ", end="")
        self.console.print(" |")

        # Row 2
        self.console.print("| ", end="")
        for i, card in enumerate(row2_cards):
            self.console.print(self.get_card_string(card), end="")
            if i < len(row2_cards) - 1:
                self.console.print(" ", end="")
        self.console.print(" |")

        self.console.print(border)

        if display_indices:
            self.console.print("  " + indices_str_2)

    def print_card_message(self, parts: list[str | Card]) -> None:
        """Print a message composed of strings and cards."""
        msg = Text()
        for part in parts:
            if isinstance(part, Card):
                msg.append(self.get_card_string(part))
            else:
                msg.append(part)
        self.console.print(msg)

    def create_draw_choice_prompt(
        self, deck_card: Card | None, discard_card: Card | None
    ) -> Text:
        """Create a prompt for drawing choice."""
        deck_card_text = self.get_card_string(deck_card)
        discard_card_text = self.get_card_string(discard_card)
        prompt = Text("Draw from (d)eck ")
        prompt.append(deck_card_text)
        prompt.append(" or (p)ile ")
        prompt.append(discard_card_text)
        prompt.append("? (d/p) ")
        return prompt

    def display_drawn_card(self, event: CardDrawnDeckEvent) -> None:
        """Display the card drawn from the deck."""
        player_name = (
            self.players[event.player_idx].name
            if self.players
            else f"Player {event.player_idx}"
        )
        self.print_card_message([f"{player_name} drew: ", event.card])
        self.wait_for_enter()

    def display_discard_draw(self, event: CardDrawnDiscardEvent) -> None:
        """Display the card drawn from the discard pile."""
        player_name = (
            self.players[event.player_idx].name
            if self.players
            else f"Player {event.player_idx}"
        )
        self.print_card_message(
            [
                f"{player_name} drew ",
                event.card,
                " from the discard pile. They must replace one of their cards with it.",
            ]
        )
        self.wait_for_enter()

    def display_replace_action(self, event: CardSwappedEvent) -> None:
        """Display the action of replacing a card in hand."""
        player_name = (
            self.players[event.player_idx].name
            if self.players
            else f"Player {event.player_idx}"
        )
        msg = f"{player_name} replaced card at position {event.hand_index + 1} with "
        self.print_card_message(
            [
                msg,
                event.new_card,
                ". Discarded ",
                event.old_card,
                ".",
            ]
        )
        self.wait_for_enter()

    def display_flip_action(self, event: CardFlippedEvent) -> None:
        """Display the action of flipping a card in hand."""
        player_name = (
            self.players[event.player_idx].name
            if self.players
            else f"Player {event.player_idx}"
        )
        msg = f"{player_name} flipped card at position {event.hand_index + 1}: "
        self.print_card_message(
            [
                msg,
                event.card,
            ]
        )
        self.wait_for_enter()

    def display_turn_start(self, event: TurnStartEvent) -> None:
        """Display the start of a player's turn."""
        if self.players:
            player = self.players[event.player_idx]
            self.console.print(f"It's {player.name}'s turn.")

            num_players = len(self.players)
            num_to_display = min(num_players - 1, self.MAX_OPPONENT_HANDS_TO_DISPLAY)
            for i in reversed(range(1, num_to_display + 1)):
                opp_idx = (event.player_idx + i) % num_players
                opp_player = self.players[opp_idx]
                label = "Next Player" if i == 1 else f"Opponent {i}"
                self.console.print(f"{opp_player.name}'s Hand ({label}):")
                self.display_hand(opp_player, display_indices=False)

            self.console.print(f"{player.name}'s Hand (Current Player):")
            self.display_hand(player, display_indices=True)
        else:
            self.console.print(f"It's Player {event.player_idx}'s turn.")
        self.wait_for_enter()

    def display_discard_action(self, event: CardDiscardedEvent) -> None:
        """Display the action of discarding a card."""
        player_name = (
            self.players[event.player_idx].name
            if self.players
            else f"Player {event.player_idx}"
        )
        self.print_card_message([f"{player_name} discarded ", event.card, "."])
        self.wait_for_enter()

    def display_round_start(self, event: RoundStartEvent) -> None:
        """Display the start of a round."""
        self.console.print(
            Panel(f"[bold cyan]--- Starting Round {event.round_num} ---[/bold cyan]")
        )
        self.wait_for_enter()

    def display_scoreboard(self, event: ScoreBoardEvent) -> None:
        """Display current scores for all players."""
        self.console.print("\n[bold]Current Scores:[/bold]")
        for player, score in event.scores.items():
            self.console.print(f"{player.name}: {score}")
        self.wait_for_enter()

    def display_game_over(self, event: GameOverEvent) -> None:
        """Display game over message."""
        self.console.print(Panel("[bold red]--- Game Over ---[/bold red]"))
        msg = (
            f"[bold gold1]Winner: {event.winner.name} with score "
            f"{event.winning_score}![/bold gold1]"
        )
        self.console.print(Panel(msg))

    def display_standings(self, standings: list[tuple[BasePlayer, int]]) -> None:
        """Display standings. List of (player, score) tuples, sorted by rank."""
        self.console.print("[bold]Final Standings:[/bold]")
        for i, (player, score) in enumerate(standings):
            color = "green" if i == 0 else "white"
            self.console.print(f"[{color}]{i + 1}. {player.name}: {score}[/{color}]")

    def display_initial_flip_prompt(self, player: BasePlayer, num_to_flip: int) -> None:
        """Prompt player to select initial cards to flip."""
        msg = (
            f"[bold]{player.name}, draw start! "
            f"Select {num_to_flip} cards to flip.[/bold]"
        )
        self.console.print(msg)

    def display_initial_flip_selection_prompt(
        self, current_count: int, total_count: int
    ) -> None:
        """Prompt to select a specific card during initial flip."""
        self.console.print(f"Select card {current_count} of {total_count} to flip.")

    def display_initial_flip_error_already_selected(self) -> None:
        """Error when selecting an already selected card during initial flip."""
        self.console.print(
            "[bold red]You already selected that card. "
            "Please choose another one.[/bold red]"
        )

    def display_final_turn_notification(self, player: BasePlayer) -> None:
        """Notify that a player triggered the final turn."""
        self.console.print(
            Panel(
                f"[bold yellow]{player.name} has revealed all their cards! "
                "Everyone gets one final turn.[/bold yellow]"
            )
        )

    @staticmethod
    def validate_color(color: str) -> None:
        """Validate that a color string is supported by the interface via Rich."""
        try:
            Color.parse(color)
        except ColorParseError as e:
            msg = f"Invalid color '{color}': {e}"
            raise GameConfigError(msg) from e

    def display_game_stats(self, event: GameStatsEvent) -> None:
        """Display game statistics.

        Args:
            event: A GameStatsEvent containing the stats mapping.

        """
        self.console.print("\n[bold]Game Statistics:[/bold]")
        for player, player_stats in event.stats.items():
            self.console.print(Panel(f"[bold]{player.name}[/bold]"))
            for field in dataclasses.fields(player_stats):
                name = field.name.replace("_", " ").title()
                value = getattr(player_stats, field.name)
                if isinstance(value, float):
                    self.console.print(f"  {name}: {value:.2f}")
                elif isinstance(value, list):
                    # For list of scores, join them nicely
                    value_str = ", ".join(map(str, value))
                    self.console.print(f"  {name}: {value_str}")
                else:
                    self.console.print(f"  {name}: {value}")

    def display_initial_flip_choices(
        self, player: BasePlayer, choices: list[int]
    ) -> None:
        """Display the choices made for initial cards to flip."""
        cards = [player.hand[i] for i in choices]
        msg_parts: list[str | Card] = [f"{player.name} flipped initial cards: "]
        for i, card in enumerate(cards):
            msg_parts.append(card)
            if i < len(cards) - 1:
                msg_parts.append(", ")
        self.print_card_message(msg_parts)
