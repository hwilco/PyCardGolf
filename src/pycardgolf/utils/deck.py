from __future__ import annotations

import random
import sys
from typing import List, Optional

from pycardgolf.utils.card import Card, Suit, Rank


class CardStack:
    """
    A class to represent a stack of cards.
    """

    def __init__(self, cards: Optional[List[Card]] = None, seed: Optional[int] = None) -> None:
        """
        Construct a CardStack object.

        Args:
            cards (optional): List of Cards to place in the stack.
            seed (optional): Seed for self.rand. Defaults to a random value between 0 and sys.maxsize.
        """
        self._cards: List[Card] = [] if cards is None else cards
        self.seed = random.randrange(sys.maxsize) if seed is None else seed
        self.rand = random.Random(self.seed)

    @property
    def num_cards(self) -> int:
        """
        Returns:
            num_cards: The number of cards in the CardStack.
        """
        return len(self._cards)

    def add_card_stack(self, other: CardStack, clear_other: Optional[bool] = None, shuffle: Optional[bool] = None) -> None:
        """
        Add the cards from a different card stack to this card stack. By default, this also clears other stack.

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

    def peek_color(self) -> str:
        """
        Find the color of the top card on the pile.

        Returns:
            str: The color of the top card on the pile.

        Raises:
            IndexError: If the card stack is empty.
        """
        if len(self._cards) == 0:
            raise IndexError("No cards left in stack")
        return self._cards[-1].color

    def draw(self) -> Card:
        """
        Draw the top card from the card stack.

        Returns:
            Card: The top card of the card stack.

        Raises:
            IndexError: If no cards are left in the card stack but draw is called.
        """
        if len(self._cards) == 0:
            raise IndexError("No cards left in stack")
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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CardStack):
            return NotImplemented
        return self.seed == other.seed and self._cards == other._cards

    def __repr__(self) -> str:
        return f"CardStack(cards={self._cards}, seed={self.seed})"

    def __str__(self) -> str:
        return "Stack of {} card{}".format(self.num_cards, "" if self.num_cards == 1 else "s")


class Deck(CardStack):
    """
    A class to represent a deck of cards.
    """

    def __init__(self, color: str, seed: Optional[int] = None) -> None:
        """
        Construct a Deck object of 52 ordered cards.

        Args:
            color: Color of cards in this deck. Converted to lowercase.
            seed (optional): Seed for self.rand. Defaults to a random value between 0 and sys.maxsize
        """
        super().__init__(seed=seed)
        self.color = color.lower()
        self.reset()

    def add_card_stack(self, other: CardStack, clear_other: Optional[bool] = None, shuffle: Optional[bool] = None) -> None:
        """
        Add the cards from a different card stack to this deck. The other card stack must contain only cards of the
            deck's color and may not contain cards already in the deck. By default, this also clears other stack.

        Args:
            other: The card stack to add to this stack.
            clear_other (optional): If True, clear the other card stack after adding its cards to this stack. Defaults
                to True.
            shuffle (optional): If True, shuffle the card stack after adding the other stack. Defaults to False.

        Raises:
            ValueError: If any of the cards to be added do not match the deck's color or already exist in the deck.
        """
        if any((c.color != self.color for c in other._cards)):
            raise ValueError(f"Card to be added does not match the deck's color ({self.color}).")
        if any((c in self._cards for c in other._cards)):
            raise ValueError("Card to be added is a duplicate of a card in the deck.")
        super().add_card_stack(other, clear_other, shuffle)

    def reset(self) -> None:
        """
        Reset the deck to the full 52 card state (Ace, 2-10, Jack, Queen, King of each of the four suits).
        """
        self._cards = [Card(rank, suit, self.color) for rank in Rank for suit in Suit]

    def __repr__(self) -> str:
        return f"Deck <color={self.color}, seed={self.seed}, _cards={self._cards}>"

    def __str__(self) -> str:
        return "Deck of {} {} card{}".format(self.num_cards, self.color, "" if self.num_cards == 1 else "s")


class DiscardStack(CardStack):
    """
    A class to represent a discard pile of cards.
    """

    @property
    def cards(self) -> List[Card]:
        """Returns a copy of the cards list to prevent external mutation."""
        return self._cards.copy()

    def add_card(self, new_card: Card) -> None:
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

        Raises:
            IndexError: If the discard stack is empty.
        """
        if len(self._cards) == 0:
            raise IndexError("No cards in discard stack")
        return self._cards[-1]

    def __repr__(self) -> str:
        return f"DiscardStack(cards={self._cards})"

    def __str__(self) -> str:
        return "Discard stack of {} card{}{}".format(self.num_cards, "" if self.num_cards == 1 else "s",
                                                     "" if self.num_cards == 0 else ". Top card: " + str(self.peek()))
