"""Module containing the RandomBot player class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pycardgolf.players.player import BasePlayer
from pycardgolf.utils.mixins import RNGMixin

if TYPE_CHECKING:
    from pycardgolf.core.actions import Action
    from pycardgolf.core.observation import Observation


class RandomBot(BasePlayer, RNGMixin):
    """A bot player that makes random moves.

    ``RandomBot`` requires no interface — it selects uniformly at random
    from the available valid actions returned in the observation.
    """

    def __init__(
        self,
        name: str,
        seed: int | None = None,
    ) -> None:
        """Initialize the bot with a name and an optional RNG seed."""
        BasePlayer.__init__(self, name)
        RNGMixin.__init__(self, seed=seed)

    def get_action(self, observation: Observation) -> Action:
        """Decide on an action given the current observation."""
        if not observation.valid_actions:
            # Should not occur in a valid game state unless the game is over
            msg = "No valid actions found."
            raise RuntimeError(msg)
        return self.rng.choice(observation.valid_actions)
