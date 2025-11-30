"""Module containing the abstract GameInterface class."""

from abc import ABC, abstractmethod
from typing import Any


class GameInterface(ABC):
    """Abstract base class for game interfaces."""

    @abstractmethod
    def display_state(self, game_round: Any) -> None:
        """Display the current state of the game round."""

    @abstractmethod
    def get_input(self, prompt: str) -> str:
        """Get input from the user."""

    @abstractmethod
    def notify(self, message: str) -> None:
        """Notify the user of an event."""
