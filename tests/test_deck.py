import unittest
from unittest import mock
from pycardgolf.utils import card, deck
from pycardgolf.utils.const import Suit
import sys
import random

__unittest = True


def random_cards(num_cards: int):
    return [card.Card(random.randint(1, 13), random.choice(list(Suit)), random.choice(['red', 'blue'])) for
            _ in range(num_cards)]


class TestCardStack(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cards_5 = random_cards(5)

    def test_add_card_stack(self):
        card_stack = deck.CardStack(cards=self.cards_5.copy())
        other_cards = random_cards(3)
        other_card_stack = deck.CardStack(cards=other_cards.copy())
        card_stack.add_card_stack(other_card_stack)
        self.assertEqual(card_stack._cards, self.cards_5 + other_cards)
        self.assertEqual(other_card_stack.num_cards, 0)

    def test_add_card_stack_no_clear(self):
        card_stack = deck.CardStack(cards=self.cards_5.copy())
        other_cards = random_cards(3)
        other_card_stack = deck.CardStack(cards=other_cards.copy())
        card_stack.add_card_stack(other_card_stack, clear_other=False)
        self.assertEqual(card_stack._cards, self.cards_5 + other_cards)
        self.assertEqual(other_card_stack._cards, other_cards)

    def test_add_card_stack_shuffle(self):
        card_stack = deck.CardStack(cards=self.cards_5.copy())
        other_cards = random_cards(3)
        other_card_stack = deck.CardStack(cards=other_cards.copy())
        card_stack.rand = mock.MagicMock()
        card_stack.add_card_stack(other_card_stack, shuffle=True)
        card_stack.rand.shuffle.assert_called_once_with(self.cards_5 + other_cards)
        self.assertEqual(card_stack._cards, self.cards_5 + other_cards)
        self.assertEqual(other_card_stack.num_cards, 0)

    def test_draw(self):
        card_stack = deck.CardStack(cards=self.cards_5.copy())
        for num_draws in range(1, len(self.cards_5) + 1):
            with self.subTest(num_draws=num_draws):
                self.assertEqual(card_stack.draw(), self.cards_5[-num_draws])

    def test_draw_empty(self):
        card_stack = deck.CardStack()
        self.assertRaises(IndexError, card_stack.draw)

    def test_clear(self):
        card_stack = deck.CardStack(cards=self.cards_5.copy())
        self.assertEqual(card_stack.num_cards, len(self.cards_5))
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
        self.assertEqual(deck.CardStack(seed=1), deck.CardStack(seed=1))
        self.assertEqual(deck.CardStack(seed=1, cards=self.cards_5.copy()), deck.CardStack(seed=1, cards=self.cards_5
                                                                                           .copy()))

        self.assertNotEqual(deck.CardStack(seed=1), deck.CardStack(seed=2))
        self.assertNotEqual(deck.CardStack(seed=1, cards=self.cards_5.copy()), deck.CardStack(seed=2, cards=self.cards_5
                                                                                              .copy()))
        self.assertNotEqual(deck.CardStack(seed=1, cards=self.cards_5.copy()), deck.CardStack(seed=1))
        self.assertNotEqual(deck.CardStack(seed=1, cards=self.cards_5.copy()), deck.CardStack(seed=1, cards=self.cards_5
                                                                                              .copy()[:2]))

    def test_str(self):
        self.assertEqual(str(deck.CardStack(seed=1)), "Stack of 0 cards")
        card_stack = deck.CardStack(cards=self.cards_5.copy())
        self.assertEqual(str(card_stack), "Stack of {} cards".format(len(self.cards_5)))
        card_stack.draw()
        self.assertEqual(str(card_stack), "Stack of {} cards".format(len(self.cards_5) - 1))

    def test_repr(self):
        self.assertEqual(repr(deck.CardStack(seed=1)), "CardStack(cards=[], seed=1)")
        card_stack = deck.CardStack(cards=self.cards_5.copy(), seed=1)
        self.assertEqual(repr(card_stack), "CardStack(cards={}, seed=1)".format(self.cards_5))
        card_stack.draw()
        self.assertEqual(repr(card_stack), "CardStack(cards={}, seed=1)".format(self.cards_5[:-1]))


class TestDeck(unittest.TestCase):
    def setUp(self):
        self.red_deck = deck.Deck(color='red', seed=1)

    def test_deck_cards(self):
        pass


if __name__ == '__main__':
    unittest.main()
