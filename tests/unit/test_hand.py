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
        pytest.param(0, (Rank.ACE, Rank.FOUR), id="col_0_ace_four"),
        pytest.param(1, (Rank.TWO, Rank.FIVE), id="col_1_two_five"),
        pytest.param(2, (Rank.THREE, Rank.SIX), id="col_2_three_six"),
    ],
)
def test_get_column_valid(standard_hand, col_index, expected_ranks):
    """Test getting a valid column."""
    top, bottom = standard_hand.get_column(col_index)
    assert top._Card__rank == expected_ranks[0]
    assert bottom._Card__rank == expected_ranks[1]


@pytest.mark.parametrize(
    "col_index",
    [
        pytest.param(-1, id="negative_one"),
        pytest.param(3, id="three"),
        pytest.param(10, id="ten"),
    ],
)
def test_get_column_invalid(standard_hand, col_index):
    """Test getting an invalid column raises IndexError."""
    with pytest.raises(IndexError, match=f"Column index out of range: {col_index}"):
        standard_hand.get_column(col_index)


# ... (skip to replace_invalid)


@pytest.mark.parametrize(
    "index",
    [
        pytest.param(-1, id="negative_one"),
        pytest.param(6, id="six"),
        pytest.param(10, id="ten"),
    ],
)
def test_replace_invalid(standard_hand, index):
    """Test replacing at invalid index raises IndexError."""
    new_card = Card(Rank.KING, Suit.HEARTS, "red")
    with pytest.raises(IndexError, match=f"Card index out of range: {index}"):
        standard_hand.replace(index, new_card)


# ... (skip to flip_card_invalid)


@pytest.mark.parametrize(
    "index",
    [
        pytest.param(-1, id="negative_one"),
        pytest.param(6, id="six"),
        pytest.param(10, id="ten"),
    ],
)
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
    assert standard_hand[0]._Card__rank == Rank.ACE
    assert standard_hand[5]._Card__rank == Rank.SIX


def test_getitem_slice(standard_hand):
    """Test accessing cards by slice."""
    # Test slicing returns a list of cards
    first_three = standard_hand[0:3]
    assert isinstance(first_three, list)
    assert len(first_three) == 3
    assert first_three[0]._Card__rank == Rank.ACE
    assert first_three[1]._Card__rank == Rank.TWO
    assert first_three[2]._Card__rank == Rank.THREE

    # Test slicing with step
    every_other = standard_hand[::2]
    assert len(every_other) == 3
    assert every_other[0]._Card__rank == Rank.ACE
    assert every_other[1]._Card__rank == Rank.THREE
    assert every_other[2]._Card__rank == Rank.FIVE


def test_iter(standard_hand):
    """Test iterating over the hand."""
    cards = list(standard_hand)
    assert len(cards) == 6
    assert cards[0]._Card__rank == Rank.ACE
    assert cards[5]._Card__rank == Rank.SIX
