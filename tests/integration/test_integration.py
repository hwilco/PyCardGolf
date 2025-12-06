from pycardgolf.core.game import Game
from pycardgolf.interfaces.base import GameInterface
from pycardgolf.players.bots.random_bot import RandomBot


def test_full_game_execution(mocker):
    # Setup
    mock_interface = mocker.MagicMock(spec=GameInterface)

    # Create two random bots
    bot1 = RandomBot("Bot 1", mock_interface)
    bot2 = RandomBot("Bot 2", mock_interface)

    players = [bot1, bot2]

    # Initialize game with 2 rounds
    game = Game(players, mock_interface, num_rounds=2)

    # Execute
    game.start()

    # Verification

    # 1. Verify game completed (current_round_num should be 2)
    assert game.current_round_num == 2

    # 2. Verify scores are calculated (should be non-zero usually, but
    # technically could be 0 if lucky)
    # At least check they are integers
    assert isinstance(game.scores[bot1], int)
    assert isinstance(game.scores[bot2], int)

    # 3. Verify interface calls
    # Should have notified start of rounds
    mock_interface.display_round_start.assert_any_call(1)
    mock_interface.display_round_start.assert_any_call(2)

    # Should have declared game over
    mock_interface.display_game_over.assert_called_once()

    # Should have announced a winner
    mock_interface.display_winner.assert_called_once()

    # Verify bots took turns
    # With generic interface calls replaced, we rely on game state changes
    # (score updates, round progression) which are already asserted above.
