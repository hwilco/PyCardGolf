import pytest

from pycardgolf.core.game import Game
from pycardgolf.core.player import Player
from pycardgolf.core.round import Round
from pycardgolf.interfaces.base import DrawSource, GameInterface
from pycardgolf.utils.card import Card


class MockPlayer(Player):
    def take_turn(self, game_round: Round) -> None:
        _ = game_round

    def choose_initial_card_to_flip(self, game_round: Round) -> int:
        _ = game_round
        return 0

    def _choose_draw_source(self, game_round: Round) -> DrawSource:
        _ = game_round
        return DrawSource.DECK

    def _should_keep_drawn_card(self, card: Card, game_round: Round) -> bool:
        _ = card
        _ = game_round
        return True

    def _choose_card_to_replace(self, new_card: Card, game_round: Round) -> int:
        _ = new_card
        _ = game_round
        return 0

    def _choose_card_to_flip_after_discard(self, game_round: Round) -> int | None:
        _ = game_round
        return None


@pytest.fixture
def mock_player(mock_interface):
    return MockPlayer("P1", mock_interface)


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
    mock_interface.display_round_start.assert_any_call(1)
    mock_interface.display_round_start.assert_any_call(2)
    mock_interface.display_game_over.assert_called_once()


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
    assert game.scores[mock_player] == 12


def test_display_scores(mock_interface):
    p1 = MockPlayer("P1", mock_interface)
    p2 = MockPlayer("P2", mock_interface)

    game = Game([p1, p2], mock_interface)
    game.scores[p1] = 10
    game.scores[p2] = 5

    game.display_scores()

    mock_interface.display_scores.assert_called_once_with({p1: 10, p2: 5})


def test_declare_winner(mock_interface):
    p1 = MockPlayer("P1", mock_interface)
    p2 = MockPlayer("P2", mock_interface)

    game = Game([p1, p2], mock_interface)
    game.scores[p1] = 10
    game.scores[p2] = 5  # Winner (lowest score)

    game.declare_winner()

    mock_interface.display_game_over.assert_called_once()
    mock_interface.display_standings.assert_called_once_with([(p2, 5), (p1, 10)])
    mock_interface.display_winner.assert_called_once_with(p2, 5)


def test_get_standings(game, mock_interface):
    p1 = game.players[0]
    p2 = MockPlayer("P2", mock_interface)
    p3 = MockPlayer("P3", mock_interface)

    game.players = [p1, p2, p3]
    # Initialize scores for new players
    game.scores[p1] = 10
    game.scores[p2] = 5
    game.scores[p3] = 15

    standings = game.get_standings()
    assert standings == [p2, p1, p3]


def test_get_winner(game, mock_interface):
    p1 = game.players[0]
    p2 = MockPlayer("P2", mock_interface)

    game.players = [p1, p2]
    # Initialize scores for new players
    game.scores[p1] = 10
    game.scores[p2] = 5

    assert game.get_winner() == p2
