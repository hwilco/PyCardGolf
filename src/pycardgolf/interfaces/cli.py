"""Module containing the CLI (command-line interface) implementation."""

from typing import TYPE_CHECKING

from rich.console import Console

from pycardgolf.core.game import Game
from pycardgolf.core.player import Player
from pycardgolf.core.stats import PlayerStats
from pycardgolf.interfaces.base import (
    ActionChoice,
    DrawSource,
    FlipChoice,
    GameInterface,
)
from pycardgolf.interfaces.cli_input import CLIInputHandler
from pycardgolf.interfaces.cli_renderer import CLIRenderer
from pycardgolf.utils.card import Card
from pycardgolf.utils.constants import HAND_SIZE

if TYPE_CHECKING:
    from rich.text import Text

    from pycardgolf.core.hand import Hand


class CLIInterface(GameInterface):
    """Command-line interface for the game."""

    def __init__(self, delay: float = 0.0) -> None:
        self.console = Console()
        self.renderer = CLIRenderer(self.console)
        self.input_handler = CLIInputHandler(self.console, delay)

    def wait_for_enter(self) -> None:
        """Wait for the configured delay. Key press skips delay."""
        self.input_handler.wait_for_enter()

    def display_state(self, game: Game) -> None:
        """Display the current state of the game round."""
        self.renderer.display_state(game)

    def display_round_end(self, game: Game) -> None:
        """Display the state of the game at the end of a round."""
        self.renderer.display_round_end(game)

    def display_hand(self, player: Player, display_indices: bool = False) -> None:
        """Display a player's hand."""
        self.renderer.display_hand(player, display_indices)

    def get_input(self, prompt: "str | Text") -> str:
        """Get input from the user."""
        return self.input_handler.get_input(prompt)

    def get_draw_choice(self, deck_card: Card, discard_card: Card) -> DrawSource:
        """Get the user's choice to draw from the deck or discard pile."""
        prompt = self.renderer.create_draw_choice_prompt(deck_card, discard_card)
        choice = self.input_handler.get_valid_input(
            prompt,
            valid_options=["d", "p"],
            error_msg="Invalid input. Please enter 'd' or 'p'.",
        )
        if choice == "d":
            return DrawSource.DECK
        return DrawSource.DISCARD

    def get_keep_or_discard_choice(self) -> ActionChoice:
        """Get the user's choice to keep the drawn card or discard it."""
        choice = self.input_handler.get_valid_input(
            "Action: (k)eep or (d)iscard? (k/d) ",
            valid_options=["k", "d"],
            error_msg="Invalid input. Please enter 'k' or 'd'.",
        )
        if choice == "k":
            return ActionChoice.KEEP
        return ActionChoice.DISCARD

    def get_flip_choice(self) -> FlipChoice:
        """Get the user's choice to flip a card."""
        choice = self.input_handler.get_valid_input(
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

        return self.input_handler.get_valid_input(
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

        return self.input_handler.get_valid_input(
            "Which card to flip (1-6)? ",
            validation_func=validate,
            error_msg="Invalid input. Please enter a number between 1 and 6.",
        )

    def get_initial_cards_to_flip(self, player: Player, num_to_flip: int) -> list[int]:
        """Get the indices of cards to flip at the start of the round."""
        self.renderer.display_initial_flip_prompt(player, num_to_flip)

        # Show initial hand (all face down)
        self.renderer.display_hand(player, display_indices=True)

        selected_indices: list[int] = []
        while len(selected_indices) < num_to_flip:
            self.renderer.display_initial_flip_selection_prompt(
                len(selected_indices) + 1, num_to_flip
            )
            idx = self.get_index_to_flip()

            if idx in selected_indices:
                self.renderer.display_initial_flip_error_already_selected()
            else:
                # Flip the card immediately to show it to the user
                player.hand[idx].face_up = True
                selected_indices.append(idx)
                # Show the hand with the newly flipped card
                self.renderer.display_hand(player, display_indices=True)

        return selected_indices

    def display_initial_flip_choices(self, player: Player, choices: list[int]) -> None:
        """Display the choices made for initial cards to flip."""
        self.renderer.display_initial_flip_choices(player, choices)

    def get_valid_flip_index(self, hand: "Hand") -> int:  # type: ignore[name-defined]
        """Get a valid index of a face-down card to flip."""
        # Note: hand type hint uses string forward ref or needs import if used.
        # Original cli.py imported Hand? Yes. I missed Hand import.
        # Adding Hand import to be safe, or use type checking block.
        # Original used `from pycardgolf.core.hand import Hand`.
        while True:
            idx = self.get_index_to_flip()
            if not hand[idx].face_up:
                return idx
            self.renderer.display_message("Card is already face up.")

    def display_drawn_card(self, player: Player, card: Card) -> None:
        """Display the card drawn from the deck."""
        self.renderer.display_drawn_card(player, card)
        self.wait_for_enter()

    def display_discard_draw(self, player: Player, card: Card) -> None:
        """Display the card drawn from the discard pile."""
        self.renderer.display_discard_draw(player, card)
        self.wait_for_enter()

    def display_replace_action(
        self, player: Player, index: int, new_card: Card, old_card: Card
    ) -> None:
        """Display the action of replacing a card in hand."""
        self.renderer.display_replace_action(player, index, new_card, old_card)
        self.wait_for_enter()

    def display_flip_action(self, player: Player, index: int, card: Card) -> None:
        """Display the action of flipping a card in hand."""
        self.renderer.display_flip_action(player, index, card)
        self.wait_for_enter()

    def display_turn_start(self, player: Player) -> None:
        """Display the start of a player's turn."""
        self.renderer.display_turn_start(player)
        self.wait_for_enter()

    def display_discard_action(self, player: Player, card: Card) -> None:
        """Display the action of discarding a card."""
        self.renderer.display_discard_action(player, card)
        self.wait_for_enter()

    def display_round_start(self, round_num: int) -> None:
        """Display the start of a round."""
        self.renderer.display_round_start(round_num)
        self.wait_for_enter()

    def display_scores(self, scores: dict[Player, int]) -> None:
        """Display scores. scores is a map of player -> score."""
        self.renderer.display_scores(scores)
        self.wait_for_enter()

    def display_game_over(self) -> None:
        """Display game over message."""
        self.renderer.display_game_over()

    def display_standings(self, standings: list[tuple[Player, int]]) -> None:
        """Display standings. List of (player, score) tuples, sorted by rank."""
        self.renderer.display_standings(standings)

    def display_winner(self, winner: Player, score: int) -> None:
        """Display the winner."""
        self.renderer.display_winner(winner, score)

    def display_message(self, message: str) -> None:
        """Display a generic message."""
        self.renderer.display_message(message)

    def display_initial_flip_prompt(self, player: Player, num_to_flip: int) -> None:
        """Prompt player to select initial cards to flip."""
        self.renderer.display_initial_flip_prompt(player, num_to_flip)

    def display_initial_flip_selection_prompt(
        self, current_count: int, total_count: int
    ) -> None:
        """Prompt to select a specific card during initial flip."""
        self.renderer.display_initial_flip_selection_prompt(current_count, total_count)

    def display_initial_flip_error_already_selected(self) -> None:
        """Error when selecting an already selected card during initial flip."""
        self.renderer.display_initial_flip_error_already_selected()

    def display_final_turn_notification(self, player: Player) -> None:
        """Notify that a player triggered the final turn."""
        self.renderer.display_final_turn_notification(player)

    def validate_color(self, color: str) -> None:
        """Validate that a color string is supported by the interface via Rich."""
        self.renderer.validate_color(color)

    def display_game_stats(self, stats: dict[Player, PlayerStats]) -> None:
        """Display game statistics."""
        self.renderer.display_game_stats(stats)
