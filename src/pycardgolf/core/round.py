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
from pycardgolf.core.events import (
    CardDiscardedEvent,
    CardDrawnDeckEvent,
    CardDrawnDiscardEvent,
    CardFlippedEvent,
    CardSwappedEvent,
)
from pycardgolf.exceptions import GameConfigError, IllegalActionError
from pycardgolf.utils.constants import HAND_SIZE
from pycardgolf.utils.deck import CardStack, Deck
from pycardgolf.utils.mixins import RNGMixin


class Round(RNGMixin):
    """Class representing a single round of Golf (Engine Version)."""

    def __init__(
        self,
        player_names: list[str],
        seed: int | None = None,
    ) -> None:
        """Initialize a round with players."""
        super().__init__(seed=seed)
        self.player_names: list[str] = player_names
        self.num_players: int = len(player_names)

        # Game State
        deck_color = "blue"
        deck_seed = self.rng.randrange(sys.maxsize)
        self.deck: Deck = Deck(back_color=deck_color, seed=deck_seed)

        discard_seed = self.rng.randrange(sys.maxsize)
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
        self.hands: list[Hand] = [Hand([]) for _ in range(self.num_players)]

    def clone(self, preserve_rng: bool = False) -> Round:
        """Create a deep copy of the round for tree search simulation.

        Args:
            preserve_rng: If True, copies the exact random number generator state.
                If False (default), creates a new randomized seed for the clone.

        """
        # Bypass __init__ to avoid expensive setup (deck creation/shuffling)
        cloned = Round.__new__(Round)

        cloned.player_names = self.player_names.copy()
        cloned.num_players = self.num_players

        cloned.rng = random.Random()
        if preserve_rng:
            self.copy_rng_state(cloned)
        else:
            cloned.seed = random.randrange(sys.maxsize)
            cloned.rng = random.Random(cloned.seed)

        cloned.deck = self.deck.clone(preserve_rng=preserve_rng)
        cloned.discard_pile = self.discard_pile.clone(preserve_rng=preserve_rng)
        cloned.hands = [h.clone() for h in self.hands]

        cloned.phase = self.phase
        cloned.current_player_idx = self.current_player_idx
        cloned.turn_count = self.turn_count
        cloned.last_turn_player_idx = self.last_turn_player_idx
        cloned.drawn_card = self.drawn_card.clone() if self.drawn_card else None
        cloned.drawn_from_deck = self.drawn_from_deck
        cloned.cards_flipped_in_setup = self.cards_flipped_in_setup.copy()

        return cloned

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

    def draw_from_deck(self, player_idx: int) -> CardDrawnDeckEvent:
        """Draw a card from the deck."""
        card = self.deck.draw()
        card.face_up = True
        self.drawn_card = card
        self.drawn_from_deck = True
        return CardDrawnDeckEvent(player_idx=player_idx, card=card)

    def draw_from_discard(self, player_idx: int) -> CardDrawnDiscardEvent:
        """Draw a card from the discard pile."""
        if self.discard_pile.num_cards == 0:
            msg = "Discard pile is empty."
            raise IllegalActionError(msg)
        card = self.discard_pile.draw()
        self.drawn_card = card
        self.drawn_from_deck = False
        return CardDrawnDiscardEvent(player_idx=player_idx, card=card)

    def swap_drawn_card(self, player_idx: int, hand_index: int) -> CardSwappedEvent:
        """Swap the drawn card with a card in hand."""
        if self.drawn_card is None:
            msg = "No card drawn."
            raise IllegalActionError(msg)

        hand = self.hands[player_idx]
        old_card = hand.replace(hand_index, self.drawn_card)
        old_card.face_up = True
        self.discard_pile.add_card(old_card)
        event = CardSwappedEvent(
            player_idx=player_idx,
            hand_index=hand_index,
            new_card=self.drawn_card,
            old_card=old_card,
        )
        self.drawn_card = None
        return event

    def discard_drawn_card(self, player_idx: int) -> CardDiscardedEvent:
        """Discard the previously drawn card."""
        if self.drawn_card is None:
            msg = "No card drawn."
            raise IllegalActionError(msg)

        self.discard_pile.add_card(self.drawn_card)
        event = CardDiscardedEvent(player_idx=player_idx, card=self.drawn_card)
        self.drawn_card = None
        return event

    def flip_card_in_hand(self, player_idx: int, hand_index: int) -> CardFlippedEvent:
        """Flip a card in hand face up."""
        hand = self.hands[player_idx]
        if hand[hand_index].face_up:
            msg = "Card already face up."
            raise IllegalActionError(msg)

        hand.flip_card(hand_index)
        return CardFlippedEvent(
            player_idx=player_idx,
            hand_index=hand_index,
            card=hand[hand_index],
        )

    def reveal_hands(self) -> None:
        """Reveal all cards for all players."""
        for hand in self.hands:
            hand.reveal_all()

    def get_scores(self) -> dict[int, int]:
        """Calculate scores for all players."""
        return {i: calculate_score(hand) for i, hand in enumerate(self.hands)}

    def __repr__(self) -> str:
        return f"Round(phase={self.phase}, num_players={self.num_players})"


class RoundFactory:
    """Factory for creating and setting up rounds."""

    @staticmethod
    def create_standard_round(
        player_names: list[str],
        seed: int | None = None,
    ) -> Round:
        """Create a standard round, including dealing cards to players."""
        round_obj = Round(player_names=player_names, seed=seed)

        # Validate configuration
        Round.validate_config(round_obj.num_players, round_obj.deck.num_cards)

        # Initialize hands immediately
        round_obj.deck.shuffle()
        for i in range(round_obj.num_players):
            cards = [round_obj.deck.draw() for _ in range(HAND_SIZE)]
            round_obj.hands[i] = Hand(cards)

        # Start discard pile
        card = round_obj.deck.draw()
        card.face_up = True
        round_obj.discard_pile.add_card(card)

        return round_obj
