"""Tests for the abstract Player class."""

from unittest.mock import MagicMock, Mock

import pytest

from pycardgolf.core.game import Game
from pycardgolf.core.hand import Hand
from pycardgolf.core.round import Round
from pycardgolf.exceptions import GameConfigError
from pycardgolf.interfaces.base import DrawSource, GameInterface
from pycardgolf.players.player import Player
from pycardgolf.utils.card import Card, Rank, Suit


class TestPlayerCoverage:
    """Coverage tests for abstract Player logic via a concrete subclass."""

    class ConcretePlayer(Player):
        """Concrete implementation of Player for testing abstract base class logic."""

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

    @pytest.fixture
    def interface(self):
        return Mock(spec=GameInterface)

    @pytest.fixture
    def player(self, interface):
        return self.ConcretePlayer("TestPlayer", interface)

    @pytest.fixture
    def mock_game(self):
        game = Mock(spec=Game)
        game.current_round = Mock(spec=Round)
        game.current_round.deck = Mock()
        game.current_round.discard_pile = Mock()
        return game

    @pytest.fixture
    def mock_round(self, mock_game):
        return mock_game.current_round

    def test_init(self, interface):
        """Test initialization sets name, empty hand, and interface."""
        p = self.ConcretePlayer("Bob", interface)
        assert p.name == "Bob"
        assert isinstance(p.hand, Hand)
        assert len(p.hand) == 0
        assert p.interface == interface

    def test_repr(self, player):
        """Test string representation."""
        player.hand = Hand([Card(Rank.ACE, Suit.SPADES, "red")])
        assert "TestPlayer" in repr(player)
        assert "ACE" in repr(player)

    def test_take_turn_no_round(self, player, mock_game):
        """Test error when taking turn with no current round."""
        mock_game.current_round = None

        with pytest.raises(GameConfigError, match="Game round is None"):
            player.take_turn(mock_game)

    def test_take_turn_invalid_draw_source(self, player, mock_game):
        """Test error when draw source is invalid."""
        # Override _choose_draw_source to return invalid value
        player._choose_draw_source = Mock(return_value="INVALID")

        with pytest.raises(GameConfigError, match="Invalid draw source"):
            player.take_turn(mock_game)

        # Verify display_turn_start was called before error
        player.interface.display_turn_start.assert_called_once_with(player)

    def test_take_turn_discard_pile_draw(self, player, mock_game, mock_round):
        """Test taking a turn: draw from discard pile."""
        # Setup decision
        player._choose_draw_source = Mock(return_value=DrawSource.DISCARD)
        player._choose_card_to_replace = Mock(return_value=1)

        # Setup pile card
        pile_card = Card(Rank.KING, Suit.HEARTS, "red")
        mock_round.discard_pile.draw.return_value = pile_card

        # Setup player hand with mock replace
        player.hand = MagicMock()
        old_card = Card(Rank.TWO, Suit.CLUBS, "red")
        player.hand.replace.return_value = old_card

        player.take_turn(mock_game)

        # 1. Verify draw source decision
        player._choose_draw_source.assert_called_once_with(mock_round)

        # 2. Verify draw from discard pile
        mock_round.discard_pile.draw.assert_called_once()
        player.interface.display_discard_draw.assert_called_once_with(player, pile_card)

        # 3. Verify replace decision
        player._choose_card_to_replace.assert_called_once_with(pile_card, mock_round)

        # 4. Verify replace execution (_replace_card)
        player.hand.replace.assert_called_once_with(1, pile_card)
        assert old_card.face_up is True
        mock_round.discard_pile.add_card.assert_called_once_with(old_card)
        player.interface.display_replace_action.assert_called_once_with(
            player, 1, pile_card, old_card
        )

    def test_take_turn_deck_draw_keep(self, player, mock_game, mock_round):
        """Test taking a turn: draw from deck and keep it."""
        # Setup decisions
        player._choose_draw_source = Mock(return_value=DrawSource.DECK)
        player._should_keep_drawn_card = Mock(return_value=True)
        player._choose_card_to_replace = Mock(return_value=0)

        # Setup deck card
        drawn_card = Card(Rank.ACE, Suit.SPADES, "red")
        mock_round.deck.draw.return_value = drawn_card

        # Setup player hand
        player.hand = MagicMock()
        old_card = Card(Rank.FIVE, Suit.DIAMONDS, "red")
        player.hand.replace.return_value = old_card

        player.take_turn(mock_game)

        # 1. Verify draw from deck
        mock_round.deck.draw.assert_called_once()
        assert drawn_card.face_up is True  # Should be set to visible
        player.interface.display_drawn_card.assert_called_once_with(player, drawn_card)

        # 2. Verify keep decision
        player._should_keep_drawn_card.assert_called_once_with(drawn_card, mock_round)

        # 3. Verify replace execution
        player.hand.replace.assert_called_once_with(0, drawn_card)
        mock_round.discard_pile.add_card.assert_called_once_with(old_card)
        player.interface.display_replace_action.assert_called_once_with(
            player, 0, drawn_card, old_card
        )

    def test_take_turn_deck_draw_discard_no_flip(self, player, mock_game, mock_round):
        """Test taking a turn: draw from deck, discard it, and choose NOT to flip."""
        # Setup decisions
        player._choose_draw_source = Mock(return_value=DrawSource.DECK)
        player._should_keep_drawn_card = Mock(return_value=False)
        player._choose_card_to_flip_after_discard = Mock(return_value=None)

        # Setup deck card
        drawn_card = Card(Rank.SEVEN, Suit.CLUBS, "red")
        mock_round.deck.draw.return_value = drawn_card

        # Setup hand
        player.hand = MagicMock()

        player.take_turn(mock_game)

        # 1. Verify discard
        mock_round.discard_pile.add_card.assert_called_once_with(drawn_card)
        player.interface.display_discard_action.assert_called_once_with(
            player, drawn_card
        )

        # 2. Verify flip decision
        player._choose_card_to_flip_after_discard.assert_called_once_with(mock_round)

        # 3. Verify no flip happened
        player.hand.flip_card.assert_not_called()
        player.interface.display_flip_action.assert_not_called()

    def test_take_turn_deck_draw_discard_with_flip(self, player, mock_game, mock_round):
        """Test taking a turn: draw from deck, discard it, and choose TO flip."""
        # Setup decisions
        player._choose_draw_source = Mock(return_value=DrawSource.DECK)
        player._should_keep_drawn_card = Mock(return_value=False)
        player._choose_card_to_flip_after_discard = Mock(return_value=2)

        # Setup deck card
        drawn_card = Card(Rank.EIGHT, Suit.DIAMONDS, "red")
        mock_round.deck.draw.return_value = drawn_card

        # Setup hand
        player.hand = MagicMock()
        # Mocking __getitem__ for the display call: `self.hand[flip_idx]`
        flipped_card = Card(Rank.QUEEN, Suit.HEARTS, "red")
        player.hand.__getitem__.return_value = flipped_card

        player.take_turn(mock_game)

        # 1. Verify flip execution
        player.hand.flip_card.assert_called_once_with(2)
        player.interface.display_flip_action.assert_called_once_with(
            player, 2, flipped_card
        )
