from unittest.mock import MagicMock

import pytest

from pycardgolf.core.round import Round
from pycardgolf.interfaces.base import DrawSource
from pycardgolf.interfaces.null import NullGameInterface
from pycardgolf.players.bots.random_bot import RandomBot
from pycardgolf.utils.card import Card, Rank, Suit
from pycardgolf.utils.constants import HAND_SIZE


@pytest.fixture
def bot():
    # Use a fixed seed for deterministic behavior (reproducibility)
    mock_interface = MagicMock()
    return RandomBot("Bot", mock_interface, seed=42)


@pytest.fixture
def game_round():
    round_mock = MagicMock(spec=Round)
    round_mock.deck = MagicMock()
    round_mock.discard_pile = MagicMock()
    return round_mock


def test_choose_draw_source_deck(bot, game_round):
    """Test choosing draw source when pile is empty."""
    game_round.discard_pile.num_cards = 0
    assert bot._choose_draw_source(game_round) == DrawSource.DECK


def test_choose_draw_source_pile(bot, game_round):
    """Test choosing draw source when pile has cards."""
    game_round.discard_pile.num_cards = 1

    # Run multiple times to ensure stability
    for _ in range(10):
        choice = bot._choose_draw_source(game_round)
        assert choice in {DrawSource.DECK, DrawSource.DISCARD}


def test_should_keep_drawn_card(bot, game_round):
    """Test random decision to keep card."""
    card = Card(Rank.ACE, Suit.SPADES, "red")

    for _ in range(10):
        result = bot._should_keep_drawn_card(card, game_round)
        assert isinstance(result, bool)


def test_choose_card_to_replace(bot, game_round):
    """Test random choice of card to replace."""
    card = Card(Rank.ACE, Suit.SPADES, "red")

    for _ in range(10):
        idx = bot._choose_card_to_replace(card, game_round)
        assert isinstance(idx, int)
        assert 0 <= idx < HAND_SIZE


def test_choose_card_to_flip_after_discard(bot, game_round):
    """Test random choice of card to flip."""
    # Setup hand with some face down cards
    bot.hand = MagicMock()
    c1 = MagicMock()
    c1.face_up = True
    c2 = MagicMock()
    c2.face_up = False
    # Mock iteration and indexing
    bot.hand.__iter__.return_value = [c1, c2]
    # We need to make sure the bot can access the card at the chosen index
    # Since we don't know which index it will pick, we can just mock __getitem__
    bot.hand.__getitem__.return_value = c2

    # Also need to mock len() for the hand if the bot uses it,
    # but RandomBot uses enumerate(self.hand) so __iter__ is key.

    for _ in range(10):
        result = bot._choose_card_to_flip_after_discard(game_round)
        if result is not None:
            assert isinstance(result, int)
            assert 0 <= result < HAND_SIZE


class TestInitialFlip:
    def test_choose_initial_card_to_flip(self, bot):
        """Test that a valid face-down card index is chosen."""
        # Setup real hand for this test
        cards = [Card(Rank.ACE, Suit.SPADES, "blue") for _ in range(6)]
        bot.hand = MagicMock()
        # Make the mocked hand behave like a list
        bot.hand.__iter__.side_effect = lambda: iter(cards)
        bot.hand.__getitem__.side_effect = lambda i: cards[i]

        choice = bot.choose_initial_card_to_flip(None)
        assert 0 <= choice < 6
        assert cards[choice].face_up is False

        # Test that it doesn't choose face-up cards
        # Flip all but index 5
        for i in range(5):
            cards[i].face_up = True

        choice = bot.choose_initial_card_to_flip(None)
        assert choice == 5


def test_init_default_interface():
    """Test initialization with default interface."""
    bot = RandomBot("TestBot")
    assert isinstance(bot.interface, NullGameInterface)


def test_choose_initial_card_to_flip_fallback():
    """Test fallback when no cards are face down (defensive)."""
    bot = RandomBot("TestBot")
    # Manually set a hand with all face-up cards
    cards = [Card(Rank.ACE, Suit.SPADES, "red", face_up=True) for _ in range(6)]
    bot.hand = MagicMock()
    # Need to mock __iter__ to return the cards
    bot.hand.__iter__.side_effect = lambda: iter(cards)

    # Mock game_round (unused in method but required by signature)
    mock_round = MagicMock(spec=Round)

    # Should return 0 as fallback
    assert bot.choose_initial_card_to_flip(mock_round) == 0
