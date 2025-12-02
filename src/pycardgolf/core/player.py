"""Module containing the abstract Player class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pycardgolf.core.hand import Hand
    from pycardgolf.core.round import Round


class Player(ABC):
    """Abstract base class for a game player."""

    def __init__(self, name: str) -> None:
        """Initialize a player with a name."""
        self.name: str = name
        self.hand: Hand | None = None
        self.score: int = 0

    @abstractmethod
    def take_turn(self, game_round: Round) -> None:
        """Execute the player's turn."""
