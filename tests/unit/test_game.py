import pytest

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
def mock_interface(mocker):
    return mocker.MagicMock(spec=GameInterface)


@pytest.fixture
def game(mock_player, mock_interface):
    return Game([mock_player], mock_interface, num_rounds=5)


def test_game_start(mock_player, mock_interface, mocker):
    game = Game([mock_player], mock_interface, num_rounds=2)

    mock_round_cls = mocker.patch("pycardgolf.core.game.Round")

    mock_round_instance = mocker.MagicMock()
    mock_round_cls.return_value = mock_round_instance
    mock_round_instance.play.return_value = {mock_player: 10}

    game.start()

    assert mock_round_cls.call_count == 2
    assert mock_round_instance.play.call_count == 2
    assert game.current_round_num == 2

    # Check notify calls for round start
    assert (
        mocker.call("--- Starting Round 1 ---") in mock_interface.notify.call_args_list
    )
    assert (
        mocker.call("--- Starting Round 2 ---") in mock_interface.notify.call_args_list
    )
    assert mocker.call("\n--- Game Over ---") in mock_interface.notify.call_args_list


def test_score_accumulation(mock_player, mock_interface, mocker):
    """Test that player scores accumulate correctly across rounds."""
    game = Game([mock_player], mock_interface, num_rounds=3)

    mock_round_cls = mocker.patch("pycardgolf.core.game.Round")
    mock_round_instance = mocker.MagicMock()
    mock_round_cls.return_value = mock_round_instance

    # Return different scores for each round
    mock_round_instance.play.side_effect = [
        {mock_player: 5},
        {mock_player: 10},
        {mock_player: -3},
    ]

    game.start()

    # Player should have accumulated score of 5 + 10 - 3 = 12
    assert mock_player.score == 12


def test_display_scores(mock_interface, mocker):
    p1 = MockPlayer("P1")
    p1.score = 10
    p2 = MockPlayer("P2")
    p2.score = 5

    game = Game([p1, p2], mock_interface)
    game.display_scores()

    assert mocker.call("P1: 10") in mock_interface.notify.call_args_list
    assert mocker.call("P2: 5") in mock_interface.notify.call_args_list


def test_declare_winner(mock_interface, mocker):
    p1 = MockPlayer("P1")
    p1.score = 10
    p2 = MockPlayer("P2")
    p2.score = 5  # Winner (lowest score)

    game = Game([p1, p2], mock_interface)
    game.declare_winner()

    assert mocker.call("\n--- Game Over ---") in mock_interface.notify.call_args_list
    assert mocker.call("Final Standings:") in mock_interface.notify.call_args_list
    assert mocker.call("1. P2: 5") in mock_interface.notify.call_args_list
    assert mocker.call("2. P1: 10") in mock_interface.notify.call_args_list
    assert (
        mocker.call("\nWinner: P2 with score 5") in mock_interface.notify.call_args_list
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
