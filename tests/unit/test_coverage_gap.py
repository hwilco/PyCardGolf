"""Tests to reach 100% coverage in core/phases.py by bypassing Action validation."""

from unittest.mock import MagicMock

import pytest

from pycardgolf.core.actions import Action, ActionType
from pycardgolf.core.phases import (
    ActionPhaseState,
    DrawPhaseState,
    FlipPhaseState,
    SetupPhaseState,
)
from pycardgolf.exceptions import IllegalActionError


@pytest.fixture
def mock_round():
    return MagicMock()


@pytest.mark.parametrize(
    ("state", "action_type", "target_index", "match_msg"),
    [
        # SetupPhaseState
        (
            SetupPhaseState(),
            ActionType.FLIP,
            None,
            "Action FLIP requires a valid target_index",
        ),
        # DrawPhaseState
        (
            DrawPhaseState(),
            ActionType.DRAW_DECK,
            0,
            "Invalid action or parameters for DRAW phase",
        ),
        # ActionPhaseState
        (
            ActionPhaseState(drawn_from_deck=True),
            ActionType.SWAP,
            None,
            "Action SWAP requires a valid target_index",
        ),
        (
            ActionPhaseState(drawn_from_deck=True),
            ActionType.DISCARD_DRAWN,
            0,
            "Invalid action or parameters for ACTION phase",
        ),
        # FlipPhaseState
        (
            FlipPhaseState(),
            ActionType.FLIP,
            None,
            "Action FLIP requires a valid target_index",
        ),
        (FlipPhaseState(), ActionType.PASS, 0, "Invalid parameters for PASS action"),
    ],
)
def test_phase_handle_action_defensive_checks(
    mock_round, state, action_type, target_index, match_msg
):
    """Reach unreachable safety lines in phases.py by bypassing Action validation."""
    mock_action = MagicMock(spec=Action)
    mock_action.action_type = action_type
    mock_action.target_index = target_index

    with pytest.raises(IllegalActionError, match=match_msg):
        state.handle_action(mock_round, mock_action)
