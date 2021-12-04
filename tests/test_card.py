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


if __name__ == '__main__':
    unittest.main()
