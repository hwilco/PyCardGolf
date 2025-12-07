import pytest

from pycardgolf.exceptions import CardStateError
from pycardgolf.utils.card import Card
from pycardgolf.utils.enums import Rank, Suit


@pytest.mark.parametrize(
    "rank",
    [
        pytest.param(0, id="zero_rank"),
        pytest.param(14, id="fourteen_rank"),
        pytest.param(-1, id="negative_rank"),
        pytest.param(15, id="fifteen_rank"),
        pytest.param(100, id="hundred_rank"),
    ],
)
def test_rank_outside_range(rank):
    with pytest.raises(ValueError, match="Card rank must be a member of Rank enum"):
        Card(rank, Suit.HEARTS, "blue")


def test_rank_enum_members():
    c = Card(Rank.ACE, Suit.HEARTS, "blue", face_up=True)
    assert c.rank == Rank.ACE


def test_invalid_suit():
    with pytest.raises(ValueError, match="Card suit must be in"):
        Card(Rank.ACE, 1, "red")  # type: ignore[arg-type]


def test_card_creation():
    c = Card(Rank.ACE, Suit.SPADES, "Red")
    assert c._Card__rank == Rank.ACE
    assert c._Card__suit == Suit.SPADES
    assert c.back_color == "red"
    assert c.face_color == "black"  # Default
    assert not c.face_up


def test_card_str():
    c = Card(Rank.ACE, Suit.SPADES, "Red", face_up=True)
    assert str(c) == "A\u2664"  # Using outline suit


def test_card_repr():
    c = Card(Rank.ACE, Suit.SPADES, "Red", face_up=True)
    assert (
        repr(c)
        == "Card(<Rank.ACE: (1, 'A')>, <Suit.SPADES: (3, 'S')>, 'red', 'black', True)"
    )


def test_card_equality():
    c1 = Card(Rank.ACE, Suit.SPADES, "Red")
    c2 = Card(Rank.ACE, Suit.SPADES, "Red")
    c3 = Card(Rank.KING, Suit.SPADES, "Red")
    assert c1 == c2
    assert c1 != c3
    assert c1 != "Not a card"


def test_flip():
    c = Card(Rank.ACE, Suit.SPADES, "Red")
    assert not c.face_up
    c.flip()
    assert c.face_up
    c.flip()
    assert not c.face_up


@pytest.mark.parametrize(
    ("rank", "expected_rank"),
    [
        pytest.param(Rank.ACE, "A", id="ace"),
        pytest.param(Rank.TWO, "2", id="two"),
        pytest.param(Rank.TEN, "10", id="ten"),
        pytest.param(Rank.JACK, "J", id="jack"),
        pytest.param(Rank.QUEEN, "Q", id="queen"),
        pytest.param(Rank.KING, "K", id="king"),
    ],
)
def test_rank_str_property(rank, expected_rank):
    c = Card(rank, Suit.SPADES, "red", face_up=True)
    # Accessing private property for testing via name mangling
    assert c._Card__rank_str == expected_rank


@pytest.mark.parametrize(
    ("suit", "expected_symbol"),
    [
        pytest.param(Suit.CLUBS, "\u2667", id="clubs"),
        pytest.param(Suit.DIAMONDS, "\u2662", id="diamonds"),
        pytest.param(Suit.HEARTS, "\u2661", id="hearts"),
        pytest.param(Suit.SPADES, "\u2664", id="spades"),
    ],
)
def test_suit_str_property_outline(suit, expected_symbol):
    c = Card(Rank.ACE, suit, "red", face_up=True)
    # Accessing private property for testing via name mangling
    assert c._Card__suit_str == expected_symbol


@pytest.mark.parametrize(
    ("suit", "expected_symbol"),
    [
        pytest.param(Suit.CLUBS, "\u2663", id="clubs"),
        pytest.param(Suit.DIAMONDS, "\u2666", id="diamonds"),
        pytest.param(Suit.HEARTS, "\u2665", id="hearts"),
        pytest.param(Suit.SPADES, "\u2660", id="spades"),
    ],
)
def test_str_no_outline(suit, expected_symbol):
    # Save the original class variable value
    original_outline_suits = Card._outline_suits
    try:
        # Set the class variable to False
        Card._outline_suits = False
        c = Card(Rank.ACE, suit, "red")
        c.face_up = True
        assert str(c) == f"A{expected_symbol}"
    finally:
        # Restore the original value
        Card._outline_suits = original_outline_suits


def test_str_face_down():
    assert str(Card(Rank.ACE, Suit.HEARTS, "red", face_up=False)) == "??"


@pytest.mark.parametrize(
    ("rank", "suit", "color", "face_up", "expected"),
    [
        pytest.param(
            Rank.ACE,
            Suit.SPADES,
            "red",
            False,
            "Card(<Rank.ACE: (1, 'A')>, <Suit.SPADES: (3, 'S')>, "
            "'red', 'black', False)",
            id="basic-ace-spades",
        ),
        pytest.param(
            Rank.ACE,
            Suit.HEARTS,
            "red",
            False,
            "Card(<Rank.ACE: (1, 'A')>, <Suit.HEARTS: (2, 'H')>, "
            "'red', 'black', False)",
            id="different-suit-hearts",
        ),
        pytest.param(
            Rank.TWO,
            Suit.SPADES,
            "red",
            False,
            "Card(<Rank.TWO: (2, '2')>, <Suit.SPADES: (3, 'S')>, "
            "'red', 'black', False)",
            id="different-rank-two",
        ),
        pytest.param(
            Rank.ACE,
            Suit.SPADES,
            "blue",
            False,
            "Card(<Rank.ACE: (1, 'A')>, <Suit.SPADES: (3, 'S')>, "
            "'blue', 'black', False)",
            id="different-color-blue",
        ),
        pytest.param(
            Rank.ACE,
            Suit.SPADES,
            "Red",
            False,
            "Card(<Rank.ACE: (1, 'A')>, <Suit.SPADES: (3, 'S')>, "
            "'red', 'black', False)",
            id="color-lowercase-Red",
        ),
        pytest.param(
            Rank.ACE,
            Suit.SPADES,
            "RED",
            False,
            "Card(<Rank.ACE: (1, 'A')>, <Suit.SPADES: (3, 'S')>, "
            "'red', 'black', False)",
            id="color-lowercase-RED",
        ),
        pytest.param(
            Rank.ACE,
            Suit.SPADES,
            "red",
            True,
            "Card(<Rank.ACE: (1, 'A')>, <Suit.SPADES: (3, 'S')>, 'red', 'black', True)",
            id="face-up-true",
        ),
    ],
)
def test_repr(rank, suit, color, face_up, expected):
    assert repr(Card(rank, suit, color, face_up=face_up)) == expected


def test_property_getters():
    # Test that all property getters return correct values
    card = Card(Rank.JACK, Suit.DIAMONDS, "Blue", face_up=True)
    assert card.rank == Rank.JACK
    assert card.suit == Suit.DIAMONDS
    assert card.back_color == "blue"  # Should be lowercase
    assert card.face_up is True

    card2 = Card(Rank.ACE, Suit.SPADES, "RED", face_up=False)
    with pytest.raises(CardStateError, match="face down"):
        _ = card2.rank
    with pytest.raises(CardStateError, match="face down"):
        _ = card2.suit
    assert card2.back_color == "red"  # Should be lowercase
    assert card2.face_up is False


def test_face_up_setter():
    # Test face_up setter
    card = Card(Rank.FIVE, Suit.CLUBS, "green", face_up=False)
    assert card.face_up is False

    card.face_up = True
    assert card.face_up is True

    card.face_up = False
    assert card.face_up is False


@pytest.mark.parametrize(
    "other",
    [
        "Not a Card",
        123,
        None,
        [],
        {},
    ],
)
def test_eq_with_non_card(other):
    # Test that __eq__ returns NotImplemented for non-Card objects
    # This allows Python to try reverse comparison or fall back to identity comparison
    card = Card(Rank.THREE, Suit.HEARTS, "red")
    assert card.__eq__(other) is NotImplemented
