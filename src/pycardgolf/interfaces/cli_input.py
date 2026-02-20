"""Module containing the CLI input handler implementation."""

import sys
import time
from collections.abc import Callable
from typing import TypeVar

from rich.console import Console
from rich.text import Text

from pycardgolf.exceptions import GameConfigError, GameExitError

try:
    import msvcrt
except ImportError:
    msvcrt = None  # type: ignore[assignment]

try:
    import select
except ImportError:
    select = None  # type: ignore[assignment]


T = TypeVar("T")


class CLIInputHandler:
    """Input handler for the CLI interface."""

    def __init__(self, console: Console, delay: float = 0.0) -> None:
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
                if msvcrt.kbhit():
                    msvcrt.getch()
                    break
                time.sleep(0.05)

        elif select:
            # Unix / Linux / macOS
            while time.time() < end_time:
                # Check for input availability (non-blocking)
                dr, _, _ = select.select([sys.stdin], [], [], 0)
                if dr:
                    # Input available, read line to consume (assuming Enter pressed)
                    sys.stdin.readline()
                    break
                time.sleep(0.05)

        else:
            # Fallback
            time.sleep(self.delay)

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
