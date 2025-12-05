"""Module containing the RandomBot player class."""

import random
import sys

from pycardgolf.core.round import Round
from pycardgolf.interfaces.base import GameInterface
from pycardgolf.players.bots.bot_player import BotPlayer
from pycardgolf.utils.card import Card
from pycardgolf.utils.constants import HAND_SIZE


class RandomBot(BotPlayer):
    """A bot player that makes random moves."""

    def __init__(
        self,
        name: str,
        interface: GameInterface,
        seed: int = random.randrange(sys.maxsize),
    ) -> None:
        """Initialize the bot with a name and optional seed for random numbers."""
        super().__init__(name, interface)
        self.seed = seed
        self._random = random.Random(self.seed)

    def choose_draw_source(self, game_round: Round) -> str:
        """Decide whether to draw from deck ('d') or discard pile ('p')."""
        # Check if pile has cards
        if game_round.discard_pile.num_cards > 0 and self._random.choices(
            [True, False]
        ):
            return "p"
        return "d"

    def should_keep_drawn_card(self, card: Card, game_round: Round) -> bool:
        """Decide whether to keep a card drawn from the deck."""
        _ = card
        _ = game_round
        return self._random.choice([True, False])

    def choose_card_to_replace(self, new_card: Card, game_round: Round) -> int:
        """Choose which card index (0-based) to replace with the new card."""
        _ = new_card
        _ = game_round
        return random.randint(0, HAND_SIZE - 1)

    def choose_card_to_flip(self, game_round: Round) -> int | None:
        """Choose which card index (0-based) to flip, or None to skip."""
        _ = game_round
        if self._random.choice([True, False]):
            # Find face down cards
            face_down_indices = [i for i, c in enumerate(self.hand) if not c.face_up]
            if face_down_indices:
                return self._random.choice(face_down_indices)
        return None
