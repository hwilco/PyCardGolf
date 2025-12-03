import pytest

from pycardgolf.core.hand import Hand
from pycardgolf.core.player import Player
from pycardgolf.core.round import Round
from pycardgolf.exceptions import GameConfigError
from pycardgolf.utils.card import Card
from pycardgolf.utils.constants import HAND_SIZE
from pycardgolf.utils.enums import Rank, Suit


class MockPlayer(Player):
    def take_turn(self, game_round: Round) -> None:
        pass


def test_round_setup():
    p1 = MockPlayer("P1")
    p2 = MockPlayer("P2")
    game_round = Round([p1, p2])
    game_round.setup()

    assert len(p1.hand) == HAND_SIZE
    assert len(p2.hand) == HAND_SIZE
    # Check 2 cards are face up
    assert sum(1 for c in p1.hand if c.face_up) == 2
    assert sum(1 for c in p2.hand if c.face_up) == 2

    assert game_round.discard_pile.num_cards == 1
    assert game_round.discard_pile.peek().face_up


@pytest.mark.parametrize(
    ("num_players", "hand_size", "deck_cards"),
    [
        # 3 players * 6 cards = 18 needed, 18 available - not enough (no discard)
        pytest.param(3, 6, 18, id="exact_no_discard"),
        # 4 players * 6 cards = 24 needed, 18 available - way not enough
        pytest.param(4, 6, 18, id="six_cards_short"),
    ],
)
def test_round_init_too_many_players(num_players, hand_size, deck_cards, mocker):
    """Test that GameConfigError is raised when not enough cards for players."""
    # Mock HAND_SIZE constant
    mocker.patch("pycardgolf.core.round.HAND_SIZE", hand_size)

    # Create players
    players = [MockPlayer(f"P{i}") for i in range(num_players)]

    # Mock the Deck class to have the specified number of cards
    mock_deck = mocker.MagicMock()
    mock_deck.num_cards = deck_cards
    mocker.patch("pycardgolf.core.round.Deck", return_value=mock_deck)

    # Creating Round should raise GameConfigError
    with pytest.raises(GameConfigError, match="Not enough cards for players"):
        Round(players)


def test_check_round_end_condition():
    p1 = MockPlayer("P1")
    game_round = Round([p1])
    # Give p1 a hand
    cards = [Card(Rank.ACE, Suit.CLUBS, "blue") for _ in range(HAND_SIZE)]
    p1.hand = Hand(cards)

    # All face down
    for c in p1.hand:
        c.face_up = False
    assert not game_round.check_round_end_condition(p1)

    # All face up
    for c in p1.hand:
        c.face_up = True
    assert game_round.check_round_end_condition(p1)


def test_get_scores_requires_face_up():
    p1 = MockPlayer("P1")
    game_round = Round([p1])
    cards = [Card(Rank.ACE, Suit.CLUBS, "blue") for _ in range(HAND_SIZE)]
    p1.hand = Hand(cards)
    for c in p1.hand:
        c.face_up = False

    # Should raise ValueError because cards are not face up
    with pytest.raises(ValueError, match="All cards must be face up"):
        game_round.get_scores()


def test_reveal_hands():
    p1 = MockPlayer("P1")
    p2 = MockPlayer("P2")
    game_round = Round([p1, p2])
    cards = [Card(Rank.ACE, Suit.CLUBS, "blue") for _ in range(HAND_SIZE)]
    p1.hand = Hand(cards)
    p2.hand = Hand(cards)
    for c in p1.hand:
        c.face_up = False
    for c in p2.hand:
        c.face_up = False

    game_round.reveal_hands()
    assert all(c.face_up for c in p1.hand)
    assert all(c.face_up for c in p2.hand)


def test_get_scores_returns_correct_scores():
    p1 = MockPlayer("P1")
    p2 = MockPlayer("P2")
    game_round = Round([p1, p2])
    cards_p1 = [Card(Rank.ACE, Suit.CLUBS, "blue") for _ in range(HAND_SIZE)]
    cards_p2 = [Card(Rank.THREE, Suit.CLUBS, "blue") for _ in range(HAND_SIZE // 2)]
    cards_p2.extend(
        [Card(Rank.KING, Suit.CLUBS, "blue") for _ in range(HAND_SIZE // 2)]
    )
    p1.hand = Hand(cards_p1)
    p2.hand = Hand(cards_p2)
    game_round.reveal_hands()

    scores = game_round.get_scores()

    # Score for 6 Aces (3 pairs) = 0
    assert scores[p1] == 0
    # Score for half 3s and half Kings = 3 * HAND_SIZE // 2 (6 for 6 cards)
    assert scores[p2] == (HAND_SIZE // 2) * 3
    # Player score should NOT be updated by Round
    assert p1.score == 0
    assert p2.score == 0


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
