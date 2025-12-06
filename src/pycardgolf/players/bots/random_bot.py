"""Module containing the RandomBot player class."""

import random
import sys

from pycardgolf.core.player import Player
from pycardgolf.core.round import Round
from pycardgolf.interfaces.base import DrawSource, GameInterface
from pycardgolf.interfaces.null import NullGameInterface
from pycardgolf.utils.card import Card
from pycardgolf.utils.constants import HAND_SIZE


class RandomBot(Player):
    """A bot player that makes random moves."""

    def __init__(
        self,
        name: str,
        interface: GameInterface | None = None,
        seed: int = random.randrange(sys.maxsize),
    ) -> None:
        """Initialize the bot with a name and optional seed for random numbers.

        Args:
            name: The name of the bot.
            interface: The interface to use for communication with the bot. Optional.
                Defaults to NullGameInterface if no interface is provided.
            seed: Random seed for reproducibility. Defaults to a random value.

        """
        if interface is None:
            interface = NullGameInterface()
        super().__init__(name, interface)
        self.seed = seed
        self._random = random.Random(self.seed)

    def _choose_draw_source(self, game_round: Round) -> DrawSource:
        """Decide whether to draw from deck or discard pile."""
        # Check if pile has cards
        if game_round.discard_pile.num_cards > 0 and self._random.choices(
            [True, False]
        ):
            return DrawSource.DISCARD
        return DrawSource.DECK

    def _should_keep_drawn_card(self, card: Card, game_round: Round) -> bool:
        """Decide whether to keep a card drawn from the deck."""
        _ = card
        _ = game_round
        return self._random.choice([True, False])

    def _choose_card_to_replace(self, new_card: Card, game_round: Round) -> int:
        """Choose which card index (0-based) to replace with the new card."""
        _ = new_card
        _ = game_round
        return random.randint(0, HAND_SIZE - 1)

    def _choose_card_to_flip_after_discard(self, game_round: Round) -> int | None:
        """Choose card index (0-based) to flip after discarding, or None."""
        _ = game_round
        if self._random.choice([True, False]):
            # Find face down cards
            face_down_indices = [i for i, c in enumerate(self.hand) if not c.face_up]
            if face_down_indices:
                return self._random.choice(face_down_indices)
        return None

    def choose_initial_card_to_flip(self, game_round: Round) -> int:
        """Choose one card to flip at the start of the round."""
        _ = game_round
        face_down_indices = [i for i, c in enumerate(self.hand) if not c.face_up]
        if not face_down_indices:
            # Should not happen if logic is correct
            return 0
        return self._random.choice(face_down_indices)
