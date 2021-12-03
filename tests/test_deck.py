import unittest
from unittest import mock
from pycardgolf import deck
import string
import sys
import random

__unittest = True


def random_cards(num_cards: int):
    return [deck.Card(random.randint(1, 13), random.choice('cdhs'), random.choice(['red', 'blue'])) for
            _ in range(num_cards)]


class TestCard(unittest.TestCase):
    def test_value_outside_range(self):
        for value in [0, 14]:
            with self.subTest(value=value):
                self.assertRaises(ValueError, deck.Card, value, 'h', 'blue')

    def test_value_inside_range(self):
        for value in range(1, 14):
            with self.subTest(msg="ValueError unexpectedly raised by Card({}, 'h')".format(value), value=value):
                try:
                    deck.Card(value, 'h', 'blue')
                except ValueError:
                    self.fail()

    def test_suit_invalid(self):
        for suit in ['clubs', 'diamonds', 'hearts', 'spades'] + [s for s in string.ascii_lowercase if s not in 'cdhs']:
            with self.subTest(suit=suit):
                self.assertRaises(ValueError, deck.Card, 1, suit, 'blue')

    def test_suit_valid(self):
        for suit in 'cdhsCDHS':
            with self.subTest(msg="ValueError unexpectedly raised by Card(1, {})".format(suit), suit=suit):
                try:
                    deck.Card(1, suit, 'blue')
                except ValueError:
                    self.fail()

    def test_eq(self):
        self.assertEqual(deck.Card(3, 'h', 'red'), deck.Card(3, 'h', 'red'))
        self.assertEqual(deck.Card(3, 'H', 'red'), deck.Card(3, 'h', 'red'))
        self.assertEqual(deck.Card(3, 'h', 'red'), deck.Card(3, 'h', 'RED'))

        self.assertNotEqual(deck.Card(3, 'h', 'red'), deck.Card(4, 'h', 'red'))
        self.assertNotEqual(deck.Card(3, 'h', 'red'), deck.Card(3, 's', 'red'))
        self.assertNotEqual(deck.Card(3, 'h', 'red'), deck.Card(3, 'h', 'blue'))


class TestCardStack(unittest.TestCase):
    def test_add_card_stack(self):
        cards = random_cards(5)
        card_stack = deck.CardStack(cards=cards.copy())
        other_cards = random_cards(3)
        other_card_stack = deck.CardStack(cards=other_cards.copy())
        card_stack.add_card_stack(other_card_stack)
        self.assertEqual(card_stack._cards, cards + other_cards)
        self.assertEqual(other_card_stack.num_cards, 0)

    def test_add_card_stack_no_clear(self):
        cards = random_cards(5)
        card_stack = deck.CardStack(cards=cards.copy())
        other_cards = random_cards(3)
        other_card_stack = deck.CardStack(cards=other_cards.copy())
        card_stack.add_card_stack(other_card_stack, clear_other=False)
        self.assertEqual(card_stack._cards, cards + other_cards)
        self.assertEqual(other_card_stack._cards, other_cards)

    def test_add_card_stack_shuffle(self):
        cards = random_cards(5)
        card_stack = deck.CardStack(cards=cards.copy())
        other_cards = random_cards(3)
        other_card_stack = deck.CardStack(cards=other_cards.copy())
        card_stack.rand = mock.MagicMock()
        card_stack.add_card_stack(other_card_stack, shuffle=True)
        card_stack.rand.shuffle.assert_called_once_with(cards + other_cards)
        self.assertEqual(card_stack._cards, cards + other_cards)
        self.assertEqual(other_card_stack.num_cards, 0)

    def test_draw(self):
        cards = random_cards(5)
        card_stack = deck.CardStack(cards=cards.copy())
        for num_draws in range(1, len(cards) + 1):
            with self.subTest(num_draws=num_draws):
                self.assertEqual(card_stack.draw(), cards[-num_draws])

    def test_draw_empty(self):
        card_stack = deck.CardStack()
        self.assertRaises(IndexError, card_stack.draw)

    def test_clear(self):
        num_cards = 2
        card_stack = deck.CardStack(cards=random_cards(num_cards))
        self.assertEqual(card_stack.num_cards, num_cards)
        card_stack.clear()
        self.assertEqual(card_stack.num_cards, 0)
        card_stack.clear()
        self.assertEqual(card_stack.num_cards, 0)

    def test_shuffle(self):
        # test that card_stack.rand.shuffle() is called exactly once with card_stack._cards as the argument
        cards = random_cards(20)
        card_stack = deck.CardStack(cards=cards.copy())
        card_stack.rand = mock.MagicMock()
        card_stack.shuffle()
        card_stack.rand.shuffle.assert_called_once_with(cards)
        # test that card_stack.rand is correctly seeded
        r = random.Random()
        for seed in [random.randint(0, sys.maxsize) for _ in range(10)]:
            card_stack = deck.CardStack(cards=cards.copy(), seed=seed)
            r.seed(seed)
            comp_cards = cards.copy()
            r.shuffle(comp_cards)
            card_stack.shuffle()
            self.assertEqual(card_stack._cards, comp_cards)

    def test_eq(self):
        cards = random_cards(4)
        self.assertEqual(deck.CardStack(seed=1), deck.CardStack(seed=1))
        self.assertEqual(deck.CardStack(seed=1, cards=cards.copy()), deck.CardStack(seed=1, cards=cards.copy()))

        self.assertNotEqual(deck.CardStack(seed=1), deck.CardStack(seed=2))
        self.assertNotEqual(deck.CardStack(seed=1, cards=cards.copy()), deck.CardStack(seed=2, cards=cards.copy()))
        self.assertNotEqual(deck.CardStack(seed=1, cards=cards.copy()), deck.CardStack(seed=1))
        self.assertNotEqual(deck.CardStack(seed=1, cards=cards.copy()), deck.CardStack(seed=1, cards=cards.copy()[:2]))


class TestDeck(unittest.TestCase):
    def setUp(self):
        self.red_deck = deck.Deck(color='red', seed=1)

    def test_deck_cards(self):
        pass


if __name__ == '__main__':
    unittest.main()
