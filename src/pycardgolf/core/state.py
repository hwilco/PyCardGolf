"""Module containing state definitions for the game engine."""

from dataclasses import dataclass
from enum import Enum, auto

from pycardgolf.core.actions import Action
from pycardgolf.utils.card import Card


class RoundPhase(Enum):
    """Phases of a round."""

    SETUP = auto()  # Initial flipping of cards
    DRAW = auto()  # Waiting for player to draw
    ACTION = auto()  # Waiting for player to swap/discard
    FLIP = auto()  # Waiting for player to flip (optional after discard)
    FINISHED = auto()


@dataclass
class Observation:
    """A sanitized view of the game state for a player."""

    my_hand: list[Card]  # Face down cards object with face_up=False
    other_hands: dict[str, list[Card]]
    discard_top: Card | None
    deck_size: int
    current_player_name: str
    phase: RoundPhase
    valid_actions: list[Action]
    # Additional info needed for decision making
    drawn_card: Card | None = None  # Only visible if in ACTION/FLIP phase and drawn
    can_discard_drawn: bool = False  # True if drawn from Deck
