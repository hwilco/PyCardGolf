"""Tests for the CLI input handler."""

import pytest
from rich.console import Console

from pycardgolf.exceptions import GameExitError
from pycardgolf.interfaces.cli_input import CLIInputHandler
from pycardgolf.interfaces.cli_renderer import CLIRenderer


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
