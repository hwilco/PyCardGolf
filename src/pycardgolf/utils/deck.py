"""Module containing CardStack, Deck, and DiscardStack classes."""

from __future__ import annotations

from typing import ClassVar

from pycardgolf.utils.card import Card
from pycardgolf.utils.enums import Rank, Suit
from pycardgolf.utils.mixins import RNGMixin


class CardStack(RNGMixin):
    """A class to represent a stack of cards."""

    def __init__(
        self,
        cards: list[Card] | None = None,
        seed: int | None = None,
    ) -> None:
        """Construct a CardStack object.

        Args:
            cards (optional): List of Cards to place in the stack.
            seed (optional): Seed for the random number generator.

        """
        super().__init__(seed=seed)
        self._cards: list[Card] = [] if cards is None else cards

    @property
    def num_cards(self) -> int:
        """Returns the number of cards in the CardStack."""
        return len(self._cards)

    @property
    def cards(self) -> list[Card]:
        """Returns a copy of the cards list to prevent external mutation."""
        return self._cards.copy()

    def add_card(self, new_card: Card) -> None:
        """Add a card to the top of the stack.

        Args:
            new_card: Card to add to the top of the stack.

        """
        self._cards.append(new_card)

    def add_card_stack(
        self,
        other: CardStack,
        clear_other: bool = True,
        shuffle: bool = False,
    ) -> None:
        """Add the cards from a different card stack to this card stack.

        By default, this also clears other stack.

        Args:
            other: The card stack to add to this stack.
            clear_other (optional): If True, clear the other card stack after
                adding its cards to this stack. Defaults to True.
            shuffle (optional): If True, shuffle the card stack after adding
                the other stack. Defaults to False.

        """
        self._cards.extend(other._cards)
        if clear_other:
            other.clear()
        if shuffle:
            self.shuffle()

    def peek(self) -> Card:
        """Peek at the top card of the card stack without removing it.

        Returns:
            The top card of the card stack.

        Raises:
            IndexError: If the card stack is empty.

        """
        if len(self._cards) == 0:
            msg = "No cards in card stack"
            raise IndexError(msg)
        return self._cards[-1]

    def draw(self) -> Card:
        """Draw the top card from the card stack.

        Returns:
            The top card of the card stack.

        Raises:
            IndexError: If no cards are left in the card stack but draw is called.

        """
        if len(self._cards) == 0:
            msg = "No cards left in stack"
            raise IndexError(msg)
        return self._cards.pop()

    def clear(self) -> None:
        """Clear the card stack."""
        self._cards = []

    def shuffle(self) -> None:
        """Randomly order the cards remaining in the stack."""
        self.rng.shuffle(self._cards)

    def clone(self, preserve_rng: bool = False) -> CardStack:
        """Return a deep copy of the CardStack.

        Args:
            preserve_rng: If True, copies the exact random number generator state.
                If False (default), creates a new randomized seed for the clone.

        """
        cloned_stack = CardStack(
            cards=[c.clone() for c in self._cards],
            seed=self.seed if preserve_rng else None,
        )
        if preserve_rng:
            self.copy_rng_state(cloned_stack)
        return cloned_stack

    def __eq__(self, other: object) -> bool:
        """Check equality with another object."""
        if not isinstance(other, CardStack):
            return NotImplemented
        return self.seed == other.seed and self._cards == other._cards

    __hash__ = None  # type: ignore[assignment]

    def __repr__(self) -> str:
        """Return string representation of the CardStack."""
        return f"CardStack(cards={self._cards}, seed={self.seed})"

    def __str__(self) -> str:
        """Return human-readable string representation."""
        return "Stack of {} card{}".format(
            self.num_cards,
            "" if self.num_cards == 1 else "s",
        )


class Deck(CardStack):
    """A class to represent a deck of cards."""

    _DEFAULT_SUIT_COLORS: ClassVar[dict[Suit, str]] = {
        Suit.CLUBS: "black",
        Suit.DIAMONDS: "red",
        Suit.HEARTS: "red",
        Suit.SPADES: "black",
    }

    def __init__(
        self,
        back_color: str,
        suit_colors: dict[Suit, str] | None = None,
        seed: int | None = None,
    ) -> None:
        """Construct a Deck object of 52 ordered cards.

        Args:
            back_color: Color of the back of cards in this deck. Converted to lowercase.
            suit_colors (optional): Dictionary of suit colors. Defaults to
                Deck._DEFAULT_SUIT_COLORS. Any Suits not provided will use the default
                color.
            seed (optional): Seed for the random number generator.

        """
        super().__init__(seed=seed)
        self.back_color: str = back_color.lower()
        self.suit_colors: dict[Suit, str] = self._DEFAULT_SUIT_COLORS.copy()
        if suit_colors:
            self.suit_colors.update(suit_colors)
        self.reset()

    def add_card(self, new_card: Card) -> None:
        """Add a card to the deck with validation.

        The card must match the deck's color and not already exist in the deck.

        Args:
            new_card: Card to add.

        Raises:
            ValueError: If the card does not match the deck's color or is a duplicate.

        """
        if new_card.back_color != self.back_color:
            msg = (
                "Card to be added does not match the deck's back color "
                f"({self.back_color})"
            )
            raise ValueError(msg)
        if new_card in self._cards:
            msg = "Card to be added is a duplicate of a card in the deck"
            raise ValueError(msg)
        super().add_card(new_card)

    def add_card_stack(
        self,
        other: CardStack,
        clear_other: bool = True,
        shuffle: bool = False,
    ) -> None:
        """Add the cards from a different card stack to this deck.

        The other card stack must contain only cards of the deck's color and
        may not contain cards already in the deck.
        By default, this also clears other stack.

        Args:
            other: The card stack to add to this stack.
            clear_other (optional): If True, clear the other card stack after
                adding its cards to this stack. Defaults to True.
            shuffle (optional): If True, shuffle the card stack after adding
                the other stack. Defaults to False.

        Raises:
            ValueError: If any of the cards to be added do not match the
                deck's color or already exist in the deck.

        """
        if any(c.back_color != self.back_color for c in other.cards):
            msg = (
                "Card to be added does not match the deck's back color"
                f" ({self.back_color})"
            )
            raise ValueError(msg)
        if any(c in self._cards for c in other.cards):
            msg = "Card to be added is a duplicate of a card in the deck"
            raise ValueError(msg)
        super().add_card_stack(other, clear_other, shuffle)

    def reset(self) -> None:
        """Reset the deck to the full 52 card state."""
        self._cards = [
            Card(rank, suit, self.back_color, self.suit_colors[suit])
            for rank in Rank
            if rank != Rank.HIDDEN
            for suit in Suit
            if suit != Suit.HIDDEN
        ]

    def clone(self, preserve_rng: bool = False) -> Deck:
        """Return a deep copy of the Deck.

        Args:
            preserve_rng: If True, copies the exact random number generator state.
                If False (default), creates a new randomized seed for the clone.

        """
        cloned_deck = Deck(
            back_color=self.back_color,
            suit_colors=self.suit_colors.copy(),
            seed=self.seed if preserve_rng else None,
        )
        cloned_deck._cards = [c.clone() for c in self._cards]
        if preserve_rng:
            self.copy_rng_state(cloned_deck)
        return cloned_deck

    def __repr__(self) -> str:
        """Return string representation of the Deck."""
        return (
            f"Deck <back_color={self.back_color}, seed={self.seed}, "
            f"_cards={self._cards}, suit_colors={self.suit_colors}>"
        )

    def __str__(self) -> str:
        """Return human-readable string representation."""
        return "Deck of {} {} card{}".format(
            self.num_cards,
            self.back_color,
            "" if self.num_cards == 1 else "s",
        )

    def __eq__(self, other: object) -> bool:
        """Check equality with another Deck."""
        if not isinstance(other, Deck):
            return NotImplemented
        return (
            self.back_color == other.back_color
            and self.seed == other.seed
            and self._cards == other._cards
            and self.suit_colors == other.suit_colors
        )

    __hash__ = None  # type: ignore[assignment]
