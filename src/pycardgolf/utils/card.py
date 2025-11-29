from __future__ import annotations

from typing import ClassVar, Dict

from pycardgolf.utils.enums import Rank, Suit


class Card:
    """
    A class to represent a playing card.
    """

    __SUIT_STR: ClassVar[Dict[Suit, str]] = {
        Suit.SPADES: "\u2660",
        Suit.HEARTS: "\u2665",
        Suit.DIAMONDS: "\u2666",
        Suit.CLUBS: "\u2663",
    }
    __SUIT_OUTLINE_STR: ClassVar[Dict[Suit, str]] = {
        Suit.SPADES: "\u2664",
        Suit.HEARTS: "\u2661",
        Suit.DIAMONDS: "\u2662",
        Suit.CLUBS: "\u2667",
    }
    _outline_suits: ClassVar[bool] = True

    def __init__(
        self, rank: Rank, suit: Suit, color: str, face_up: bool = False
    ) -> None:
        """
        Construct a Card object.

        Args:
            rank: The rank of the card. Must be a member of the Rank enum.
            suit: The suit of the card. Must be a member of the Suit enum. (Suit.CLUBS, Suit.DIAMONDS,
                Suit.HEARTS, or Suit.SPADES)
            color: A string representing the color of the card. Used to differentiate cards from different decks.
                Converted to lower case.
            face_up (optional): True if the card is face up (showing its rank and suit), False if it is face down.
                Defaults to False.

        Raises:
            ValueError: If rank or suit are out of range.
        """

        self.__rank = rank
        if self.__rank not in Rank:
            raise ValueError(
                f"Card rank must be a member of Rank enum. Given rank: {rank}"
            )
        self.__suit = suit
        if self.__suit not in Suit:
            raise ValueError(
                "Card suit must be in [Suit.CLUBS, Suit.DIAMONDS, Suit.HEARTS, or Suit.SPADES]. Given "
                f"suit: {suit}"
            )
        self.__color = color.lower()
        self.__face_up = face_up

    @property
    def rank(self) -> Rank:
        """
        Returns:
            rank: The rank of the card as a Rank enum.
        """
        return self.__rank

    @property
    def suit(self) -> Suit:
        """
        Returns:
            suit: The suit of the card. One of Suit.CLUBS, Suit.DIAMONDS, Suit.HEARTS, or Suit.SPADES.
        """
        return self.__suit

    @property
    def color(self) -> str:
        """
        Returns:
            color: A string representing the color of the card. Used to differentiate cards from different decks.
        """
        return self.__color

    @property
    def face_up(self) -> bool:
        """
        Returns:
            face_up: True if the card is face up (showing its rank and suit), False if it is face down.
        """
        return self.__face_up

    @face_up.setter
    def face_up(self, value: bool) -> None:
        self.__face_up = value

    @property
    def __rank_str(self) -> str:
        """
        Returns:
            __value_str: Human-readable representation of the rank of the card. Converts face cards to their letter
                representations.
        """
        return str(self.rank)

    @property
    def __suit_str(self) -> str:
        """
        Returns:
            __suit_str: Human-readable representation of the suit of the card using unicode suit characters.
        """
        # TODO: handle configuration of suit display (outline or filled)
        if self._outline_suits:
            return Card.__SUIT_OUTLINE_STR[self.suit]
        else:
            return Card.__SUIT_STR[self.suit]

    def __repr__(self) -> str:
        return f"Card({self.rank!r}, {self.suit!r}, '{self.color}', {self.face_up})"

    def __str__(self) -> str:
        if self.face_up:
            return self.__rank_str + self.__suit_str
        else:
            return "??"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return (
            self.rank == other.rank
            and self.suit == other.suit
            and self.color == other.color
            and self.face_up == other.face_up
        )

    __hash__ = None

    def flip(self) -> None:
        """
        Flips the card. If the card was face up, it will become face down and vice versa.
        """
        self.face_up = not self.face_up
