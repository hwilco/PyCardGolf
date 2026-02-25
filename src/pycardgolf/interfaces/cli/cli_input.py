"""Module containing the CLI input handler implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pycardgolf.core.actions import Action, ActionSpace
from pycardgolf.core.hand import Hand
from pycardgolf.core.phases import RoundPhase
from pycardgolf.exceptions import GameExitError
from pycardgolf.interfaces.base import GameInput
from pycardgolf.utils.constants import HAND_SIZE

if TYPE_CHECKING:
    from collections.abc import Callable

    from rich.console import Console
    from rich.text import Text

    from pycardgolf.core.observation import Observation
    from pycardgolf.interfaces.cli.cli_renderer import CLIRenderer
    from pycardgolf.players import BasePlayer


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

    def get_validated_input[T](
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

    def get_action(self, player: BasePlayer, observation: Observation) -> Action:
        """Get the user's action based on the current phase."""
        if observation.phase == RoundPhase.SETUP:
            return self._handle_setup_phase(player, observation)
        if observation.phase == RoundPhase.DRAW:
            return self._handle_draw_phase(player, observation)
        if observation.phase == RoundPhase.ACTION:
            return self._handle_action_phase(player, observation)
        if observation.phase == RoundPhase.FLIP:
            return self._handle_flip_phase(player, observation)

        return ActionSpace.PASS

    def _handle_setup_phase(
        self, player: BasePlayer, observation: Observation
    ) -> Action:
        idx = self._get_valid_flip_index(player, observation)
        return ActionSpace.FLIP[idx]

    def _handle_draw_phase(
        self, player: BasePlayer, observation: Observation
    ) -> Action:
        prompt = self.renderer.create_draw_choice_prompt(
            observation.deck_top, observation.discard_top
        )
        self.console.print(f"{player.name}'s turn:")
        choice = self.get_choice(
            prompt,
            valid_options=["d", "p"],
            error_msg="Invalid input. Please enter 'd' or 'p'.",
        )
        if choice == "d":
            return ActionSpace.DRAW_DECK
        return ActionSpace.DRAW_DISCARD

    def _handle_action_phase(
        self, player: BasePlayer, observation: Observation
    ) -> Action:
        if observation.can_discard_drawn:
            choice = self.get_choice(
                f"{player.name}, (k)eep or (d)iscard? (k/d) ",
                valid_options=["k", "d"],
                error_msg="Invalid input. Please enter 'k' or 'd'.",
                capitilization_sensitive=False,
            )
            if choice == "d":
                return ActionSpace.DISCARD_DRAWN

        obs_hand = Hand(observation.my_hand, face_up_mask=(1 << HAND_SIZE) - 1)
        self.renderer.display_hand(obs_hand, display_indices=True)
        idx = self.get_validated_input(
            "Select which card to replace (1-6): ",
            validation_func=self._validate_card_index,
            error_msg="Invalid input. Please enter a number between 1 and 6.",
        )
        return ActionSpace.SWAP[idx]

    def _handle_flip_phase(
        self, player: BasePlayer, observation: Observation
    ) -> Action:
        choice = self.get_choice(
            f"{player.name}, flip a card? (y/n) ",
            valid_options=["y", "n"],
            error_msg="Invalid input. Please enter 'y' or 'n'.",
            capitilization_sensitive=False,
        )
        if choice == "y":
            idx = self._get_valid_flip_index(player, observation)
            return ActionSpace.FLIP[idx]
        return ActionSpace.PASS

    def _validate_card_index(self, s: str) -> int:
        """Validate input is a valid card index mapping to 0-based index."""
        try:
            idx = int(s)
        except (ValueError, TypeError) as e:
            msg = f"Not a valid number: {s}"
            raise ValueError(msg) from e

        if 1 <= idx <= HAND_SIZE:
            return idx - 1
        msg = f"Card index must be between 1 and {HAND_SIZE}. Got: {s}"
        raise ValueError(msg)

    def _get_valid_flip_index(
        self, player: BasePlayer, observation: Observation
    ) -> int:
        """Get a valid index of a face-down card to flip."""
        # Show hand for context (especially critical in setup phase)
        # player name is used in other contexts, but here we just need observation
        _ = player  # Explicitly mark as unused
        obs_hand = Hand(observation.my_hand, face_up_mask=(1 << HAND_SIZE) - 1)
        self.renderer.display_hand(obs_hand, display_indices=True)

        face_down_indices = [
            str(i + 1) for i, card_id in enumerate(observation.my_hand) if card_id < 0
        ]
        choice = self.get_choice(
            f"Select which card to flip (1-{HAND_SIZE}): ",
            valid_options=face_down_indices,
            error_msg=(
                f"Invalid input. Please select a face-down card. ({face_down_indices})"
            ),
        )
        return int(choice) - 1
