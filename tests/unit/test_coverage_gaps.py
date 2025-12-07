"""Tests to fill specific coverage gaps."""

from unittest.mock import Mock

import pytest

from pycardgolf.core.game import Game
from pycardgolf.core.hand import Hand
from pycardgolf.core.player import Player
from pycardgolf.core.round import Round
from pycardgolf.exceptions import GameConfigError
from pycardgolf.interfaces.base import DrawSource, FlipChoice
from pycardgolf.interfaces.null import NullGameInterface
from pycardgolf.players.bots.random_bot import RandomBot
from pycardgolf.players.human import HumanPlayer
from pycardgolf.utils.card import Card, Rank, Suit
from pycardgolf.utils.deck import Deck


class TestRandomBotCoverage:
    """Coverage tests for RandomBot."""

    def test_init_default_interface(self):
        """Test initialization with default interface."""
        bot = RandomBot("TestBot")
        assert isinstance(bot.interface, NullGameInterface)

    def test_choose_initial_card_to_flip_fallback(self):
        """Test fallback when no cards are face down (defensive)."""
        bot = RandomBot("TestBot")
        # Manually set a hand with all face-up cards
        cards = [Card(Rank.ACE, Suit.SPADES, "red", face_up=True) for _ in range(6)]
        bot.hand = Hand(cards)

        # Mock game_round (unused in method but required by signature)
        mock_round = Mock(spec=Round)

        # Should return 0 as fallback
        assert bot.choose_initial_card_to_flip(mock_round) == 0


class TestHumanPlayerCoverage:
    """Coverage tests for HumanPlayer."""

    def test_choose_card_to_flip_after_discard_no(self):
        """Test choosing NOT to flip a card after discard."""
        interface = Mock()
        player = HumanPlayer("TestHuman", interface)

        # Determine behavior: FlipChoice.NO
        interface.get_flip_choice.return_value = FlipChoice.NO

        mock_round = Mock(spec=Round)

        result = player._choose_card_to_flip_after_discard(mock_round)
        assert result is None

        # Verify get_valid_flip_index was NOT called
        interface.get_valid_flip_index.assert_not_called()


class TestDeckCoverage:
    """Coverage tests for Deck."""

    def test_add_card_wrong_color(self):
        """Test error when adding card with mismatching back color."""
        deck = Deck(back_color="red")
        # Remove a card so we can theoretically add one
        _ = deck.draw()

        blue_card = Card(Rank.ACE, Suit.SPADES, back_color="blue")

        with pytest.raises(ValueError, match="does not match"):
            deck.add_card(blue_card)

    def test_add_card_duplicate(self):
        """Test error when adding a duplicate card."""
        deck = Deck(back_color="red")
        # Peek top card
        top_card = deck.peek()

        with pytest.raises(ValueError, match="duplicate"):
            deck.add_card(top_card)

    def test_add_card_success(self):
        """Test successfully adding a valid card to the deck."""
        deck = Deck(back_color="red")
        # Draw a card to make space (and have a valid card to add back)
        card = deck.draw()

        # Verify card is gone
        assert card not in deck.cards

        # Add it back
        deck.add_card(card)

        # Verify it's back
        assert card in deck.cards
        assert deck.peek() == card


class TestPlayerCoverage:
    """Coverage tests for abstract Player logic via a concrete subclass."""

    class ConcretePlayer(Player):
        def _choose_draw_source(self, game_round):
            return DrawSource.DECK  # Default return

        def _should_keep_drawn_card(self, card, game_round):
            return True

        def _choose_card_to_replace(self, new_card, game_round):
            return 0

        def _choose_card_to_flip_after_discard(self, game_round):
            return None

        def choose_initial_card_to_flip(self, game_round):
            return 0

    def test_take_turn_no_round(self):
        """Test error when taking turn with no current round."""
        player = self.ConcretePlayer("Test", NullGameInterface())
        game = Mock(spec=Game)
        game.current_round = None

        with pytest.raises(GameConfigError, match="Game round is None"):
            player.take_turn(game)

    def test_take_turn_invalid_draw_source(self):
        """Test error when draw source is invalid."""
        player = self.ConcretePlayer("Test", NullGameInterface())

        # Override _choose_draw_source to return invalid value
        player._choose_draw_source = Mock(return_value="INVALID")

        game = Mock(spec=Game)
        mock_round = Mock(spec=Round)
        game.current_round = mock_round

        # Mock display_turn_start
        player.interface.display_turn_start = Mock()

        with pytest.raises(GameConfigError, match="Invalid draw source"):
            player.take_turn(game)
