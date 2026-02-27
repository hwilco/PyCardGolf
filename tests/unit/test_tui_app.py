from unittest.mock import MagicMock

import pytest

from pycardgolf.core.actions import ActionSpace
from pycardgolf.core.game import Game
from pycardgolf.interfaces.tui.tui_app import PyCardGolfApp
from pycardgolf.interfaces.tui.tui_input import TUIInputHandler
from pycardgolf.interfaces.tui.tui_renderer import TUIRenderer


@pytest.mark.asyncio
async def test_app_mounting():
    """Test that the app mounts correctly and initializes its components."""
    mock_game = MagicMock(spec=Game)
    mock_renderer = MagicMock(spec=TUIRenderer)
    mock_input_handler = MagicMock(spec=TUIInputHandler)

    mock_game.players = []
    mock_game.tick.return_value = False  # Prevent worker hang

    app = PyCardGolfApp(mock_game, mock_renderer, mock_input_handler)

    async with app.run_test() as pilot:
        await pilot.pause()
        # The worker might have finished or might still be in WAITING
        assert app.game_phase in ("WAITING", "FINISHED")

        mock_renderer.set_app.assert_called_with(app)
        mock_input_handler.set_app.assert_called_with(app)


@pytest.mark.asyncio
async def test_phase_reactivity():
    """Test that action availability changes with game phase and turn."""
    mock_game = MagicMock(spec=Game)
    mock_game.players = []
    mock_game.tick.return_value = False
    mock_renderer = MagicMock(spec=TUIRenderer)
    mock_input_handler = MagicMock(spec=TUIInputHandler)

    app = PyCardGolfApp(mock_game, mock_renderer, mock_input_handler)

    async with app.run_test() as pilot:
        await pilot.pause()

        # Manually drive the reactive state for testing
        app.game_over = False
        app.is_human_turn = False
        assert app.check_action("draw_deck", ()) is False
        assert app.check_action("quit_game", ()) is True

        app.game_phase = "DRAW"
        app.is_human_turn = True
        await pilot.pause()

        assert app.check_action("draw_deck", ()) is True
        assert app.check_action("select_1", ()) is False

        app.game_phase = "ACTION"
        await pilot.pause()
        assert app.check_action("draw_deck", ()) is False
        assert app.check_action("select_1", ()) is True


@pytest.mark.asyncio
async def test_input_submission():
    """Test that key presses trigger action submission to the input handler."""
    mock_game = MagicMock(spec=Game)
    mock_game.players = []
    mock_game.tick.return_value = False
    mock_renderer = MagicMock(spec=TUIRenderer)
    mock_input_handler = MagicMock(spec=TUIInputHandler)

    app = PyCardGolfApp(mock_game, mock_renderer, mock_input_handler)

    async with app.run_test() as pilot:
        await pilot.pause()

        # Ensure game is NOT over for input to be accepted
        app.game_over = False
        app.game_phase = "DRAW"
        app.is_human_turn = True
        await pilot.pause()

        await pilot.press("d")
        mock_input_handler.submit_action.assert_called_with(ActionSpace.DRAW_DECK)

        await pilot.press("p")
        mock_input_handler.submit_action.assert_called_with(ActionSpace.DRAW_DISCARD)


@pytest.mark.asyncio
async def test_quit_action():
    """Test that 'q' triggers the quit logic."""
    mock_game = MagicMock(spec=Game)
    mock_game.players = []
    mock_game.tick.return_value = False
    mock_renderer = MagicMock(spec=TUIRenderer)
    mock_input_handler = MagicMock(spec=TUIInputHandler)

    app = PyCardGolfApp(mock_game, mock_renderer, mock_input_handler)

    async with app.run_test() as pilot:
        await pilot.pause()

        await pilot.press("q")

        assert app._shutting_down is True
        mock_input_handler.shutdown.assert_called_once()
