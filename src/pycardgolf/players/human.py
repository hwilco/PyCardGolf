"""Module containing the HumanPlayer class."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pycardgolf.core.observation import Observation
    from pycardgolf.interfaces.base import GameInput

from pycardgolf.core.actions import (
    Action,
    ActionDiscardDrawn,
    ActionDrawDeck,
    ActionDrawDiscard,
    ActionFlipCard,
    ActionPass,
    ActionSwapCard,
)
from pycardgolf.core.phases import RoundPhase
from pycardgolf.players.player import BasePlayer
from pycardgolf.utils.enums import DrawSourceChoice, KeepOrDiscardChoice


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
        if observation.phase == RoundPhase.SETUP:
            return self._handle_setup_phase(observation)
        if observation.phase == RoundPhase.DRAW:
            return self._handle_draw_phase(observation)
        if observation.phase == RoundPhase.ACTION:
            return self._handle_action_phase(observation)
        if observation.phase == RoundPhase.FLIP:
            return self._handle_flip_phase(observation)

        # Default fallback — should not occur in a valid game state
        return ActionPass()

    def _handle_setup_phase(self, _observation: Observation) -> Action:
        idx = self.input_handler.get_valid_flip_index(self)
        return ActionFlipCard(hand_index=idx)

    def _handle_draw_phase(self, observation: Observation) -> Action:
        deck_card = observation.deck_top
        discard_card = observation.discard_top
        choice = self.input_handler.get_draw_choice(self, deck_card, discard_card)
        if choice == DrawSourceChoice.DISCARD_PILE:
            return ActionDrawDiscard()
        return ActionDrawDeck()

    def _handle_action_phase(self, observation: Observation) -> Action:
        can_discard = observation.can_discard_drawn
        if can_discard:
            choice = self.input_handler.get_keep_or_discard_choice(self)
            if choice == KeepOrDiscardChoice.DISCARD:
                return ActionDiscardDrawn()
        idx = self.input_handler.get_index_to_replace(self)
        return ActionSwapCard(hand_index=idx)

    def _handle_flip_phase(self, _: Observation) -> Action:
        wants_flip = self.input_handler.get_flip_choice(self)
        if wants_flip:
            idx = self.input_handler.get_valid_flip_index(self)
            return ActionFlipCard(hand_index=idx)
        return ActionPass()
