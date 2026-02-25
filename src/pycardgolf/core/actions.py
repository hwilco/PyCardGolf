"""Module containing Action definitions for the game engine."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from pycardgolf.exceptions import IllegalActionError
from pycardgolf.utils.constants import HAND_SIZE


class ActionType(Enum):
    """Types of actions a player can take."""

    FLIP = 1
    DRAW_DECK = 2
    DRAW_DISCARD = 3
    SWAP = 4
    DISCARD_DRAWN = 5
    PASS = 6


# Actions that require a target index
TARGETED_ACTIONS = frozenset({ActionType.FLIP, ActionType.SWAP})


@dataclass(frozen=True)
class Action:
    """Pure data representation of an action."""

    action_type: ActionType
    target_index: int | None = None  # e.g., which card in hand to flip/swap

    def __post_init__(self) -> None:
        """Strictly validate action data upon creation.

        Raises IllegalActionError to ensure invalid actions can never be instantiated,
        even in optimized modes where asserts are stripped.
        """
        is_targeted = self.action_type in TARGETED_ACTIONS

        if is_targeted:
            if self.target_index is None:
                msg = f"Action {self.action_type} must have a target_index."
                raise IllegalActionError(msg)
            if not (0 <= self.target_index < HAND_SIZE):
                msg = f"Target index {self.target_index} out of bounds."
                raise IllegalActionError(msg)
        elif self.target_index is not None:
            msg = f"Action {self.action_type} must not have a target_index."
            raise IllegalActionError(msg)

    @property
    def safe_target_index(self) -> int:
        """Returns the target_index as an int, strictly satisfying the type checker."""
        if self.target_index is None:
            msg = f"{self.action_type} requires a target index."
            raise IllegalActionError(msg)
        return self.target_index


class ActionSpace:
    """Flyweight cache for Action objects to avoid allocations."""

    # Static actions
    DRAW_DECK = Action(ActionType.DRAW_DECK)
    DRAW_DISCARD = Action(ActionType.DRAW_DISCARD)
    DISCARD_DRAWN = Action(ActionType.DISCARD_DRAWN)
    PASS = Action(ActionType.PASS)

    # Targeted actions (pre-allocated for HAND_SIZE)
    FLIP: tuple[Action, ...] = tuple(
        Action(ActionType.FLIP, i) for i in range(HAND_SIZE)
    )
    SWAP: tuple[Action, ...] = tuple(
        Action(ActionType.SWAP, i) for i in range(HAND_SIZE)
    )
