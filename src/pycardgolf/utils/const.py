from typing import Dict, Final
from pycardgolf.utils.suit import Suit

RANK_STR: Final[Dict[int, str]] = {1: 'A',
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
SUIT_STR: Final[Dict['Suit', str]] = {Suit.SPADES: '\u2660',
                                      Suit.HEARTS: '\u2665',
                                      Suit.DIAMONDS: '\u2666',
                                      Suit.CLUBS: '\u2663'}
SUIT_OUTLINE_STR: Final[Dict['Suit', str]] = {Suit.SPADES: '\u2664',
                                              Suit.HEARTS: '\u2661',
                                              Suit.DIAMONDS: '\u2662',
                                              Suit.CLUBS: '\u2667'}
