import unittest
from pycardgolf import deck
import string
__unittest = True


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


if __name__ == '__main__':
    unittest.main()
