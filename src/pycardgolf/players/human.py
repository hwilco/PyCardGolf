"""Module containing the HumanPlayer class."""

from __future__ import annotations

from pycardgolf.core.actions import (
    Action,
    ActionDiscardDrawn,
    ActionDrawDeck,
    ActionDrawDiscard,
    ActionFlipCard,
    ActionPass,
    ActionSwapCard,
)
from pycardgolf.core.state import Observation, RoundPhase
from pycardgolf.interfaces.base import (
    ActionChoice,
    DrawSource,
    FlipChoice,
    GameInterface,
)
from pycardgolf.players.player import BasePlayer


class HumanPlayer(BasePlayer):
    """A human player that interacts via the game interface.

    All notifications and prompts should be delegated to the interface. Only
    the player's internal logic should be implemented here.
    """

    def __init__(self, name: str, interface: GameInterface) -> None:
        """Initialize the human player with a name and interface."""
        super().__init__(name, interface)

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

        # Default fallback (should not happen in valid state)
        return ActionPass()

    def _handle_setup_phase(self, _observation: Observation) -> Action:
        self.interface.display_hand(self, display_indices=True)
        # Note: Logic for "initial cards to flip" was complex in old round.
        # Here we just pick ONE card. The engine repeats until enough flipped.
        while True:
            idx = self.interface.get_index_to_flip()
            # Validate that card is not currently face up.
            # Engine syncs player.hand, so checking self.hand is safe.
            if self.hand[idx].face_up:
                self.interface.display_initial_flip_error_already_selected()
            else:
                return ActionFlipCard(hand_index=idx)

    def _handle_draw_phase(self, observation: Observation) -> Action:
        deck_card = observation.deck_top
        discard_card = observation.discard_top
        choice = self.interface.get_draw_choice(deck_card, discard_card)
        if choice == DrawSource.DISCARD:
            return ActionDrawDiscard()
        return ActionDrawDeck()

    def _handle_action_phase(self, observation: Observation) -> Action:
        # We have a drawn card (in observation.drawn_card).
        # Ask Keep or Discard

        can_discard = observation.can_discard_drawn

        if can_discard:
            choice = self.interface.get_keep_or_discard_choice()
            if choice == ActionChoice.DISCARD:
                return ActionDiscardDrawn()

        # If can't discard, or card is kept, proceed to swap
        idx = self.interface.get_index_to_replace()
        return ActionSwapCard(hand_index=idx)

    def _handle_flip_phase(self, _: Observation) -> Action:
        choice = self.interface.get_flip_choice()
        if choice == FlipChoice.YES:
            idx = self.interface.get_valid_flip_index(self.hand)
            return ActionFlipCard(hand_index=idx)
        return ActionPass()
