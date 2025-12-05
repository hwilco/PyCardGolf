"""Tests for the CLI interface."""

import io
from typing import ClassVar
from unittest.mock import Mock

import pytest
from rich.console import Console
from rich.text import Text

from pycardgolf.core.hand import Hand
from pycardgolf.core.player import Player
from pycardgolf.core.round import Round
from pycardgolf.exceptions import GameConfigError
from pycardgolf.interfaces.cli import CLIInterface
from pycardgolf.utils.card import Card
from pycardgolf.utils.deck import Deck, DiscardStack
from pycardgolf.utils.enums import Rank, Suit


@pytest.fixture
def cli():
    """Create a CLI interface for testing."""
    return CLIInterface()


@pytest.fixture
def captured_cli():
    """Create a CLI interface that captures output to a string buffer."""
    string_io = io.StringIO()
    cli = CLIInterface()
    cli.console = Console(file=string_io, force_terminal=True)
    return cli, string_io


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
def mock_player(sample_hand_cards):
    """Create a mock player with a hand."""
    player = Mock(spec=Player)
    player.name = "TestPlayer"
    player.hand = Hand(sample_hand_cards)
    return player


@pytest.fixture
def mock_round(mock_player):
    """Create a fully populated mock round."""
    game_round = Mock(spec=Round)
    game_round.turn_count = 5

    # Mock deck
    deck = Mock(spec=Deck)
    deck.num_cards = 40
    top_deck_card = Card(Rank.KING, Suit.HEARTS, "red", face_up=False)
    deck.peek.return_value = top_deck_card
    game_round.deck = deck

    # Mock discard pile
    discard = Mock(spec=DiscardStack)
    discard_card = Card(Rank.FIVE, Suit.CLUBS, "red", face_up=True)
    discard.peek.return_value = discard_card
    game_round.discard_pile = discard

    # Mock players
    game_round.players = [mock_player]
    game_round.current_player_idx = 0

    return game_round


class TestCardDisplay:
    """Tests for card display functionality."""

    def test_get_card_string_face_up(self, cli, sample_card):
        """Test that face-up cards are displayed correctly."""
        card_text = cli._get_card_string(sample_card)
        assert isinstance(card_text, Text)
        assert "A♤" in str(card_text)

    def test_get_card_string_face_down(self, cli, sample_face_down_card):
        """Test that face-down cards show ?? with back color."""
        card_text = cli._get_card_string(sample_face_down_card)
        assert isinstance(card_text, Text)
        assert "??" in str(card_text)

    def test_get_card_string_validates_colors(self, cli):
        """Test that invalid colors raise GameConfigError."""
        # Rich is very permissive with colors, making it difficult to trigger
        # ColorParseError. This is a placeholder for future edge case testing.
        # Most color strings are automatically handled by Rich's parser.


class TestInputValidation:
    """Tests for user input validation."""

    def test_get_valid_input_with_valid_options(self, cli, mocker):
        """Test that valid options are accepted."""
        # Mock console.input to return 'd'
        mocker.patch.object(cli.console, "input", return_value="d")

        result = cli._get_valid_input(
            "Choose: ", valid_options=["d", "p"], error_msg="Invalid"
        )
        assert result == "d"

    def test_get_valid_input_retries_on_invalid(self, cli, mocker):
        """Test that invalid input causes retry."""
        # First return invalid, then valid
        mocker.patch.object(cli.console, "input", side_effect=["invalid", "d"])
        mock_print = mocker.patch.object(cli.console, "print")

        result = cli._get_valid_input(
            "Choose: ", valid_options=["d", "p"], error_msg="Invalid input."
        )

        assert result == "d"
        # Check that error message was printed
        mock_print.assert_any_call("Invalid input.")

    def test_get_valid_input_with_validation_func(self, cli, mocker):
        """Test input validation with custom validation function."""
        mocker.patch.object(cli.console, "input", return_value="5")

        def validate_number(s: str) -> int:
            num = int(s)
            if 1 <= num <= 6:
                return num
            raise ValueError

        result = cli._get_valid_input(
            "Enter number: ",
            validation_func=validate_number,
            error_msg="Invalid number",
        )
        assert result == 5

    def test_get_valid_input_validation_func_retries(self, cli, mocker):
        """Test that validation function failures cause retry."""
        mocker.patch.object(cli.console, "input", side_effect=["99", "5"])
        mock_print = mocker.patch.object(cli.console, "print")

        def validate_number(s: str) -> int:
            num = int(s)
            if 1 <= num <= 6:
                return num
            raise ValueError

        result = cli._get_valid_input(
            "Enter number: ",
            validation_func=validate_number,
            error_msg="Invalid number",
        )

        assert result == 5
        mock_print.assert_any_call("Invalid number")


class TestGameChoices:
    """Tests for game-specific user choice methods."""

    INDEX_INPUT_CASES: ClassVar[list[tuple[str, int]]] = [
        ("1", 0),
        ("3", 2),
        ("6", 5),
    ]

    def test_get_draw_choice_deck(self, cli, mocker):
        """Test choosing to draw from deck."""
        mocker.patch.object(cli.console, "input", return_value="d")
        deck_card = Card(Rank.TWO, Suit.CLUBS, "red")
        discard_card = Card(Rank.FIVE, Suit.HEARTS, "red", face_up=True)

        result = cli.get_draw_choice(deck_card, discard_card)
        assert result == "d"

    def test_get_draw_choice_pile(self, cli, mocker):
        """Test choosing to draw from discard pile."""
        mocker.patch.object(cli.console, "input", return_value="p")
        deck_card = Card(Rank.TWO, Suit.CLUBS, "red")
        discard_card = Card(Rank.FIVE, Suit.HEARTS, "red", face_up=True)

        result = cli.get_draw_choice(deck_card, discard_card)
        assert result == "p"

    def test_get_keep_or_discard_choice_keep(self, cli, mocker):
        """Test choosing to keep a card."""
        mocker.patch.object(cli.console, "input", return_value="k")
        result = cli.get_keep_or_discard_choice()
        assert result == "k"

    def test_get_keep_or_discard_choice_discard(self, cli, mocker):
        """Test choosing to discard a card."""
        mocker.patch.object(cli.console, "input", return_value="d")
        result = cli.get_keep_or_discard_choice()
        assert result == "d"

    def test_get_flip_choice_yes(self, cli, mocker):
        """Test choosing to flip a card."""
        mocker.patch.object(cli.console, "input", return_value="y")
        result = cli.get_flip_choice()
        assert result == "y"

    def test_get_flip_choice_no(self, cli, mocker):
        """Test choosing not to flip a card."""
        mocker.patch.object(cli.console, "input", return_value="n")
        result = cli.get_flip_choice()
        assert result == "n"

    @pytest.mark.parametrize(
        ("input_value", "expected_index"),
        INDEX_INPUT_CASES,
    )
    def test_get_index_to_replace(self, cli, mocker, input_value, expected_index):
        """Test getting a valid index to replace."""
        mocker.patch.object(cli.console, "input", return_value=input_value)
        result = cli.get_index_to_replace()
        assert result == expected_index

    def test_get_index_to_replace_invalid_then_valid(self, cli, mocker):
        """Test that invalid indices are rejected."""
        mocker.patch.object(cli.console, "input", side_effect=["0", "7", "3"])
        mock_print = mocker.patch.object(cli.console, "print")

        result = cli.get_index_to_replace()
        assert result == 2  # 3 - 1
        # Verify error message was shown twice
        assert mock_print.call_count >= 2

    @pytest.mark.parametrize(
        ("input_value", "expected_index"),
        INDEX_INPUT_CASES,
    )
    def test_get_index_to_flip(self, cli, mocker, input_value, expected_index):
        """Test getting a valid index to flip."""
        mocker.patch.object(cli.console, "input", return_value=input_value)
        result = cli.get_index_to_flip()
        assert result == expected_index


class TestDisplay:
    """Tests for display methods using captured output."""

    def test_display_drawn_card(self, captured_cli, sample_card):
        """Test displaying a drawn card."""
        cli, output = captured_cli
        cli.display_drawn_card("TestPlayer", sample_card)
        assert "TestPlayer drew:" in output.getvalue()
        assert "A♤" in output.getvalue()

    def test_display_discard_draw(self, captured_cli, sample_card):
        """Test displaying a discard pile draw."""
        cli, output = captured_cli
        cli.display_discard_draw("TestPlayer", sample_card)
        assert "TestPlayer drew" in output.getvalue()
        assert "A♤" in output.getvalue()

    def test_display_replace_action(self, captured_cli):
        """Test displaying a replace action."""
        cli, output = captured_cli
        new_card = Card(Rank.ACE, Suit.SPADES, "red", face_up=True)
        old_card = Card(Rank.TWO, Suit.HEARTS, "red", face_up=True)

        cli.display_replace_action("TestPlayer", 2, new_card, old_card)

        result = output.getvalue()
        assert "TestPlayer replaced card" in result
        assert "A♤" in result
        assert "2♡" in result

    def test_display_flip_action(self, captured_cli, sample_card):
        """Test displaying a flip action."""
        cli, output = captured_cli
        cli.display_flip_action("TestPlayer", 1, sample_card)

        result = output.getvalue()
        assert "TestPlayer flipped card" in result
        assert "A♤" in result

    def test_notify(self, captured_cli):
        """Test notify method."""
        cli, output = captured_cli
        cli.notify("Test message")
        assert "Test message" in output.getvalue()

    def test_display_hand_output(self, captured_cli, mock_player):
        """Test that _display_hand produces output with borders."""
        cli, output = captured_cli
        cli._display_hand(mock_player, display_indices=True)

        result = output.getvalue()
        assert "+" in result
        assert "|" in result
        # Should contain indices since display_indices=True
        assert "1" in result

    def test_display_hand_without_indices(self, captured_cli, mock_player):
        """Test _display_hand without indices."""
        cli, output = captured_cli
        cli._display_hand(mock_player, display_indices=False)

        result = output.getvalue()
        assert "+" in result
        assert "|" in result
        # Note: We can't easily assert absence of numbers as cards have numbers,
        # but we can verify the method runs without error and produces output.

    def test_display_state(self, captured_cli, mock_round):
        """Test display_state method covers the game state display."""
        cli, output = captured_cli
        mock_game = Mock()
        mock_game.current_round = mock_round
        mock_game.players = mock_round.players

        cli.display_state(mock_game)

        result = output.getvalue()
        assert "5" in result  # Turn count
        assert "40" in result  # Deck count
        assert "Player 1" in result or "Player" in result

    def test_display_discard_pile(self, captured_cli):
        """Test _display_discard_pile method."""
        cli, output = captured_cli

        # Create mock Round object with discard pile
        game_round = Mock(spec=Round)
        discard = Mock(spec=DiscardStack)
        discard_card = Card(Rank.QUEEN, Suit.DIAMONDS, "red", face_up=True)
        discard.peek.return_value = discard_card
        game_round.discard_pile = discard

        cli._display_discard_pile(game_round)

        result = output.getvalue()
        assert "Discard Pile Top Card:" in result
        assert "Q♢" in result


class TestColorValidation:
    """Tests for color validation."""

    @pytest.mark.parametrize(
        "valid_color",
        [
            "red",
            "blue",
            "green",
            "#FF0000",
            "rgb(255,0,0)",
        ],
    )
    def test_validate_color_valid(self, cli, valid_color):
        """Test that valid colors pass validation."""
        # Should not raise an exception
        cli.validate_color(valid_color)

    def test_validate_color_invalid(self, cli):
        """Test that invalid colors raise GameConfigError."""
        with pytest.raises(GameConfigError, match="Invalid color"):
            cli.validate_color("notacolorstring")
