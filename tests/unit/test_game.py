from unittest.mock import MagicMock

import pytest

from pycardgolf.core.events import RoundEndEvent
from pycardgolf.core.game import Game
from pycardgolf.core.round import Round
from pycardgolf.players.player import BasePlayer


@pytest.fixture
def mock_interface():
    return MagicMock()


@pytest.fixture
def players():
    p1 = MagicMock(spec=BasePlayer)
    p1.name = "P1"
    p2 = MagicMock(spec=BasePlayer)
    p2.name = "P2"
    return [p1, p2]


def test_game_init(players, mock_interface):
    game = Game(players, mock_interface, num_rounds=5)
    assert game.num_rounds == 5
    assert len(game.players) == 2
    assert game.scores[players[0]] == 0


def test_game_start_and_loop_flow(players, mock_interface, mocker):
    game = Game(players, mock_interface, num_rounds=2)

    # Mock Round class
    mock_round_cls = mocker.patch("pycardgolf.core.game.Round")
    mock_round_instance = MagicMock(spec=Round)
    mock_round_instance.get_scores.return_value = {
        0: 10,
        1: 5,
    }  # Return scores by index
    # Mock hands for player sync
    mock_round_instance.hands = [MagicMock(), MagicMock()]
    mock_round_cls.return_value = mock_round_instance

    # Mock _run_round_loop to verify it is called
    mock_run_loop = mocker.patch.object(game, "_run_round_loop")

    game.start()

    assert mock_round_cls.call_count == 2
    assert mock_run_loop.call_count == 2

    # Verify connection between Round scores and Game scores
    # Game stores mapping of players to indices implicitely by order
    # Index 0 -> P1, Index 1 -> P2
    # P1 gets 10 per round * 2 rounds = 20
    assert game.scores[players[0]] == 20
    # P2 gets 5 per round * 2 rounds = 10
    assert game.scores[players[1]] == 10

    # Check notifications
    mock_interface.display_round_start.assert_any_call(1)
    mock_interface.display_round_start.assert_any_call(2)
    mock_interface.display_game_over.assert_called_once()
    mock_interface.display_standings.assert_called_once()
    mock_interface.display_winner.assert_called_once()


def test_process_events_round_end(players, mock_interface):
    game = Game(players, mock_interface)

    # Simulate RoundEndEvent with player indices
    scores = {0: 10, 1: 5}
    event = RoundEndEvent(scores=scores)

    game.display_events([event])

    # Check display called (process_events purely updates UI for this event)
    mock_interface.display_round_end.assert_called_once()


def test_declare_winner(players, mock_interface):
    game = Game(players, mock_interface)
    game.scores[players[0]] = 10
    game.scores[players[1]] = 5  # Winner

    game.declare_winner()

    mock_interface.display_winner.assert_called_once_with(players[1], 5)
