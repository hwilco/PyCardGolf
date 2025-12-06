"""Module containing the HumanPlayer class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pycardgolf.core.player import Player
from pycardgolf.interfaces.base import (
    ActionChoice,
    DrawSource,
    FlipChoice,
    GameInterface,
)

if TYPE_CHECKING:
    from pycardgolf.core.game import Game
    from pycardgolf.core.round import Round
    from pycardgolf.utils.card import Card


class HumanPlayer(Player):
    """A human player that interacts via the game interface.

    All notifications and prompts should be delegated to the interface. Only
    the player's internal logic should be implemented here.
    """

    def __init__(self, name: str, interface: GameInterface) -> None:
        """Initialize the human player with a name and interface."""
        super().__init__(name, interface)

    def take_turn(self, game: Game) -> None:
        """Execute the human player's turn."""
        self.interface.display_state(game)
        super().take_turn(game)

    def _choose_draw_source(self, game_round: Round) -> DrawSource:
        """Decide whether to draw from deck or discard pile."""
        deck_card = game_round.deck.peek()
        discard_card = game_round.discard_pile.peek()
        return self.interface.get_draw_choice(deck_card, discard_card)

    def _should_keep_drawn_card(self, card: Card, game_round: Round) -> bool:
        """Decide whether to keep a card drawn from the deck."""
        _ = card
        _ = game_round
        choice = self.interface.get_keep_or_discard_choice()
        return choice == ActionChoice.KEEP

    def _choose_card_to_replace(self, new_card: Card, game_round: Round) -> int:
        """Choose which card index (0-based) to replace with the new card."""
        _ = new_card
        _ = game_round
        return self.interface.get_index_to_replace()

    def _choose_card_to_flip_after_discard(self, game_round: Round) -> int | None:
        """Choose card index (0-based) to flip after discarding, or None."""
        _ = game_round
        choice = self.interface.get_flip_choice()
        if choice == FlipChoice.YES:
            return self.interface.get_valid_flip_index(self.hand)
        return None

    def choose_initial_card_to_flip(self, game_round: Round) -> int:
        """Select one card to flip at the start of the round."""
        _ = game_round
        self.interface.display_hand(self, display_indices=True)

        while True:
            # Note: Round (Engine) handles the overall loop. We just pick one.
            idx = self.interface.get_index_to_flip()

            if self.hand[idx].face_up:
                self.interface.display_initial_flip_error_already_selected()
            else:
                return idx
