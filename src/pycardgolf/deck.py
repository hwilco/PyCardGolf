import random
import sys
from typing import ClassVar, Dict, List


class Card:
    """
    A class to represent a playing card.
    """

    __value_dict: ClassVar[Dict[int, int]] = {1: "A",
                                              2: "2",
                                              3: "3",
                                              4: "4",
                                              5: "5",
                                              6: "6",
                                              7: "7",
                                              8: "8",
                                              9: "9",
                                              10: "10",
                                              11: "J",
                                              12: "Q",
                                              13: "K"}
    __suit_dict: ClassVar[Dict[str, str]] = {"s": '\u2660',
                                             "h": '\u2665',
                                             "d": '\u2666',
                                             "c": '\u2663',
                                             "s_outline": '\u2664',
                                             "h_outline": '\u2661',
                                             "d_outline": '\u2662',
                                             "c_outline": '\u2667'}

    def __init__(self, value: int, suit: str):
        """
        Construct a Card object.

        Args:
            value: The value of the card. 1 -> Ace, 2-10 -> 2-10, 11 -> Jack, 12 -> Queen, 13 -> King.
            suit: A single letter indicating the suit of the card. 's' -> Spades, 'h' - > Hearts, 'd' -> Diamonds,
                'c' -> Clubs

        Raises:
            ValueError: If value or suit are out of range.
        """
        suit = suit.lower()
        if value not in Card.__value_dict:
            raise ValueError("Card value must be an int in range(1,14). Given value: {}".format(value))
        if suit not in Card.__suit_dict:
            raise ValueError("Card suit must be in ['s', 'h', 'd', 'c']. Given value: {}".format(suit))
        self.value = value
        self.suit = suit

    @property
    def __value_str(self):
        return Card.__value_dict[self.value]

    @property
    def __suit_str(self):
        return Card.__suit_dict[self.suit.lower() + "_outline"]

    def __repr__(self):
        return "Card({}, '{}')".format(self.value, self.suit.upper())

    def __str__(self):
        return self.__value_str + self.__suit_str

    def __eq__(self, other: 'Card'):
        return self.value == other.value and \
               self.suit == other.suit


class CardStack:
    """
    A class to represent a stack of cards.
    """

    def __init__(self, seed: int = None, cards: 'List[Card]' = None):
        self._cards: 'List[Card]' = [] if cards is None else cards
        self.seed = random.randrange(sys.maxsize) if seed is None else seed
        self.rand = random.Random(self.seed)

    @property
    def num_cards(self):
        return len(self._cards)

    def add_card_stack(self, other: 'CardStack', clear_other: bool = None, shuffle: bool = None):
        """
        Add the cards from a different card stack to this card stack. By default this also clears other and shuffles
            this card stack.

        Args:
            other: The card stack to add to this stack.
            clear_other (optional): If True, clear the other card stack after adding its cards to this stack. Defaults
                to True.
            shuffle (optional): If True, shuffle the card stack after adding the other stack. Defaults to False.
        """
        clear_other = True if clear_other is None else clear_other
        shuffle = False if shuffle is None else shuffle

        self._cards.extend(other._cards)
        if clear_other:
            other.clear()
        if shuffle:
            self.shuffle()

    def draw(self):
        """
        Draw the top card from the card stack.

        Returns:
            Card: The top card of the card stack.

        Raises:
            IndexError: If no cards are left in the card stack but draw is called.
        """
        if len(self._cards) == 0:
            raise IndexError("No cards left in deck")
        return self._cards.pop()

    def clear(self):
        """
        Clear the card stack.
        """
        self._cards = []

    def shuffle(self):
        """
        Randomly order the cards remaining in the stack.
        """
        self.rand.shuffle(self._cards)

    def __eq__(self, other):
        # noinspection PyProtectedMember
        return self.seed == other.seed and self._cards == other._cards

    def __repr__(self):
        return "CardStack({}, {})".format(self.seed, self._cards)

    def __str__(self):
        return "Stack of {} card{}".format(self.num_cards, "" if self.num_cards == 1 else "s")


class Deck(CardStack):
    """
    A class to represent a deck of cards.
    """

    def __init__(self, seed: int = None):
        """
        Construct a Deck object of 52 ordered cards.

        Args:
            seed (optional): Seed for self.rand. Defaults to a random value between 0 and sys.maxsize
        """
        super().__init__(seed=seed)
        self.reset()

    def reset(self):
        """
        Reset the deck to the full 52 card state (Ace, 2-10, Jack, Queen, King of each of the four suits).
        """
        self._cards = [Card(v, s) for s in ('c', 'd', 'h', 's') for v in range(1, 14)]

    def __repr__(self):
        return "Deck <seed={}, _cards={}>".format(self.seed, self._cards)

    def __str__(self):
        return "Deck of {} card{}".format(self.num_cards, "" if self.num_cards == 1 else "s")


class DiscardPile(CardStack):
    """
    A class to represent a discard pile of cards.
    """

    @property
    def cards(self):
        return self._cards

    def add_card(self, new_card: 'Card'):
        """
        Add a card to the top of the discard pile.

        Args:
            new_card: Card to add to the top of the pile.
        """
        self._cards.append(new_card)

    def peek(self):
        """
        Peek at the top card of the discard pile without removing it.

        Returns:
            Card: The top card of the discard pile.
        """
        return self._cards[-1]

    def __repr__(self):
        return "DiscardPile({})".format(self._cards)

    def __str__(self):
        return "Discard pile of {} card{}{}".format(self.num_cards, "" if self.num_cards == 1 else "s",
                                                    "" if self.num_cards == 0 else ". Top card: " + str(self.peek()))
