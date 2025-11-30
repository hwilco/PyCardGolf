"""Module containing scoring logic."""

from pycardgolf.utils.card import Card
from pycardgolf.utils.enums import Rank


def calculate_score(hand: list[Card]) -> int:
    """Calculate the score for a hand of cards in Golf.

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

    # 3 4 5
    hand_size = 6
    if len(hand) != hand_size:
        msg = f"Hand must be a list of {hand_size} cards"
        raise ValueError(msg)

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
    if card.rank == Rank.TWO:
        return -2
    if card.rank == Rank.KING:
        return 0
    if card.rank in (Rank.JACK, Rank.QUEEN):
        return 10
    return card.rank.value[0]
