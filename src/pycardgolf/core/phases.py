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
    GameEvent,
    TurnStartEvent,
)
from pycardgolf.exceptions import IllegalActionError
from pycardgolf.utils.constants import HAND_SIZE, INITIAL_CARDS_TO_FLIP

if TYPE_CHECKING:
    from pycardgolf.core.round import Round


class RoundPhase(Enum):
    """Phases of a round."""

    SETUP = auto()
    DRAW = auto()
    ACTION = auto()
    FLIP = auto()
    FINISHED = auto()


class PhaseState(ABC):
    """Abstract base class for round phase logic."""

    phase_enum: RoundPhase
    __hash__ = None  # type: ignore[assignment]

    @abstractmethod
    def get_valid_actions(self, round_state: Round, player_idx: int) -> list[Action]:
        """Return a list of valid actions for the given player."""

    @abstractmethod
    def handle_action(self, round_state: Round, action: Action) -> list[GameEvent]:
        """Advance the round state based on the action and return events."""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.phase_enum == other.phase_enum


class SetupPhaseState(PhaseState):
    """Logic for the SETUP phase."""

    phase_enum = RoundPhase.SETUP

    def get_valid_actions(self, round_state: Round, player_idx: int) -> list[Action]:
        """Return a list of valid actions for the given player."""
        hand = round_state.hands[player_idx]
        return [
            ActionFlipCard(hand_index=i)
            for i in range(len(hand))
            if not hand.is_face_up(i)
        ]

    def handle_action(self, round_state: Round, action: Action) -> list[GameEvent]:
        """Advance the round state based on the action and return events."""
        if not isinstance(action, ActionFlipCard):
            msg = "Must flip a card in setup phase."
            raise IllegalActionError(msg)

        player_idx = round_state.current_player_idx
        events = action.execute(round_state)
        round_state.cards_flipped_in_setup[player_idx] += 1

        if round_state.cards_flipped_in_setup[player_idx] >= INITIAL_CARDS_TO_FLIP:
            # Move to next player
            round_state.current_player_idx += 1
            if round_state.current_player_idx >= round_state.num_players:
                # All players done setup
                round_state.current_player_idx = 0
                events.append(
                    TurnStartEvent(
                        player_idx=0,
                        hands={
                            i: round_state.hands[i]
                            for i in range(round_state.num_players)
                        },
                    )
                )
                round_state.phase_state = DrawPhaseState()
                return events

        return events


class DrawPhaseState(PhaseState):
    """Logic for the DRAW phase."""

    phase_enum = RoundPhase.DRAW

    def get_valid_actions(self, round_state: Round, player_idx: int) -> list[Action]:  # noqa: ARG002
        """Return a list of valid actions for the given player."""
        actions: list[Action] = [ActionDrawDeck()]
        if round_state.discard_pile.num_cards > 0:
            actions.append(ActionDrawDiscard())
        return actions

    def handle_action(self, round_state: Round, action: Action) -> list[GameEvent]:
        """Advance the round state based on the action and return events."""
        if not isinstance(action, (ActionDrawDeck, ActionDrawDiscard)):
            msg = f"Invalid action for DRAW phase: {action}"
            raise IllegalActionError(msg)

        events = action.execute(round_state)

        # Inversion of Control: The phase transition decides the state!
        is_from_deck = isinstance(action, ActionDrawDeck)
        round_state.phase_state = ActionPhaseState(drawn_from_deck=is_from_deck)

        return events


class ActionPhaseState(PhaseState):
    """Logic for the ACTION phase."""

    phase_enum = RoundPhase.ACTION

    def __init__(self, drawn_from_deck: bool) -> None:
        self.drawn_from_deck = drawn_from_deck

    def get_valid_actions(self, round_state: Round, player_idx: int) -> list[Action]:  # noqa: ARG002
        """Return a list of valid actions for the given player."""
        actions: list[Action] = [ActionSwapCard(hand_index=i) for i in range(HAND_SIZE)]
        if self.drawn_from_deck:
            actions.append(ActionDiscardDrawn())
        return actions

    def handle_action(self, round_state: Round, action: Action) -> list[GameEvent]:
        """Advance the round state based on the action and return events."""
        if not isinstance(action, (ActionSwapCard, ActionDiscardDrawn)):
            msg = f"Invalid action for ACTION phase: {action}"
            raise IllegalActionError(msg)

        events = action.execute(round_state)

        if isinstance(action, ActionSwapCard):
            return _end_turn(round_state, events)

        round_state.phase_state = FlipPhaseState()
        return events


class FlipPhaseState(PhaseState):
    """Logic for the FLIP phase."""

    phase_enum = RoundPhase.FLIP

    def get_valid_actions(self, round_state: Round, player_idx: int) -> list[Action]:
        """Return a list of valid actions for the given player."""
        actions: list[Action] = [ActionPass()]
        hand = round_state.hands[player_idx]
        actions.extend(
            [
                ActionFlipCard(hand_index=i)
                for i in range(len(hand))
                if not hand.is_face_up(i)
            ]
        )
        return actions

    def handle_action(self, round_state: Round, action: Action) -> list[GameEvent]:
        """Advance the round state based on the action and return events."""
        if not isinstance(action, (ActionFlipCard, ActionPass)):
            msg = f"Invalid action for FLIP phase: {action}"
            raise IllegalActionError(msg)

        events = action.execute(round_state)
        return _end_turn(round_state, events)


class FinishedPhaseState(PhaseState):
    """Logic for the FINISHED phase."""

    phase_enum = RoundPhase.FINISHED

    def get_valid_actions(self, round_state: Round, player_idx: int) -> list[Action]:  # noqa: ARG002
        """Return a list of valid actions for the given player."""
        return []

    def handle_action(self, round_state: Round, action: Action) -> list[GameEvent]:  # noqa: ARG002
        """Advance the round state based on the action and return events."""
        return []


def _end_turn(round_state: Round, events: list[GameEvent]) -> list[GameEvent]:
    """Finalize turn, check end conditions, and advance."""
    player_idx = round_state.current_player_idx

    if (
        round_state.hands[player_idx].all_face_up()
        and round_state.last_turn_player_idx is None
    ):
        round_state.last_turn_player_idx = round_state.current_player_idx

    round_state.current_player_idx = (
        round_state.current_player_idx + 1
    ) % round_state.num_players
    if round_state.current_player_idx == 0:
        round_state.turn_count += 1

    if (
        round_state.last_turn_player_idx is not None
        and round_state.current_player_idx == round_state.last_turn_player_idx
    ):
        round_state.reveal_hands()
        round_state.phase_state = FinishedPhaseState()
        return events

    events.append(
        TurnStartEvent(
            player_idx=round_state.current_player_idx,
            hands={i: round_state.hands[i] for i in range(round_state.num_players)},
        )
    )
    round_state.phase_state = DrawPhaseState()
    return events
