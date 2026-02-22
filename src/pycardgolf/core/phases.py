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
    ) -> tuple[list[GameEvent], RoundPhase]:
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
    ) -> tuple[list[GameEvent], RoundPhase]:
        """Advance the round state based on the action and return events."""
        if not isinstance(action, ActionFlipCard):
            msg = "Must flip a card in setup phase."
            raise IllegalActionError(msg)

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
                return events, RoundPhase.DRAW

        return events, round_state.phase


class DrawPhaseState(PhaseState):
    """Logic for the DRAW phase."""

    def get_valid_actions(self, round_state: Round, player_idx: int) -> list[Action]:  # noqa: ARG002
        """Return a list of valid actions for the given player."""
        actions: list[Action] = [ActionDrawDeck()]
        if round_state.discard_pile.num_cards > 0:
            actions.append(ActionDrawDiscard())
        return actions

    def handle_step(
        self,
        round_state: Round,
        player_idx: int,  # noqa: ARG002
        action: Action,
    ) -> tuple[list[GameEvent], RoundPhase]:
        """Advance the round state based on the action and return events."""
        if not isinstance(action, (ActionDrawDeck, ActionDrawDiscard)):
            msg = f"Invalid action for DRAW phase: {action}"
            raise IllegalActionError(msg)

        events = action.execute(round_state)
        return events, RoundPhase.ACTION


class ActionPhaseState(PhaseState):
    """Logic for the ACTION phase."""

    def get_valid_actions(self, round_state: Round, player_idx: int) -> list[Action]:  # noqa: ARG002
        """Return a list of valid actions for the given player."""
        actions: list[Action] = [ActionSwapCard(hand_index=i) for i in range(HAND_SIZE)]
        if round_state.drawn_from_deck:
            actions.append(ActionDiscardDrawn())
        return actions

    def handle_step(
        self,
        round_state: Round,
        player_idx: int,  # noqa: ARG002
        action: Action,
    ) -> tuple[list[GameEvent], RoundPhase]:
        """Advance the round state based on the action and return events."""
        if not isinstance(action, (ActionSwapCard, ActionDiscardDrawn)):
            msg = f"Invalid action for ACTION phase: {action}"
            raise IllegalActionError(msg)

        events = action.execute(round_state)

        if isinstance(action, ActionSwapCard):
            return _end_turn(round_state, events)
        return events, RoundPhase.FLIP


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
        self,
        round_state: Round,
        player_idx: int,  # noqa: ARG002
        action: Action,
    ) -> tuple[list[GameEvent], RoundPhase]:
        """Advance the round state based on the action and return events."""
        if not isinstance(action, (ActionFlipCard, ActionPass)):
            msg = f"Invalid action for FLIP phase: {action}"
            raise IllegalActionError(msg)

        events = action.execute(round_state)
        return _end_turn(round_state, events)


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
    ) -> tuple[list[GameEvent], RoundPhase]:
        """Advance the round state based on the action and return events."""
        return [], RoundPhase.FINISHED


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
    if not state:
        msg = f"Unknown round phase: {round_state.phase}"
        raise RuntimeError(msg)
    return state.get_valid_actions(round_state, player_idx)


def handle_step(round_state: Round, action: Action) -> list[GameEvent]:
    """Advance the round state based on the action and current phase."""
    if round_state.phase == RoundPhase.FINISHED:
        return []

    player_idx = round_state.current_player_idx
    state = _PHASE_STATES.get(round_state.phase)
    if not state:
        msg = f"Unknown round phase: {round_state.phase}"
        raise RuntimeError(msg)
    events, next_phase = state.handle_step(round_state, player_idx, action)
    round_state.phase = next_phase
    return events


def _end_turn(
    round_state: Round, events: list[GameEvent]
) -> tuple[list[GameEvent], RoundPhase]:
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
        round_state.reveal_hands()  # Reveal hidden cards
        return events, RoundPhase.FINISHED

    events.append(
        TurnStartEvent(
            player_idx=round_state.current_player_idx,
            hands={i: round_state.hands[i] for i in range(round_state.num_players)},
        )
    )
    return events, RoundPhase.DRAW
