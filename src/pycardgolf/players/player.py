"""Module containing the abstract BasePlayer class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pycardgolf.core.actions import Action
    from pycardgolf.core.observation import Observation


class BasePlayer(ABC):
    """Abstract base class for a game player.

    Players receive an ``Observation`` and return an ``Action``.  They are
    deliberately decoupled from any display or input interface — that
    responsibility belongs to implementations (like ``HumanPlayer`` which
    holds a ``GameInput``) or is handled by ``Game`` itself.
    """

    def __init__(self, name: str) -> None:
        """Initialize the player with a name."""
        self.name: str = name

    @abstractmethod
    def get_action(self, observation: Observation) -> Action:
        """Decide on an action given the current observation."""

    def __repr__(self) -> str:
        return f"Player(name={self.name})"
