"""Module containing Suit and Rank enums."""

from __future__ import annotations

from enum import Enum, EnumMeta, auto


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


class DrawSourceChoice(Enum):
    """Source to draw a card from."""

    DECK = auto()
    DISCARD_PILE = auto()


class KeepOrDiscardChoice(Enum):
    """Choice to keep or discard a drawn card."""

    KEEP = auto()
    DISCARD = auto()
