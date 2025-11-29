import pytest
from unittest.mock import MagicMock
from pycardgolf.core.round import Round
from pycardgolf.core.player import Player
from pycardgolf.utils.enums import Rank, Suit
from pycardgolf.utils.card import Card

class MockPlayer(Player):
    def take_turn(self, game_round: Round) -> None:
        pass

def test_round_setup():
    p1 = MockPlayer("P1")
    p2 = MockPlayer("P2")
    game_round = Round([p1, p2])
    game_round.setup()

    assert len(p1.hand) == 6
    assert len(p2.hand) == 6
    # Check 2 cards are face up
    assert sum(1 for c in p1.hand if c.face_up) == 2
    assert sum(1 for c in p2.hand if c.face_up) == 2
    
    assert game_round.discard_pile.num_cards == 1
    assert game_round.discard_pile.peek().face_up

def test_check_round_end_condition():
    p1 = MockPlayer("P1")
    game_round = Round([p1])
    # Give p1 a hand
    p1.hand = [Card(Rank.ACE, Suit.CLUBS, "blue") for _ in range(6)]
    
    # All face down
    for c in p1.hand:
        c.face_up = False
    assert not game_round.check_round_end_condition(p1)
    
    # All face up
    for c in p1.hand:
        c.face_up = True
    assert game_round.check_round_end_condition(p1)

def test_calculate_scores_flips_all():
    p1 = MockPlayer("P1")
    game_round = Round([p1])
    p1.hand = [Card(Rank.ACE, Suit.CLUBS, "blue") for _ in range(6)]
    for c in p1.hand:
        c.face_up = False
        
    game_round.calculate_scores()
    
    assert all(c.face_up for c in p1.hand)
    # Score for 6 Aces (3 pairs) = 0
    assert p1.score == 0

def test_advance_turn():
    # Test normal turn advancement
    p1 = MockPlayer("P1")
    p2 = MockPlayer("P2")
    p3 = MockPlayer("P3")
    game_round = Round([p1, p2, p3])
    
    assert game_round.current_player_idx == 0
    game_round.advance_turn()
    assert game_round.current_player_idx == 1
    game_round.advance_turn()
    assert game_round.current_player_idx == 2

def test_advance_turn_wraps_around():
    # Test that turn wraps to 0 after last player
    p1 = MockPlayer("P1")
    p2 = MockPlayer("P2")
    game_round = Round([p1, p2])
    
    game_round.current_player_idx = 1
    game_round.advance_turn()
    assert game_round.current_player_idx == 0
    assert not game_round.round_over

def test_advance_turn_ends_round():
    # Test that round ends when we return to last_turn_player_idx
    p1 = MockPlayer("P1")
    p2 = MockPlayer("P2")
    p3 = MockPlayer("P3")
    game_round = Round([p1, p2, p3])
    
    # Set player 1 as the one who ended the round
    game_round.last_turn_player_idx = 1
    game_round.current_player_idx = 0
    
    # Advance from 0 to 1 - should end the round
    game_round.advance_turn()
    assert game_round.current_player_idx == 1
    assert game_round.round_over
