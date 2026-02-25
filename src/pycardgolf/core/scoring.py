"""Module containing scoring logic using CardIDs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pycardgolf.utils.card import get_rank
from pycardgolf.utils.constants import HAND_SIZE
from pycardgolf.utils.deck import Rank

if TYPE_CHECKING:
    from pycardgolf.core.hand import Hand
    from pycardgolf.utils.types import CardID


def calculate_score(hand: Hand) -> int:
    """Calculate the score for a hand of cards in Golf."""
    if hand is None or len(hand) != HAND_SIZE:
        msg = f"Hand must be a list of {HAND_SIZE} cards. Received: {hand}"
        raise ValueError(msg)

    if not hand.all_face_up():
        face_down_indices = [i for i in range(len(hand)) if not hand.is_face_up(i)]
        msg = f"All cards must be face up to calculate score. Cards in indices \
        {face_down_indices} are face down"
        raise ValueError(msg)

    # Score by column
    score = 0
    for col in range(hand.cols):
        col_card_ids = hand.get_column(col)
        col_score = 0
        first_rank = get_rank(col_card_ids[0])
        # If only one row, same rank cards don't cancel
        all_same_rank = hand.rows > 1

        for i in range(len(col_card_ids)):
            if get_rank(col_card_ids[i]) != first_rank:
                all_same_rank = False
            col_score += _card_value(col_card_ids[i])

        if all_same_rank:
            continue  # If all cards are the same rank, the column cancels

        score += col_score
    return score


def calculate_visible_score(hand: Hand) -> int:
    """Calculate the score for a hand based ONLY on face-up cards."""
    if hand is None or len(hand) != HAND_SIZE:
        msg = f"Hand must have {HAND_SIZE} cards. Received: {hand}"
        raise ValueError(msg)

    score = 0
    for col in range(hand.cols):
        col_card_ids = hand.get_column(col)
        col_score = 0
        all_face_up = True
        first_rank = get_rank(col_card_ids[0])
        # If only one row, same rank cards don't cancel
        all_same_rank = hand.rows > 1

        for row in range(hand.rows):
            idx = col + row * hand.cols
            if not hand.is_face_up(idx):
                all_face_up = False
            else:
                col_score += _card_value(col_card_ids[row])

            if get_rank(col_card_ids[row]) != first_rank:
                all_same_rank = False

        if all_face_up and all_same_rank:
            continue  # If all cards are the same rank, the column cancels

        score += col_score
    return score


def _card_value(card_id: CardID) -> int:
    rank = get_rank(card_id)
    match rank:
        case Rank.HIDDEN:
            msg = "Cannot calculate value of face-down card"
            raise ValueError(msg)
        case Rank.ACE:
            return 1
        case Rank.TWO:
            return -2
        case Rank.KING:
            return 0
        case Rank.JACK | Rank.QUEEN:
            return 10
        case _:
            return rank.value[0]
