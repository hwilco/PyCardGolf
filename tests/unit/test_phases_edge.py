from unittest.mock import MagicMock

import pytest

from pycardgolf.core.actions import ActionDiscardDrawn, ActionDrawDeck, ActionPass
from pycardgolf.core.phases import (
    ActionPhaseState,
    DrawPhaseState,
    FlipPhaseState,
    SetupPhaseState,
    get_phase_actions,
    handle_phase_step,
)
from pycardgolf.core.round import Round
from pycardgolf.exceptions import IllegalActionError


def test_action_phase_get_valid_actions_drawn_from_discard():
    """Test get_valid_actions in ACTION phase when drawn from discard."""
    state = ActionPhaseState()
    round_mock = MagicMock(spec=Round)
    round_mock.drawn_from_deck = False

    actions = state.get_valid_actions(round_mock, 0)
    # Should NOT contain ActionDiscardDrawn
    assert not any(isinstance(a, ActionDiscardDrawn) for a in actions)


def test_setup_phase_invalid_action():
    """Test that SetupPhaseState raises IllegalActionError for non-flip action."""
    state = SetupPhaseState()
    round_mock = MagicMock(spec=Round)
    with pytest.raises(IllegalActionError, match="Must flip a card"):
        state.handle_action(round_mock, ActionPass())


def test_draw_phase_invalid_action():
    """Test that DrawPhaseState raises IllegalActionError for invalid action."""
    state = DrawPhaseState()
    round_mock = MagicMock(spec=Round)
    with pytest.raises(IllegalActionError, match="Invalid action for DRAW phase"):
        state.handle_action(round_mock, ActionPass())


def test_action_phase_invalid_action():
    """Test that ActionPhaseState raises IllegalActionError for invalid action."""
    state = ActionPhaseState()
    round_mock = MagicMock(spec=Round)
    with pytest.raises(IllegalActionError, match="Invalid action for ACTION phase"):
        state.handle_action(round_mock, ActionDrawDeck())


def test_flip_phase_invalid_action():
    """Test that FlipPhaseState raises IllegalActionError for invalid action."""
    state = FlipPhaseState()
    round_mock = MagicMock(spec=Round)
    with pytest.raises(IllegalActionError, match="Invalid action for FLIP phase"):
        state.handle_action(round_mock, ActionDrawDeck())


def test_handle_phase_step_unknown_phase():
    """Test that handle_phase_step raises RuntimeError for unknown phase."""
    round_mock = MagicMock(spec=Round)
    round_mock.phase = "INVALID_PHASE"
    with pytest.raises(RuntimeError, match="Unknown round phase"):
        handle_phase_step(round_mock, ActionPass())


def test_get_phase_actions_unknown_phase():
    """Test that get_phase_actions raises RuntimeError for unknown phase."""
    round_mock = MagicMock(spec=Round)
    round_mock.phase = "INVALID_PHASE"
    with pytest.raises(RuntimeError, match="Unknown round phase"):
        get_phase_actions(round_mock, 0)
