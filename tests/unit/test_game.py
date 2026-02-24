"""Tests for the Game class."""

from unittest.mock import MagicMock

import pytest

from pycardgolf.core.event_bus import EventBus
from pycardgolf.core.events import (
    GameOverEvent,
    GameStatsEvent,
    RoundStartEvent,
    ScoreBoardEvent,
)
from pycardgolf.core.game import Game
from pycardgolf.core.phases import RoundPhase
from pycardgolf.core.round import Round
from pycardgolf.players.player import BasePlayer
from pycardgolf.utils.mixins import RNGMixin


@pytest.fixture
def mock_event_bus():
    """Create a mock EventBus."""
    return MagicMock(spec=EventBus)


@pytest.fixture
def players():
    """Create two mock players."""
    p1 = MagicMock(spec=BasePlayer)
    p1.name = "P1"
    p2 = MagicMock(spec=BasePlayer)
    p2.name = "P2"
    return [p1, p2]


def test_game_init(players, mock_event_bus):
    """Test Game initializes with correct defaults."""
    game = Game(players, mock_event_bus, num_rounds=5)
    assert game.num_rounds == 5
    assert len(game.players) == 2
    assert game.scores[players[0]] == 0


def test_game_start_and_loop_flow(players, mock_event_bus, mocker):
    """Test the full game loop calls Round and display methods."""
    game = Game(players, mock_event_bus, num_rounds=2)

    mock_factory = mocker.patch("pycardgolf.core.game.RoundFactory")
    mock_round_instance = MagicMock(spec=Round)
    mock_round_instance.get_scores.return_value = {0: 10, 1: 5}
    mock_round_instance.hands = [MagicMock(), MagicMock()]
    mock_factory.create_standard_round.return_value = mock_round_instance

    mock_run_loop = mocker.patch.object(game, "_run_round_loop")

    game.start()

    assert mock_factory.create_standard_round.call_count == 2
    assert mock_run_loop.call_count == 2

    # P1 (index 0) gets 10 per round * 2 = 20
    assert game.scores[players[0]] == 20
    # P2 (index 1) gets 5 per round * 2 = 10
    assert game.scores[players[1]] == 10

    # Test event publishing
    assert mock_event_bus.publish.call_count > 0
    published_events = [call.args[0] for call in mock_event_bus.publish.call_args_list]

    assert any(
        isinstance(e, RoundStartEvent) and e.round_num == 1 for e in published_events
    )
    assert any(
        isinstance(e, RoundStartEvent) and e.round_num == 2 for e in published_events
    )
    assert any(isinstance(e, GameOverEvent) for e in published_events)
    assert any(isinstance(e, ScoreBoardEvent) for e in published_events)


def test_publish_events(players, mock_event_bus):
    """Test that publish_events sends events to the event bus."""
    game = Game(players, mock_event_bus)

    event = RoundStartEvent(round_num=1)
    game.publish_events([event])

    mock_event_bus.publish.assert_called_once_with(event)


def test_publish_scores(players, mock_event_bus):
    """Test that publish_scores publishes a ScoreBoardEvent."""
    game = Game(players, mock_event_bus)
    game.scores = {players[0]: 10, players[1]: 5}

    game.publish_scores()

    assert mock_event_bus.publish.call_count == 1
    published_event = mock_event_bus.publish.call_args[0][0]
    assert isinstance(published_event, ScoreBoardEvent)
    assert published_event.scores == game.scores


def test_declare_winner(players, mock_event_bus):
    """Test that declare_winner notifies the renderer correctly."""
    game = Game(players, mock_event_bus)
    game.scores[players[0]] = 10
    game.scores[players[1]] = 5  # Winner (lower is better)

    game.declare_winner()

    published_events = [call.args[0] for call in mock_event_bus.publish.call_args_list]

    assert any(isinstance(e, GameStatsEvent) for e in published_events)
    assert any(isinstance(e, ScoreBoardEvent) for e in published_events)
    game_over_events = [e for e in published_events if isinstance(e, GameOverEvent)]
    assert len(game_over_events) == 1
    assert game_over_events[0].winner == players[1]
    assert game_over_events[0].winning_score == 5


def test_run_round_loop_none_round(players, mock_event_bus):
    """Test that _run_round_loop returns early if current_round is None."""
    game = Game(players, mock_event_bus)
    game.current_round = None
    # Should return early without error
    game._run_round_loop()


def test_get_winner(players, mock_event_bus):
    """Test get_winner returns player with lowest score."""
    game = Game(players, mock_event_bus)
    game.scores[players[0]] = 10
    game.scores[players[1]] = 5
    assert game.get_winner() == players[1]


def test_game_init_reseeds_players(mock_event_bus):
    """Test that Game.__init__ reseeds players that are RNGMixins."""

    class RNGPlayer(BasePlayer, RNGMixin):
        def get_action(self, observation):
            return MagicMock()

    p1 = RNGPlayer("P1")
    p1.reseed(42)  # Initial seed
    p2 = MagicMock(spec=BasePlayer)
    p2.name = "P2"

    _ = Game([p1, p2], mock_event_bus, seed=123)

    assert p1.seed != 42  # Should be reseeded


def test_run_round_loop_executes_steps(players, mock_event_bus, mocker):
    """Test that _run_round_loop calls get_action and step until FINISHED."""
    game = Game(players, mock_event_bus)
    mock_round = MagicMock(spec=Round)

    # Setup side effects for phase to end the loop
    type(mock_round).phase = mocker.PropertyMock(
        side_effect=[RoundPhase.SETUP, RoundPhase.FINISHED]
    )
    mock_round.get_current_player_idx.return_value = 0

    mock_action = MagicMock()
    players[0].get_action.return_value = mock_action

    mock_round.step.return_value = [MagicMock()]

    # Patch ObservationBuilder to avoid using the MagicMock in build
    mock_build = mocker.patch("pycardgolf.core.game.ObservationBuilder.build")
    mock_build.return_value = MagicMock()

    game.current_round = mock_round
    game._run_round_loop()

    assert players[0].get_action.call_count == 1
    assert mock_round.step.call_count == 1
    assert mock_event_bus.publish.call_count == 1
