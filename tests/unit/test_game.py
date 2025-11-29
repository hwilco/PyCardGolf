import pytest
from unittest.mock import MagicMock, call
from pycardgolf.core.game import Game
from pycardgolf.core.player import Player
from pycardgolf.core.round import Round
from pycardgolf.interfaces.base import GameInterface


class MockPlayer(Player):
    def take_turn(self, game_round: Round) -> None:
        pass


@pytest.fixture
def mock_player():
    return MockPlayer("P1")


@pytest.fixture
def mock_interface():
    return MagicMock(spec=GameInterface)


@pytest.fixture
def game(mock_player, mock_interface):
    return Game([mock_player], mock_interface, num_rounds=5)


def test_game_start(mock_player, mock_interface, mocker):
    game = Game([mock_player], mock_interface, num_rounds=2)

    mock_round_cls = mocker.patch("pycardgolf.core.game.Round")

    mock_round_instance = MagicMock()
    mock_round_cls.return_value = mock_round_instance

    game.start()

    assert mock_round_cls.call_count == 2
    assert mock_round_instance.play.call_count == 2
    assert game.current_round_num == 2

    # Check notify calls for round start
    assert (
        call("--- Starting Round 1 ---")
        in mock_interface.notify.call_args_list
    )
    assert (
        call("--- Starting Round 2 ---")
        in mock_interface.notify.call_args_list
    )
    assert call("\n--- Game Over ---") in mock_interface.notify.call_args_list


def test_display_scores(mock_interface):
    p1 = MockPlayer("P1")
    p1.score = 10
    p2 = MockPlayer("P2")
    p2.score = 5

    game = Game([p1, p2], mock_interface)
    game.display_scores()

    assert call("\nCurrent Scores:") in mock_interface.notify.call_args_list
    assert call("P1: 10") in mock_interface.notify.call_args_list
    assert call("P2: 5") in mock_interface.notify.call_args_list


def test_declare_winner(mock_interface):
    p1 = MockPlayer("P1")
    p1.score = 10
    p2 = MockPlayer("P2")
    p2.score = 5  # Winner (lowest score)

    game = Game([p1, p2], mock_interface)
    game.declare_winner()

    assert call("\n--- Game Over ---") in mock_interface.notify.call_args_list
    assert (
        call("Winner: P2 with score 5") in mock_interface.notify.call_args_list
    )


def test_get_standings(game):
    p1 = game.players[0]
    p1.score = 10

    p2 = MockPlayer("P2")
    p2.score = 5

    p3 = MockPlayer("P3")
    p3.score = 15

    game.players = [p1, p2, p3]

    standings = game.get_standings()
    assert standings == [p2, p1, p3]


def test_get_winner(game):
    p1 = game.players[0]
    p1.score = 10

    p2 = MockPlayer("P2")
    p2.score = 5

    game.players = [p1, p2]

    assert game.get_winner() == p2
