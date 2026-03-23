"""Module containing the TUIInputHandler — a GameInput for the Textual TUI."""

from __future__ import annotations

import queue
from typing import TYPE_CHECKING

from pycardgolf.exceptions import GameExitError
from pycardgolf.interfaces.base import GameInput
from pycardgolf.interfaces.tui.constants import QUIT_SENTINEL

if TYPE_CHECKING:
    from pycardgolf.core.actions import Action
    from pycardgolf.core.observation import Observation
    from pycardgolf.interfaces.tui.tui_app import PyCardGolfApp
    from pycardgolf.players.player import BasePlayer


class TUIInputHandler(GameInput):
    """GameInput that receives actions from Textual hotkeys via a queue.

    The background worker thread (running ``Game.tick()``) calls
    ``get_action()`` which blocks on ``queue.Queue.get()``.  When the
    user presses a hotkey, the Textual action handler calls
    ``action_queue.put_nowait(action)`` to wake the worker.
    """

    def __init__(self) -> None:
        """Initialize the input handler with an empty action queue."""
        self.action_queue: queue.Queue[Action | object] = queue.Queue()
        self._app: PyCardGolfApp | None = None
        self._shutdown = False

    def set_app(self, app: PyCardGolfApp) -> None:
        """Attach the Textual app instance (called at startup)."""
        self._app = app

    @property
    def app(self) -> PyCardGolfApp:
        """Return the Textual app reference."""
        if self._app is None:
            msg = "TUIInputHandler.app not set. Call set_app() before use."
            raise RuntimeError(msg)
        return self._app

    def get_input(self, prompt: str) -> str:
        """Return a raw string response (used for name entry before app starts)."""
        return input(prompt)

    def get_action(self, player: BasePlayer, observation: Observation) -> Action:
        """Block until the UI thread provides an action via hotkey.

        1. Signal the app to update the UI for this player's turn and
           enable the phase-appropriate hotkey bindings.
        2. Block on the queue until a hotkey pushes an action.
        3. Return the action to the game engine.
        """
        # Update UI state from the worker thread
        self.app.call_from_thread(self.app.prepare_for_input, player, observation)

        # Block until the user presses a valid hotkey (or shutdown)
        while not self._shutdown:
            try:
                result = self.action_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            else:
                if result is QUIT_SENTINEL:
                    raise GameExitError
                return result  # type: ignore[return-value]

        raise GameExitError

    def submit_action(self, action: Action) -> None:
        """Push an action into the queue (called from UI thread hotkey handlers)."""
        self.action_queue.put_nowait(action)

    def clear_actions(self) -> None:
        """Clear any buffered actions from the queue."""
        while not self.action_queue.empty():
            try:
                self.action_queue.get_nowait()
            except queue.Empty:
                break

    def shutdown(self) -> None:
        """Signal the input handler to stop blocking."""
        self._shutdown = True
        self.action_queue.put_nowait(QUIT_SENTINEL)
