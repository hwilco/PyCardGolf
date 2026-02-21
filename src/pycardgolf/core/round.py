"""Module containing the Round class."""

from __future__ import annotations

import random
import sys
from typing import TYPE_CHECKING

from pycardgolf.core.hand import Hand
from pycardgolf.core.phases import RoundPhase, get_valid_actions, handle_step
from pycardgolf.core.scoring import calculate_score

if TYPE_CHECKING:
    from pycardgolf.core.actions import Action
    from pycardgolf.core.events import GameEvent
    from pycardgolf.utils.card import Card
from pycardgolf.exceptions import GameConfigError
from pycardgolf.utils.constants import HAND_SIZE
from pycardgolf.utils.deck import CardStack, Deck


class Round:
    """Class representing a single round of Golf (Engine Version)."""

    def __init__(
        self,
        player_names: list[str],
        seed: int | None = None,
    ) -> None:
        """Initialize a round with players."""
        self.player_names: list[str] = player_names
        self.num_players: int = len(player_names)
        self.seed: int = seed if seed is not None else random.randrange(sys.maxsize)
        self._rng: random.Random = random.Random(self.seed)

        # Game State
        deck_color = "blue"
        deck_seed = self._rng.randrange(sys.maxsize)
        self.deck: Deck = Deck(back_color=deck_color, seed=deck_seed)

        discard_seed = self._rng.randrange(sys.maxsize)
        self.discard_pile: CardStack = CardStack(seed=discard_seed)

        self.current_player_idx: int = 0
        self.last_turn_player_idx: int | None = None
        self.turn_count: int = 1

        self.phase: RoundPhase = RoundPhase.SETUP
        self.drawn_card: Card | None = None
        self.drawn_from_deck: bool = False
        self.cards_flipped_in_setup: dict[int, int] = dict.fromkeys(
            range(self.num_players), 0
        )
        self.hands: list[Hand] = []

        # Validate configuration
        self.validate_config(self.num_players, self.deck.num_cards)

        # Initialize hands immediately
        self.deck.shuffle()
        for _ in range(self.num_players):
            cards = [self.deck.draw() for _ in range(HAND_SIZE)]
            self.hands.append(Hand(cards))

        # Start discard pile
        card = self.deck.draw()
        card.face_up = True
        self.discard_pile.add_card(card)

    def get_current_player_idx(self) -> int:
        """Return the index of the player whose turn it is."""
        return self.current_player_idx

    def get_valid_actions(self, player_idx: int) -> list[Action]:
        """Return a list of valid actions for the given player."""
        return get_valid_actions(self, player_idx)

    @classmethod
    def validate_config(cls, num_players: int, deck_size: int = 52) -> None:
        """Validate game configuration before starting a round.

        Args:
            num_players: Number of players in the game.
            deck_size (optional): Number of cards in the deck. Defaults to 52.

        Raises:
            GameConfigError: If there are not enough cards for the number of players.

        """
        cards_needed_for_hands = num_players * HAND_SIZE
        if cards_needed_for_hands >= deck_size:
            msg = (
                f"Not enough cards for players. "
                f"{num_players} players need {cards_needed_for_hands + 1} cards, "
                f"but deck only has {deck_size} cards."
            )
            raise GameConfigError(msg)

    def step(self, action: Action) -> list[GameEvent]:
        """Advance the game state by one step based on the action."""
        return handle_step(self, action)

    def reveal_hands(self) -> None:
        """Reveal all cards for all players."""
        for hand in self.hands:
            hand.reveal_all()

    def get_scores(self) -> dict[int, int]:
        """Calculate scores for all players."""
        return {i: calculate_score(hand) for i, hand in enumerate(self.hands)}

    def __repr__(self) -> str:
        return f"Round(phase={self.phase}, num_players={self.num_players})"
