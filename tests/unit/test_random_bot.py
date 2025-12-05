"""Unit tests for the RandomBot class."""

from unittest.mock import MagicMock

import pytest

from pycardgolf.core.round import Round
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
    assert bot.choose_draw_source(game_round) == "d"


def test_choose_draw_source_pile(bot, game_round):
    """Test choosing draw source when pile has cards."""
    game_round.discard_pile.num_cards = 1

    # Run multiple times to ensure stability
    for _ in range(10):
        choice = bot.choose_draw_source(game_round)
        assert choice in {"d", "p"}


def test_should_keep_drawn_card(bot, game_round):
    """Test random decision to keep card."""
    card = Card(Rank.ACE, Suit.SPADES, "red")

    for _ in range(10):
        result = bot.should_keep_drawn_card(card, game_round)
        assert isinstance(result, bool)


def test_choose_card_to_replace(bot, game_round):
    """Test random choice of card to replace."""
    card = Card(Rank.ACE, Suit.SPADES, "red")

    for _ in range(10):
        idx = bot.choose_card_to_replace(card, game_round)
        assert isinstance(idx, int)
        assert 0 <= idx < HAND_SIZE


def test_choose_card_to_flip(bot, game_round):
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
        result = bot.choose_card_to_flip(game_round)
        if result is not None:
            assert isinstance(result, int)
            assert 0 <= result < HAND_SIZE
