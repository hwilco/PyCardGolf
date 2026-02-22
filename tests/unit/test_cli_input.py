"""Tests for the CLI input handler."""

import pytest
from rich.console import Console

from pycardgolf.exceptions import GameExitError
from pycardgolf.interfaces.cli import CLIInputHandler, CLIRenderer
from pycardgolf.utils.enums import DrawSourceChoice, KeepOrDiscardChoice


@pytest.fixture
def mock_console(mocker):
    """Create a mock console."""
    return mocker.Mock(spec=Console)


@pytest.fixture
def mock_renderer(mocker):
    """Create a mock renderer."""
    return mocker.Mock(spec=CLIRenderer)


@pytest.fixture
def input_handler(mock_console, mock_renderer):
    """Create a CLI input handler with a mock console and renderer."""
    return CLIInputHandler(mock_console, mock_renderer)


@pytest.fixture
def mock_player(mocker):
    """Create a mock player."""
    player = mocker.Mock()
    player.name = "Test Player"
    player.hand = [mocker.Mock() for _ in range(6)]
    return player


class TestInputHandlerValidation:
    """Tests for user input validation in CLIInputHandler."""

    def test_get_input(self, input_handler, mock_console):
        """Test basic input retrieval."""
        mock_console.input.return_value = "test"
        result = input_handler.get_input("Prompt: ")
        assert result == "test"
        mock_console.input.assert_called_once_with("Prompt: ")

    def test_get_choice_with_valid_options(self, input_handler, mock_console):
        """Test that valid options are accepted."""
        mock_console.input.return_value = "d"
        result = input_handler.get_choice(
            "Choose: ", valid_options=["d", "p"], error_msg="Invalid"
        )
        assert result == "d"

    def test_get_choice_retries_on_invalid(self, input_handler, mock_console):
        """Test that invalid input causes retry."""
        # First return invalid, then valid
        mock_console.input.side_effect = ["invalid", "d"]

        result = input_handler.get_choice(
            "Choose: ", valid_options=["d", "p"], error_msg="Invalid input."
        )

        assert result == "d"
        # Check that error message was printed
        mock_console.print.assert_any_call("Invalid input.")

    @pytest.mark.parametrize(
        "quit_input",
        [
            pytest.param("q", id="q"),
            pytest.param("quit", id="quit"),
            pytest.param("Q", id="Q"),
            pytest.param("QUIT", id="QUIT"),
        ],
    )
    def test_get_choice_quit(self, input_handler, mock_console, quit_input):
        """Test that quit inputs raise GameExitError."""
        mock_console.input.return_value = quit_input
        with pytest.raises(GameExitError):
            input_handler.get_choice("Choose: ", valid_options=["a", "b"])

    def test_get_validated_input_with_func(self, input_handler, mock_console):
        """Test input validation with custom validation function."""
        mock_console.input.return_value = "5"

        def validate_number(s: str) -> int:
            num = int(s)
            if 1 <= num <= 6:
                return num
            raise ValueError

        result = input_handler.get_validated_input(
            "Enter number: ",
            validation_func=validate_number,
            error_msg="Invalid number",
        )
        assert result == 5

    def test_get_validated_input_retries(self, input_handler, mock_console):
        """Test that validation function failures cause retry."""
        mock_console.input.side_effect = ["99", "5"]

        def validate_number(s: str) -> int:
            num = int(s)
            if 1 <= num <= 6:
                return num
            raise ValueError

        result = input_handler.get_validated_input(
            "Enter number: ",
            validation_func=validate_number,
            error_msg="Invalid number",
        )

        assert result == 5
        mock_console.print.assert_any_call("Invalid number")

    def test_get_index_to_replace_shows_hand(
        self, input_handler, mock_console, mock_renderer, mock_player
    ):
        """Test that get_index_to_replace shows the hand."""
        mock_console.input.return_value = "1"
        result = input_handler.get_index_to_replace(mock_player)
        assert result == 0
        mock_renderer.display_hand.assert_called_once_with(
            mock_player, display_indices=True
        )

    def test_get_index_to_flip_shows_hand(
        self, input_handler, mock_console, mock_renderer, mock_player
    ):
        """Test that get_index_to_flip shows the hand."""
        mock_console.input.return_value = "6"
        result = input_handler.get_index_to_flip(mock_player)
        assert result == 5
        mock_renderer.display_hand.assert_called_once_with(
            mock_player, display_indices=True
        )

    def test_get_valid_flip_index_shows_hand(
        self, input_handler, mock_console, mock_renderer, mock_player
    ):
        """Test that get_valid_flip_index shows the hand and filters valid indices."""
        # Setup hand: indices 0, 1 are face up, rest are face down
        for i in range(2):
            mock_player.hand[i].face_up = True
        for i in range(2, 6):
            mock_player.hand[i].face_up = False

        # Mock input to pick index 3 (human 4)
        mock_console.input.return_value = "4"

        result = input_handler.get_valid_flip_index(mock_player)

        assert result == 3
        mock_renderer.display_hand.assert_called_once_with(
            mock_player, display_indices=True
        )

    def test_get_validated_input_quit(self, input_handler, mock_console):
        """Test that quit input in get_validated_input raises GameExitError."""
        mock_console.input.return_value = "q"
        with pytest.raises(GameExitError):
            input_handler.get_validated_input("Prompt: ", lambda x: x)

    def test_get_draw_choice_deck(self, input_handler, mock_console, mock_player):
        """Test get_draw_choice returning DECK."""
        mock_console.input.return_value = "d"
        result = input_handler.get_draw_choice(mock_player, None, None)
        assert result == DrawSourceChoice.DECK

    def test_get_draw_choice_discard(self, input_handler, mock_console, mock_player):
        """Test get_draw_choice returning DISCARD."""
        mock_console.input.return_value = "p"
        result = input_handler.get_draw_choice(mock_player, None, None)
        assert result == DrawSourceChoice.DISCARD_PILE

    def test_get_keep_or_discard_choice_keep(
        self, input_handler, mock_console, mock_player
    ):
        """Test get_keep_or_discard_choice returning KEEP."""
        mock_console.input.return_value = "k"
        result = input_handler.get_keep_or_discard_choice(mock_player)
        assert result == KeepOrDiscardChoice.KEEP

    def test_get_keep_or_discard_choice_discard(
        self, input_handler, mock_console, mock_player
    ):
        """Test get_keep_or_discard_choice returning DISCARD."""
        mock_console.input.return_value = "d"
        result = input_handler.get_keep_or_discard_choice(mock_player)
        assert result == KeepOrDiscardChoice.DISCARD

    def test_get_flip_choice_yes(self, input_handler, mock_console, mock_player):
        """Test get_flip_choice returning YES."""
        mock_console.input.return_value = "y"
        result = input_handler.get_flip_choice(mock_player)
        assert result is True

    def test_get_flip_choice_no(self, input_handler, mock_console, mock_player):
        """Test get_flip_choice returning NO."""
        mock_console.input.return_value = "n"
        result = input_handler.get_flip_choice(mock_player)
        assert result is False

    def test_validate_card_index_out_of_range(self, input_handler):
        """Test that out-of-range indices raise ValueError."""
        with pytest.raises(ValueError, match="Card index must be between"):
            input_handler._validate_card_index("0")
        with pytest.raises(ValueError, match="Card index must be between"):
            input_handler._validate_card_index("7")
        with pytest.raises(ValueError, match="invalid literal"):
            input_handler._validate_card_index("not_a_number")
