import pytest

from pycardgolf.core.hand import Hand


# Helper to create a standard hand of 6 cards
@pytest.fixture
def standard_hand():
    cards = [0, 1, 2, 3, 4, 5]
    return Hand(cards)


def test_init(standard_hand):
    """Test initialization of Hand."""
    assert len(standard_hand) == 6
    assert standard_hand.rows == 2
    assert standard_hand.cols == 3
    assert standard_hand.face_up_mask == 0


@pytest.mark.parametrize(
    ("col_index", "expected_ids"),
    [
        pytest.param(0, (0, 3), id="col_0"),
        pytest.param(1, (1, 4), id="col_1"),
        pytest.param(2, (2, 5), id="col_2"),
    ],
)
def test_get_column_valid(standard_hand, col_index, expected_ids):
    """Test getting a valid column."""
    top, bottom = standard_hand.get_column(col_index)
    assert top == expected_ids[0]
    assert bottom == expected_ids[1]


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


def test_is_face_up(standard_hand):
    assert not standard_hand.is_face_up(0)
    standard_hand.face_up_mask |= 1 << 0
    assert standard_hand.is_face_up(0)


def test_all_face_up(standard_hand):
    assert not standard_hand.all_face_up()
    standard_hand.face_up_mask = (1 << 6) - 1
    assert standard_hand.all_face_up()


def test_replace(standard_hand):
    old_card = standard_hand.replace(0, 99)
    assert old_card == 0
    assert standard_hand[0] == 99
    assert standard_hand.is_face_up(0)


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
    with pytest.raises(IndexError, match=f"Card index out of range: {index}"):
        standard_hand.replace(index, 99)


def test_flip_card(standard_hand):
    assert not standard_hand.is_face_up(2)
    standard_hand.flip_card(2)
    assert standard_hand.is_face_up(2)


def test_reveal_all(standard_hand):
    standard_hand.reveal_all()
    assert standard_hand.all_face_up()


def test_clone(standard_hand):
    cloned = standard_hand.clone()
    assert cloned.card_ids == standard_hand.card_ids
    assert int(cloned.face_up_mask) == int(standard_hand.face_up_mask)
    assert cloned.card_ids is not standard_hand.card_ids


def test_getitem(standard_hand):
    assert standard_hand[0] == 0
    assert standard_hand[5] == 5


def test_getitem_slice(standard_hand):
    first_three = standard_hand[0:3]
    assert first_three == [0, 1, 2]


def test_iter(standard_hand):
    assert list(standard_hand) == [0, 1, 2, 3, 4, 5]
