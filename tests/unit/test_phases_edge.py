from unittest.mock import MagicMock

import pytest

from pycardgolf.core.actions import Action, ActionSpace, ActionType
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
        state.handle_action(round_mock, ActionSpace.PASS)


def test_setup_phase_flip_missing_index():
    """Test that SetupPhaseState raises IllegalActionError for FLIP without index."""
    state = SetupPhaseState()
    round_mock = MagicMock(spec=Round)

    try:
        action = Action(ActionType.FLIP, None)
    except AssertionError:
        return  # Success: Validation caught it in debug mode

    with pytest.raises(
        IllegalActionError, match="Action FLIP requires a valid target_index"
    ):
        state.handle_action(round_mock, action)


def test_draw_phase_missing_target_index_validation():
    """Test DrawPhaseState error if target_index is provided."""
    state = DrawPhaseState()
    round_mock = MagicMock(spec=Round)

    try:
        action = Action(ActionType.DRAW_DECK, 0)
    except AssertionError:
        return

    with pytest.raises(
        IllegalActionError, match="Invalid action or parameters for DRAW phase"
    ):
        state.handle_action(round_mock, action)


def test_draw_phase_invalid_action():
    """Test that DrawPhaseState raises IllegalActionError for invalid action."""
    state = DrawPhaseState()
    round_mock = MagicMock(spec=Round)
    with pytest.raises(IllegalActionError, match="Invalid action for DRAW phase"):
        state.handle_action(round_mock, ActionSpace.PASS)


def test_action_phase_invalid_action():
    """Test that ActionPhaseState raises IllegalActionError for invalid action."""
    state = ActionPhaseState(drawn_from_deck=True)
    round_mock = MagicMock(spec=Round)
    with pytest.raises(IllegalActionError, match="Invalid action for ACTION phase"):
        state.handle_action(round_mock, ActionSpace.DRAW_DECK)


def test_action_phase_swap_missing_index():
    """Test that ActionPhaseState raises IllegalActionError for SWAP without index."""
    state = ActionPhaseState(drawn_from_deck=True)
    round_mock = MagicMock(spec=Round)

    try:
        action = Action(ActionType.SWAP, None)
    except AssertionError:
        return

    with pytest.raises(
        IllegalActionError, match="Action SWAP requires a valid target_index"
    ):
        state.handle_action(round_mock, action)


def test_action_phase_discard_drawn_invalid():
    """Test ActionPhaseState raises IllegalActionError for invalid DISCARD_DRAWN."""
    state = ActionPhaseState(drawn_from_deck=False)
    round_mock = MagicMock(spec=Round)
    with pytest.raises(
        IllegalActionError,
        match="Cannot discard if the card was not drawn from the deck",
    ):
        state.handle_action(round_mock, ActionSpace.DISCARD_DRAWN)


def test_action_phase_discard_drawn_with_index():
    """Test ActionPhaseState error for DISCARD_DRAWN with index."""
    state = ActionPhaseState(drawn_from_deck=True)
    round_mock = MagicMock(spec=Round)

    try:
        action = Action(ActionType.DISCARD_DRAWN, 0)
    except AssertionError:
        return

    with pytest.raises(
        IllegalActionError, match="Invalid action or parameters for ACTION phase"
    ):
        state.handle_action(round_mock, action)


def test_flip_phase_invalid_action():
    """Test that FlipPhaseState raises IllegalActionError for invalid action."""
    state = FlipPhaseState()
    round_mock = MagicMock(spec=Round)
    with pytest.raises(IllegalActionError, match="Invalid action for FLIP phase"):
        state.handle_action(round_mock, ActionSpace.DRAW_DECK)


def test_flip_phase_flip_missing_index():
    """Test that FlipPhaseState raises IllegalActionError for FLIP without index."""
    state = FlipPhaseState()
    round_mock = MagicMock(spec=Round)

    try:
        action = Action(ActionType.FLIP, None)
    except AssertionError:
        return

    with pytest.raises(
        IllegalActionError, match="Action FLIP requires a valid target_index"
    ):
        state.handle_action(round_mock, action)


def test_flip_phase_pass_with_index():
    """Test that FlipPhaseState raises IllegalActionError for PASS with index."""
    state = FlipPhaseState()
    round_mock = MagicMock(spec=Round)

    try:
        action = Action(ActionType.PASS, 0)
    except AssertionError:
        return

    with pytest.raises(IllegalActionError, match="Invalid parameters for PASS action"):
        state.handle_action(round_mock, action)


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
