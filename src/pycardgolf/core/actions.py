"""Module containing Action definitions for the game engine."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

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
        """Validate action data.

        This uses an assertion so that validation is stripped in optimized mode.
        """
        is_targeted = self.action_type in TARGETED_ACTIONS
        msg = (
            f"Action {self.action_type} must "
            f"{'have' if is_targeted else 'not have'} a target_index"
        )
        assert is_targeted == (self.target_index is not None), msg  # noqa: S101


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
