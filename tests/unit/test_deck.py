import pytest

from pycardgolf.utils.card import Card
from pycardgolf.utils.deck import CardStack, Deck, DiscardStack
from pycardgolf.utils.enums import Rank, Suit


# Fixed test data for deterministic, reproducible tests
@pytest.fixture
def cards_5():
    """Returns a fixed set of 5 cards for testing."""
    return [
        Card(Rank.THREE, Suit.HEARTS, "red"),
        Card(Rank.SEVEN, Suit.CLUBS, "blue"),
        Card(Rank.ACE, Suit.SPADES, "red"),
        Card(Rank.KING, Suit.DIAMONDS, "blue"),
        Card(Rank.FIVE, Suit.HEARTS, "green"),
    ]


@pytest.fixture
def cards_3():
    """Returns a fixed set of 3 cards for testing."""
    return [
        Card(Rank.TEN, Suit.SPADES, "red"),
        Card(Rank.TWO, Suit.HEARTS, "blue"),
        Card(Rank.JACK, Suit.CLUBS, "red"),
    ]


def test_add_card_stack(cards_5, cards_3):
    card_stack = CardStack(cards=cards_5.copy())
    other_card_stack = CardStack(cards=cards_3.copy())
    card_stack.add_card_stack(other_card_stack)
    assert card_stack._cards == cards_5 + cards_3
    assert other_card_stack.num_cards == 0


def test_add_card_stack_no_clear(cards_5, cards_3):
    card_stack = CardStack(cards=cards_5.copy())
    other_card_stack = CardStack(cards=cards_3.copy())
    card_stack.add_card_stack(other_card_stack, clear_other=False)
    assert card_stack._cards == cards_5 + cards_3
    assert other_card_stack._cards == cards_3


def test_add_card_stack_shuffle(cards_5, cards_3, mocker):
    card_stack = CardStack(cards=cards_5.copy())
    other_card_stack = CardStack(cards=cards_3.copy())
    card_stack.rand = mocker.MagicMock()
    card_stack.add_card_stack(other_card_stack, shuffle=True)
    card_stack.rand.shuffle.assert_called_once_with(cards_5 + cards_3)
    assert card_stack._cards == cards_5 + cards_3
    assert other_card_stack.num_cards == 0


def test_peek_color():
    cards = [
        Card(Rank.THREE, Suit.CLUBS, "red"),
        Card(Rank.THREE, Suit.CLUBS, "blue"),
    ]
    card_stack = CardStack(cards=cards.copy())
    assert card_stack.peek().back_color == cards[-1].back_color
    assert card_stack._cards[-1] == cards[-1]
    card_stack.draw()
    assert card_stack.peek().back_color == cards[-2].back_color
    assert card_stack._cards[-1] == cards[-2]


def test_draw(cards_5):
    card_stack = CardStack(cards=cards_5.copy())
    for num_draws in range(1, len(cards_5) + 1):
        assert card_stack.draw() == cards_5[-num_draws]


def test_num_cards(cards_5):
    card_stack = CardStack(cards_5)
    assert card_stack.num_cards == 5
    card_stack.draw()
    assert card_stack.num_cards == 4
    card_stack.clear()
    assert card_stack.num_cards == 0


def test_draw_empty():
    card_stack = CardStack()
    with pytest.raises(IndexError):
        card_stack.draw()


def test_clear(cards_5):
    card_stack = CardStack(cards=cards_5.copy())
    assert card_stack.num_cards == len(cards_5)
    card_stack.clear()
    assert card_stack.num_cards == 0
    card_stack.clear()
    assert card_stack.num_cards == 0


def test_shuffle_deterministic():
    """Test that shuffling with the same seed produces deterministic results."""
    cards = [Card(i, Suit.HEARTS, "red") for i in Rank]

    stack1 = CardStack(cards=cards.copy(), seed=42)
    stack1.shuffle()

    stack2 = CardStack(cards=cards.copy(), seed=42)
    stack2.shuffle()

    assert stack1._cards == stack2._cards

    # Verify that different seeds produce different results (with high probability)
    stack3 = CardStack(cards=cards.copy(), seed=99)
    stack3.shuffle()
    assert stack1._cards != stack3._cards


def test_eq_stack(cards_5):
    assert CardStack(seed=1) == CardStack(seed=1)
    assert CardStack(seed=1, cards=cards_5.copy()) == CardStack(
        seed=1,
        cards=cards_5.copy(),
    )

    assert CardStack(seed=1) != CardStack(seed=2)
    assert CardStack(seed=1, cards=cards_5.copy()) != CardStack(
        seed=2,
        cards=cards_5.copy(),
    )
    assert CardStack(seed=1, cards=cards_5.copy()) != CardStack(seed=1)
    assert CardStack(seed=1, cards=cards_5.copy()) != CardStack(
        seed=1,
        cards=cards_5.copy()[:2],
    )


def test_str_stack(cards_5):
    assert str(CardStack(seed=1)) == "Stack of 0 cards"
    card_stack = CardStack(cards=cards_5.copy())
    assert str(card_stack) == f"Stack of {len(cards_5)} cards"
    card_stack.draw()
    assert str(card_stack) == f"Stack of {len(cards_5) - 1} cards"


def test_repr_stack(cards_5):
    assert repr(CardStack(seed=1)) == "CardStack(cards=[], seed=1)"
    card_stack = CardStack(cards=cards_5.copy(), seed=1)
    assert repr(card_stack) == f"CardStack(cards={cards_5}, seed=1)"
    card_stack.draw()
    assert repr(card_stack) == f"CardStack(cards={cards_5[:-1]}, seed=1)"


@pytest.fixture
def red_deck():
    return Deck(back_color="red", seed=1)


def test_cards(red_deck):
    assert all(
        Card(rank, suit, "red", face_color=red_deck.suit_colors[suit])
        in red_deck._cards
        for rank in Rank
        for suit in Suit
    )


def test_reset(red_deck):
    red_deck.draw()
    red_deck.reset()
    # Re-run test_cards logic
    assert all(
        Card(rank, suit, "red", face_color=red_deck.suit_colors[suit])
        in red_deck._cards
        for rank in Rank
        for suit in Suit
    )


def test_add_card_stack_valid(red_deck):
    other_cards = red_deck._cards[:3].copy()
    del red_deck._cards[:3]
    other_card_stack = CardStack(cards=other_cards)
    red_deck.add_card_stack(other_card_stack)
    # Re-run test_cards logic
    assert all(
        Card(rank, suit, "red", face_color=red_deck.suit_colors[suit])
        in red_deck._cards
        for rank in Rank
        for suit in Suit
    )
    assert other_card_stack.num_cards == 0


def test_add_card_stack_already_in_deck(red_deck):
    other_card_stack = CardStack(cards=[Card(Rank.THREE, Suit.CLUBS, "red")])
    with pytest.raises(ValueError, match="Card to be added is a duplicate"):
        red_deck.add_card_stack(other_card_stack)
    assert other_card_stack.num_cards == 1


def test_add_card_stack_wrong_color(red_deck):
    # Create a card from the red deck to copy its properties, but change color
    # Since Card is immutable-ish (no setters for color), we create a new one
    # But wait, we need a card that is NOT in the deck but has WRONG color.
    # Actually, any card with wrong color will trigger the check.
    # Let's just create a blue card.
    other_card_stack = CardStack(
        cards=[Card(Rank.ACE, Suit.SPADES, "blue")],
    )
    with pytest.raises(
        ValueError,
        match="Card to be added does not match the deck's back color",
    ):
        red_deck.add_card_stack(other_card_stack)
    assert other_card_stack.num_cards == 1


def test_add_card_stack_no_clear_deck(red_deck):
    other_cards = red_deck._cards[:3].copy()
    del red_deck._cards[:3]
    other_card_stack = CardStack(cards=other_cards.copy())
    red_deck.add_card_stack(other_card_stack, clear_other=False)
    # Re-run test_cards logic
    assert all(
        Card(rank, suit, "red", face_color=red_deck.suit_colors[suit])
        in red_deck._cards
        for rank in Rank
        for suit in Suit
    )
    assert other_card_stack._cards == other_cards


def test_add_card_stack_shuffle_deck(red_deck, mocker):
    other_cards = red_deck._cards[:3].copy()
    del red_deck._cards[:3]
    other_card_stack = CardStack(cards=other_cards.copy())
    red_deck.rand = mocker.MagicMock()
    red_deck.add_card_stack(other_card_stack, shuffle=True)
    red_deck.rand.shuffle.assert_called_once()
    # Re-run test_cards logic
    assert all(
        Card(rank, suit, "red", face_color=red_deck.suit_colors[suit])
        in red_deck._cards
        for rank in Rank
        for suit in Suit
    )
    assert other_card_stack.num_cards == 0


def test_eq_deck():
    deck_a = Deck("blue", seed=1)
    deck_b = Deck("blue", seed=1)
    assert deck_a == deck_b

    deck_a.shuffle()
    assert deck_a != deck_b

    deck_c = Deck("blue", seed=1)
    deck_d = Deck("red", seed=1)
    assert deck_c != deck_d

    # Test that comparing a Deck with a CardStack returns NotImplemented
    stack_a = CardStack(seed=1)
    assert deck_a.__eq__(stack_a) is NotImplemented


def test_str_deck(red_deck):
    assert str(red_deck) == "Deck of 52 red cards"
    red_deck.draw()
    assert str(red_deck) == "Deck of 51 red cards"
    card_deck = Deck("blue")
    assert str(card_deck) == "Deck of 52 blue cards"


def test_repr_deck(red_deck):
    red_deck.clear()
    assert (
        repr(red_deck) == "Deck <back_color=red, seed=1, _cards=[], suit_colors={"
        "<Suit.CLUBS: (0, 'C')>: 'black', <Suit.DIAMONDS: (1, 'D')>: 'red', "
        "<Suit.HEARTS: (2, 'H')>: 'red', <Suit.SPADES: (3, 'S')>: 'black'}>"
    )


def test_peek_color_empty():
    # Test that peek_color raises IndexError on empty stack
    card_stack = CardStack()
    with pytest.raises(IndexError, match="No cards in card stack"):
        card_stack.peek()


@pytest.mark.parametrize(
    "other",
    [
        "not a card stack",
        123,
        None,
        Card(Rank.ACE, Suit.SPADES, "red"),
        [],
        {},
    ],
)
def test_eq_stack_with_non_cardstack(other):
    # Test that __eq__ returns NotImplemented for non-CardStack objects
    # This allows Python to try reverse comparison or fall back to identity comparison
    card_stack = CardStack(seed=1)
    assert card_stack.__eq__(other) is NotImplemented


@pytest.mark.parametrize(
    ("input_color", "expected_color"),
    [
        ("RED", "red"),
        ("BlUe", "blue"),
        ("green", "green"),
        ("BLUE", "blue"),
    ],
)
def test_deck_color_case_conversion(input_color, expected_color):
    # Test that deck color is converted to lowercase
    deck = Deck(input_color, seed=1)
    assert deck.back_color == expected_color


def test_deck_initialization():
    # Test that a new deck has exactly 52 cards in expected order
    deck = Deck("red", seed=1)
    assert deck.num_cards == 52

    # Verify all 52 unique cards are present
    expected_cards = [
        Card(rank, suit, "red", deck.suit_colors[suit])
        for suit in Suit
        for rank in Rank
    ]
    assert len(deck._cards) == len(expected_cards)
    for card in expected_cards:
        assert card in deck._cards


def test_deck_initialization_with_suit_colors():
    suit_colors = {
        Suit.CLUBS: "black",
        Suit.DIAMONDS: "green",
        Suit.HEARTS: "red",
        Suit.SPADES: "blue",
    }

    deck = Deck("red", suit_colors=suit_colors)
    assert deck.suit_colors == suit_colors

    deck = Deck("red", suit_colors={Suit.CLUBS: "purple"})
    assert deck.suit_colors == {
        Suit.CLUBS: "purple",
        Suit.DIAMONDS: "red",
        Suit.HEARTS: "red",
        Suit.SPADES: "black",
    }


# DiscardStack Tests


def test_discard_stack_init(cards_3):
    # Test empty initialization
    discard = DiscardStack()
    assert discard.num_cards == 0

    # Test initialization with cards
    discard_with_cards = DiscardStack(cards=cards_3.copy())
    assert discard_with_cards.num_cards == 3


def test_discard_add_card():
    discard = DiscardStack()
    card1 = Card(Rank.FIVE, Suit.HEARTS, "red")
    card2 = Card(Rank.TEN, Suit.CLUBS, "blue")

    discard.add_card(card1)
    assert discard.num_cards == 1

    discard.add_card(card2)
    assert discard.num_cards == 2

    # Verify cards are added to the top (end of list)
    assert discard._cards[-1] == card2
    assert discard._cards[-2] == card1


def test_discard_peek():
    cards = [
        Card(Rank.ACE, Suit.SPADES, "red"),
        Card(Rank.TWO, Suit.HEARTS, "blue"),
        Card(Rank.THREE, Suit.CLUBS, "green"),
    ]
    discard = DiscardStack(cards=cards.copy())

    # Peek should return top card without removing it
    top_card = discard.peek()
    assert top_card == cards[-1]
    assert discard.num_cards == 3  # Card should still be there

    # Peek again should return same card
    assert discard.peek() == cards[-1]


def test_discard_peek_empty():
    # Test that peek raises IndexError on empty discard stack
    discard = DiscardStack()
    with pytest.raises(IndexError, match="No cards in card stack"):
        discard.peek()


def test_discard_cards_property(cards_5):
    discard = DiscardStack(cards=cards_5.copy())

    # Get cards via property
    cards_copy = discard.cards

    # Verify it's a copy (not the same object)
    assert cards_copy == cards_5
    assert cards_copy is not discard._cards

    # Modifying the returned list shouldn't affect the discard stack
    cards_copy.append(Card(Rank.KING, Suit.SPADES, "red"))
    assert discard.num_cards == 5  # Should still be 5


def test_discard_str():
    # Test string representation with empty stack
    discard = DiscardStack()
    assert str(discard) == "Discard stack of 0 cards"

    # Test with one card
    card1 = Card(Rank.SEVEN, Suit.DIAMONDS, "red", face_up=True)
    discard.add_card(card1)
    assert str(discard) == "Discard stack of 1 card. Top card: 7♢"

    # Test with multiple cards
    card2 = Card(Rank.KING, Suit.SPADES, "blue", face_up=True)
    discard.add_card(card2)
    assert str(discard) == "Discard stack of 2 cards. Top card: K♤"


def test_discard_repr():
    # Test repr with empty stack
    discard = DiscardStack()
    assert repr(discard) == "DiscardStack(cards=[])"

    # Test repr with cards
    cards = [
        Card(Rank.ACE, Suit.HEARTS, "red"),
        Card(Rank.FIVE, Suit.CLUBS, "blue"),
    ]
    discard_with_cards = DiscardStack(cards=cards.copy())
    assert repr(discard_with_cards) == f"DiscardStack(cards={cards})"
