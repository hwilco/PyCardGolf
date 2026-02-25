from collections import defaultdict
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
    mock = MagicMock()
    mock.cards_flipped_in_setup = defaultdict(int)
    mock.current_player_idx = 0
    return mock


@pytest.mark.parametrize(
    ("state", "action_type", "target_index", "match_msg"),
    [
        # SetupPhaseState: line 85 action_type != ActionType.FLIP
        (
            SetupPhaseState(),
            ActionType.DRAW_DECK,
            None,
            "Must flip a valid card in SETUP phase",
        ),
        # DrawPhaseState: line 168 case _:
        (
            DrawPhaseState(),
            ActionType.FLIP,
            0,
            "Invalid action for DRAW phase",
        ),
        # ActionPhaseState: line 208-209 is_from_deck=False + DISCARD_DRAWN
        (
            ActionPhaseState(drawn_from_deck=False),
            ActionType.DISCARD_DRAWN,
            None,
            "Cannot discard if the card was not drawn from the deck.",
        ),
        # ActionPhaseState: line 214-215 case _:
        (
            ActionPhaseState(drawn_from_deck=True),
            ActionType.DRAW_DECK,
            None,
            "Invalid action for ACTION phase",
        ),
        # FlipPhaseState: line 137 case _:
        (
            FlipPhaseState(),
            ActionType.DRAW_DECK,
            None,
            "Invalid action for FLIP phase",
        ),
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
