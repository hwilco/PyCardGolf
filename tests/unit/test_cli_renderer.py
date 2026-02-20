"""Tests for the CLI renderer."""

import io

import pytest
from rich.console import Console
from rich.text import Text

from pycardgolf.core.hand import Hand
from pycardgolf.core.round import Round
from pycardgolf.core.stats import PlayerStats
from pycardgolf.exceptions import GameConfigError
from pycardgolf.interfaces.cli_renderer import CLIRenderer
from pycardgolf.players.player import BasePlayer
from pycardgolf.utils.card import Card, Rank, Suit
from pycardgolf.utils.deck import CardStack, Deck


@pytest.fixture
def captured_renderer():
    """Create a renderer that captures output to a string buffer."""
    string_io = io.StringIO()
    console = Console(file=string_io, force_terminal=False)
    renderer = CLIRenderer(console)
    return renderer, string_io


@pytest.fixture
def sample_card():
    """Create a sample card for testing."""
    return Card(Rank.ACE, Suit.SPADES, "red", face_up=True)


@pytest.fixture
def sample_face_down_card():
    """Create a sample face-down card for testing."""
    return Card(Rank.KING, Suit.HEARTS, "blue", face_up=False)


@pytest.fixture
def sample_hand_cards():
    """Create a list of cards for a hand."""
    return [
        Card(Rank.ACE, Suit.SPADES, "red", face_up=True),
        Card(Rank.TWO, Suit.HEARTS, "red", face_up=True),
        Card(Rank.THREE, Suit.CLUBS, "red", face_up=False),
        Card(Rank.FOUR, Suit.DIAMONDS, "red", face_up=True),
        Card(Rank.FIVE, Suit.SPADES, "red", face_up=False),
        Card(Rank.SIX, Suit.HEARTS, "red", face_up=True),
    ]


@pytest.fixture
def mock_player(sample_hand_cards, mocker):
    """Create a mock player with a hand."""
    player = mocker.Mock(spec=BasePlayer)
    player.name = "TestPlayer"
    player.hand = Hand(sample_hand_cards)
    return player


@pytest.fixture
def mock_round(mock_player, mocker):
    """Create a fully populated mock round."""
    game_round = mocker.Mock(spec=Round)
    game_round.turn_count = 5

    # Mock deck
    deck = mocker.Mock(spec=Deck)
    deck.num_cards = 40
    top_deck_card = Card(Rank.KING, Suit.HEARTS, "red", face_up=False)
    deck.peek.return_value = top_deck_card
    game_round.deck = deck

    # Mock discard pile
    discard = mocker.Mock(spec=CardStack)
    discard_card = Card(Rank.FIVE, Suit.CLUBS, "red", face_up=True)
    discard.peek.return_value = discard_card
    game_round.discard_pile = discard

    # Mock players - create a list of players
    game_round.players = [mock_player]
    game_round.current_player_idx = 0

    return game_round


class TestCardDisplay:
    """Tests for card display functionality."""

    def test_get_card_string_face_up(self, captured_renderer, sample_card):
        """Test that face-up cards are displayed correctly."""
        renderer, _ = captured_renderer
        card_text = renderer.get_card_string(sample_card)
        assert isinstance(card_text, Text)
        assert "A♤" in str(card_text)

    def test_get_card_string_face_down(self, captured_renderer, sample_face_down_card):
        """Test that face-down cards show ?? with back color."""
        renderer, _ = captured_renderer
        card_text = renderer.get_card_string(sample_face_down_card)
        assert isinstance(card_text, Text)
        assert "??" in str(card_text)


class TestRendererDisplay:
    """Tests for display methods using captured output."""

    def test_display_drawn_card(self, captured_renderer, sample_card, mock_player):
        """Test displaying a drawn card."""
        renderer, output = captured_renderer
        renderer.display_drawn_card(mock_player, sample_card)
        assert "TestPlayer drew:" in output.getvalue()
        assert "A♤" in output.getvalue()

    def test_display_discard_draw(self, captured_renderer, sample_card, mock_player):
        """Test displaying a discard pile draw."""
        renderer, output = captured_renderer
        renderer.display_discard_draw(mock_player, sample_card)
        assert "TestPlayer drew" in output.getvalue()
        assert "A♤" in output.getvalue()

    def test_display_replace_action(self, captured_renderer, mock_player):
        """Test displaying a replace action."""
        renderer, output = captured_renderer
        new_card = Card(Rank.ACE, Suit.SPADES, "red", face_up=True)
        old_card = Card(Rank.TWO, Suit.HEARTS, "red", face_up=True)

        renderer.display_replace_action(mock_player, 2, new_card, old_card)

        result = output.getvalue()
        assert "TestPlayer replaced card" in result
        assert "A♤" in result
        assert "2♡" in result

    def test_display_flip_action(self, captured_renderer, sample_card, mock_player):
        """Test displaying a flip action."""
        renderer, output = captured_renderer
        renderer.display_flip_action(mock_player, 1, sample_card)

        result = output.getvalue()
        assert "TestPlayer flipped card" in result
        assert "A♤" in result

    def test_display_error(self, captured_renderer):
        """Test display_error method."""
        renderer, output = captured_renderer
        renderer.display_error("Test error")
        assert "Test error" in output.getvalue()
        assert "[ERROR]" in output.getvalue()

    def test_display_hand_output(self, captured_renderer, mock_player):
        """Test that display_hand produces output with borders."""
        renderer, output = captured_renderer
        renderer.display_hand(mock_player, display_indices=True)

        result = output.getvalue()
        assert "+" in result
        assert "|" in result
        # Should contain indices since display_indices=True
        assert "1" in result

    def test_display_hand_without_indices(self, captured_renderer, mock_player):
        """Test display_hand without indices."""
        renderer, output = captured_renderer
        renderer.display_hand(mock_player, display_indices=False)

        result = output.getvalue()
        assert "+" in result
        assert "|" in result

    def test_display_state(self, captured_renderer, mock_round, mocker):
        """Test display_state method covers the game state display."""
        renderer, output = captured_renderer
        mock_game = mocker.Mock()
        mock_game.current_round = mock_round
        mock_game.players = mock_round.players

        renderer.display_state(mock_game)

        result = output.getvalue()
        assert "5" in result  # Turn count
        assert "40" in result  # Deck count
        assert "Player: TestPlayer" in result

    def test_display_state_no_round(self, captured_renderer, mocker):
        """Test display_state raises error if round is missing."""
        renderer, _ = captured_renderer
        mock_game = mocker.Mock()
        mock_game.current_round = None

        with pytest.raises(GameConfigError):
            renderer.display_state(mock_game)

    def test_display_discard_pile(self, captured_renderer, mocker):
        """Test _display_discard_pile method."""
        renderer, output = captured_renderer

        # Create mock Round object with discard pile
        game_round = mocker.Mock(spec=Round)
        discard = mocker.Mock(spec=CardStack)
        discard_card = Card(Rank.QUEEN, Suit.DIAMONDS, "red", face_up=True)
        discard.peek.return_value = discard_card
        game_round.discard_pile = discard

        renderer._display_discard_pile(game_round)

        result = output.getvalue()
        assert "Discard Pile Top Card:" in result
        assert "Q♢" in result

    def test_display_game_stats(self, captured_renderer, mock_player):
        """Test display_game_stats method formatting."""
        renderer, output = captured_renderer

        player_stats = PlayerStats(round_scores=[])
        player_stats.best_score = 42
        player_stats.worst_score = 99
        player_stats.average_score = 12.3456
        player_stats.total_score = 1000
        player_stats.round_scores = [1, 99]

        stats = {mock_player: player_stats}
        renderer.display_game_stats(stats)

        result = output.getvalue()
        assert "Game Statistics:" in result
        assert "TestPlayer" in result
        assert "Best Score: 42" in result
        assert "Worst Score: 99" in result
        assert "Average Score: 12.35" in result
        assert "Total Score: 1000" in result
        assert "Round Scores: 1, 99" in result


class TestColorValidation:
    """Tests for color validation."""

    @pytest.mark.parametrize(
        "valid_color",
        [
            pytest.param("red", id="simple_color"),
            pytest.param("blue", id="another_color"),
            pytest.param("green", id="third_color"),
            pytest.param("#FF0000", id="hex_color"),
            pytest.param("rgb(255,0,0)", id="rgb_color"),
        ],
    )
    def test_validate_color_valid(self, captured_renderer, valid_color):
        """Test that valid colors pass validation."""
        renderer, _ = captured_renderer
        renderer.validate_color(valid_color)

    def test_validate_color_invalid(self, captured_renderer):
        """Test that invalid colors raise GameConfigError."""
        renderer, _ = captured_renderer
        with pytest.raises(GameConfigError, match="Invalid color"):
            renderer.validate_color("notacolorstring")
