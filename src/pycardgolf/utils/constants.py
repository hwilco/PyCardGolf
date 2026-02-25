"""Project-wide constants."""

from typing import Final

from pycardgolf.exceptions import GameConfigError

HAND_SIZE: Final[int] = 6  # Number of cards in a hand, must be even

if HAND_SIZE % 2 != 0:  # pragma: no cover
    msg = "HAND_SIZE must be even"
    raise GameConfigError(msg)

INITIAL_CARDS_TO_FLIP: Final[int] = 2  # Number of cards to flip initially
