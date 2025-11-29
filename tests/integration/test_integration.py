import pytest
from unittest.mock import MagicMock, call
from pycardgolf.core.game import Game
from pycardgolf.players.bots.random_bot import RandomBot
from pycardgolf.interfaces.base import GameInterface

@pytest.mark.integration
def test_full_game_execution():
    # Setup
    mock_interface = MagicMock(spec=GameInterface)
    
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
    
    # 2. Verify scores are calculated (should be non-zero usually, but technically could be 0 if lucky)
    # At least check they are integers
    assert isinstance(bot1.score, int)
    assert isinstance(bot2.score, int)
    
    # 3. Verify interface calls
    # Should have notified start of rounds
    assert call("--- Starting Round 1 ---") in mock_interface.notify.call_args_list
    assert call("--- Starting Round 2 ---") in mock_interface.notify.call_args_list
    
    # Should have declared game over
    assert call("\n--- Game Over ---") in mock_interface.notify.call_args_list
    
    # Should have announced a winner
    # We don't know who won, but we know the format
    winner_calls = [c for c in mock_interface.notify.call_args_list if "Winner:" in str(c)]
    assert len(winner_calls) == 1
    
    # Verify bots took turns (interface should have received notifications from bots)
    bot_actions = [c for c in mock_interface.notify.call_args_list if "Bot" in str(c)]
    assert len(bot_actions) > 0
