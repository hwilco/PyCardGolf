"""Module containing the EventLogWidget for displaying game event messages."""

from __future__ import annotations

from textual.widgets import RichLog


class EventLogWidget(RichLog):
    """Right-docked sidebar that displays game event messages.

    Wraps Textual's RichLog to provide a dedicated game event feed
    with auto-scrolling.
    """

    DEFAULT_CSS = """
    EventLogWidget {
        height: 100%;
        width: 100%;
        border: solid $primary;
        scrollbar-size: 1 1;
    }
    """

    def __init__(
        self,
        *,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        """Initialize the event log."""
        super().__init__(
            id=id,
            classes=classes,
            highlight=True,
            markup=True,
            wrap=True,
            max_lines=100,
        )

    def log_event(self, message: str) -> None:
        """Append a game event message and auto-scroll to the bottom."""
        self.write(message)
