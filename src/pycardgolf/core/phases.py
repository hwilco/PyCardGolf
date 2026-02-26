"""Module containing phase-specific logic for the Golf engine."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import TYPE_CHECKING

from pycardgolf.core.actions import (
    Action,
    ActionSpace,
    ActionType,
)
from pycardgolf.core.events import (
    GameEvent,
    TurnStartEvent,
)
from pycardgolf.exceptions import IllegalActionError
from pycardgolf.utils.constants import HAND_SIZE, INITIAL_CARDS_TO_FLIP

if TYPE_CHECKING:
    from pycardgolf.core.round import Round


# --- Pre-computed Action Caches for MCTS ---
# These are evaluated once at module load time to provide O(1) tuple returns.

_SETUP_ACTION_CACHE: dict[int, tuple[Action, ...]] = {}
for _mask in range(1 << HAND_SIZE):
    _SETUP_ACTION_CACHE[_mask] = tuple(
        ActionSpace.FLIP[i] for i in range(HAND_SIZE) if not (_mask & (1 << i))
    )

_FLIP_PHASE_ACTION_CACHE: dict[int, tuple[Action, ...]] = {
    mask: (ActionSpace.PASS, *flips) for mask, flips in _SETUP_ACTION_CACHE.items()
}


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
    def get_valid_actions(
        self, round_state: Round, player_idx: int
    ) -> tuple[Action, ...]:
        """Return a tuple of valid actions for the given player."""

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

    def get_valid_actions(
        self, round_state: Round, player_idx: int
    ) -> tuple[Action, ...]:
        """Return a tuple of valid actions for the given player."""
        return _SETUP_ACTION_CACHE[round_state.hands[player_idx].face_up_mask]

    def handle_action(self, round_state: Round, action: Action) -> list[GameEvent]:
        """Advance the round state based on the action and return events."""
        if action.action_type != ActionType.FLIP:
            msg = f"Must flip a valid card in SETUP phase. Got: {action}"
            raise IllegalActionError(msg)

        player_idx = round_state.current_player_idx
        event = round_state.flip_card_in_hand(player_idx, action.safe_target_index)
        events: list[GameEvent] = [event]
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


class FlipPhaseState(PhaseState):
    """Logic for the FLIP phase."""

    phase_enum = RoundPhase.FLIP

    def get_valid_actions(
        self, round_state: Round, player_idx: int
    ) -> tuple[Action, ...]:
        """Return a tuple of valid actions for the given player."""
        return _FLIP_PHASE_ACTION_CACHE[round_state.hands[player_idx].face_up_mask]

    def handle_action(self, round_state: Round, action: Action) -> list[GameEvent]:
        """Advance the round state based on the action and return events."""
        player_idx = round_state.current_player_idx
        match action.action_type:
            case ActionType.FLIP:
                event = round_state.flip_card_in_hand(
                    player_idx, action.safe_target_index
                )
                return _end_turn(round_state, [event])
            case ActionType.PASS:
                return _end_turn(round_state, [])
            case _:
                msg = f"Invalid action for FLIP phase: {action.action_type}"
                raise IllegalActionError(msg)


class DrawPhaseState(PhaseState):
    """Logic for the DRAW phase."""

    phase_enum = RoundPhase.DRAW

    _ACTIONS_DECK_ONLY = (ActionSpace.DRAW_DECK,)
    _ACTIONS_WITH_DISCARD = (ActionSpace.DRAW_DECK, ActionSpace.DRAW_DISCARD)

    def get_valid_actions(
        self,
        round_state: Round,
        player_idx: int,  # noqa: ARG002
    ) -> tuple[Action, ...]:
        """Return a tuple of valid actions for the given player."""
        if round_state.discard_pile.num_cards > 0:
            return self._ACTIONS_WITH_DISCARD
        return self._ACTIONS_DECK_ONLY

    def handle_action(self, round_state: Round, action: Action) -> list[GameEvent]:
        """Advance the round state based on the action and return events."""
        player_idx = round_state.current_player_idx
        events: list[GameEvent]

        match action.action_type:
            case ActionType.DRAW_DECK:
                events = round_state.draw_from_deck(player_idx)
                is_from_deck = True
            case ActionType.DRAW_DISCARD:
                events = [round_state.draw_from_discard(player_idx)]
                is_from_deck = False
            case _:
                msg = f"Invalid action for DRAW phase: {action}"
                raise IllegalActionError(msg)

        round_state.phase_state = ActionPhaseState(drawn_from_deck=is_from_deck)
        return events


class ActionPhaseState(PhaseState):
    """Logic for the ACTION phase."""

    phase_enum = RoundPhase.ACTION

    _SWAP_ONLY = ActionSpace.SWAP
    _SWAP_AND_DISCARD = (*ActionSpace.SWAP, ActionSpace.DISCARD_DRAWN)

    def __init__(self, drawn_from_deck: bool) -> None:
        self.drawn_from_deck = drawn_from_deck
        self._cached_actions = (
            self._SWAP_AND_DISCARD if drawn_from_deck else self._SWAP_ONLY
        )

    def get_valid_actions(
        self,
        round_state: Round,  # noqa: ARG002
        player_idx: int,  # noqa: ARG002
    ) -> tuple[Action, ...]:
        """Return a tuple of valid actions for the given player."""
        return self._cached_actions

    def handle_action(self, round_state: Round, action: Action) -> list[GameEvent]:
        """Advance the round state based on the action and return events."""
        player_idx = round_state.current_player_idx
        match action.action_type:
            case ActionType.SWAP:
                event = round_state.swap_drawn_card(
                    player_idx, action.safe_target_index
                )
                return _end_turn(round_state, [event])
            case ActionType.DISCARD_DRAWN:
                if not self.drawn_from_deck:
                    msg = "Cannot discard if the card was not drawn from the deck."
                    raise IllegalActionError(msg)
                event = round_state.discard_drawn_card(player_idx)
                round_state.phase_state = FlipPhaseState()
                return [event]
            case _:
                msg = f"Invalid action for ACTION phase: {action.action_type}"
                raise IllegalActionError(msg)


class FinishedPhaseState(PhaseState):
    """Logic for the FINISHED phase."""

    phase_enum = RoundPhase.FINISHED

    def get_valid_actions(
        self,
        round_state: Round,  # noqa: ARG002
        player_idx: int,  # noqa: ARG002
    ) -> tuple[Action, ...]:
        """There are no valid actions in the FINISHED phase."""
        return ()

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
