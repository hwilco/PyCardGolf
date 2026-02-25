"""Module containing Action definitions for the game engine."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ActionType(Enum):
    """Types of actions a player can take."""

    FLIP = 1
    DRAW_DECK = 2
    DRAW_DISCARD = 3
    SWAP = 4
    DISCARD_DRAWN = 5
    PASS = 6


@dataclass(frozen=True)
class Action:
    """Pure data representation of an action."""

    action_type: ActionType
    target_index: int | None = None  # e.g., which card in hand to flip/swap
