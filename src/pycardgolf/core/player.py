"""Module containing the abstract Player class."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pycardgolf.core.round import Round
    from pycardgolf.utils.card import Card


class Player(ABC):
    """Abstract base class for a game player."""

    def __init__(self, name: str) -> None:
        """Initialize a player with a name."""
        self.name: str = name
        self.hand: list[Card] = []
        self.score: int = 0

    @abstractmethod
    def take_turn(self, game_round: "Round") -> None:
        """Execute the player's turn."""
