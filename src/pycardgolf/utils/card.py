"""Module containing the Card class."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import ClassVar
from pycardgolf.utils.enums import Rank, Suit


class Card:
    """A class to represent a playing card."""

    __SUIT_STR: ClassVar[dict[Suit, str]] = {
        Suit.SPADES: "\u2660",
        Suit.HEARTS: "\u2665",
        Suit.DIAMONDS: "\u2666",
        Suit.CLUBS: "\u2663",
        Suit.HIDDEN: "?",
    }
    __SUIT_OUTLINE_STR: ClassVar[dict[Suit, str]] = {
        Suit.SPADES: "\u2664",
        Suit.HEARTS: "\u2661",
        Suit.DIAMONDS: "\u2662",
        Suit.CLUBS: "\u2667",
        Suit.HIDDEN: "?",
    }
    _outline_suits: ClassVar[bool] = True

    def __init__(
        self,
        rank: Rank,
        suit: Suit,
        back_color: str,
        face_color: str = "black",
        face_up: bool = False,
    ) -> None:
        """Construct a Card object.

        Args:
            rank: The rank of the card. Must be a member of the Rank enum.
            suit: The suit of the card. Must be a member of the Suit enum.
                (Suit.CLUBS, Suit.DIAMONDS, Suit.HEARTS, or Suit.SPADES)
            back_color: A string representing the color of the card. Used to
                differentiate cards from different decks. Converted to lower
                case.
            face_color (optional): Color of the card face (rank/suit). Converted to
                lower case. Defaults to black.
            face_up (optional): True if the card is face up (showing its rank
                and suit), False if it is face down. Defaults to False.

        Raises:
            ValueError: If rank or suit are out of range.

        """
        self.__rank: Rank = rank
        if self.__rank not in Rank:
            msg = f"Card rank must be a member of Rank enum. Given rank: {rank}"
            raise ValueError(msg)
        self.__suit: Suit = suit
        if self.__suit not in Suit:
            msg = (
                "Card suit must be in [Suit.CLUBS, Suit.DIAMONDS, "
                "Suit.HEARTS, or Suit.SPADES]. Given "
                f"suit: {suit}"
            )
            raise ValueError(msg)
        self.__back_color: str = back_color.lower()
        self.__face_color: str = face_color.lower()
        self.__face_up: bool = face_up

    @property
    def rank(self) -> Rank:
        """The rank of the card as a Rank enum."""
        return self.__rank

    @property
    def suit(self) -> Suit:
        """The suit of the card."""
        return self.__suit

    @property
    def back_color(self) -> str:
        """A string representing the color of the back of the card."""
        return self.__back_color

    @property
    def face_color(self) -> str:
        """A string representing the color of the face of the card."""
        return self.__face_color

    @property
    def face_up(self) -> bool:
        """True if the card is face up, False otherwise."""
        return self.__face_up

    @face_up.setter
    def face_up(self, value: bool) -> None:
        self.__face_up = value

    def flip(self) -> None:
        """Flip the card.

        If the card was face up, it will become face down and vice versa.
        """
        self.face_up = not self.face_up

    def clone(self) -> Card:
        """Return a deep copy of the card."""
        return Card(
            rank=self.rank,
            suit=self.suit,
            back_color=self.back_color,
            face_color=self.face_color,
            face_up=self.face_up,
        )

    @property
    def __rank_str(self) -> str:
        """Human-readable representation of the rank of the card."""
        return str(self.rank)

    @property
    def __suit_str(self) -> str:
        """Human-readable representation of the suit of the card."""
        # TODO: handle configuration of suit display (outline or filled)
        if self._outline_suits:
            return Card.__SUIT_OUTLINE_STR[self.__suit]
        return Card.__SUIT_STR[self.__suit]

    def __repr__(self) -> str:
        return (
            f"Card({self.__rank!r}, {self.__suit!r}, '{self.__back_color}', "
            f"'{self.__face_color}', {self.__face_up})"
        )

    def __str__(self) -> str:
        """Return string representation of the card."""
        if self.face_up:
            return self.__rank_str + self.__suit_str
        return "??"

    def __eq__(self, other: object) -> bool:
        """Check equality with another object."""
        if not isinstance(other, Card):
            return NotImplemented
        return (
            self.__rank == other.__rank
            and self.__suit == other.__suit
            and self.__back_color == other.__back_color
            and self.__face_color == other.__face_color
            and self.__face_up == other.__face_up
        )

    __hash__ = None  # type: ignore[assignment]
