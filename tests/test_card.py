import pytest
from pycardgolf.utils.card import Card, Suit

@pytest.mark.parametrize("rank", [0, 14, -1, 15, 100])
def test_rank_outside_range(rank):
    with pytest.raises(ValueError):
        Card(rank, Suit.HEARTS, 'blue')

@pytest.mark.parametrize("rank", range(1, 14))
def test_rank_inside_range(rank):
    # Should not raise
    Card(rank, Suit.HEARTS, 'blue')

def test_invalid_suit():
    with pytest.raises(ValueError):
        Card(1, 1, 'red')  # type: ignore[arg-type]

@pytest.mark.parametrize("suit", list(Suit))
def test_suit_valid(suit):
    # Should not raise
    Card(1, suit, 'blue')

def test_eq():
    assert Card(3, Suit.HEARTS, 'red') == Card(3, Suit.HEARTS, 'red')
    # Color will be converted to lowercase
    assert Card(3, Suit.HEARTS, 'red') == Card(3, Suit.HEARTS, 'RED')

    # Different ranks
    assert Card(3, Suit.HEARTS, 'red') != Card(4, Suit.HEARTS, 'red')
    # Different suits
    assert Card(3, Suit.HEARTS, 'red') != Card(3, Suit.SPADES, 'red')
    # Different colors
    assert Card(3, Suit.HEARTS, 'red') != Card(3, Suit.HEARTS, 'blue')
    # Face down vs. face up
    assert Card(3, Suit.HEARTS, 'red') != Card(3, Suit.HEARTS, 'red', True)



@pytest.mark.parametrize("rank,expected_rank", [
    (1, "A"),
    (2, "2"),
    (11, "J"),
    (12, "Q"),
    (13, "K"),
])
def test_str_face_cards(rank, expected_rank):
    # Face cards are translated to their letter representations
    assert str(Card(rank, Suit.CLUBS, 'red', True)) == f"{expected_rank}\u2667"

@pytest.mark.parametrize("suit,expected_symbol", [
    (Suit.CLUBS, "\u2667"),
    (Suit.DIAMONDS, "\u2662"),
    (Suit.HEARTS, "\u2661"),
    (Suit.SPADES, "\u2664"),
])
def test_str_suits(suit, expected_symbol):
    # Suits are translated to their unicode characters
    assert str(Card(13, suit, 'red', True)) == f"K{expected_symbol}"

@pytest.mark.parametrize("suit,expected_symbol", [
    (Suit.CLUBS, '\u2663'),
    (Suit.DIAMONDS, '\u2666'),
    (Suit.HEARTS, '\u2665'),
    (Suit.SPADES, '\u2660'),
])
def test_str_no_outline(suit, expected_symbol):
    # Save the original class variable value
    original_outline_suits = Card._outline_suits
    try:
        # Set the class variable to False
        Card._outline_suits = False
        c = Card(1, suit, 'red')
        c.face_up = True
        assert str(c) == f"A{expected_symbol}"
    finally:
        # Restore the original value
        Card._outline_suits = original_outline_suits

def test_str_face_down():
    assert str(Card(1, Suit.HEARTS, 'red', False)) == "??"

def test_repr():
    assert repr(Card(1, Suit.SPADES, 'red')) == "Card(1, Suit.SPADES, 'red', False)"
    # Test a different suit
    assert repr(Card(1, Suit.HEARTS, 'red')) == "Card(1, Suit.HEARTS, 'red', False)"
    # Test a different rank
    assert repr(Card(2, Suit.SPADES, 'red')) == "Card(2, Suit.SPADES, 'red', False)"
    # Test a different color
    assert repr(Card(1, Suit.SPADES, 'blue')) == "Card(1, Suit.SPADES, 'blue', False)"

    # Color will be converted to lowercase
    assert repr(Card(1, Suit.SPADES, 'Red')) == "Card(1, Suit.SPADES, 'red', False)"
    assert repr(Card(1, Suit.SPADES, 'RED')) == "Card(1, Suit.SPADES, 'red', False)"

    # Test setting face_up to True
    assert repr(Card(1, Suit.SPADES, 'red', True)) == "Card(1, Suit.SPADES, 'red', True)"

def test_flip():
    c = Card(1, Suit.SPADES, 'red', False)
    c.flip()
    assert c.face_up
    c.flip()
    assert not c.face_up

@pytest.mark.parametrize("lesser,greater", [
    (Suit.CLUBS, Suit.DIAMONDS),
    (Suit.DIAMONDS, Suit.HEARTS),
    (Suit.HEARTS, Suit.SPADES),
])
def test_suit_comparison_less_than(lesser, greater):
    # Test Suit.__lt__ method
    assert lesser < greater
    assert not greater < lesser

def test_property_getters():
    # Test that all property getters return correct values
    card = Card(11, Suit.DIAMONDS, 'Blue', face_up=True)
    assert card.rank == 11
    assert card.suit == Suit.DIAMONDS
    assert card.color == 'blue'  # Should be lowercase
    assert card.face_up is True
    
    card2 = Card(1, Suit.SPADES, 'RED', face_up=False)
    assert card2.rank == 1
    assert card2.suit == Suit.SPADES
    assert card2.color == 'red'  # Should be lowercase
    assert card2.face_up is False

def test_face_up_setter():
    # Test face_up setter
    card = Card(5, Suit.CLUBS, 'green', face_up=False)
    assert card.face_up is False
    
    card.face_up = True
    assert card.face_up is True
    
    card.face_up = False
    assert card.face_up is False

@pytest.mark.parametrize("other", [
    "Not a Card",
    123,
    None,
    [],
    {},
])
def test_eq_with_non_card(other):
    # Compare with non-Card objects
    card = Card(3, Suit.HEARTS, 'red')
    assert card != other
