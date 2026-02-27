"""Module containing the StatusBar widget for phase and turn information."""

from __future__ import annotations

from textual.reactive import reactive
from textual.widgets import Static


class StatusBar(Static):
    """Bottom-docked bar showing current round, player, and phase."""

    DEFAULT_CSS = """
    StatusBar {
        dock: bottom;
        height: 1;
        width: 100%;
        background: $primary-background;
        color: $text;
        text-style: bold;
        padding: 0 1;
    }
    """

    round_num: reactive[int] = reactive(0)  # type: ignore[type-arg]
    phase_name: reactive[str] = reactive("")  # type: ignore[type-arg]
    current_player: reactive[str] = reactive("")  # type: ignore[type-arg]

    def render(self) -> str:
        """Render the status bar text."""
        parts: list[str] = []
        if self.round_num > 0:
            parts.append(f"Round {self.round_num}")
        if self.current_player:
            parts.append(f"Turn: {self.current_player}")
        if self.phase_name:
            parts.append(f"Phase: {self.phase_name}")
        return " │ ".join(parts) if parts else "PyCardGolf"
