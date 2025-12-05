"""Unit tests for the BotPlayer class."""

from unittest.mock import MagicMock

import pytest

from pycardgolf.core.hand import Hand
from pycardgolf.core.round import Round
from pycardgolf.players.bots.bot_player import BotPlayer
from pycardgolf.utils.card import Card, Rank, Suit


class MockBot(BotPlayer):
    """Concrete implementation of BotPlayer for testing."""

    def choose_draw_source(self, game_round: Round) -> str:
        _ = game_round
        return "d"

    def should_keep_drawn_card(self, card: Card, game_round: Round) -> bool:
        _ = card
        _ = game_round
        return True

    def choose_card_to_replace(self, new_card: Card, game_round: Round) -> int:
        _ = new_card
        _ = game_round
        return 0

    def choose_card_to_flip(self, game_round: Round) -> int | None:
        _ = game_round
        return None


@pytest.fixture
def mock_interface():
    return MagicMock()


@pytest.fixture
def bot(mock_interface):
    bot = MockBot("TestBot", mock_interface)
    # Give the bot a hand of cards

    bot.hand = Hand([Card(Rank.TWO, Suit.HEARTS, "red")])
    return bot


@pytest.fixture
def game_round():
    round_mock = MagicMock(spec=Round)
    round_mock.deck = MagicMock()
    round_mock.discard_pile = MagicMock()
    return round_mock


def test_take_turn_draw_from_deck_keep(bot, game_round, mock_interface):
    """Test drawing from deck and keeping the card."""
    # Setup
    drawn_card = Card(Rank.ACE, Suit.SPADES, "red")
    game_round.deck.draw.return_value = drawn_card

    # Configure bot decisions
    bot.choose_draw_source = MagicMock(return_value="d")
    bot.should_keep_drawn_card = MagicMock(return_value=True)
    bot.choose_card_to_replace = MagicMock(return_value=0)

    # Mock Game
    mock_game = MagicMock()
    mock_game.current_round = game_round

    # Execute
    bot.take_turn(mock_game)

    # Verify
    game_round.deck.draw.assert_called_once()
    mock_interface.display_drawn_card.assert_called_with("TestBot", drawn_card)
    mock_interface.display_replace_action.assert_called_once()


def test_take_turn_draw_from_deck_discard(bot, game_round, mock_interface):
    """Test drawing from deck and discarding it."""
    # Setup
    drawn_card = Card(Rank.ACE, Suit.SPADES, "red")
    game_round.deck.draw.return_value = drawn_card

    # Configure bot decisions
    bot.choose_draw_source = MagicMock(return_value="d")
    bot.should_keep_drawn_card = MagicMock(return_value=False)
    bot.choose_card_to_flip = MagicMock(return_value=None)

    # Mock Game
    mock_game = MagicMock()
    mock_game.current_round = game_round

    # Execute
    bot.take_turn(mock_game)

    # Verify
    game_round.deck.draw.assert_called_once()
    game_round.discard_pile.add_card.assert_called_with(drawn_card)
    mock_interface.display_drawn_card.assert_called_with("TestBot", drawn_card)
    mock_interface.display_replace_action.assert_not_called()


def test_take_turn_draw_from_pile(bot, game_round, mock_interface):
    """Test drawing from discard pile."""
    # Setup
    drawn_card = Card(Rank.ACE, Suit.SPADES, "red")
    game_round.discard_pile.draw.return_value = drawn_card

    # Configure bot decisions
    bot.choose_draw_source = MagicMock(return_value="p")
    bot.choose_card_to_replace = MagicMock(return_value=0)

    # Mock Game
    mock_game = MagicMock()
    mock_game.current_round = game_round

    # Execute
    bot.take_turn(mock_game)

    # Verify
    game_round.discard_pile.draw.assert_called_once()
    mock_interface.display_discard_draw.assert_called_with("TestBot", drawn_card)
    mock_interface.display_replace_action.assert_called_once()
