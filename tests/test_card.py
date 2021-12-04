import unittest
from pycardgolf.utils import card
import string

__unittest = True


class TestCard(unittest.TestCase):
    def test_value_outside_range(self):
        for value in [0, 14]:
            with self.subTest(value=value):
                self.assertRaises(ValueError, card.Card, value, 'h', 'blue')

    def test_value_inside_range(self):
        for value in range(1, 14):
            with self.subTest(msg="ValueError unexpectedly raised by Card({}, 'h')".format(value), value=value):
                try:
                    card.Card(value, 'h', 'blue')
                except ValueError:
                    self.fail()

    def test_suit_invalid(self):
        for suit in ['clubs', 'diamonds', 'hearts', 'spades'] + [s for s in string.ascii_lowercase if s not in 'cdhs']:
            with self.subTest(suit=suit):
                self.assertRaises(ValueError, card.Card, 1, suit, 'blue')

    def test_suit_valid(self):
        for suit in 'cdhsCDHS':
            with self.subTest(msg="ValueError unexpectedly raised by Card(1, {})".format(suit), suit=suit):
                try:
                    card.Card(1, suit, 'blue')
                except ValueError:
                    self.fail()

    def test_eq(self):
        self.assertEqual(card.Card(3, 'h', 'red'), card.Card(3, 'h', 'red'))
        self.assertEqual(card.Card(3, 'H', 'red'), card.Card(3, 'h', 'red'))
        self.assertEqual(card.Card(3, 'h', 'red'), card.Card(3, 'h', 'RED'))

        self.assertNotEqual(card.Card(3, 'h', 'red'), card.Card(4, 'h', 'red'))
        self.assertNotEqual(card.Card(3, 'h', 'red'), card.Card(3, 's', 'red'))
        self.assertNotEqual(card.Card(3, 'h', 'red'), card.Card(3, 'h', 'blue'))

    def test_str(self):
        self.assertEqual(str(card.Card(1, 'c', 'red')), "A\u2667")
        self.assertEqual(str(card.Card(2, 'c', 'red')), "2\u2667")
        self.assertEqual(str(card.Card(11, 'c', 'red')), "J\u2667")
        self.assertEqual(str(card.Card(12, 'c', 'red')), "Q\u2667")
        self.assertEqual(str(card.Card(13, 'c', 'red')), "K\u2667")

        self.assertEqual(str(card.Card(13, 'd', 'red')), "K\u2662")
        self.assertEqual(str(card.Card(13, 'h', 'red')), "K\u2661")
        self.assertEqual(str(card.Card(13, 's', 'red')), "K\u2664")

    def test_repr(self):
        self.assertEqual(repr(card.Card(1, 'c', 'red')), "Card(1, 'C', 'red')")
        self.assertEqual(repr(card.Card(1, 'C', 'red')), "Card(1, 'C', 'red')")
        self.assertEqual(repr(card.Card(1, 'C', 'Red')), "Card(1, 'C', 'red')")
        self.assertEqual(repr(card.Card(1, 'C', 'RED')), "Card(1, 'C', 'red')")


if __name__ == '__main__':
    unittest.main()
