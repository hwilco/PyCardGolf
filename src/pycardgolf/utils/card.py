import pycardgolf.utils.const as const
from pycardgolf.utils.suit import Suit


class Card:
    """
    A class to represent a playing card.
    """

    def __init__(self, rank: int, suit: 'Suit', color: str, face_up: bool = None) -> None:
        """
        Construct a Card object.

        Args:
            rank: The rank of the card. 1 -> Ace, 2-10 -> 2-10, 11 -> Jack, 12 -> Queen, 13 -> King.
            suit: The suit of the card. Must be a member of the utils.const.Suit enum. (Suit.CLUBS, Suit.DIAMONDS,
                Suit.HEARTS, or Suit.SPADES)
            color: A string representing the color of the card. Used to differentiate cards from different decks.
                Converted to lower case.
            face_up (optional): True if the card is face up (showing its rank and suit), False if it is face down.
                Defaults to False.

        Raises:
            ValueError: If rank or suit are out of range.
        """
        face_up = False if face_up is None else face_up

        self.__rank = rank
        if self.__rank not in const.RANK_STR:
            raise ValueError(f"Card rank must be an int in range(1,14). Given rank: {rank}")
        self.__suit = suit
        if self.__suit not in Suit:
            raise ValueError("Card suit must be in [Suit.CLUBS, Suit.DIAMONDS, Suit.HEARTS, or Suit.SPADES]. Given "
                             f"suit: {suit}")
        self.__color = color.lower()
        self._outline_suits = True
        self.__face_up = face_up

    @property
    def rank(self) -> int:
        """
        Returns:
            rank: The rank of the card. 1 -> Ace, 2-10 -> 2-10, 11 -> Jack, 12 -> Queen, 13 -> King.
        """
        return self.__rank
    
    @property
    def suit(self) -> 'Suit':
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
        return const.RANK_STR[self.rank]

    @property
    def __suit_str(self) -> str:
        """
        Returns:
            __suit_str: Human-readable representation of the suit of the card using unicode suit characters.
        """
        # TODO: handle configuration of suit display (outline or filled)
        if self._outline_suits:
            return const.SUIT_OUTLINE_STR[self.suit]
        else:
            return const.SUIT_STR[self.suit]

    def __repr__(self) -> str:
        return f"Card({self.rank}, {self.suit}, '{self.color}', {self.face_up})"

    def __str__(self) -> str:
        if self.face_up:
            return self.__rank_str + self.__suit_str
        else:
            return "??"

    def __eq__(self, other: 'Card') -> bool:
        return self.rank == other.rank and \
               self.suit == other.suit and \
               self.color == other.color and \
               self.face_up == other.face_up

    def flip(self) -> None:
        """
        Flips the card. If the card was face up, it will become face down and vice versa.
        """
        self.face_up = not self.face_up
