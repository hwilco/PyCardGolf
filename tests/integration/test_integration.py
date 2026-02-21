"""Integration tests for a full game execution."""

from pycardgolf.core.event_bus import EventBus
from pycardgolf.core.game import Game
from pycardgolf.players.bots.random_bot import RandomBot


def test_full_game_execution():
    """A full 2-round bot game should complete and call renderer methods."""
    event_bus = EventBus()

    bot1 = RandomBot("Bot 1")
    bot2 = RandomBot("Bot 2")

    players = [bot1, bot2]

    game = Game(players, event_bus, num_rounds=2)
    game.start()

    # Game should have completed both rounds
    assert game.current_round_num == 2

    # Scores should be integers
    assert isinstance(game.scores[bot1], int)
    assert isinstance(game.scores[bot2], int)
