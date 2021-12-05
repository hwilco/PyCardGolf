from typing import ClassVar, Dict
from pycardgolf.utils.const import Suit


class Card:
    """
    A class to represent a playing card.
    """

    __value_dict: ClassVar[Dict[int, str]] = {1: 'A',
                                              2: '2',
                                              3: '3',
                                              4: '4',
                                              5: '5',
                                              6: '6',
                                              7: '7',
                                              8: '8',
                                              9: '9',
                                              10: '10',
                                              11: 'J',
                                              12: 'Q',
                                              13: 'K'}
    __suit_dict: ClassVar[Dict['Suit', str]] = {Suit.SPADES: '\u2660',
                                                Suit.HEARTS: '\u2665',
                                                Suit.DIAMONDS: '\u2666',
                                                Suit.CLUBS: '\u2663'}
    __suit_outline_dict: ClassVar[Dict['Suit', str]] = {Suit.SPADES: '\u2664',
                                                        Suit.HEARTS: '\u2661',
                                                        Suit.DIAMONDS: '\u2662',
                                                        Suit.CLUBS: '\u2667'}

    def __init__(self, rank: int, suit: 'Suit', color: str) -> None:
        """
        Construct a Card object.

        Args:
            rank: The rank of the card. 1 -> Ace, 2-10 -> 2-10, 11 -> Jack, 12 -> Queen, 13 -> King.
            suit: The suit of the card. Must be a member of the utils.const.Suit enum. (Suit.CLUBS, Suit.DIAMONDS,
                Suit.HEARTS, or Suit.SPADES)
            color: A string representing the color of the card. Used to differentiate cards from different decks.
                Converted to lower case.

        Raises:
            ValueError: If rank or suit are out of range.
        """
        self.__rank = rank
        if self.__rank not in Card.__value_dict:
            raise ValueError("Card rank must be an int in range(1,14). Given rank: {}".format(rank))
        self.__suit = suit
        if self.__suit not in Suit:
            raise ValueError("Card suit must be in [Suit.CLUBS, Suit.DIAMONDS, Suit.HEARTS, or Suit.SPADES]. Given "
                             "suit: {}".format(suit))
        self.__color = color.lower()
        
    @property
    def rank(self):
        return self.__rank
    
    @property
    def suit(self):
        return self.__suit

    @property
    def color(self):
        return self.__color

    @property
    def __value_str(self) -> str:
        return Card.__value_dict[self.rank]

    @property
    def __suit_str(self) -> str:
        # TODO: handle configuration of suit display (outline or filled)
        outline_suits = True
        if outline_suits:
            return Card.__suit_outline_dict[self.suit]
        else:
            return Card.__suit_dict[self.suit]

    def __repr__(self) -> str:
        return "Card({}, {}, '{}')".format(self.rank, self.suit, self.color)

    def __str__(self) -> str:
        return self.__value_str + self.__suit_str

    def __eq__(self, other: 'Card') -> bool:
        return self.rank == other.rank and \
               self.suit == other.suit and \
               self.color == other.color
