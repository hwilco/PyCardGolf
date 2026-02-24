"""Module containing the Round class using primitive types."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from pycardgolf.core.events import (
    CardDiscardedEvent,
    CardDrawnDeckEvent,
    CardDrawnDiscardEvent,
    CardFlippedEvent,
    CardSwappedEvent,
)
from pycardgolf.core.hand import Hand
from pycardgolf.core.phases import RoundPhase, get_phase_actions, handle_phase_step
from pycardgolf.core.scoring import calculate_score
from pycardgolf.exceptions import GameConfigError, IllegalActionError
from pycardgolf.utils.constants import HAND_SIZE
from pycardgolf.utils.deck import CARDS_PER_DECK, CardStack, Deck
from pycardgolf.utils.mixins import RNGMixin

if TYPE_CHECKING:
    from pycardgolf.core.actions import Action
    from pycardgolf.core.events import GameEvent
    from pycardgolf.utils.types import CardID


class Round(RNGMixin):
    """Class representing a single round of Golf (Primitive Engine Version)."""

    __slots__ = (
        "cards_flipped_in_setup",
        "current_player_idx",
        "deck",
        "discard_pile",
        "drawn_card_id",
        "drawn_from_deck",
        "hands",
        "last_turn_player_idx",
        "num_players",
        "phase",
        "player_names",
        "turn_count",
    )

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
        # In the new version, Deck() just takes num_decks and seed.
        # Deck color is handled by the translation layer.
        self.deck: Deck = Deck(seed=self.rng.randrange(10**9))
        self.discard_pile: CardStack = CardStack(seed=self.rng.randrange(10**9))

        self.current_player_idx: int = 0
        self.last_turn_player_idx: int | None = None
        self.turn_count: int = 1

        self.phase: RoundPhase = RoundPhase.SETUP
        self.drawn_card_id: CardID | None = None
        self.drawn_from_deck: bool = False
        self.cards_flipped_in_setup: dict[int, int] = dict.fromkeys(
            range(self.num_players), 0
        )
        self.hands: list[Hand] = [Hand([]) for _ in range(self.num_players)]

    def clone(self, preserve_rng: bool = False) -> Round:
        """Create a deep copy of the round for tree search simulation."""
        cloned = Round.__new__(Round)

        cloned.player_names = list(self.player_names)
        cloned.num_players = self.num_players

        if preserve_rng:
            self.copy_rng_state(cloned)
        else:
            cloned.reseed(random.randrange(10**9))

        cloned.deck = self.deck.clone(preserve_rng=preserve_rng)
        cloned.discard_pile = self.discard_pile.clone(preserve_rng=preserve_rng)
        cloned.hands = [h.clone() for h in self.hands]

        cloned.phase = self.phase
        cloned.current_player_idx = self.current_player_idx
        cloned.turn_count = self.turn_count
        cloned.last_turn_player_idx = self.last_turn_player_idx
        cloned.drawn_card_id = self.drawn_card_id
        cloned.drawn_from_deck = self.drawn_from_deck
        cloned.cards_flipped_in_setup = dict(self.cards_flipped_in_setup)

        return cloned

    def get_current_player_idx(self) -> int:
        """Return the index of the player whose turn it is."""
        return self.current_player_idx

    def get_valid_actions(self, player_idx: int) -> list[Action]:
        """Return a list of valid actions for the given player."""
        return get_phase_actions(self, player_idx)

    @classmethod
    def validate_config(cls, num_players: int) -> None:
        """Validate game configuration before starting a round."""
        cards_needed_for_hands = num_players * HAND_SIZE
        if cards_needed_for_hands >= CARDS_PER_DECK:
            msg = (
                f"Not enough cards for players. "
                f"{num_players} players need {cards_needed_for_hands + 1} cards, "
                f"but deck only has {CARDS_PER_DECK} cards."
            )
            raise GameConfigError(msg)

    def step(self, action: Action) -> list[GameEvent]:
        """Advance the game state by one step based on the action."""
        return handle_phase_step(self, action)

    def draw_from_deck(self, player_idx: int) -> CardDrawnDeckEvent:
        """Draw a card from the deck."""
        card_id = self.deck.draw()
        self.drawn_card_id = card_id
        self.drawn_from_deck = True
        return CardDrawnDeckEvent(player_idx=player_idx, card_id=card_id)

    def draw_from_discard(self, player_idx: int) -> CardDrawnDiscardEvent:
        """Draw a card from the discard pile."""
        if self.discard_pile.num_cards == 0:
            msg = "Discard pile is empty."
            raise IllegalActionError(msg)
        card_id = self.discard_pile.draw()
        self.drawn_card_id = card_id
        self.drawn_from_deck = False
        return CardDrawnDiscardEvent(player_idx=player_idx, card_id=card_id)

    def swap_drawn_card(self, player_idx: int, hand_index: int) -> CardSwappedEvent:
        """Swap the drawn card with a card in hand."""
        if self.drawn_card_id is None:
            msg = "No card drawn."
            raise IllegalActionError(msg)

        hand = self.hands[player_idx]
        old_card_id = hand.replace(hand_index, self.drawn_card_id)
        self.discard_pile.add_card(old_card_id)

        event = CardSwappedEvent(
            player_idx=player_idx,
            hand_index=hand_index,
            new_card_id=self.drawn_card_id,
            old_card_id=old_card_id,
        )
        self.drawn_card_id = None
        return event

    def discard_drawn_card(self, player_idx: int) -> CardDiscardedEvent:
        """Discard the previously drawn card."""
        if self.drawn_card_id is None:
            msg = "No card drawn."
            raise IllegalActionError(msg)

        self.discard_pile.add_card(self.drawn_card_id)
        event = CardDiscardedEvent(player_idx=player_idx, card_id=self.drawn_card_id)
        self.drawn_card_id = None
        return event

    def flip_card_in_hand(self, player_idx: int, hand_index: int) -> CardFlippedEvent:
        """Flip a card in hand face up."""
        hand = self.hands[player_idx]
        if hand.is_face_up(hand_index):
            msg = "Card already face up."
            raise IllegalActionError(msg)

        hand.flip_card(hand_index)
        return CardFlippedEvent(
            player_idx=player_idx,
            hand_index=hand_index,
            card_id=hand[hand_index],
        )

    def reveal_hands(self) -> None:
        """Reveal all cards for all players."""
        for hand in self.hands:
            hand.reveal_all()

    def get_scores(self) -> dict[int, int]:
        """Calculate scores for all players."""
        return {i: calculate_score(hand) for i, hand in enumerate(self.hands)}

    def __repr__(self) -> str:
        return f"Round(phase={self.phase.name}, num_players={self.num_players})"


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
        Round.validate_config(round_obj.num_players)

        # Initialize hands immediately
        round_obj.deck.shuffle()
        for i in range(round_obj.num_players):
            cards = [round_obj.deck.draw() for _ in range(HAND_SIZE)]
            round_obj.hands[i] = Hand(cards)

        # Start discard pile
        card_id = round_obj.deck.draw()
        round_obj.discard_pile.add_card(card_id)

        return round_obj
