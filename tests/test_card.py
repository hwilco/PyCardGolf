import unittest
from pycardgolf.utils.card import Card, Suit

# Hide the contents of the TestCase.assert* methods in the traceback.
__unittest = True


class TestCard(unittest.TestCase):
    def test_rank_outside_range(self):
        for rank in [0, 14]:
            with self.subTest(rank=rank):
                self.assertRaises(ValueError, Card, rank, Suit.HEARTS, 'blue')

    def test_rank_inside_range(self):
        for rank in range(1, 14):
            with self.subTest(msg=f"ValueError unexpectedly raised by Card({rank}, Suit.HEARTS)", rank=rank):
                try:
                    Card(rank, Suit.HEARTS, 'blue')
                except ValueError:
                    self.fail()

    def test_invalid_suit(self):
        self.assertRaises(ValueError, Card, 1, 1, 'red')

    def test_suit_valid(self):
        for suit in Suit:
            with self.subTest(msg=f"ValueError unexpectedly raised by Card(1, {suit})", suit=suit):
                try:
                    Card(1, suit, 'blue')
                except ValueError:
                    self.fail()

    def test_eq(self):
        self.assertEqual(Card(3, Suit.HEARTS, 'red'), Card(3, Suit.HEARTS, 'red'))
        # Color will be converted to lowercase
        self.assertEqual(Card(3, Suit.HEARTS, 'red'), Card(3, Suit.HEARTS, 'RED'))

        # Different ranks
        self.assertNotEqual(Card(3, Suit.HEARTS, 'red'), Card(4, Suit.HEARTS, 'red'))
        # Different suits
        self.assertNotEqual(Card(3, Suit.HEARTS, 'red'), Card(3, Suit.SPADES, 'red'))
        # Different colors
        self.assertNotEqual(Card(3, Suit.HEARTS, 'red'), Card(3, Suit.HEARTS, 'blue'))
        # Face down vs. face up
        self.assertNotEqual(Card(3, Suit.HEARTS, 'red'), Card(3, Suit.HEARTS, 'red', True))

    def test_str(self):
        # Face cards are translated to their letter representations
        self.assertEqual(str(Card(1, Suit.CLUBS, 'red', True)), "A\u2667")
        self.assertEqual(str(Card(2, Suit.CLUBS, 'red', True)), "2\u2667")
        self.assertEqual(str(Card(11, Suit.CLUBS, 'red', True)), "J\u2667")
        self.assertEqual(str(Card(12, Suit.CLUBS, 'red', True)), "Q\u2667")
        self.assertEqual(str(Card(13, Suit.CLUBS, 'red', True)), "K\u2667")

        # Suits (other than clubs which is tested above) are translated to their unicode characters
        self.assertEqual(str(Card(13, Suit.DIAMONDS, 'red', True)), "K\u2662")
        self.assertEqual(str(Card(13, Suit.HEARTS, 'red', True)), "K\u2661")
        self.assertEqual(str(Card(13, Suit.SPADES, 'red', True)), "K\u2664")

    def test_str_no_outline(self):
        for suit, suit_str in zip(Suit, ['\u2663', '\u2666', '\u2665', '\u2660']):
            c = Card(1, suit, 'red')
            c._outline_suits = False
            c.face_up = True
            self.assertEqual(str(c), f"A{suit_str}")

    def test_str_face_down(self):
        self.assertEqual(str(Card(1, Suit.HEARTS, 'red', False)), "??")

    def test_repr(self):
        self.assertEqual(repr(Card(1, Suit.SPADES, 'red')), "Card(1, Suit.SPADES, 'red', False)")
        # Test a different suit
        self.assertEqual(repr(Card(1, Suit.HEARTS, 'red')), "Card(1, Suit.HEARTS, 'red', False)")
        # Test a different rank
        self.assertEqual(repr(Card(2, Suit.SPADES, 'red')), "Card(2, Suit.SPADES, 'red', False)")
        # Test a different color
        self.assertEqual(repr(Card(1, Suit.SPADES, 'blue')), "Card(1, Suit.SPADES, 'blue', False)")

        # Color will be converted to lowercase
        self.assertEqual(repr(Card(1, Suit.SPADES, 'Red')), "Card(1, Suit.SPADES, 'red', False)")
        self.assertEqual(repr(Card(1, Suit.SPADES, 'RED')), "Card(1, Suit.SPADES, 'red', False)")

        # Test setting face_up to True
        self.assertEqual(repr(Card(1, Suit.SPADES, 'red', True)), "Card(1, Suit.SPADES, 'red', True)")

    def test_flip(self):
        c = Card(1, Suit.SPADES, 'red', False)
        c.flip()
        self.assertTrue(c.face_up)
        c.flip()
        self.assertFalse(c.face_up)


if __name__ == '__main__':
    unittest.main()
