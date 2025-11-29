import pytest
from pycardgolf.core.scoring import calculate_score
from pycardgolf.utils.enums import Rank, Suit
from pycardgolf.utils.card import Card


# Helper function to create a hand from rank tuples
def _make_hand(ranks, color="blue"):
    """Create a hand from a list of 6 rank tuples (rank, suit)."""
    return [Card(rank, suit, color) for rank, suit in ranks]


@pytest.mark.parametrize(
    "ranks,expected_score",
    [
        pytest.param(
            [
                (Rank.ACE, Suit.CLUBS),
                (Rank.TWO, Suit.CLUBS),
                (Rank.THREE, Suit.CLUBS),
                (Rank.FOUR, Suit.CLUBS),
                (Rank.FIVE, Suit.CLUBS),
                (Rank.SIX, Suit.CLUBS),
            ],
            17,
            id="simple_sum_no_pairs",
        ),
        pytest.param(
            [
                (Rank.FIVE, Suit.CLUBS),
                (Rank.TWO, Suit.CLUBS),
                (Rank.THREE, Suit.CLUBS),
                (Rank.FIVE, Suit.DIAMONDS),
                (Rank.FOUR, Suit.CLUBS),
                (Rank.SIX, Suit.CLUBS),
            ],
            11,
            id="one_pair_cancels",
        ),
        pytest.param(
            [
                (Rank.KING, Suit.CLUBS),
                (Rank.QUEEN, Suit.CLUBS),
                (Rank.JACK, Suit.CLUBS),
                (Rank.KING, Suit.DIAMONDS),
                (Rank.TWO, Suit.CLUBS),
                (Rank.ACE, Suit.CLUBS),
            ],
            19,
            id="face_cards_and_king_pair",
        ),
        pytest.param(
            [
                (Rank.KING, Suit.CLUBS),
                (Rank.THREE, Suit.CLUBS),
                (Rank.FOUR, Suit.CLUBS),
                (Rank.FIVE, Suit.CLUBS),
                (Rank.SIX, Suit.CLUBS),
                (Rank.SEVEN, Suit.CLUBS),
            ],
            25,
            id="king_worth_zero",
        ),
        pytest.param(
            [
                (Rank.THREE, Suit.CLUBS),
                (Rank.SEVEN, Suit.CLUBS),
                (Rank.NINE, Suit.CLUBS),
                (Rank.THREE, Suit.DIAMONDS),
                (Rank.SEVEN, Suit.HEARTS),
                (Rank.NINE, Suit.SPADES),
            ],
            0,
            id="all_pairs_cancel",
        ),
        pytest.param(
            [
                (Rank.TWO, Suit.CLUBS),
                (Rank.TWO, Suit.DIAMONDS),
                (Rank.TWO, Suit.HEARTS),
                (Rank.KING, Suit.CLUBS),
                (Rank.KING, Suit.DIAMONDS),
                (Rank.KING, Suit.SPADES),
            ],
            -6,
            id="negative_score",
        ),
        pytest.param(
            [
                (Rank.KING, Suit.CLUBS),
                (Rank.KING, Suit.DIAMONDS),
                (Rank.KING, Suit.HEARTS),
                (Rank.KING, Suit.SPADES),
                (Rank.KING, Suit.CLUBS),
                (Rank.KING, Suit.DIAMONDS),
            ],
            0,
            id="all_kings",
        ),
    ],
)
def test_calculate_score_valid_hands(ranks, expected_score):
    """Test various valid 6-card hands."""
    hand = _make_hand(ranks)
    assert calculate_score(hand) == expected_score


@pytest.mark.parametrize(
    "hand_size",
    [
        pytest.param(0, id="empty_hand"),
        pytest.param(5, id="five_cards"),
        pytest.param(7, id="seven_cards"),
    ],
)
def test_calculate_score_invalid_hand_size(hand_size):
    """Test that non-6-card hands raise ValueError."""
    hand = [Card(Rank.ACE, Suit.CLUBS, "blue") for _ in range(hand_size)]
    with pytest.raises(ValueError, match="Hand must be a list of 6 cards"):
        calculate_score(hand)
