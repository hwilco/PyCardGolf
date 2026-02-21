"""Tests for the main entry point."""

import pytest

from pycardgolf.exceptions import GameExitError
from pycardgolf.main import _display_rules, main


def test_display_rules(mocker):
    """Test that _display_rules reads the rules file and prints it."""
    mock_console = mocker.patch("pycardgolf.main.Console")
    mock_markdown = mocker.patch("pycardgolf.main.Markdown")
    mock_path = mocker.patch("pycardgolf.main.Path")

    # Mocking Path().read_text()
    mock_path.return_value.parent.__truediv__.return_value.read_text.return_value = (
        "Mock Rules"
    )

    _display_rules()

    mock_console.return_value.print.assert_called_once()
    mock_markdown.assert_called_once_with("Mock Rules")


def test_main_rules_flag(mocker):
    """Test that --rules flag triggers rules display and exits."""
    mocker.patch("sys.argv", ["pycardgolf", "--rules"])
    mock_display = mocker.patch("pycardgolf.main._display_rules")

    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 0
    mock_display.assert_called_once()


def test_main_creates_game(mocker):
    """Test normal game bootstrap flow."""
    mocker.patch(
        "sys.argv", ["pycardgolf", "--humans", "1", "--bots", "1", "--rounds", "1"]
    )
    # Mock input for human name
    mock_input_handler = mocker.patch("pycardgolf.main.CLIInputHandler")
    mock_input_handler.return_value.get_input.return_value = "Alice"

    mock_game = mocker.patch("pycardgolf.main.Game")
    mocker.patch("pycardgolf.main.CLIRenderer")

    main()

    # Verify player creation
    # HumanPlayer + RandomBot
    mock_game.assert_called_once()
    args, _ = mock_game.call_args
    players = args[0]
    assert len(players) == 2
    assert players[0].name == "Alice"
    assert players[1].name == "Bot 1"

    mock_game.return_value.start.assert_called_once()


def test_main_game_exit_error(mocker):
    """Test main handler for GameExitError."""
    mocker.patch("sys.argv", ["pycardgolf"])
    mocker.patch(
        "pycardgolf.main.CLIInputHandler"
    ).return_value.get_input.return_value = "Alice"
    mock_game = mocker.patch("pycardgolf.main.Game")
    mock_game.return_value.start.side_effect = GameExitError

    mock_console = mocker.patch("pycardgolf.main.Console")

    main()

    # Should print error message
    mock_console.return_value.print.assert_called()
    # Find the call with the error message
    found = False
    for call in mock_console.return_value.print.call_args_list:
        if "Game exited by user" in str(call):
            found = True
            break
    assert found


def test_main_keyboard_interrupt(mocker):
    """Test main handler for KeyboardInterrupt."""
    mocker.patch("sys.argv", ["pycardgolf"])
    mocker.patch(
        "pycardgolf.main.CLIInputHandler"
    ).return_value.get_input.return_value = "Alice"
    mock_game = mocker.patch("pycardgolf.main.Game")
    mock_game.return_value.start.side_effect = KeyboardInterrupt

    mock_console = mocker.patch("pycardgolf.main.Console")

    main()

    # Should print error message
    mock_console.return_value.print.assert_called()
    found = False
    for call in mock_console.return_value.print.call_args_list:
        if "Game interrupted" in str(call):
            found = True
            break
    assert found
