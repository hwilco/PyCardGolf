import unittest
from unittest import mock

import pycardgolf.utils.card
from pycardgolf.utils import card, deck
from pycardgolf.utils.card import Suit
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

    def test_peek_color(self):
        cards = [card.Card(3, pycardgolf.utils.card.Suit.CLUBS, 'red'), card.Card(3, pycardgolf.utils.card.Suit.CLUBS, 'blue')]
        card_stack = deck.CardStack(cards=cards.copy())
        self.assertEqual(card_stack.peek_color(), cards[-1].color)
        self.assertEqual(card_stack._cards[-1], cards[-1])
        card_stack.draw()
        self.assertEqual(card_stack.peek_color(), cards[-2].color)
        self.assertEqual(card_stack._cards[-1], cards[-2])

    def test_draw(self):
        card_stack = deck.CardStack(cards=self.cards_5.copy())
        for num_draws in range(1, len(self.cards_5) + 1):
            with self.subTest(num_draws=num_draws):
                self.assertEqual(card_stack.draw(), self.cards_5[-num_draws])

    def test_num_cards(self):
        card_stack = deck.CardStack(self.cards_5)
        self.assertEqual(card_stack.num_cards, 5)
        card_stack.draw()
        self.assertEqual(card_stack.num_cards, 4)
        card_stack.clear()
        self.assertEqual(card_stack.num_cards, 0)

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
        self.assertEqual(str(card_stack), f"Stack of {len(self.cards_5)} cards")
        card_stack.draw()
        self.assertEqual(str(card_stack), f"Stack of {len(self.cards_5) - 1} cards")

    def test_repr(self):
        self.assertEqual(repr(deck.CardStack(seed=1)), "CardStack(cards=[], seed=1)")
        card_stack = deck.CardStack(cards=self.cards_5.copy(), seed=1)
        self.assertEqual(repr(card_stack), f"CardStack(cards={self.cards_5}, seed=1)")
        card_stack.draw()
        self.assertEqual(repr(card_stack), f"CardStack(cards={self.cards_5[:-1]}, seed=1)")


class TestDeck(unittest.TestCase):
    def setUp(self):
        self.red_deck = deck.Deck(color='red', seed=1)

    def test_cards(self):
        self.assertTrue(all(card.Card(rank, suit, 'red') in self.red_deck._cards
                            for rank in range(1, 14) for suit in Suit))

    def test_reset(self):
        self.red_deck.draw()
        self.red_deck.reset()
        self.test_cards()

    def test_add_card_stack_valid(self):
        other_cards = self.red_deck._cards[:3].copy()
        del(self.red_deck._cards[:3])
        other_card_stack = deck.CardStack(cards=other_cards)
        self.red_deck.add_card_stack(other_card_stack)
        self.test_cards()
        self.assertEqual(other_card_stack.num_cards, 0)

    def test_add_card_stack_already_in_deck(self):
        other_card_stack = deck.CardStack(cards=[card.Card(3, Suit.CLUBS, 'red')])
        self.assertRaises(ValueError, self.red_deck.add_card_stack, other_card_stack)
        self.assertEqual(other_card_stack.num_cards, 1)

    def test_add_card_stack_wrong_suit(self):
        copied_card = self.red_deck._cards[-1]
        del(self.red_deck._cards[-1])
        other_card_stack = deck.CardStack(cards=[card.Card(copied_card.rank, copied_card.suit, 'blue')])
        self.assertRaises(ValueError, self.red_deck.add_card_stack, other_card_stack)
        self.assertEqual(other_card_stack.num_cards, 1)

    def test_add_card_stack_no_clear(self):
        other_cards = self.red_deck._cards[:3].copy()
        del (self.red_deck._cards[:3])
        other_card_stack = deck.CardStack(cards=other_cards.copy())
        self.red_deck.add_card_stack(other_card_stack, clear_other=False)
        self.test_cards()
        self.assertEqual(other_card_stack._cards, other_cards)

    def test_add_card_stack_shuffle(self):
        other_cards = self.red_deck._cards[:3].copy()
        del (self.red_deck._cards[:3])
        other_card_stack = deck.CardStack(cards=other_cards.copy())
        self.red_deck.rand = mock.MagicMock()
        self.red_deck.add_card_stack(other_card_stack, shuffle=True)
        self.red_deck.rand.shuffle.assert_called_once()
        self.test_cards()
        self.assertEqual(other_card_stack.num_cards, 0)

    def test_eq(self):
        deck_a = deck.Deck('blue', 1)
        deck_b = deck.Deck('blue', 1)
        self.assertEqual(deck_a, deck_b)

        deck_a.shuffle()
        self.assertNotEqual(deck_a, deck_b)

        deck_c = deck.Deck('blue', 1)
        deck_d = deck.Deck('red', 1)
        self.assertNotEqual(deck_c, deck_d)

    def test_str(self):
        self.assertEqual(str(self.red_deck), "Deck of 52 red cards")
        self.red_deck.draw()
        self.assertEqual(str(self.red_deck), "Deck of 51 red cards")
        card_deck = deck.Deck('blue')
        self.assertEqual(str(card_deck), "Deck of 52 blue cards")

    def test_repr(self):
        self.red_deck.clear()
        self.assertEqual(repr(self.red_deck), "Deck <color=red, seed=1, _cards=[]>")


if __name__ == '__main__':
    unittest.main()
