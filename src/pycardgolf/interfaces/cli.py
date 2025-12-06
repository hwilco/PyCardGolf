"""Module containing the CLI (command-line interface) implementation."""

from collections.abc import Callable
from typing import ClassVar, TypeVar, cast

from color_contrast import ModulationMode, modulate
from rich.color import Color, ColorParseError
from rich.console import Console
from rich.panel import Panel
from rich.text import Style, Text

from pycardgolf.core.game import Game
from pycardgolf.core.hand import Hand
from pycardgolf.core.player import Player
from pycardgolf.core.round import Round
from pycardgolf.core.scoring import calculate_score, calculate_visible_score
from pycardgolf.exceptions import GameConfigError
from pycardgolf.interfaces.base import (
    ActionChoice,
    DrawSource,
    FlipChoice,
    GameInterface,
)
from pycardgolf.utils.card import Card
from pycardgolf.utils.constants import HAND_SIZE

T = TypeVar("T")


class CLIInterface(GameInterface):
    """Command-line interface for the game."""

    CARD_DISPLAY_WIDTH: ClassVar[int] = 4
    FACE_BACKGROUND_COLOR: ClassVar[str] = "white"
    LUMINANCE_THRESHOLD: ClassVar[float] = 0.179
    MAX_OPPONENT_HANDS_TO_DISPLAY: ClassVar[int] = 1

    def __init__(self) -> None:
        self.console: Console = Console()

    def _get_card_string(self, card: Card) -> Text:
        """Get a rich Text object for a card with appropriate coloring."""
        text: str
        text_color: str

        if card.face_up:
            text = str(card).center(self.CARD_DISPLAY_WIDTH)
            text_color = card.face_color
            background_color = self.FACE_BACKGROUND_COLOR
        else:
            text = "??".center(self.CARD_DISPLAY_WIDTH)
            text_color = "black"
            background_color = card.back_color
            text_color, background_color = (
                str(color)
                for color in modulate(
                    text_color, background_color, mode=ModulationMode.FOREGROUND
                )[:2]
            )
        style = Style(color=text_color, bgcolor=background_color, bold=True)

        try:
            return Text(text, style=style)
        except ColorParseError as e:
            msg = f"Invalid color 'color': {e}"
            raise GameConfigError(msg) from e

    def display_state(self, game: Game) -> None:
        """Display the current state of the game round."""
        if game.current_round is None:
            msg = "Game round is None."
            raise GameConfigError(msg)
        game_round = game.current_round
        top_card_text = self._get_card_string(game_round.deck.peek())
        self.console.print(
            (
                f"\nTurn: {game_round.turn_count} | Deck: {game_round.deck.num_cards} "
                f"cards - Top Card: "
            ),
            style="bold",
            end="",
        )
        self.console.print(top_card_text)
        self._display_discard_pile(game_round)

        for i, player in enumerate(game_round.players):
            is_current_turn_player = i == game_round.current_player_idx
            marker = "*" if is_current_turn_player else " "
            visible_score = calculate_visible_score(player.hand)
            self.console.print(
                f"{marker} Player: {player.name} (Visible Score: {visible_score})"
            )
            if (i - game_round.current_player_idx) % len(
                game.players
            ) <= self.MAX_OPPONENT_HANDS_TO_DISPLAY:
                self.display_hand(player, display_indices=is_current_turn_player)

    def display_round_end(self, game: Game) -> None:
        """Display the state of the game at the end of a round."""
        if game.current_round is None:
            msg = "Game round is None."
            raise GameConfigError(msg)

        self.console.print(
            Panel(f"[bold cyan]--- Round {game.current_round_num} End ---[/bold cyan]")
        )

        for player in game.players:
            round_score = calculate_score(player.hand)
            self.console.print(f"Player: {player.name} (Round Score: {round_score})")
            self.display_hand(player, display_indices=False)

    def _display_discard_pile(self, game_round: Round) -> None:
        """Display the discard pile."""
        top_card = game_round.discard_pile.peek()
        card_text = self._get_card_string(top_card)

        discard_pile_text = "\nDiscard Pile Top Card: "
        line_len = len(discard_pile_text) + len(card_text)
        self.console.print(discard_pile_text, end="")
        self.console.print(card_text)
        self.console.print("-" * line_len)

    def display_hand(self, player: Player, display_indices: bool = False) -> None:
        """Display a player's hand.

        Args:
            player: The player whose hand to display.
            display_indices: Whether to display the position indices of the cards.

        """
        # Display hand in 2 rows with position indicators
        cols = HAND_SIZE // 2

        # Prepare card strings
        row1_cards = player.hand[0:cols]
        row2_cards = player.hand[cols:HAND_SIZE]

        indices_str_2 = ""
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
            self.console.print(self._get_card_string(card), end="")
            if i < len(row1_cards) - 1:
                self.console.print(" ", end="")
        self.console.print(" |")

        # Row 2
        self.console.print("| ", end="")
        for i, card in enumerate(row2_cards):
            self.console.print(self._get_card_string(card), end="")
            if i < len(row2_cards) - 1:
                self.console.print(" ", end="")
        self.console.print(" |")

        self.console.print(border)

        if display_indices:
            self.console.print("  " + indices_str_2)

    def get_input(self, prompt: str | Text) -> str:
        """Get input from the user."""
        return self.console.input(prompt)

    def _get_valid_input(
        self,
        prompt: str | Text,
        valid_options: list[str] | None = None,
        validation_func: Callable[[str], T] | None = None,
        error_msg: str = "Invalid input.",
    ) -> T:
        """Get valid input from the user."""
        while True:
            user_input = self.get_input(prompt)

            if valid_options:
                normalized_input = user_input.lower()
                if normalized_input in valid_options:
                    return cast("T", normalized_input)

            elif validation_func:
                try:
                    return validation_func(user_input)
                except ValueError:
                    pass

            self.display_message(error_msg)

    def _print_card_message(self, parts: list[str | Card]) -> None:
        """Print a message composed of strings and cards."""
        msg = Text()
        for part in parts:
            if isinstance(part, Card):
                msg.append(self._get_card_string(part))
            else:
                msg.append(part)
        self.console.print(msg)

    def get_draw_choice(self, deck_card: Card, discard_card: Card) -> DrawSource:
        """Get the user's choice to draw from the deck or discard pile."""
        deck_card_text = self._get_card_string(deck_card)
        discard_card_text = self._get_card_string(discard_card)
        prompt = Text("Draw from (d)eck ")
        prompt.append(deck_card_text)
        prompt.append(" or (p)ile ")
        prompt.append(discard_card_text)
        prompt.append("? (d/p) ")

        choice = self._get_valid_input(
            prompt,
            valid_options=["d", "p"],
            error_msg="Invalid input. Please enter 'd' or 'p'.",
        )
        if choice == "d":
            return DrawSource.DECK
        return DrawSource.DISCARD

    def get_keep_or_discard_choice(self) -> ActionChoice:
        """Get the user's choice to keep the drawn card or discard it."""
        choice = self._get_valid_input(
            "Action: (k)eep or (d)iscard? (k/d) ",
            valid_options=["k", "d"],
            error_msg="Invalid input. Please enter 'k' or 'd'.",
        )
        if choice == "k":
            return ActionChoice.KEEP
        return ActionChoice.DISCARD

    def get_flip_choice(self) -> FlipChoice:
        """Get the user's choice to flip a card."""
        choice = self._get_valid_input(
            "Flip a card? (y/n) ",
            valid_options=["y", "n"],
            error_msg="Invalid input. Please enter 'y' or 'n'.",
        )
        if choice == "y":
            return FlipChoice.YES
        return FlipChoice.NO

    def get_index_to_replace(self) -> int:
        """Get the index of the card to replace in the hand."""

        def validate(s: str) -> int:
            idx = int(s)
            if 1 <= idx <= HAND_SIZE:
                return idx - 1
            raise ValueError

        return self._get_valid_input(
            "Select which card to replace (1-6)? ",
            validation_func=validate,
            error_msg="Invalid input. Please enter a number between 1 and 6.",
        )

    def get_index_to_flip(self) -> int:
        """Get the index of the card to flip in the hand."""

        def validate(s: str) -> int:
            idx = int(s)
            if 1 <= idx <= HAND_SIZE:
                return idx - 1
            raise ValueError

        return self._get_valid_input(
            "Which card to flip (1-6)? ",
            validation_func=validate,
            error_msg="Invalid input. Please enter a number between 1 and 6.",
        )

    def get_initial_cards_to_flip(self, player: Player, num_to_flip: int) -> list[int]:
        """Get the indices of cards to flip at the start of the round."""
        self.display_initial_flip_prompt(player, num_to_flip)

        # Show initial hand (all face down)
        self.display_hand(player, display_indices=True)

        selected_indices: list[int] = []
        while len(selected_indices) < num_to_flip:
            self.display_initial_flip_selection_prompt(
                len(selected_indices) + 1, num_to_flip
            )
            idx = self.get_index_to_flip()

            if idx in selected_indices:
                self.display_initial_flip_error_already_selected()
            else:
                # Flip the card immediately to show it to the user
                player.hand[idx].face_up = True
                selected_indices.append(idx)
                # Show the hand with the newly flipped card
                self.display_hand(player, display_indices=True)

        return selected_indices

    def display_initial_flip_choices(self, player: Player, choices: list[int]) -> None:
        """Display the choices made for initial cards to flip."""
        cards = [player.hand[i] for i in choices]
        msg_parts: list[str | Card] = [f"{player.name} flipped initial cards: "]
        for i, card in enumerate(cards):
            msg_parts.append(card)
            if i < len(cards) - 1:
                msg_parts.append(", ")
        self._print_card_message(msg_parts)

    def get_valid_flip_index(self, hand: Hand) -> int:
        """Get a valid index of a face-down card to flip."""
        while True:
            idx = self.get_index_to_flip()
            if not hand[idx].face_up:
                return idx
            self.display_message("Card is already face up.")

    def display_drawn_card(self, player: Player, card: Card) -> None:
        """Display the card drawn from the deck."""
        self._print_card_message([f"{player.name} drew: ", card])

    def display_discard_draw(self, player: Player, card: Card) -> None:
        """Display the card drawn from the discard pile."""
        self._print_card_message(
            [
                f"{player.name} drew ",
                card,
                " from the discard pile. They must replace one of their cards with it.",
            ]
        )

    def display_replace_action(
        self, player: Player, index: int, new_card: Card, old_card: Card
    ) -> None:
        """Display the action of replacing a card in hand."""
        self._print_card_message(
            [
                f"{player.name} replaced card at position {index + 1} with ",
                new_card,
                ". Discarded ",
                old_card,
                ".",
            ]
        )

    def display_flip_action(self, player: Player, index: int, card: Card) -> None:
        """Display the action of flipping a card in hand."""
        self._print_card_message(
            [f"{player.name} flipped card at position {index + 1}: ", card]
        )

    def display_turn_start(self, player: Player) -> None:
        """Display the start of a player's turn."""
        self.display_message(f"It's {player.name}'s turn.")

    def display_discard_action(self, player: Player, card: Card) -> None:
        """Display the action of discarding a card."""
        self._print_card_message([f"{player.name} discarded ", card, "."])

    def display_round_start(self, round_num: int) -> None:
        """Display the start of a round."""
        self.console.print(
            Panel(f"[bold cyan]--- Starting Round {round_num} ---[/bold cyan]")
        )

    def display_scores(self, scores: dict[Player, int]) -> None:
        """Display scores. scores is a map of player -> score."""
        self.console.print("\n[bold]Current Scores:[/bold]")
        for player, score in scores.items():
            self.console.print(f"{player.name}: {score}")

    def display_game_over(self) -> None:
        """Display game over message."""
        self.console.print(Panel("[bold red]--- Game Over ---[/bold red]"))

    def display_standings(self, standings: list[tuple[Player, int]]) -> None:
        """Display standings. List of (player, score) tuples, sorted by rank."""
        self.console.print("[bold]Final Standings:[/bold]")
        for i, (player, score) in enumerate(standings):
            color = "green" if i == 0 else "white"
            self.console.print(f"[{color}]{i + 1}. {player.name}: {score}[/{color}]")

    def display_winner(self, winner: Player, score: int) -> None:
        """Display the winner."""
        self.console.print(
            Panel(f"[bold gold1]Winner: {winner.name} with score {score}![/bold gold1]")
        )

    def display_message(self, message: str) -> None:
        """Display a generic message."""
        self.console.print(message)

    def display_initial_flip_prompt(self, player: Player, num_to_flip: int) -> None:
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

    def display_final_turn_notification(self, player: Player) -> None:
        """Notify that a player triggered the final turn."""
        self.console.print(
            Panel(
                f"[bold yellow]{player.name} has revealed all their cards! "
                "Everyone gets one final turn.[/bold yellow]"
            )
        )

    def validate_color(self, color: str) -> None:
        """Validate that a color string is supported by the interface via Rich."""
        try:
            Color.parse(color)
        except ColorParseError as e:
            msg = f"Invalid color '{color}': {e}"
            raise GameConfigError(msg) from e
