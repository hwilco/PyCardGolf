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
    __suit_dict: ClassVar[Dict[str, str]] = {"S": '\u2660',
                                             "H": '\u2665',
                                             "D": '\u2666',
                                             "C": '\u2663'}
    __suit_outline_dict: ClassVar[Dict[str, str]] = {"S": '\u2664',
                                                     "H": '\u2661',
                                                     "D": '\u2662',
                                                     "C": '\u2667'}

    def __init__(self, value: int, suit: str, color: str) -> None:
        """
        Construct a Card object.

        Args:
            value: The value of the card. 1 -> Ace, 2-10 -> 2-10, 11 -> Jack, 12 -> Queen, 13 -> King.
            suit: A single letter indicating the suit of the card. 's' -> Spades, 'h' - > Hearts, 'd' -> Diamonds,
                'c' -> Clubs. Converted to upper case.
            color: A string representing the color of the card. Used to differentiate cards from different decks.
                Converted to lower case.

        Raises:
            ValueError: If value or suit are out of range.
        """
        self.value = value
        if self.value not in Card.__value_dict:
            raise ValueError("Card value must be an int in range(1,14). Given value: {}".format(value))
        self.suit = suit
        if self.suit not in Card.__suit_dict:
            raise ValueError("Card suit must be in ['S', 'H', 'D', 'C']. Given value: {}".format(suit))
        self.color = color

    @property
    def __value_str(self) -> str:
        return Card.__value_dict[self.value]

    @property
    def __suit_str(self) -> str:
        # TODO: handle configuration of suit display (outline or filled)
        outline_suits = True
        if outline_suits:
            return Card.__suit_outline_dict[self.suit]
        else:
            return Card.__suit_dict[self.suit]

    def __setattr__(self, key, value) -> None:
        if key == 'suit':
            value = value.upper()
        elif key == 'color':
            value = value.lower()
        super().__setattr__(key, value)

    def __repr__(self) -> str:
        return "Card({}, '{}', '{}')".format(self.value, self.suit, self.color)

    def __str__(self) -> str:
        return self.__value_str + self.__suit_str

    def __eq__(self, other: 'Card') -> bool:
        return self.value == other.value and \
               self.suit == other.suit and \
               self.color == other.color


class CardStack:
    """
    A class to represent a stack of cards.
    """

    def __init__(self, cards: 'List[Card]' = None, seed: int = None) -> None:
        """
        Construct a CardStack object.

        Args:
            cards (optional): List of Cards to place in the stack.
            seed (optional): Seed for self.rand. Defaults to a random value between 0 and sys.maxsize
        """
        self._cards: 'List[Card]' = [] if cards is None else cards
        self.seed = random.randrange(sys.maxsize) if seed is None else seed
        self.rand = random.Random(self.seed)

    @property
    def num_cards(self) -> int:
        return len(self._cards)

    def add_card_stack(self, other: 'CardStack', clear_other: bool = None, shuffle: bool = None) -> None:
        """
        Add the cards from a different card stack to this card stack. By default this also clears other stack.

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

    def draw(self) -> 'Card':
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

    def clear(self) -> None:
        """
        Clear the card stack.
        """
        self._cards = []

    def shuffle(self) -> None:
        """
        Randomly order the cards remaining in the stack.
        """
        self.rand.shuffle(self._cards)

    def __eq__(self, other: 'CardStack') -> bool:
        # noinspection PyProtectedMember
        return self.seed == other.seed and \
               self._cards == other._cards

    def __repr__(self) -> str:
        return "CardStack(cards={}, seed={})".format(self._cards, self.seed)

    def __str__(self) -> str:
        return "Stack of {} card{}".format(self.num_cards, "" if self.num_cards == 1 else "s")


class Deck(CardStack):
    """
    A class to represent a deck of cards.
    """

    def __init__(self, color: str, seed: int = None) -> None:
        """
        Construct a Deck object of 52 ordered cards.

        Args:
            seed (optional): Seed for self.rand. Defaults to a random value between 0 and sys.maxsize
        """
        super().__init__(seed=seed)
        self.color = color
        self.reset()

    def add_card_stack(self, other: 'CardStack', clear_other: bool = None, shuffle: bool = None) -> None:
        """
        Add the cards from a different card stack to this deck. The other card stack must contain only cards of the
            deck's color and may not contain cards already in the deck. By default this also clears other stack.

        Args:
            other: The card stack to add to this stack.
            clear_other (optional): If True, clear the other card stack after adding its cards to this stack. Defaults
                to True.
            shuffle (optional): If True, shuffle the card stack after adding the other stack. Defaults to False.

        Raises:
            ValueError: If any of the cards to be added do not match the deck's color or already exist in the deck.
        """
        # noinspection PyProtectedMember
        if any((c.color != self.color for c in other._cards)):
            raise ValueError("Card to be added does not match the deck's color ({}).".format(self.color))
        # noinspection PyProtectedMember
        if any((c in self._cards for c in other._cards)):
            raise ValueError("Card to be added is a duplicate of a card in the deck.")
        super().add_card_stack(other, clear_other, shuffle)

    def reset(self) -> None:
        """
        Reset the deck to the full 52 card state (Ace, 2-10, Jack, Queen, King of each of the four suits).
        """
        self._cards = [Card(v, s, self.color) for s in ('c', 'd', 'h', 's') for v in range(1, 14)]

    def __repr__(self) -> str:
        return "Deck <color={}, seed={}, _cards={}>".format(self.color, self.seed, self._cards)

    def __str__(self) -> str:
        return "Deck of {} card{}".format(self.num_cards, "" if self.num_cards == 1 else "s")


class DiscardStack(CardStack):
    """
    A class to represent a discard pile of cards.
    """

    @property
    def cards(self) -> 'List[Card]':
        return self._cards

    def add_card(self, new_card: 'Card') -> None:
        """
        Add a card to the top of the discard stack.

        Args:
            new_card: Card to add to the top of the stack.
        """
        self._cards.append(new_card)

    def peek(self) -> Card:
        """
        Peek at the top card of the discard stack without removing it.

        Returns:
            Card: The top card of the discard stack.
        """
        return self._cards[-1]

    def __repr__(self) -> str:
        return "DiscardStack(cards={})".format(self._cards)

    def __str__(self) -> str:
        return "Discard stack of {} card{}{}".format(self.num_cards, "" if self.num_cards == 1 else "s",
                                                     "" if self.num_cards == 0 else ". Top card: " + str(self.peek()))
