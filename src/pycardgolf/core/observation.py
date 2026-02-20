"""Module for building sanitized observations from Game state."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pycardgolf.utils.card import Card
from pycardgolf.utils.enums import Rank, Suit

if TYPE_CHECKING:
    from pycardgolf.core.actions import Action
    from pycardgolf.core.phases import RoundPhase
    from pycardgolf.core.round import Round


@dataclass
class Observation:
    """A sanitized view of the game state for a player."""

    my_hand: list[Card]  # Face down cards object with face_up=False
    other_hands: dict[str, list[Card]]
    discard_top: Card | None
    deck_size: int
    deck_top: Card | None  # Top card of deck (sanitized/dummy if strictly face down)
    current_player_name: str
    phase: RoundPhase
    valid_actions: list[Action]
    # Additional info needed for decision making
    drawn_card: Card | None = None  # Only visible if in ACTION/FLIP phase and drawn
    can_discard_drawn: bool = False  # True if drawn from Deck


class ObservationBuilder:
    """Class to build sanitized observations for a player."""

    @classmethod
    def build(cls, round_state: Round, player_idx: int) -> Observation:
        """Create a sanitized observation of the round for a specific player.

        This ensures that players only see face-up cards (other than their own
        unseen cards which are returned as dummy objects).
        """
        # Current player's hand: sanitized copy
        my_hand_view = cls._sanitize_cards(list(round_state.hands[player_idx]))

        # Other players' hands: sanitized copies
        other_hands_view = {}
        for i, name in enumerate(round_state.player_names):
            if i != player_idx:
                other_hands_view[name] = cls._sanitize_cards(list(round_state.hands[i]))

        # Deck top: dummy/hidden if available
        deck_top = None
        if round_state.deck.num_cards > 0:
            deck_top = cls._sanitize_card(round_state.deck.peek())

        return Observation(
            my_hand=my_hand_view,
            other_hands=other_hands_view,
            discard_top=(
                None
                if round_state.discard_pile.num_cards == 0
                else round_state.discard_pile.peek()
            ),
            deck_size=round_state.deck.num_cards,
            deck_top=deck_top,
            current_player_name=round_state.player_names[
                round_state.current_player_idx
            ],
            phase=round_state.phase,
            valid_actions=round_state.get_valid_actions(player_idx),
            drawn_card=(
                round_state.drawn_card
                if round_state.current_player_idx == player_idx
                else None
            ),
            can_discard_drawn=(
                round_state.drawn_from_deck
                if round_state.current_player_idx == player_idx
                else False
            ),
        )

    @classmethod
    def _sanitize_card(cls, card: Card) -> Card:
        """Return a safe copy of a card.

        If face_up, returns a full copy.
        If face_down, returns a dummy card with hidden rank/suit.
        """
        if card.face_up:
            return copy.copy(card)
        return Card(
            rank=Rank.HIDDEN,
            suit=Suit.HIDDEN,
            back_color=card.back_color,
            face_color="?",
            face_up=False,
        )

    @classmethod
    def _sanitize_cards(cls, cards: list[Card]) -> list[Card]:
        """Return a list of sanitized cards."""
        return [cls._sanitize_card(card) for card in cards]
