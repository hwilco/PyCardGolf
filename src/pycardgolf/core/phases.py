"""Module containing phase-specific logic for the Golf engine."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import TYPE_CHECKING

from pycardgolf.core.actions import (
    Action,
    ActionDiscardDrawn,
    ActionDrawDeck,
    ActionDrawDiscard,
    ActionFlipCard,
    ActionPass,
    ActionSwapCard,
)
from pycardgolf.core.events import (
    CardDiscardedEvent,
    CardDrawnDeckEvent,
    CardDrawnDiscardEvent,
    CardFlippedEvent,
    CardSwappedEvent,
    GameEvent,
    TurnStartEvent,
)
from pycardgolf.exceptions import IllegalActionError
from pycardgolf.utils.constants import HAND_SIZE, INITIAL_CARDS_TO_FLIP

if TYPE_CHECKING:
    from pycardgolf.core.round import Round


class RoundPhase(Enum):
    """Phases of a round."""

    SETUP = auto()  # Initial flipping of cards
    DRAW = auto()  # Waiting for player to draw
    ACTION = auto()  # Waiting for player to swap/discard
    FLIP = auto()  # Waiting for player to flip (optional after discard)
    FINISHED = auto()


class PhaseState(ABC):
    """Abstract base class for round phase logic."""

    @abstractmethod
    def get_valid_actions(self, round_state: Round, player_idx: int) -> list[Action]:
        """Return a list of valid actions for the given player."""

    @abstractmethod
    def handle_step(
        self, round_state: Round, player_idx: int, action: Action
    ) -> list[GameEvent]:
        """Advance the round state based on the action and return events."""


class SetupPhaseState(PhaseState):
    """Logic for the SETUP phase."""

    def get_valid_actions(self, round_state: Round, player_idx: int) -> list[Action]:
        """Return a list of valid actions for the given player."""
        return [
            ActionFlipCard(hand_index=i)
            for i, card in enumerate(round_state.hands[player_idx])
            if not card.face_up
        ]

    def handle_step(
        self, round_state: Round, player_idx: int, action: Action
    ) -> list[GameEvent]:
        """Advance the round state based on the action and return events."""
        match action:
            case ActionFlipCard(hand_index=idx):
                hand = round_state.hands[player_idx]
                if hand[idx].face_up:
                    msg = "Card already face up."
                    raise IllegalActionError(msg)

                hand.flip_card(idx)
                events: list[GameEvent] = [
                    CardFlippedEvent(
                        player_idx=player_idx,
                        hand_index=idx,
                        card=hand[idx],
                    )
                ]
                round_state.cards_flipped_in_setup[player_idx] += 1

                if (
                    round_state.cards_flipped_in_setup[player_idx]
                    >= INITIAL_CARDS_TO_FLIP
                ):
                    # Move to next player
                    round_state.current_player_idx += 1
                    if round_state.current_player_idx >= round_state.num_players:
                        # All players done setup
                        round_state.current_player_idx = 0
                        round_state.phase = RoundPhase.DRAW
                        events.append(TurnStartEvent(player_idx=0))

                return events
            case _:
                msg = "Must flip a card in setup phase."
                raise IllegalActionError(msg)


class DrawPhaseState(PhaseState):
    """Logic for the DRAW phase."""

    def get_valid_actions(self, round_state: Round, player_idx: int) -> list[Action]:  # noqa: ARG002
        """Return a list of valid actions for the given player."""
        actions: list[Action] = [ActionDrawDeck()]
        if round_state.discard_pile.num_cards > 0:
            actions.append(ActionDrawDiscard())
        return actions

    def handle_step(
        self, round_state: Round, player_idx: int, action: Action
    ) -> list[GameEvent]:
        """Advance the round state based on the action and return events."""
        events: list[GameEvent] = []
        match action:
            case ActionDrawDeck():
                card = round_state.deck.draw()
                card.face_up = True
                round_state.drawn_card = card
                round_state.drawn_from_deck = True
                round_state.phase = RoundPhase.ACTION
                events.append(CardDrawnDeckEvent(player_idx=player_idx, card=card))
            case ActionDrawDiscard():
                if round_state.discard_pile.num_cards == 0:
                    msg = "Discard pile is empty."
                    raise IllegalActionError(msg)
                card = round_state.discard_pile.draw()
                round_state.drawn_card = card
                round_state.drawn_from_deck = False
                round_state.phase = RoundPhase.ACTION
                events.append(CardDrawnDiscardEvent(player_idx=player_idx, card=card))
            case _:
                msg = f"Invalid action for DRAW phase: {action}"
                raise IllegalActionError(msg)

        return events


class ActionPhaseState(PhaseState):
    """Logic for the ACTION phase."""

    def get_valid_actions(self, round_state: Round, player_idx: int) -> list[Action]:  # noqa: ARG002
        """Return a list of valid actions for the given player."""
        actions: list[Action] = [ActionSwapCard(hand_index=i) for i in range(HAND_SIZE)]
        if round_state.drawn_from_deck:
            actions.append(ActionDiscardDrawn())
        return actions

    def handle_step(
        self, round_state: Round, player_idx: int, action: Action
    ) -> list[GameEvent]:
        """Advance the round state based on the action and return events."""
        events: list[GameEvent] = []
        if round_state.drawn_card is None:
            msg = "No card drawn."
            raise IllegalActionError(msg)

        hand = round_state.hands[player_idx]

        match action:
            case ActionSwapCard(hand_index=idx):
                old_card = hand.replace(idx, round_state.drawn_card)
                old_card.face_up = True
                round_state.discard_pile.add_card(old_card)
                events.append(
                    CardSwappedEvent(
                        player_idx=player_idx,
                        hand_index=idx,
                        new_card=round_state.drawn_card,
                        old_card=old_card,
                    )
                )
                round_state.drawn_card = None
                _end_turn(round_state, events)
            case ActionDiscardDrawn():
                round_state.discard_pile.add_card(round_state.drawn_card)
                events.append(
                    CardDiscardedEvent(
                        player_idx=player_idx, card=round_state.drawn_card
                    )
                )
                round_state.drawn_card = None
                round_state.phase = RoundPhase.FLIP
            case _:
                msg = f"Invalid action for ACTION phase: {action}"
                raise IllegalActionError(msg)

        return events


class FlipPhaseState(PhaseState):
    """Logic for the FLIP phase."""

    def get_valid_actions(self, round_state: Round, player_idx: int) -> list[Action]:
        """Return a list of valid actions for the given player."""
        actions: list[Action] = [ActionPass()]
        actions.extend(
            [
                ActionFlipCard(hand_index=i)
                for i, card in enumerate(round_state.hands[player_idx])
                if not card.face_up
            ]
        )
        return actions

    def handle_step(
        self, round_state: Round, player_idx: int, action: Action
    ) -> list[GameEvent]:
        """Advance the round state based on the action and return events."""
        events: list[GameEvent] = []
        hand = round_state.hands[player_idx]
        match action:
            case ActionFlipCard(hand_index=idx):
                if hand[idx].face_up:
                    msg = "Card already face up."
                    raise IllegalActionError(msg)
                hand.flip_card(idx)
                events.append(
                    CardFlippedEvent(
                        player_idx=player_idx,
                        hand_index=idx,
                        card=hand[idx],
                    )
                )
                _end_turn(round_state, events)
            case ActionPass():
                _end_turn(round_state, events)
            case _:
                msg = f"Invalid action for FLIP phase: {action}"
                raise IllegalActionError(msg)
        return events


class FinishedPhaseState(PhaseState):
    """Logic for the FINISHED phase."""

    def get_valid_actions(self, round_state: Round, player_idx: int) -> list[Action]:  # noqa: ARG002
        """Return a list of valid actions for the given player."""
        return []

    def handle_step(
        self,
        round_state: Round,  # noqa: ARG002
        player_idx: int,  # noqa: ARG002
        action: Action,  # noqa: ARG002
    ) -> list[GameEvent]:
        """Advance the round state based on the action and return events."""
        return []


_PHASE_STATES: dict[RoundPhase, PhaseState] = {
    RoundPhase.SETUP: SetupPhaseState(),
    RoundPhase.DRAW: DrawPhaseState(),
    RoundPhase.ACTION: ActionPhaseState(),
    RoundPhase.FLIP: FlipPhaseState(),
    RoundPhase.FINISHED: FinishedPhaseState(),
}


def get_valid_actions(round_state: Round, player_idx: int) -> list[Action]:
    """Return a list of valid actions for the given player."""
    state = _PHASE_STATES.get(round_state.phase)
    if state:
        return state.get_valid_actions(round_state, player_idx)
    return []


def handle_step(round_state: Round, action: Action) -> list[GameEvent]:
    """Advance the round state based on the action and current phase."""
    if round_state.phase == RoundPhase.FINISHED:
        return []

    player_idx = round_state.current_player_idx
    state = _PHASE_STATES.get(round_state.phase)
    if state:
        return state.handle_step(round_state, player_idx, action)
    return []


def _end_turn(round_state: Round, events: list[GameEvent]) -> None:
    """Finalize turn, check end conditions, and advance."""
    player_idx = round_state.current_player_idx

    # Check round end condition
    if (
        round_state.hands[player_idx].all_face_up()
        and round_state.last_turn_player_idx is None
    ):
        round_state.last_turn_player_idx = round_state.current_player_idx

    # Advance to the next player
    round_state.current_player_idx = (
        round_state.current_player_idx + 1
    ) % round_state.num_players
    if round_state.current_player_idx == 0:
        round_state.turn_count += 1

    # Check if round is over
    if (
        round_state.last_turn_player_idx is not None
        and round_state.current_player_idx == round_state.last_turn_player_idx
    ):
        round_state.phase = RoundPhase.FINISHED
        round_state.reveal_hands()  # Reveal hidden cards
    else:
        round_state.phase = RoundPhase.DRAW
        events.append(TurnStartEvent(player_idx=round_state.current_player_idx))
