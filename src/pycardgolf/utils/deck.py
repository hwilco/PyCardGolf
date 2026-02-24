"""Module containing CardStack and Deck classes."""

from __future__ import annotations

from enum import Enum, EnumMeta
from typing import TYPE_CHECKING, Final

from pycardgolf.utils.mixins import RNGMixin

if TYPE_CHECKING:
    from pycardgolf.utils.types import CardID


class _ContainsEnumMeta(EnumMeta):
    def __contains__(cls, value: object) -> bool:
        return value in cls.__members__.values()


class Suit(Enum, metaclass=_ContainsEnumMeta):
    """Enum representing card suits."""

    CLUBS = (0, "C")
    DIAMONDS = (1, "D")
    HEARTS = (2, "H")
    SPADES = (3, "S")
    HIDDEN = (None, "?")

    def __lt__(self, other: Suit) -> bool:
        """Compare suits based on their value."""
        return self.value[0] < other.value[0]


class Rank(Enum, metaclass=_ContainsEnumMeta):
    """Enum representing card ranks."""

    ACE = (1, "A")
    TWO = (2, "2")
    THREE = (3, "3")
    FOUR = (4, "4")
    FIVE = (5, "5")
    SIX = (6, "6")
    SEVEN = (7, "7")
    EIGHT = (8, "8")
    NINE = (9, "9")
    TEN = (10, "10")
    JACK = (11, "J")
    QUEEN = (12, "Q")
    KING = (13, "K")
    HIDDEN = (None, "?")

    def __lt__(self, other: Rank) -> bool:
        """Compare ranks based on their value."""
        return self.value[0] < other.value[0]

    def __str__(self) -> str:
        """Return the string representation of the rank for display."""
        return self.value[1]


# Source of truth for logical card mapping
_SUIT_ORDER: Final[list[Suit]] = [Suit.SPADES, Suit.HEARTS, Suit.DIAMONDS, Suit.CLUBS]
_RANK_ORDER: Final[list[Rank]] = [
    Rank.ACE,
    Rank.TWO,
    Rank.THREE,
    Rank.FOUR,
    Rank.FIVE,
    Rank.SIX,
    Rank.SEVEN,
    Rank.EIGHT,
    Rank.NINE,
    Rank.TEN,
    Rank.JACK,
    Rank.QUEEN,
    Rank.KING,
]

# Derived constants
NUM_SUITS: Final[int] = len(_SUIT_ORDER)
CARDS_PER_SUIT: Final[int] = len(_RANK_ORDER)
CARDS_PER_DECK: Final[int] = NUM_SUITS * CARDS_PER_SUIT


class CardStack(RNGMixin):
    """A class to represent a stack of cards using CardID integers."""

    __slots__ = ("_card_ids",)
    __hash__ = None  # type: ignore[assignment]

    def __init__(
        self,
        card_ids: list[CardID] | None = None,
        seed: int | None = None,
    ) -> None:
        """Construct a CardStack object."""
        super().__init__(seed=seed)
        self._card_ids: list[CardID] = [] if card_ids is None else card_ids

    @property
    def num_cards(self) -> int:
        """Returns the number of cards in the CardStack."""
        return len(self._card_ids)

    @property
    def card_ids(self) -> list[CardID]:
        """Returns a copy of the cards list."""
        return self._card_ids.copy()

    def add_card(self, new_card_id: CardID) -> None:
        """Add a card to the top of the stack."""
        self._card_ids.append(new_card_id)

    def add_card_stack(
        self,
        other: CardStack,
        clear_other: bool = True,
        shuffle: bool = False,
    ) -> None:
        """Add the cards from a different card stack to this card stack."""
        self._card_ids.extend(other._card_ids)
        if clear_other:
            other.clear()
        if shuffle:
            self.shuffle()

    def peek(self) -> CardID:
        """Peek at the top card."""
        if len(self._card_ids) == 0:
            msg = "No cards in card stack"
            raise IndexError(msg)
        return self._card_ids[-1]

    def draw(self) -> CardID:
        """Draw the top card."""
        if len(self._card_ids) == 0:
            msg = "No cards left in stack"
            raise IndexError(msg)
        return self._card_ids.pop()

    def clear(self) -> None:
        """Clear the card stack."""
        self._card_ids = []

    def shuffle(self) -> None:
        """Randomly order the cards remaining in the stack."""
        self.rng.shuffle(self._card_ids)

    def clone(self, preserve_rng: bool = False) -> CardStack:
        """Return a deep copy of the CardStack."""
        cloned_stack = CardStack(
            card_ids=list(self._card_ids),
            seed=self.seed if preserve_rng else None,
        )
        if preserve_rng:
            self.copy_rng_state(cloned_stack)
        return cloned_stack

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CardStack):
            return NotImplemented
        return self.seed == other.seed and self._card_ids == other._card_ids

    def __repr__(self) -> str:
        return f"CardStack(card_ids={self._card_ids}, seed={self.seed})"


class Deck(CardStack):
    """A class to represent a deck of cards using CardID integers."""

    # TODO: rexamine how this should differ from CardStack (own color?)
    # TODO: determine if it should validate card_ids match the deck id
    __slots__ = ("num_decks",)

    def __init__(
        self,
        num_decks: int = 1,
        seed: int | None = None,
    ) -> None:
        """Construct a Deck object of (num_decks * CARDS_PER_DECK) cards.

        Args:
            num_decks: Number of standard decks to include.
            seed (optional): Seed for the random number generator.

        """
        super().__init__(seed=seed)
        self.num_decks: int = num_decks
        self.reset()

    def reset(self) -> None:
        """Reset the deck to the full size."""
        self._card_ids = list(range(self.num_decks * CARDS_PER_DECK))

    def clone(self, preserve_rng: bool = False) -> Deck:
        """Return a deep copy of the Deck."""
        cloned_deck = Deck(
            num_decks=self.num_decks,
            seed=self.seed if preserve_rng else None,
        )
        cloned_deck._card_ids = list(self._card_ids)
        if preserve_rng:
            self.copy_rng_state(cloned_deck)
        return cloned_deck

    def __repr__(self) -> str:
        return f"Deck(num_decks={self.num_decks}, \
            seed={self.seed}, \
            card_ids={self._card_ids})"
