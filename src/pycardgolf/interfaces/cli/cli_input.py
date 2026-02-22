"""Module containing the CLI input handler implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from pycardgolf.exceptions import GameExitError
from pycardgolf.interfaces.base import GameInput
from pycardgolf.utils.constants import HAND_SIZE
from pycardgolf.utils.enums import DrawSourceChoice, KeepOrDiscardChoice

if TYPE_CHECKING:
    from collections.abc import Callable

    from rich.console import Console
    from rich.text import Text

    from pycardgolf.interfaces.cli.cli_renderer import CLIRenderer
    from pycardgolf.players import BasePlayer
    from pycardgolf.utils.card import Card


T = TypeVar("T")


class CLIInputHandler(GameInput):
    """Input handler for the CLI interface."""

    def __init__(self, console: Console, renderer: CLIRenderer) -> None:
        self.console = console
        self.renderer = renderer

    def get_input(self, prompt: str | Text) -> str:
        """Get input from the user."""
        return self.console.input(prompt)

    def get_choice(
        self,
        prompt: str | Text,
        valid_options: list[str],
        error_msg: str = "Invalid input.",
        capitilization_sensitive: bool = False,
    ) -> str:
        """Get a valid choice from limited options from the user.

        Args:
            prompt: The prompt to display to the user.
            valid_options: A list of valid options strings.
            error_msg: The error message to display if the input is invalid.
            capitilization_sensitive: Whether to check capitalization.

        Returns:
            The valid option selected by the user.

        Raises:
            GameExitError: If the user inputs 'q' or 'quit'.

        """
        while True:
            user_input = self.get_input(prompt)

            if user_input.lower() in ("q", "quit"):
                raise GameExitError

            normalized_input = (
                user_input.lower() if not capitilization_sensitive else user_input
            )
            if normalized_input in valid_options:
                return normalized_input

            self.console.print(error_msg)

    def get_validated_input(
        self,
        prompt: str | Text,
        validation_func: Callable[[str], T],
        error_msg: str = "Invalid input.",
    ) -> T:
        """Get valid input using a custom validation function.

        Args:
            prompt: The prompt to display to the user.
            validation_func: A function that takes input string and returns
                validated value or raises ValueError.
            error_msg: The error message to display if validation fails.

        Returns:
            The validated input value.

        Raises:
            GameExitError: If the user inputs 'q' or 'quit'.

        """
        while True:
            user_input = self.get_input(prompt)

            if user_input.lower() in ("q", "quit"):
                raise GameExitError

            try:
                return validation_func(user_input)
            except ValueError:
                self.console.print(error_msg)

    def get_draw_choice(
        self, player: BasePlayer, deck_card: Card | None, discard_card: Card | None
    ) -> DrawSourceChoice:
        """Get the user's choice to draw from the deck or discard pile."""
        prompt = self.renderer.create_draw_choice_prompt(deck_card, discard_card)
        self.console.print(f"{player.name}'s turn:")
        choice = self.get_choice(
            prompt,
            valid_options=["d", "p"],
            error_msg="Invalid input. Please enter 'd' or 'p'.",
        )
        if choice == "d":
            return DrawSourceChoice.DECK
        return DrawSourceChoice.DISCARD_PILE

    def get_keep_or_discard_choice(self, player: BasePlayer) -> KeepOrDiscardChoice:
        """Get the user's choice to keep the drawn card or discard it."""
        choice = self.get_choice(
            f"{player.name}, (k)eep or (d)iscard? (k/d) ",
            valid_options=["k", "d"],
            error_msg="Invalid input. Please enter 'k' or 'd'.",
            capitilization_sensitive=False,
        )
        if choice == "k":
            return KeepOrDiscardChoice.KEEP
        return KeepOrDiscardChoice.DISCARD

    def get_flip_choice(self, player: BasePlayer) -> bool:
        """Get the user's choice to flip a card."""
        choice = self.get_choice(
            f"{player.name}, flip a card? (y/n) ",
            valid_options=["y", "n"],
            error_msg="Invalid input. Please enter 'y' or 'n'.",
            capitilization_sensitive=False,
        )
        return choice == "y"

    def _validate_card_index(self, s: str) -> int:
        """Validate input is a valid card index mapping to 0-based index."""
        idx = int(s)
        if 1 <= idx <= HAND_SIZE:
            return idx - 1
        msg = f"Card index must be between 1 and {HAND_SIZE}. Got: {s}"
        raise ValueError(msg)

    def get_index_to_replace(self, player: BasePlayer) -> int:
        """Get the index of the card to replace in the hand."""
        self.renderer.display_hand(player, display_indices=True)
        return self.get_validated_input(
            "Select which card to replace (1-6): ",
            validation_func=self._validate_card_index,
            error_msg="Invalid input. Please enter a number between 1 and 6.",
        )

    def get_index_to_flip(self, player: BasePlayer) -> int:
        """Get the index of the card to flip in the hand."""
        self.renderer.display_hand(player, display_indices=True)
        return self.get_validated_input(
            "Select which card to flip (1-6): ",
            validation_func=self._validate_card_index,
            error_msg="Invalid input. Please enter a number between 1 and 6.",
        )

    def get_valid_flip_index(self, player: BasePlayer) -> int:
        """Get a valid index of a face-down card to flip."""
        # Show hand for context (especially critical in setup phase)
        self.renderer.display_hand(player, display_indices=True)

        face_down_indices = [
            str(i + 1) for i, card in enumerate(player.hand) if not card.face_up
        ]
        choice = self.get_choice(
            f"Select which card to flip (1-{HAND_SIZE}): ",
            valid_options=face_down_indices,
            error_msg=(
                f"Invalid input. Please select a face-down card. ({face_down_indices})"
            ),
        )
        return int(choice) - 1
