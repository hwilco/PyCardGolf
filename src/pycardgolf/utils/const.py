from enum import EnumMeta, Enum


class _ContainsEnumMeta(EnumMeta):
    def __contains__(self, item):
        return item in self.__members__.values()


class Suit(Enum, metaclass=_ContainsEnumMeta):
    CLUBS = 0
    DIAMONDS = 1
    HEARTS = 2
    SPADES = 3

    def __lt__(self, other: 'Suit'):
        return self.value < other.value


__all__ = ['Suit']
