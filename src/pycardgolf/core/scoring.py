from typing import List
from pycardgolf.utils.enums import Rank
from pycardgolf.utils.card import Card


def calculate_score(hand: List[Card]) -> int:
    """
    Calculate the score for a hand of cards in Golf.
    Standard 6-card Golf scoring (simplified for now, can be expanded).

    Basic rules assumed:
    - Pairs in a column cancel out (score 0).
    - Ace: 1
    - 2: -2
    - 3-10: Face value
    - Jack, Queen: 10
    - King: 0
    """
    score = 0
    # Assuming hand is a 1D list representing a 2x3 grid:
    # 0 1 2
    # 3 4 5

    if len(hand) != 6:
        raise ValueError("Hand must be a list of 6 cards")

    # Check columns
    for col in range(3):
        top_card = hand[col]
        bottom_card = hand[col + 3]

        if top_card.rank == bottom_card.rank:
            continue  # Pair cancels out

        score += _card_value(top_card)
        score += _card_value(bottom_card)

    return score


def _card_value(card: Card) -> int:
    if card.rank == Rank.ACE:
        return 1
    elif card.rank == Rank.TWO:
        return -2
    elif card.rank == Rank.KING:
        return 0
    elif card.rank in (Rank.JACK, Rank.QUEEN):
        return 10
    else:
        return card.rank.value[0]
