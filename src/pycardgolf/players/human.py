"""Module containing the HumanPlayer class."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pycardgolf.core.actions import Action
    from pycardgolf.core.observation import Observation
    from pycardgolf.interfaces.base import GameInput
from pycardgolf.players.player import BasePlayer


class HumanPlayer(BasePlayer):
    """A human player that delegates all decisions to a ``GameInput`` handler.

    All notifications and prompts are issued through ``self.input_handler``.
    Only decision-routing logic lives in this class.
    """

    def __init__(self, name: str, input_handler: GameInput) -> None:
        """Initialize the human player with a name and an input handler."""
        super().__init__(name)
        self.input_handler: GameInput = input_handler

    def get_action(self, observation: Observation) -> Action:
        """Decide on an action given the current observation."""
        return self.input_handler.get_action(self, observation)
