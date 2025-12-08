from unittest.mock import MagicMock
import pytest

from pycardgolf.core.game import Game
from pycardgolf.core.round import Round
from pycardgolf.core.events import RoundEndEvent
from pycardgolf.players.player import Player


@pytest.fixture
def mock_interface():
    return MagicMock()


@pytest.fixture
def players():
    p1 = MagicMock(spec=Player)
    p1.name = "P1"
    p2 = MagicMock(spec=Player)
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
    mock_round_cls.return_value = mock_round_instance

    # Mock _run_round_loop to verify it is called
    # We patch it on the INSTANCE of game, but we haven't created it yet?
    # No, we created 'game'.
    mock_run_loop = mocker.patch.object(game, "_run_round_loop")

    # Simulate scores being updated (usually happens in _run_round_loop via events)
    # But Game.start also relies on game.process_events logic?
    # Actually Game.start loop:
    # 1. Init Round
    # 2. Call _run_round_loop
    # 3. Next round

    game.start()

    assert mock_round_cls.call_count == 2
    assert mock_run_loop.call_count == 2

    # Check notifications
    mock_interface.display_round_start.assert_any_call(1)
    mock_interface.display_round_start.assert_any_call(2)
    mock_interface.display_game_over.assert_called_once()
    mock_interface.display_standings.assert_called_once()
    mock_interface.display_winner.assert_called_once()


def test_process_events_round_end(players, mock_interface):
    game = Game(players, mock_interface)

    # Simulate RoundEndEvent
    scores = {players[0]: 10, players[1]: 5}
    event = RoundEndEvent(scores=scores)

    game.process_events([event])

    # Check display called (process_events purely updates UI for this event)
    mock_interface.display_round_end.assert_called_once()
    # Note: display_scores is NOT called for RoundEndEvent in current logic,
    # as display_round_end handles showing round summary.
    # Scores update happens in Game.start() loop.


def test_declare_winner(players, mock_interface):
    game = Game(players, mock_interface)
    game.scores[players[0]] = 10
    game.scores[players[1]] = 5  # Winner

    game.declare_winner()

    mock_interface.display_winner.assert_called_once_with(players[1], 5)
