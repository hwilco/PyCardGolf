"""Project-wide constants."""

from typing import Final

HAND_SIZE: Final[int] = 6  # Number of cards in a hand, must be even

if HAND_SIZE % 2 != 0:  # pragma: no cover
    msg = "HAND_SIZE must be even"
    raise ValueError(msg)
