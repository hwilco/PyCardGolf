"""Module containing the CLI input handler implementation."""

import sys
import time
from collections.abc import Callable
from typing import TypeVar, cast

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

    def get_valid_input(
        self,
        prompt: str | Text,
        valid_options: list[str] | None = None,
        validation_func: Callable[[str], T] | None = None,
        error_msg: str = "Invalid input.",
    ) -> T:
        """Get valid input from the user."""
        while True:
            user_input = self.get_input(prompt)

            if user_input.lower() in ("q", "quit"):
                raise GameExitError

            if valid_options:
                normalized_input = user_input.lower()
                if normalized_input in valid_options:
                    return cast("T", normalized_input)

            elif validation_func:
                try:
                    return validation_func(user_input)
                except ValueError:
                    pass

            self.console.print(error_msg)
