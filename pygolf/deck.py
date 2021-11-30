import random
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar, Dict, List


@dataclass
class Card:
    """
    A class to represent a playing card.
    """
    value: int
    suit: str
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
               self.suit.lower() == other.suit.lower()


class CardStack(ABC):
    """
    An abstract class representing a stack of cards.
    """
    def __init__(self, cards: List['Card'] = None):
        self._cards: List['Card'] = [] if cards is None else cards

    @property
    def num_cards(self):
        return len(self._cards)

    def draw(self):
        """
        Draw the top card from the deck.

        :raises IndexError: Raised when no cards are left in the deck but draw is called.
        :return: (Card) The top card of the deck.
        """
        if len(self._cards) == 0:
            raise IndexError("No cards left in deck")
        return self._cards.pop()

    @abstractmethod
    def reset(self):
        pass


class Deck(CardStack):
    """
    A class to represent a deck of cards.
    """
    def __init__(self, seed: int = None, cards: List['Card'] = None):

        """
        Construct a Deck object.

        :param seed: (Optional) Seed for self.rand. Defaults to a random value between 0 and sys.maxsize
        :param cards: (Optional) Cards to be put in self.__cards, in order. Defaults to a shuffled deck of 52 cards.
        :return: None
        """
        super().__init__(cards)
        self.seed = random.randrange(sys.maxsize) if seed is None else seed
        self.rand = random.Random(self.seed)
        if cards is None:
            self.reset()
            self.shuffle()

    def reset(self):
        """
        Reset the deck to the full 52 card state (Ace, 2-10, Jack, Queen, King of each of the four suits).

        :return: None
        """
        self._cards = [Card(v, s) for s in ('h', 'c', 'd', 's') for v in range(1, 14)]

    def add_discard_pile(self, discard_pile: 'DiscardPile'):
        """
        Adds a discard pile back into the deck, shuffles the deck, and resets the discard pile.

        :param discard_pile: The discard pile to be added back into the deck. Will be reset as a side effect.
        :return: None
        """
        # noinspection PyProtectedMember
        self._cards.extend(discard_pile._cards)
        discard_pile.reset()
        self.shuffle()

    def shuffle(self):
        """
        Randomly order the cards remaining in the deck.

        :return: None
        """
        self.rand.shuffle(self._cards)

    def __repr__(self):
        return "Deck({}, {})".format(self.seed, self._cards)

    def __str__(self):
        return "Deck of {} card{}".format(self.num_cards, "" if self.num_cards == 1 else "s")


class DiscardPile(CardStack):
    """
    A class to represent a discard pile of cards.
    """
    def peek(self):
        """
        Peek at the top card of the discard pile without removing it.

        :return: The top card of the discard pile.
        """
        return self._cards[-1]

    def reset(self):
        """
        Empty the discard pile.

        :return: None
        """
        self._cards = []

    def add_card(self, new_card: 'Card'):
        """
        Add a card to the top of the discard pile.

        :type new_card: Card
        :param new_card: Card to add to the top of the pile.
        :return: None
        """
        self._cards.append(new_card)

    def __repr__(self):
        return "DiscardPile({})".format(self._cards)

    def __str__(self):
        return "Discard pile of {} card{}{}".format(self.num_cards, "" if self.num_cards == 1 else "s",
                                                    "" if self.num_cards == 0 else ". Top card: " + str(self.peek()))
