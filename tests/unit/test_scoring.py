import pytest

from pycardgolf.core.hand import Hand
from pycardgolf.core.scoring import (
    _card_value,
    calculate_score,
    calculate_visible_score,
)
from pycardgolf.utils.constants import HAND_SIZE
from pycardgolf.utils.deck import CARDS_PER_SUIT, Rank


def _make_hand(card_ids, face_up_mask=None):
    """Create a hand from a list of CardIDs."""
    if face_up_mask is None:
        face_up_mask = (1 << len(card_ids)) - 1
    return Hand(card_ids, face_up_mask)


def _get_card_id(rank, suit_idx=0):
    """Helper to get a CardID for a specific rank."""
    # Suit order: Spades, Hearts, Diamonds, Clubs
    # Suit index: 0, 1, 2, 3
    # rank_idx: ACE(0) ... KING(12)
    rank_idx = rank.value[0] - 1
    return suit_idx * CARDS_PER_SUIT + rank_idx


@pytest.mark.parametrize(
    ("ranks", "expected_score"),
    [
        pytest.param(
            [Rank.ACE, Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX],
            17,
            id="simple_sum_no_pairs",
        ),
        pytest.param(
            [Rank.FIVE, Rank.TWO, Rank.THREE, Rank.FIVE, Rank.FOUR, Rank.SIX],
            11,
            id="one_pair_cancels",
        ),
        pytest.param(
            [Rank.KING, Rank.QUEEN, Rank.JACK, Rank.KING, Rank.TWO, Rank.ACE],
            19,
            id="face_cards_and_king_pair",
        ),
        pytest.param(
            [Rank.KING, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX, Rank.SEVEN],
            25,
            id="king_worth_zero",
        ),
        pytest.param(
            [Rank.THREE, Rank.SEVEN, Rank.NINE, Rank.THREE, Rank.SEVEN, Rank.NINE],
            0,
            id="all_pairs_cancel",
        ),
        pytest.param(
            [Rank.TWO, Rank.TWO, Rank.TWO, Rank.KING, Rank.KING, Rank.KING],
            -6,
            id="negative_score",
        ),
    ],
)
def test_calculate_score_valid_hands(ranks, expected_score):
    card_ids = [_get_card_id(r) for r in ranks]
    # Ensure they are different cards for pairs to simulate different suits if needed,
    # though our scoring only cares about Rank.
    # Actually, let's use different suit indices for the bottom row.
    for i in range(3, 6):
        card_ids[i] = _get_card_id(ranks[i], suit_idx=1)

    hand = _make_hand(card_ids)
    assert calculate_score(hand) == expected_score


def test_calculate_score_none_hand():
    with pytest.raises(ValueError, match="Hand must be a list of"):
        calculate_score(None)


def test_calculate_score_invalid_hand_size():
    hand = Hand([1, 2, 3])
    with pytest.raises(ValueError, match=f"Hand must be a list of {HAND_SIZE} cards"):
        calculate_score(hand)


def test_calculate_score_face_down_cards():
    hand = _make_hand([0] * HAND_SIZE)
    hand.face_up_mask = 0b111110  # One card face down
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
        pytest.param([0, 3, 1, 4], 0, id="two_pairs_cancel"),
    ],
)
def test_calculate_visible_score_valid_hands(face_up_indices, expected_score):
    # All Aces
    card_ids = [_get_card_id(Rank.ACE)] * HAND_SIZE
    mask = 0
    for idx in face_up_indices:
        mask |= 1 << idx
    hand = Hand(card_ids, mask)
    assert calculate_visible_score(hand) == expected_score


def test_card_value_hidden_rank_raises():
    with pytest.raises(ValueError, match="Cannot calculate value of face-down card"):
        _card_value(-1)
