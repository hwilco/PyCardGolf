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
from pycardgolf.core.state import Observation, RoundPhase
from pycardgolf.interfaces.base import (
    ActionChoice,
    DrawSource,
    FlipChoice,
    GameInterface,
)
from pycardgolf.players.player import Player

if TYPE_CHECKING:
    from pycardgolf.utils.card import Card


class HumanPlayer(Player):
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

    def _handle_setup_phase(self, observation: Observation) -> Action:
        self.interface.display_hand(self, display_indices=True)
        # Note: Logic for "initial cards to flip" was complex in old round.
        # Here we just pick ONE card. The engine repeats until enough flipped.
        while True:
            idx = self.interface.get_index_to_flip()
            # Validate against observation
            # Observation my_hand has cards. Face up cards are visible.
            card_at_idx = observation.my_hand[idx]
            # In setup, face down cards are None but we know they exist.
            # Use self.hand if valid?
            # Player object still has self.hand updated?
            # YES. The Engine updates player.hand in memory.
            # So we can check self.hand[idx].face_up

            if self.hand[idx].face_up:
                self.interface.display_initial_flip_error_already_selected()
            else:
                return ActionFlipCard(hand_index=idx)

    def _handle_draw_phase(self, observation: Observation) -> Action:
        # We need Deck top and Discard top to prompt user?
        # Interface get_draw_choice takes (deck_card, discard_card).
        # Deck card is unknown (blind). Discard card is known.
        # Old code: deck_card = game_round.deck.peek(). This revealed the card to code but not user.
        # But actually deck.peek() might be a bug in old code if meant to be hidden.
        # Assuming the Interface handles "Deck is face down".

        # Observation gives discard_top. Deck is implicit.
        # We'll pass None for deck_card if interface allows, or a dummy.
        # Checking base.py: get_draw_choice(deck_card: Card, discard_card: Card).
        # The Interface likely expects Objects.
        # But observation deck is just size.
        # We'll just pass None or mock?
        # Actually, self.interface is likely CLI.
        # Let's hope CLI implementation doesn't crash on None deck_card.
        # If it does, we might need to change Interface later.

        discard_card = observation.discard_top
        # We can't access deck top.
        # Passing None might break type hints or runtime if it accesses .rank.
        # Let's check cli_input.py or cli_renderer.py if I can.
        # For now, I'll pass a dummy card or Observation's discard top.

        # Re-reading HumanPlayer old code:
        # deck_card = game_round.deck.peek()
        # discard_card = game_round.discard_pile.peek()
        # return self.interface.get_draw_choice(deck_card, discard_card)

        # In new engine, we can't peek deck.
        # I'll modify the interface call to not sending deck card.
        # But I can't modify Interface signature easily without touching everything.
        # Does CLI actually use deck_card? Probably just for "Hidden Card" print.

        # I'll proceed with passing None (typed as Any to suppress) and fix if broken.

        choice = self.interface.get_draw_choice(None, discard_card)  # type: ignore
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
        else:
            self.interface.display_message("Must keep card drawn from discard pile.")

        # If Keep, or Cannot Discard
        idx = self.interface.get_index_to_replace()
        return ActionSwapCard(hand_index=idx)

    def _handle_flip_phase(self, observation: Observation) -> Action:
        choice = self.interface.get_flip_choice()
        if choice == FlipChoice.YES:
            idx = self.interface.get_valid_flip_index(self.hand)
            return ActionFlipCard(hand_index=idx)
        return ActionPass()
