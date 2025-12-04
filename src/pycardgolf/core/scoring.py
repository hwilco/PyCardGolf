"""Module containing scoring logic."""

from pycardgolf.core.hand import Hand
from pycardgolf.utils.card import Card
from pycardgolf.utils.constants import HAND_SIZE
from pycardgolf.utils.enums import Rank


def calculate_score(hand: Hand) -> int:
    """Calculate the score for a hand of cards in Golf.

    Scoring rules:
    - Pairs in a column cancel out (score 0).
    - Ace: 1
    - 2: -2
    - 3-10: Face value
    - Jack, Queen: 10
    - King: 0
    """
    # Validate hand
    if hand is None:
        msg = "Hand must not be None"
        raise ValueError(msg)

    if hand is None or len(hand) != HAND_SIZE:
        msg = f"Hand must be a list of {HAND_SIZE} cards. Received: {hand}"
        raise ValueError(msg)

    if not hand.all_face_up():
        face_up_indices = [i for i, card in enumerate(hand) if not card.face_up]
        msg = f"All cards must be face up to calculate score. Cards in indices \
        {face_up_indices} are face down"
        raise ValueError(msg)

    score = 0

    # Check columns
    for col in range(hand.cols):
        top_card, bottom_card = hand.get_column(col)

        if top_card.rank == bottom_card.rank:
            continue  # Pair cancels out

        score += _card_value(top_card)
        score += _card_value(bottom_card)

    return score


def calculate_visible_score(hand: Hand) -> int:
    """Calculate the score for a hand based ONLY on face-up cards.

    Pairs only cancel out if both cards in the column are face up.
    """
    if len(hand) != HAND_SIZE:
        msg = f"Hand must be a list of {HAND_SIZE} cards"
        raise ValueError(msg)

    score = 0

    # Check columns
    for col in range(hand.cols):
        top_card, bottom_card = hand.get_column(col)

        # Check for visible pair
        if (
            top_card.face_up
            and bottom_card.face_up
            and top_card.rank == bottom_card.rank
        ):
            continue  # Pair cancels out

        if top_card.face_up:
            score += _card_value(top_card)
        if bottom_card.face_up:
            score += _card_value(bottom_card)

    return score


def _card_value(card: Card) -> int:
    match card.rank:
        case Rank.ACE:
            return 1
        case Rank.TWO:
            return -2
        case Rank.KING:
            return 0
        case Rank.JACK | Rank.QUEEN:
            return 10
        case _:
            return card.rank.value[0]
