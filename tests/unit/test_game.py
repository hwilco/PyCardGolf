"""Tests for the Game class."""

from unittest.mock import MagicMock

import pytest

from pycardgolf.core.events import GameEvent, RoundEndEvent
from pycardgolf.core.game import Game
from pycardgolf.core.round import Round
from pycardgolf.interfaces.base import GameRenderer
from pycardgolf.players.player import BasePlayer


@pytest.fixture
def mock_renderer():
    """Create a mock GameRenderer."""
    return MagicMock(spec=GameRenderer)


@pytest.fixture
def players():
    """Create two mock players."""
    p1 = MagicMock(spec=BasePlayer)
    p1.name = "P1"
    p2 = MagicMock(spec=BasePlayer)
    p2.name = "P2"
    return [p1, p2]


def test_game_init(players, mock_renderer):
    """Test Game initializes with correct defaults."""
    game = Game(players, mock_renderer, num_rounds=5)
    assert game.num_rounds == 5
    assert len(game.players) == 2
    assert game.scores[players[0]] == 0


def test_game_start_and_loop_flow(players, mock_renderer, mocker):
    """Test the full game loop calls Round and display methods."""
    game = Game(players, mock_renderer, num_rounds=2)

    mock_round_cls = mocker.patch("pycardgolf.core.game.Round")
    mock_round_instance = MagicMock(spec=Round)
    mock_round_instance.get_scores.return_value = {0: 10, 1: 5}
    mock_round_instance.hands = [MagicMock(), MagicMock()]
    mock_round_cls.return_value = mock_round_instance

    mock_run_loop = mocker.patch.object(game, "_run_round_loop")

    game.start()

    assert mock_round_cls.call_count == 2
    assert mock_run_loop.call_count == 2

    # P1 (index 0) gets 10 per round * 2 = 20
    assert game.scores[players[0]] == 20
    # P2 (index 1) gets 5 per round * 2 = 10
    assert game.scores[players[1]] == 10

    mock_renderer.display_round_start.assert_any_call(1)
    mock_renderer.display_round_start.assert_any_call(2)
    mock_renderer.display_game_over.assert_called_once()
    mock_renderer.display_standings.assert_called_once()
    mock_renderer.display_winner.assert_called_once()


def test_display_events_unknown_event(players, mock_renderer):
    """Test that display_events raises TypeError for unregistered events."""
    game = Game(players, mock_renderer)

    class UnknownEvent(GameEvent):
        pass

    event = UnknownEvent(event_type="UNKNOWN")  # type: ignore[arg-type]

    # Should raise TypeError
    with pytest.raises(TypeError, match="No handler registered for UnknownEvent"):
        game.display_events([event])
    mock_renderer.assert_not_called()


def test_process_events_round_end(players, mock_renderer):
    """Test that RoundEndEvent triggers display_round_end."""
    game = Game(players, mock_renderer)

    scores = {0: 10, 1: 5}
    event = RoundEndEvent(scores=scores)
    game.display_events([event])

    mock_renderer.display_round_end.assert_called_once_with(
        game.current_round_num, players
    )


def test_declare_winner(players, mock_renderer):
    """Test that declare_winner notifies the renderer correctly."""
    game = Game(players, mock_renderer)
    game.scores[players[0]] = 10
    game.scores[players[1]] = 5  # Winner (lower is better)

    game.declare_winner()

    mock_renderer.display_winner.assert_called_once_with(players[1], 5)


def test_run_round_loop_none_round(players, mock_renderer):
    """Test that _run_round_loop returns early if current_round is None."""
    game = Game(players, mock_renderer)
    game.current_round = None
    # Should return early without error
    game._run_round_loop()


def test_get_winner(players, mock_renderer):
    """Test get_winner returns player with lowest score."""
    game = Game(players, mock_renderer)
    game.scores[players[0]] = 10
    game.scores[players[1]] = 5
    assert game.get_winner() == players[1]
