from unittest.mock import MagicMock

import pytest

from pycardgolf.core.actions import Action, ActionType
from pycardgolf.core.phases import (
    ActionPhaseState,
    DrawPhaseState,
    FlipPhaseState,
    SetupPhaseState,
)
from pycardgolf.core.round import Round
from pycardgolf.exceptions import IllegalActionError


def test_action_phase_get_valid_actions_drawn_from_discard():
    """Test get_valid_actions in ACTION phase when drawn from discard."""
    state = ActionPhaseState(drawn_from_deck=False)
    round_mock = MagicMock(spec=Round)

    actions = state.get_valid_actions(round_mock, 0)
    # Should NOT contain DISCARD_DRAWN
    assert not any(a.action_type == ActionType.DISCARD_DRAWN for a in actions)


def test_setup_phase_invalid_action():
    """Test that SetupPhaseState raises IllegalActionError for non-flip action."""
    state = SetupPhaseState()
    round_mock = MagicMock(spec=Round)
    with pytest.raises(IllegalActionError, match="Must flip a valid card"):
        state.handle_action(round_mock, Action(action_type=ActionType.PASS))


def test_draw_phase_invalid_action():
    """Test that DrawPhaseState raises IllegalActionError for invalid action."""
    state = DrawPhaseState()
    round_mock = MagicMock(spec=Round)
    with pytest.raises(IllegalActionError, match="Invalid action for DRAW phase"):
        state.handle_action(round_mock, Action(action_type=ActionType.PASS))


def test_action_phase_invalid_action():
    """Test that ActionPhaseState raises IllegalActionError for invalid action."""
    state = ActionPhaseState(drawn_from_deck=True)
    round_mock = MagicMock(spec=Round)
    with pytest.raises(IllegalActionError, match="Invalid action for ACTION phase"):
        state.handle_action(round_mock, Action(action_type=ActionType.DRAW_DECK))


def test_flip_phase_invalid_action():
    """Test that FlipPhaseState raises IllegalActionError for invalid action."""
    state = FlipPhaseState()
    round_mock = MagicMock(spec=Round)
    with pytest.raises(IllegalActionError, match="Invalid action for FLIP phase"):
        state.handle_action(round_mock, Action(action_type=ActionType.DRAW_DECK))


def test_phase_state_eq_incompatible_type():
    """Test that PhaseState.__eq__ returns False for incompatible types."""
    state = SetupPhaseState()
    assert state != "NOT_A_PHASE_STATE"
    assert state != 42
    assert state != None  # noqa: E711
    # Compare different phase states
    assert state != DrawPhaseState()


def test_phase_state_eq_same_type():
    """Test that PhaseState.__eq__ returns True for same type."""
    state = SetupPhaseState()
    assert state == SetupPhaseState()
