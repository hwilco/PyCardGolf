import pytest

from pycardgolf.core.hand import Hand
from pycardgolf.utils.card import Card
from pycardgolf.utils.enums import Rank, Suit


# Helper to create a standard hand of 6 cards
@pytest.fixture
def standard_hand():
    cards = [
        Card(Rank.ACE, Suit.CLUBS, "blue"),
        Card(Rank.TWO, Suit.CLUBS, "blue"),
        Card(Rank.THREE, Suit.CLUBS, "blue"),
        Card(Rank.FOUR, Suit.CLUBS, "blue"),
        Card(Rank.FIVE, Suit.CLUBS, "blue"),
        Card(Rank.SIX, Suit.CLUBS, "blue"),
    ]
    return Hand(cards)


def test_init(standard_hand):
    """Test initialization of Hand."""
    assert len(standard_hand) == 6
    assert standard_hand.rows == 2
    assert standard_hand.cols == 3


@pytest.mark.parametrize(
    ("col_index", "expected_ranks"),
    [
        (0, (Rank.ACE, Rank.FOUR)),
        (1, (Rank.TWO, Rank.FIVE)),
        (2, (Rank.THREE, Rank.SIX)),
    ],
)
def test_get_column_valid(standard_hand, col_index, expected_ranks):
    """Test getting a valid column."""
    top, bottom = standard_hand.get_column(col_index)
    assert top.rank == expected_ranks[0]
    assert bottom.rank == expected_ranks[1]


@pytest.mark.parametrize("col_index", [-1, 3, 10])
def test_get_column_invalid(standard_hand, col_index):
    """Test getting an invalid column raises IndexError."""
    with pytest.raises(IndexError, match=f"Column index out of range: {col_index}"):
        standard_hand.get_column(col_index)


def test_all_face_up(standard_hand):
    """Test all_face_up method."""
    assert not standard_hand.all_face_up()

    # Flip all cards
    standard_hand.reveal_all()
    assert standard_hand.all_face_up()


def test_replace_valid(standard_hand):
    """Test replacing a card."""
    new_card = Card(Rank.KING, Suit.HEARTS, "red")
    old_card = standard_hand.replace(0, new_card)

    assert old_card.rank == Rank.ACE
    assert standard_hand[0].rank == Rank.KING
    assert standard_hand[0] == new_card


@pytest.mark.parametrize("index", [-1, 6, 10])
def test_replace_invalid(standard_hand, index):
    """Test replacing at invalid index raises IndexError."""
    new_card = Card(Rank.KING, Suit.HEARTS, "red")
    with pytest.raises(IndexError, match=f"Card index out of range: {index}"):
        standard_hand.replace(index, new_card)


def test_flip_card_valid(standard_hand):
    """Test flipping a card."""
    assert not standard_hand[0].face_up
    standard_hand.flip_card(0)
    assert standard_hand[0].face_up


@pytest.mark.parametrize("index", [-1, 6, 10])
def test_flip_card_invalid(standard_hand, index):
    """Test flipping at invalid index raises IndexError."""
    with pytest.raises(IndexError, match=f"Card index out of range: {index}"):
        standard_hand.flip_card(index)


def test_reveal_all(standard_hand):
    """Test reveal_all makes all cards face up."""
    assert not standard_hand.all_face_up()
    standard_hand.reveal_all()
    assert standard_hand.all_face_up()
    for card in standard_hand:
        assert card.face_up


def test_getitem(standard_hand):
    """Test accessing cards by index."""
    assert standard_hand[0].rank == Rank.ACE
    assert standard_hand[5].rank == Rank.SIX


def test_iter(standard_hand):
    """Test iterating over the hand."""
    cards = list(standard_hand)
    assert len(cards) == 6
    assert cards[0].rank == Rank.ACE
    assert cards[5].rank == Rank.SIX
