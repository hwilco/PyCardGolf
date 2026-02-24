import pytest

from pycardgolf.utils.deck import (
    CARDS_PER_DECK,
    CardStack,
    Deck,
)


# Fixed test data for deterministic, reproducible tests
@pytest.fixture
def cards_5():
    """Returns a fixed set of 5 CardIDs for testing."""
    return [10, 20, 30, 40, 50]


@pytest.fixture
def cards_3():
    """Returns a fixed set of 3 CardIDs for testing."""
    return [60, 70, 80]


def test_add_card_stack(cards_5, cards_3):
    card_stack = CardStack(card_ids=cards_5.copy())
    other_card_stack = CardStack(card_ids=cards_3.copy())
    card_stack.add_card_stack(other_card_stack)
    assert card_stack._card_ids == cards_5 + cards_3
    assert other_card_stack.num_cards == 0


def test_add_card_stack_no_clear(cards_5, cards_3):
    card_stack = CardStack(card_ids=cards_5.copy())
    other_card_stack = CardStack(card_ids=cards_3.copy())
    card_stack.add_card_stack(other_card_stack, clear_other=False)
    assert card_stack._card_ids == cards_5 + cards_3
    assert other_card_stack._card_ids == cards_3


def test_add_card_stack_shuffle(cards_5, cards_3, mocker):
    card_stack = CardStack(card_ids=cards_5.copy())
    other_card_stack = CardStack(card_ids=cards_3.copy())
    card_stack._rng = mocker.MagicMock()
    card_stack.add_card_stack(other_card_stack, shuffle=True)
    card_stack._rng.shuffle.assert_called_once_with(cards_5 + cards_3)
    assert card_stack._card_ids == cards_5 + cards_3
    assert other_card_stack.num_cards == 0


def test_draw(cards_5):
    card_stack = CardStack(card_ids=cards_5.copy())
    for num_draws in range(1, len(cards_5) + 1):
        assert card_stack.draw() == cards_5[-num_draws]


def test_num_cards(cards_5):
    card_stack = CardStack(card_ids=cards_5)
    assert card_stack.num_cards == 5
    card_stack.draw()
    assert card_stack.num_cards == 4
    card_stack.clear()
    assert card_stack.num_cards == 0


def test_draw_empty():
    card_stack = CardStack()
    with pytest.raises(IndexError):
        card_stack.draw()


def test_peek_empty():
    """Test peek on empty stack raises IndexError."""
    card_stack = CardStack()
    with pytest.raises(IndexError, match="No cards in card stack"):
        card_stack.peek()


def test_clear(cards_5):
    card_stack = CardStack(card_ids=cards_5.copy())
    assert card_stack.num_cards == len(cards_5)
    card_stack.clear()
    assert card_stack.num_cards == 0


def test_deck_unique_default_seed(mocker):
    """Test that multiple Decks without seeds get unique seeds."""
    mock_randrange = mocker.patch("pycardgolf.utils.mixins.random.randrange")
    mock_randrange.side_effect = [100, 200, 300]

    d1 = Deck()
    d2 = Deck()
    d3 = Deck()

    assert d1.seed == 100
    assert d2.seed == 200
    assert d3.seed == 300


def test_shuffle_deterministic():
    """Test that shuffling with the same seed produces deterministic results."""
    cards = list(range(13))

    stack1 = CardStack(card_ids=cards.copy(), seed=42)
    stack1.shuffle()

    stack2 = CardStack(card_ids=cards.copy(), seed=42)
    stack2.shuffle()

    assert stack1._card_ids == stack2._card_ids


def test_eq_stack(cards_5):
    assert CardStack(seed=1) == CardStack(seed=1)
    assert CardStack(seed=1, card_ids=cards_5.copy()) == CardStack(
        seed=1,
        card_ids=cards_5.copy(),
    )


def test_card_stack_eq_other_type():
    """Test equality with non-CardStack object returns NotImplemented (False)."""
    assert CardStack() != "not a stack"


def test_deck_cards():
    deck = Deck(num_decks=1)
    assert deck.num_cards == CARDS_PER_DECK
    assert deck.card_ids == list(range(CARDS_PER_DECK))


def test_deck_clone() -> None:
    """Test that a deck clones."""
    deck = Deck(num_decks=1, seed=42)
    deck.shuffle()
    clone1 = deck.clone(preserve_rng=True)
    assert deck.draw() == clone1.draw()


def test_cardstack_clone_preserve_rng() -> None:
    """Test CardStack cloning with preserve_rng=True."""
    stack = CardStack(card_ids=[10, 20], seed=42)
    stack.shuffle()
    cloned = stack.clone(preserve_rng=True)
    assert stack.draw() == cloned.draw()


def test_card_stack_add_card():
    stack = CardStack()
    stack.add_card(5)
    assert stack.num_cards == 1
    assert stack._card_ids[-1] == 5
