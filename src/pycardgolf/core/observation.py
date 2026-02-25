"""Module for building sanitized observations from Game state."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pycardgolf.core.phases import ActionPhaseState
from pycardgolf.utils.card import get_masked_id

if TYPE_CHECKING:
    from pycardgolf.core.actions import Action
    from pycardgolf.core.hand import Hand
    from pycardgolf.core.phases import RoundPhase
    from pycardgolf.core.round import Round
    from pycardgolf.utils.types import CardID


@dataclass
class Observation:
    """A sanitized (no info on face-down cards) view of the game state for a player."""

    my_hand: list[CardID]
    other_hands: dict[str, list[CardID]]
    discard_top: CardID | None
    deck_size: int
    deck_top: CardID | None
    current_player_name: str
    phase: RoundPhase
    valid_actions: list[Action]
    drawn_card_id: CardID | None = None
    can_discard_drawn: bool = False


class ObservationBuilder:
    """Class to build sanitized observations for a player."""

    @classmethod
    def build(cls, round_state: Round, player_idx: int) -> Observation:
        """Create a sanitized observation of the round for a specific player."""
        # Sanitized hand for player
        my_hand_view = cls.sanitize_hand(round_state.hands[player_idx])

        # Other players' hands
        other_hands_view = {}
        for i, name in enumerate(round_state.player_names):
            if i != player_idx:
                other_hands_view[name] = cls.sanitize_hand(round_state.hands[i])

        # Deck top: sanitized
        deck_top = None
        if round_state.deck.num_cards > 0:
            deck_top = get_masked_id(round_state.deck.peek())

        can_discard = False
        if round_state.current_player_idx == player_idx and isinstance(
            round_state.phase_state, ActionPhaseState
        ):
            can_discard = round_state.phase_state.drawn_from_deck

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
            drawn_card_id=(
                round_state.drawn_card_id
                if round_state.current_player_idx == player_idx
                else None
            ),
            can_discard_drawn=can_discard,
        )

    @classmethod
    def sanitize_hand(cls, hand: Hand) -> list[CardID]:
        """Return a list of sanitized CardIDs for a hand."""
        sanitized = []
        for i, card_id in enumerate(hand):
            if hand.is_face_up(i):
                sanitized.append(card_id)
            else:
                sanitized.append(get_masked_id(card_id))
        return sanitized
