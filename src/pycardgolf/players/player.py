"""Module containing the abstract Player class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pycardgolf.core.hand import Hand

if TYPE_CHECKING:
    from pycardgolf.core.actions import Action
    from pycardgolf.core.state import Observation
    from pycardgolf.interfaces.base import GameInterface


class BasePlayer(ABC):
    """Abstract base class for a game player."""

    def __init__(self, name: str, interface: GameInterface) -> None:
        """Initialize a player with a name."""
        self.name: str = name
        self.hand: Hand = Hand([])
        self.interface: GameInterface = interface

    @abstractmethod
    def get_action(self, observation: Observation) -> Action:
        """Decide on an action given the current observation."""

    def __repr__(self) -> str:
        return f"Player(name={self.name}, hand={self.hand})"
