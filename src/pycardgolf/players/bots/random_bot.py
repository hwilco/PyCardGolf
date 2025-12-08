"""Module containing the RandomBot player class."""

from __future__ import annotations

import random
import sys
from typing import TYPE_CHECKING

from pycardgolf.core.actions import Action, ActionPass
from pycardgolf.core.state import Observation
from pycardgolf.interfaces.base import GameInterface
from pycardgolf.interfaces.null import NullGameInterface
from pycardgolf.players.player import Player

if TYPE_CHECKING:
    pass


class RandomBot(Player):
    """A bot player that makes random moves."""

    def __init__(
        self,
        name: str,
        interface: GameInterface | None = None,
        seed: int = random.randrange(sys.maxsize),
    ) -> None:
        """Initialize the bot with a name and optional seed for random numbers."""
        if interface is None:
            interface = NullGameInterface()
        super().__init__(name, interface)
        self.seed = seed
        self._random = random.Random(self.seed)

    def get_action(self, observation: Observation) -> Action:
        """Decide on an action given the current observation."""
        if not observation.valid_actions:
            # Should not happen in a valid game state unless game is over
            return ActionPass()
        return self._random.choice(observation.valid_actions)
