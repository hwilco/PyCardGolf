"""Module containing the HumanPlayer class."""

from __future__ import annotations

from typing import TYPE_CHECKING

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

if TYPE_CHECKING:
    from pycardgolf.core.observation import Observation

from pycardgolf.interfaces.base import (
    ActionChoice,
    DrawSource,
    FlipChoice,
    GameInput,
)
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
        self.input_handler.display_hand(self, display_indices=True)
        # Keep asking until the player picks a face-down card
        while True:
            idx = self.input_handler.get_index_to_flip()
            if self.hand[idx].face_up:
                self.input_handler.display_initial_flip_error_already_selected()
            else:
                return ActionFlipCard(hand_index=idx)

    def _handle_draw_phase(self, observation: Observation) -> Action:
        deck_card = observation.deck_top
        discard_card = observation.discard_top
        choice = self.input_handler.get_draw_choice(deck_card, discard_card)
        if choice == DrawSource.DISCARD:
            return ActionDrawDiscard()
        return ActionDrawDeck()

    def _handle_action_phase(self, observation: Observation) -> Action:
        can_discard = observation.can_discard_drawn
        if can_discard:
            choice = self.input_handler.get_keep_or_discard_choice()
            if choice == ActionChoice.DISCARD:
                return ActionDiscardDrawn()
        idx = self.input_handler.get_index_to_replace()
        return ActionSwapCard(hand_index=idx)

    def _handle_flip_phase(self, _: Observation) -> Action:
        choice = self.input_handler.get_flip_choice()
        if choice == FlipChoice.YES:
            idx = self.input_handler.get_valid_flip_index(self.hand)
            return ActionFlipCard(hand_index=idx)
        return ActionPass()
