import pytest

from pycardgolf.core.hand import Hand
from pycardgolf.core.scoring import calculate_score, calculate_visible_score
from pycardgolf.utils.card import Card
from pycardgolf.utils.constants import HAND_SIZE
from pycardgolf.utils.enums import Rank, Suit


def _make_hand(card_values, color="blue"):
    """Create a hand from a list of tuples (rank, suit)."""
    cards = [Card(rank, suit, color, face_up=True) for rank, suit in card_values]
    return Hand(cards)


@pytest.mark.parametrize(
    ("card_values", "expected_score"),
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
def test_calculate_score_valid_hands(card_values, expected_score):
    """Test various valid 6-card hands."""
    hand = _make_hand(card_values)
    assert calculate_score(hand) == expected_score


def test_calculate_score_none_hand():
    """Test that a None hand raises ValueError."""
    with pytest.raises(ValueError, match="Hand must be a list of"):
        calculate_score(None)


@pytest.mark.parametrize(
    "hand_size",
    [
        pytest.param(0, id="empty_hand"),
        pytest.param(5, id="five_cards"),
        pytest.param(7, id="seven_cards"),
    ],
)
def test_calculate_score_invalid_hand_size(hand_size):
    """Test that non-<HAND_SIZE>-card hands raise ValueError."""
    cards = [Card(Rank.ACE, Suit.CLUBS, "blue") for _ in range(hand_size)]
    hand = Hand(cards)
    with pytest.raises(ValueError, match=f"Hand must be a list of {HAND_SIZE} cards"):
        calculate_score(hand)


def test_calculate_score_face_down_cards():
    """Test that a hand with any face-down cards raises ValueError."""
    hand = _make_hand([(Rank.ACE, Suit.CLUBS)] * HAND_SIZE)
    hand[0].face_up = False
    with pytest.raises(
        ValueError, match="All cards must be face up to calculate score"
    ):
        calculate_score(hand)


@pytest.mark.parametrize(
    ("face_up_indices", "expected_score"),
    [
        pytest.param([], 0, id="all_face_down"),
        pytest.param([0, 4], 2, id="two_aces_no_cancel"),
        pytest.param([0, 3], 0, id="pair_cancels_col_0"),
        pytest.param([1], 1, id="one_card_of_pair_visible"),
        pytest.param([1, 2], 2, id="one_card_of_pair_visible_plus_other"),
        pytest.param([0, 3, 1, 4], 0, id="two_pairs_cancel"),
    ],
)
def test_calculate_visible_score_valid_hands(face_up_indices, expected_score):
    """Test calculating score of only face-up cards."""
    # Hand setup:
    # Col 0: Ace (0), Ace (3)
    # Col 1: Ace (1), Ace (4)
    # Col 2: Ace (2), Ace (5)
    cards = [Card(Rank.ACE, Suit.CLUBS, "blue") for _ in range(HAND_SIZE)]
    hand = Hand(cards)

    for idx in face_up_indices:
        hand[idx].face_up = True

    assert calculate_visible_score(hand) == expected_score


@pytest.mark.parametrize(
    "hand_size",
    [
        pytest.param(0, id="empty_hand"),
        pytest.param(5, id="five_cards"),
        pytest.param(7, id="seven_cards"),
    ],
)
def test_calculate_visible_score_invalid_hand_size(hand_size):
    """Test that non-<HAND_SIZE>-card hands raise ValueError."""
    cards = [Card(Rank.ACE, Suit.CLUBS, "blue") for _ in range(hand_size)]
    hand = Hand(cards)
    with pytest.raises(ValueError, match=f"Hand must be a list of {HAND_SIZE} cards"):
        calculate_visible_score(hand)
