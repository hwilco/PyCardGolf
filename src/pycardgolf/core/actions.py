"""Module containing Action definitions for the game engine."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from pycardgolf.core.events import GameEvent
    from pycardgolf.core.round import Round

ActionType = Literal[
    "DRAW_DECK",
    "DRAW_DISCARD",
    "SWAP_CARD",
    "DISCARD_DRAWN",
    "FLIP_CARD",
    "PASS",
]


@dataclass(frozen=True, kw_only=True)
class Action(ABC):
    """Base class for all actions."""

    action_type: ActionType

    @abstractmethod
    def execute(self, round_state: Round) -> list[GameEvent]:
        """Apply the action to the round state and return generated events."""


@dataclass(frozen=True, kw_only=True)
class ActionDrawDeck(Action):
    """Action to draw a card from the deck."""

    action_type: ActionType = "DRAW_DECK"

    def execute(self, round_state: Round) -> list[GameEvent]:
        """Apply the action to the round state and return generated events."""
        player_idx = round_state.current_player_idx
        event = round_state.draw_from_deck(player_idx)
        return [event]


@dataclass(frozen=True, kw_only=True)
class ActionDrawDiscard(Action):
    """Action to draw a card from the discard pile."""

    action_type: ActionType = "DRAW_DISCARD"

    def execute(self, round_state: Round) -> list[GameEvent]:
        """Apply the action to the round state and return generated events."""
        player_idx = round_state.current_player_idx
        event = round_state.draw_from_discard(player_idx)
        return [event]


@dataclass(frozen=True, kw_only=True)
class ActionSwapCard(Action):
    """Action to swap a card in hand with the held card (drawn card)."""

    hand_index: int
    action_type: ActionType = "SWAP_CARD"

    def execute(self, round_state: Round) -> list[GameEvent]:
        """Apply the action to the round state and return generated events."""
        player_idx = round_state.current_player_idx
        event = round_state.swap_drawn_card(player_idx, self.hand_index)
        return [event]


@dataclass(frozen=True, kw_only=True)
class ActionDiscardDrawn(Action):
    """Action to discard the card drawn from the deck."""

    action_type: ActionType = "DISCARD_DRAWN"

    def execute(self, round_state: Round) -> list[GameEvent]:
        """Apply the action to the round state and return generated events."""
        player_idx = round_state.current_player_idx
        event = round_state.discard_drawn_card(player_idx)
        return [event]


@dataclass(frozen=True, kw_only=True)
class ActionFlipCard(Action):
    """Action to flip a card in hand."""

    hand_index: int
    action_type: ActionType = "FLIP_CARD"

    def execute(self, round_state: Round) -> list[GameEvent]:
        """Apply the action to the round state and return generated events."""
        player_idx = round_state.current_player_idx
        event = round_state.flip_card_in_hand(player_idx, self.hand_index)
        return [event]


@dataclass(frozen=True, kw_only=True)
class ActionPass(Action):
    """Action to pass (e.g., choose not to flip a card)."""

    action_type: ActionType = "PASS"

    def execute(
        self,
        round_state: Round,  # noqa: ARG002
    ) -> list[GameEvent]:
        """Apply the action to the round state and return generated events."""
        return []
