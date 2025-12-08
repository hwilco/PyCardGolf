"""Module containing Action definitions for the game engine."""

from dataclasses import dataclass
from typing import Literal

ActionType = Literal[
    "DRAW_DECK",
    "DRAW_DISCARD",
    "SWAP_CARD",
    "DISCARD_DRAWN",
    "FLIP_CARD",
    "PASS",
]


@dataclass(frozen=True, kw_only=True)
class Action:
    """Base class for all actions."""

    action_type: ActionType


@dataclass(frozen=True, kw_only=True)
class ActionDrawDeck(Action):
    """Action to draw a card from the deck."""

    action_type: ActionType = "DRAW_DECK"


@dataclass(frozen=True, kw_only=True)
class ActionDrawDiscard(Action):
    """Action to draw a card from the discard pile."""

    action_type: ActionType = "DRAW_DISCARD"


@dataclass(frozen=True, kw_only=True)
class ActionSwapCard(Action):
    """Action to swap a card in hand with the held card (drawn card)."""

    hand_index: int
    action_type: ActionType = "SWAP_CARD"


@dataclass(frozen=True, kw_only=True)
class ActionDiscardDrawn(Action):
    """Action to discard the card drawn from the deck."""

    action_type: ActionType = "DISCARD_DRAWN"


@dataclass(frozen=True, kw_only=True)
class ActionFlipCard(Action):
    """Action to flip a card in hand."""

    hand_index: int
    action_type: ActionType = "FLIP_CARD"


@dataclass(frozen=True)
class ActionPass(Action):
    """Action to pass (e.g., choose not to flip a card)."""

    action_type: ActionType = "PASS"
