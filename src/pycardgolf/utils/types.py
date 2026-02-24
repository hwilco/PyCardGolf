"""Module defining primitive type aliases for the game engine."""

# Unique identifier for a card, encoding suit, rank, and deck number.
# Negative IDs are face-down cards (only encoded with deck number).
type CardID = int
type FaceUpMask = int  # Bitmask for face-up cards
