"""Module containing scoring logic."""

from pycardgolf.utils.card import Card
from pycardgolf.utils.constants import HAND_SIZE
from pycardgolf.utils.enums import Rank


def calculate_score(hand: list[Card]) -> int:
    """Calculate the score for a hand of cards in Golf.

    Scoring rules:
    - Pairs in a column cancel out (score 0).
    - Ace: 1
    - 2: -2
    - 3-10: Face value
    - Jack, Queen: 10
    - King: 0
    """
    score = 0
    # Assuming hand is a 1D list representing a 2xHAND_SIZE//2 grid:
    # 0 1 2
    # 3 4 5

    if len(hand) != HAND_SIZE:
        msg = f"Hand must be a list of {HAND_SIZE} cards"
        raise ValueError(msg)

    # Check columns
    for col in range(HAND_SIZE // 2):
        top_card = hand[col]
        bottom_card = hand[col + HAND_SIZE // 2]

        if top_card.rank == bottom_card.rank:
            continue  # Pair cancels out

        score += _card_value(top_card)
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
