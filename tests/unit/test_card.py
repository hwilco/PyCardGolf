import pytest
from pycardgolf.utils.enums import Rank, Suit
from pycardgolf.utils.card import Card


@pytest.mark.parametrize("rank", [0, 14, -1, 15, 100])
def test_rank_outside_range(rank):
    with pytest.raises(ValueError):
        Card(rank, Suit.HEARTS, "blue")


@pytest.mark.parametrize("rank", list(Rank))
def test_rank_inside_range(rank):
    # Should not raise
    Card(rank, Suit.HEARTS, "blue")


def test_invalid_suit():
    with pytest.raises(ValueError):
        Card(Rank.ACE, 1, "red")  # type: ignore[arg-type]


@pytest.mark.parametrize("suit", list(Suit))
def test_suit_valid(suit):
    # Should not raise
    Card(Rank.ACE, suit, "blue")


def test_eq():
    assert Card(Rank.THREE, Suit.HEARTS, "red") == Card(
        Rank.THREE, Suit.HEARTS, "red"
    )
    # Color will be converted to lowercase
    assert Card(Rank.THREE, Suit.HEARTS, "red") == Card(
        Rank.THREE, Suit.HEARTS, "RED"
    )

    # Different ranks
    assert Card(Rank.THREE, Suit.HEARTS, "red") != Card(
        Rank.FOUR, Suit.HEARTS, "red"
    )
    # Different suits
    assert Card(Rank.THREE, Suit.HEARTS, "red") != Card(
        Rank.THREE, Suit.SPADES, "red"
    )
    # Different colors
    assert Card(Rank.THREE, Suit.HEARTS, "red") != Card(
        Rank.THREE, Suit.HEARTS, "blue"
    )
    # Face down vs. face up
    assert Card(Rank.THREE, Suit.HEARTS, "red") != Card(
        Rank.THREE, Suit.HEARTS, "red", True
    )


@pytest.mark.parametrize(
    "rank,expected_rank",
    [
        (Rank.ACE, "A"),
        (Rank.TWO, "2"),
        (Rank.JACK, "J"),
        (Rank.QUEEN, "Q"),
        (Rank.KING, "K"),
    ],
)
def test_str_face_cards(rank, expected_rank):
    # Face cards are translated to their letter representations
    assert str(Card(rank, Suit.CLUBS, "red", True)) == f"{expected_rank}\u2667"


@pytest.mark.parametrize(
    "suit,expected_symbol",
    [
        (Suit.CLUBS, "\u2667"),
        (Suit.DIAMONDS, "\u2662"),
        (Suit.HEARTS, "\u2661"),
        (Suit.SPADES, "\u2664"),
    ],
)
def test_str_suits(suit, expected_symbol):
    # Suits are translated to their unicode characters
    assert str(Card(Rank.KING, suit, "red", True)) == f"K{expected_symbol}"


@pytest.mark.parametrize(
    "suit,expected_symbol",
    [
        (Suit.CLUBS, "\u2663"),
        (Suit.DIAMONDS, "\u2666"),
        (Suit.HEARTS, "\u2665"),
        (Suit.SPADES, "\u2660"),
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
    assert str(Card(Rank.ACE, Suit.HEARTS, "red", False)) == "??"


def test_repr():
    assert (
        repr(Card(Rank.ACE, Suit.SPADES, "red"))
        == "Card(<Rank.ACE: (1, 'A')>, <Suit.SPADES: (3, 'S')>, 'red', False)"
    )
    # Test a different suit
    assert (
        repr(Card(Rank.ACE, Suit.HEARTS, "red"))
        == "Card(<Rank.ACE: (1, 'A')>, <Suit.HEARTS: (2, 'H')>, 'red', False)"
    )
    # Test a different rank
    assert (
        repr(Card(Rank.TWO, Suit.SPADES, "red"))
        == "Card(<Rank.TWO: (2, '2')>, <Suit.SPADES: (3, 'S')>, 'red', False)"
    )
    # Test a different color
    assert (
        repr(Card(Rank.ACE, Suit.SPADES, "blue"))
        == "Card(<Rank.ACE: (1, 'A')>, <Suit.SPADES: (3, 'S')>, 'blue', False)"
    )

    # Color will be converted to lowercase
    assert (
        repr(Card(Rank.ACE, Suit.SPADES, "Red"))
        == "Card(<Rank.ACE: (1, 'A')>, <Suit.SPADES: (3, 'S')>, 'red', False)"
    )
    assert (
        repr(Card(Rank.ACE, Suit.SPADES, "RED"))
        == "Card(<Rank.ACE: (1, 'A')>, <Suit.SPADES: (3, 'S')>, 'red', False)"
    )

    # Test setting face_up to True
    assert (
        repr(Card(Rank.ACE, Suit.SPADES, "red", True))
        == "Card(<Rank.ACE: (1, 'A')>, <Suit.SPADES: (3, 'S')>, 'red', True)"
    )


def test_flip():
    c = Card(Rank.ACE, Suit.SPADES, "red", False)
    c.flip()
    assert c.face_up
    c.flip()
    assert not c.face_up


def test_property_getters():
    # Test that all property getters return correct values
    card = Card(Rank.JACK, Suit.DIAMONDS, "Blue", face_up=True)
    assert card.rank == Rank.JACK
    assert card.suit == Suit.DIAMONDS
    assert card.color == "blue"  # Should be lowercase
    assert card.face_up is True

    card2 = Card(Rank.ACE, Suit.SPADES, "RED", face_up=False)
    assert card2.rank == Rank.ACE
    assert card2.suit == Suit.SPADES
    assert card2.color == "red"  # Should be lowercase
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
    # Compare with non-Card objects
    card = Card(Rank.THREE, Suit.HEARTS, "red")
    assert card != other
