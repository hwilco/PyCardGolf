"""Project-wide constants."""

HAND_SIZE: int = 6  # Number of cards each player holds during a round. Must be even.

if HAND_SIZE % 2 != 0:
    msg = "HAND_SIZE must be even."
    raise ValueError(msg)
