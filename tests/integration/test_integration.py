"""Integration tests for a full game execution."""

from unittest.mock import MagicMock

from pycardgolf.core.game import Game
from pycardgolf.interfaces.base import GameRenderer
from pycardgolf.players.bots.random_bot import RandomBot


def test_full_game_execution():
    """A full 2-round bot game should complete and call renderer methods."""
    mock_renderer = MagicMock(spec=GameRenderer)

    bot1 = RandomBot("Bot 1")
    bot2 = RandomBot("Bot 2")

    players = [bot1, bot2]

    game = Game(players, mock_renderer, num_rounds=2)
    game.start()

    # Game should have completed both rounds
    assert game.current_round_num == 2

    # Scores should be integers
    assert isinstance(game.scores[bot1], int)
    assert isinstance(game.scores[bot2], int)

    # Renderer should have been notified at each round start
    mock_renderer.display_round_start.assert_any_call(1)
    mock_renderer.display_round_start.assert_any_call(2)

    # Game over and winner should have been declared
    mock_renderer.display_game_over.assert_called_once()
    mock_renderer.display_winner.assert_called_once()
