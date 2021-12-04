from typing import ClassVar, Dict


class Card:
    """
    A class to represent a playing card.
    """

    __value_dict: ClassVar[Dict[int, str]] = {1: "A",
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
