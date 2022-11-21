import unittest
from pycardgolf.utils import card
from pycardgolf.utils.const import Suit

__unittest = True


class TestCard(unittest.TestCase):
    def test_rank_outside_range(self):
        for rank in [0, 14]:
            with self.subTest(rank=rank):
                self.assertRaises(ValueError, card.Card, rank, Suit.HEARTS, 'blue')

    def test_rank_inside_range(self):
        for rank in range(1, 14):
            with self.subTest(msg=f"ValueError unexpectedly raised by Card({rank}, Suit.HEARTS)", rank=rank):
                try:
                    card.Card(rank, Suit.HEARTS, 'blue')
                except ValueError:
                    self.fail()

    def test_invalid_suit(self):
        self.assertRaises(ValueError, card.Card, 1, 1, 'red')

    def test_suit_valid(self):
        for suit in Suit:
            with self.subTest(msg=f"ValueError unexpectedly raised by Card(1, {suit})", suit=suit):
                try:
                    card.Card(1, suit, 'blue')
                except ValueError:
                    self.fail()

    def test_eq(self):
        self.assertEqual(card.Card(3, Suit.HEARTS, 'red'), card.Card(3, Suit.HEARTS, 'red'))
        self.assertEqual(card.Card(3, Suit.HEARTS, 'red'), card.Card(3, Suit.HEARTS, 'red'))
        self.assertEqual(card.Card(3, Suit.HEARTS, 'red'), card.Card(3, Suit.HEARTS, 'RED'))

        self.assertNotEqual(card.Card(3, Suit.HEARTS, 'red'), card.Card(4, Suit.HEARTS, 'red'))
        self.assertNotEqual(card.Card(3, Suit.HEARTS, 'red'), card.Card(3, Suit.SPADES, 'red'))
        self.assertNotEqual(card.Card(3, Suit.HEARTS, 'red'), card.Card(3, Suit.HEARTS, 'blue'))

    def test_str(self):
        self.assertEqual(str(card.Card(1, Suit.CLUBS, 'red')), "A\u2667")
        self.assertEqual(str(card.Card(2, Suit.CLUBS, 'red')), "2\u2667")
        self.assertEqual(str(card.Card(11, Suit.CLUBS, 'red')), "J\u2667")
        self.assertEqual(str(card.Card(12, Suit.CLUBS, 'red')), "Q\u2667")
        self.assertEqual(str(card.Card(13, Suit.CLUBS, 'red')), "K\u2667")

        self.assertEqual(str(card.Card(13, Suit.DIAMONDS, 'red')), "K\u2662")
        self.assertEqual(str(card.Card(13, Suit.HEARTS, 'red')), "K\u2661")
        self.assertEqual(str(card.Card(13, Suit.SPADES, 'red')), "K\u2664")

    def test_str_no_outline(self):
        for s, s_str in zip(Suit, ['\u2663', '\u2666', '\u2665', '\u2660']):
            c = card.Card(1, s, 'red')
            c._outline_suits = False
            self.assertEqual(str(c), f"A{s_str}")

    def test_repr(self):
        self.assertEqual(repr(card.Card(1, Suit.CLUBS, 'red')), "Card(1, Suit.CLUBS, 'red')")
        self.assertEqual(repr(card.Card(1, Suit.CLUBS, 'red')), "Card(1, Suit.CLUBS, 'red')")
        self.assertEqual(repr(card.Card(1, Suit.CLUBS, 'Red')), "Card(1, Suit.CLUBS, 'red')")
        self.assertEqual(repr(card.Card(1, Suit.CLUBS, 'RED')), "Card(1, Suit.CLUBS, 'red')")


if __name__ == '__main__':
    unittest.main()
