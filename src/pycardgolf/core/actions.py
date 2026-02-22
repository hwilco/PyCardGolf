"""Module containing Action definitions for the game engine."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from pycardgolf.core.events import (
    CardDiscardedEvent,
    CardDrawnDeckEvent,
    CardDrawnDiscardEvent,
    CardFlippedEvent,
    CardSwappedEvent,
    GameEvent,
)
from pycardgolf.exceptions import IllegalActionError

if TYPE_CHECKING:
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
    def execute(self, round_state: "Round") -> list[GameEvent]:
        """Apply the action to the round state and return generated events."""


@dataclass(frozen=True, kw_only=True)
class ActionDrawDeck(Action):
    """Action to draw a card from the deck."""

    action_type: ActionType = "DRAW_DECK"

    def execute(self, round_state: "Round") -> list[GameEvent]:
        """Apply the action to the round state and return generated events."""
        player_idx = round_state.current_player_idx
        card = round_state.deck.draw()
        card.face_up = True
        round_state.drawn_card = card
        round_state.drawn_from_deck = True
        return [CardDrawnDeckEvent(player_idx=player_idx, card=card)]


@dataclass(frozen=True, kw_only=True)
class ActionDrawDiscard(Action):
    """Action to draw a card from the discard pile."""

    action_type: ActionType = "DRAW_DISCARD"

    def execute(self, round_state: "Round") -> list[GameEvent]:
        """Apply the action to the round state and return generated events."""
        player_idx = round_state.current_player_idx
        if round_state.discard_pile.num_cards == 0:
            msg = "Discard pile is empty."
            raise IllegalActionError(msg)
        card = round_state.discard_pile.draw()
        round_state.drawn_card = card
        round_state.drawn_from_deck = False
        return [CardDrawnDiscardEvent(player_idx=player_idx, card=card)]


@dataclass(frozen=True, kw_only=True)
class ActionSwapCard(Action):
    """Action to swap a card in hand with the held card (drawn card)."""

    hand_index: int
    action_type: ActionType = "SWAP_CARD"

    def execute(self, round_state: "Round") -> list[GameEvent]:
        """Apply the action to the round state and return generated events."""
        if round_state.drawn_card is None:
            msg = "No card drawn."
            raise IllegalActionError(msg)

        player_idx = round_state.current_player_idx
        hand = round_state.hands[player_idx]
        old_card = hand.replace(self.hand_index, round_state.drawn_card)
        old_card.face_up = True
        round_state.discard_pile.add_card(old_card)
        event = CardSwappedEvent(
            player_idx=player_idx,
            hand_index=self.hand_index,
            new_card=round_state.drawn_card,
            old_card=old_card,
        )
        round_state.drawn_card = None
        return [event]


@dataclass(frozen=True, kw_only=True)
class ActionDiscardDrawn(Action):
    """Action to discard the card drawn from the deck."""

    action_type: ActionType = "DISCARD_DRAWN"

    def execute(self, round_state: "Round") -> list[GameEvent]:
        """Apply the action to the round state and return generated events."""
        if round_state.drawn_card is None:
            msg = "No card drawn."
            raise IllegalActionError(msg)

        player_idx = round_state.current_player_idx
        round_state.discard_pile.add_card(round_state.drawn_card)
        event = CardDiscardedEvent(player_idx=player_idx, card=round_state.drawn_card)
        round_state.drawn_card = None
        return [event]


@dataclass(frozen=True, kw_only=True)
class ActionFlipCard(Action):
    """Action to flip a card in hand."""

    hand_index: int
    action_type: ActionType = "FLIP_CARD"

    def execute(self, round_state: "Round") -> list[GameEvent]:
        """Apply the action to the round state and return generated events."""
        player_idx = round_state.current_player_idx
        hand = round_state.hands[player_idx]
        if hand[self.hand_index].face_up:
            msg = "Card already face up."
            raise IllegalActionError(msg)

        hand.flip_card(self.hand_index)
        return [
            CardFlippedEvent(
                player_idx=player_idx,
                hand_index=self.hand_index,
                card=hand[self.hand_index],
            )
        ]


@dataclass(frozen=True, kw_only=True)
class ActionPass(Action):
    """Action to pass (e.g., choose not to flip a card)."""

    action_type: ActionType = "PASS"

    def execute(
        self,
        round_state: "Round",  # noqa: ARG002
    ) -> list[GameEvent]:
        """Apply the action to the round state and return generated events."""
        return []
