import pytest

from pycardgolf.utils.card import (
    card_to_string,
    get_card_display,
    get_masked_id,
    get_suit,
    is_face_down,
    is_face_up,
)
from pycardgolf.utils.deck import CARDS_PER_DECK, Suit


@pytest.mark.parametrize(
    ("card_id", "expected"),
    [
        (0, "A of Spades (blue back)"),
        (12, "K of Spades (blue back)"),
        (13, "A of Hearts (blue back)"),
        (CARDS_PER_DECK - 1, "K of Clubs (blue back)"),
        (CARDS_PER_DECK, "A of Spades (red back)"),
        (-1, "[Hidden blue Card]"),
        (-2, "[Hidden red Card]"),
        (-3, "[Hidden green Card]"),
    ],
)
def test_get_card_display(card_id, expected):
    assert get_card_display(card_id) == expected


@pytest.mark.parametrize(
    ("card_id", "expected"),
    [
        (0, True),
        (51, True),
        (52, True),
        (-1, False),
        (-2, False),
        (None, False),
    ],
)
def test_is_face_up(card_id, expected):
    assert is_face_up(card_id) == expected


@pytest.mark.parametrize(
    ("card_id", "expected"),
    [
        (0, False),
        (51, False),
        (52, False),
        (-1, True),
        (-2, True),
        (None, False),
    ],
)
def test_is_face_down(card_id, expected):
    assert is_face_down(card_id) == expected


@pytest.mark.parametrize(
    ("card_id", "expected"),
    [
        (0, -1),  # Blue back
        (51, -1),
        (52, -2),  # Red back
        (103, -2),
        (104, -3),  # Green back
    ],
)
def test_get_mask_id(card_id, expected):
    assert get_masked_id(card_id) == expected


def test_card_to_string_hidden():
    """Test card_to_string with hidden card ID."""
    assert card_to_string(-1) == "??"


def test_get_suit_hidden():
    """Test get_suit with hidden card ID."""
    assert get_suit(-1) == Suit.HIDDEN
