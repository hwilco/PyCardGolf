from unittest.mock import MagicMock

import pytest

from pycardgolf.core.events import IllegalActionEvent
from pycardgolf.core.game import Game
from pycardgolf.core.phases import RoundPhase
from pycardgolf.core.round import Round
from pycardgolf.exceptions import IllegalActionError


@pytest.fixture
def mock_event_bus():
    """Create a mock EventBus."""
    return MagicMock()


@pytest.fixture
def players():
    """Create two mock players."""
    p1 = MagicMock()
    p1.name = "P1"
    p2 = MagicMock()
    p2.name = "P2"
    return [p1, p2]


def test_tick_catches_illegal_action_error(players, mock_event_bus, mocker):
    """Test that Game.tick() catches IllegalActionError and publishes an event."""
    game = Game(players, mock_event_bus)

    # Set up a mock round in SETUP phase
    mock_round = MagicMock(spec=Round)
    mock_round.phase = RoundPhase.SETUP
    mock_round.get_current_player_idx.return_value = 0
    game.current_round = mock_round

    # Mock observation building
    mocker.patch(
        "pycardgolf.core.game.ObservationBuilder.build", return_value=MagicMock()
    )

    # 1. Setup an illegal action
    illegal_action = MagicMock()
    players[0].get_action.return_value = illegal_action
    mock_round.step.side_effect = IllegalActionError("Test illegal move")

    # 2. Run tick
    result = game.tick()

    # 3. Verify resilience
    assert result is True  # Game must continue

    # Verify IllegalActionEvent was published
    assert mock_event_bus.publish.call_count == 1
    event = mock_event_bus.publish.call_args[0][0]
    assert isinstance(event, IllegalActionEvent)
    assert event.player_idx == 0
    assert event.message == "Test illegal move"

    # 4. Successive valid action (to ensure recovery)
    valid_action = MagicMock()
    players[0].get_action.return_value = valid_action
    mock_round.step.side_effect = None
    mock_round.step.return_value = []  # No events for simplicity

    result_2 = game.tick()
    assert result_2 is True
    assert mock_round.step.call_count == 2
    # Verify that the second call used the valid action
    assert mock_round.step.call_args_list[1][0][0] == valid_action
