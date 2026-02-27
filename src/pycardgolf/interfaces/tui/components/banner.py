"""Module containing the BannerWidget for prominent game warnings."""

from __future__ import annotations

from textual.reactive import reactive
from textual.widgets import Static


class SideIndicator(Static):
    """A prominent vertical indicator for important game messages (like FINAL TURN)."""

    DEFAULT_CSS = """
    SideIndicator {
        display: none;
        width: 12;
        height: 100%;
        content-align: center middle;
        text-align: center;
        text-style: bold;
        background: $error;
        color: $text;
        border-left: thick $error-darken-2;
    }

    SideIndicator.visible {
        display: block;
    }
    """

    message: reactive[str] = reactive("")  # type: ignore[type-arg]

    def watch_message(self, message: str) -> None:
        """Update content and visibility when message changes."""
        if message:
            # Format message vertically for a narrow side panel
            # e.g. "F\nI\nN\nA\nL"
            vertical_text = "\n".join(list(message.replace(" ", "")))
            if "⚠️" in message:
                vertical_text = "⚠️\n\n" + vertical_text + "\n\n⚠️"

            self.update(f"[blink]{vertical_text}[/blink]")
            self.add_class("visible")
        else:
            self.remove_class("visible")
