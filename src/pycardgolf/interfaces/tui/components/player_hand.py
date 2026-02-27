"""Module containing the PlayerHandWidget for rendering the active player's hand."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from pycardgolf.interfaces.tui.components.card_widget import CardWidget
from pycardgolf.utils.constants import HAND_SIZE

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from pycardgolf.utils.types import CardID


class PlayerHandWidget(Widget):
    """Widget rendering the current player's 2x3 card grid with position labels."""

    DEFAULT_CSS = """
    PlayerHandWidget {
        height: auto;
        width: auto;
        align: center middle;
        padding: 0 1;
    }

    PlayerHandWidget .hand-title {
        text-align: center;
        text-style: bold;
        width: 100%;
        margin-bottom: 1;
        color: $text;
    }

    PlayerHandWidget .card-row {
        height: auto;
        width: auto;
        align: center middle;
    }
    """

    hand_cards: reactive[list[int]] = reactive(  # type: ignore[type-arg]
        list, always_update=True
    )
    player_label: reactive[str] = reactive("Your Hand")  # type: ignore[type-arg]

    def compose(self) -> ComposeResult:
        """Build the 2x3 card grid with position labels."""
        cols = HAND_SIZE // 2
        yield Static(self.player_label, classes="hand-title", id="hand-title")

        # Top row labels
        with Horizontal(classes="card-row"):
            for i in range(cols):
                yield Static(f" {i + 1} ", id=f"top-label-{i}", classes="card-label")

        # Top row cards
        with Horizontal(classes="card-row"):
            for i in range(cols):
                yield CardWidget(id=f"player-card-{i}")

        # Bottom row cards
        with Horizontal(classes="card-row"):
            for i in range(cols, HAND_SIZE):
                yield CardWidget(id=f"player-card-{i}")

        # Bottom row labels
        with Horizontal(classes="card-row"):
            for i in range(cols, HAND_SIZE):
                yield Static(f" {i + 1} ", id=f"bottom-label-{i}", classes="card-label")

    def watch_hand_cards(self, cards: list[CardID]) -> None:
        """Update each CardWidget when hand_cards changes."""
        for i in range(min(len(cards), HAND_SIZE)):
            card_widget = self.query_one(f"#player-card-{i}", CardWidget)
            card_widget.card_id = cards[i]

    def watch_player_label(self, label: str) -> None:
        """Update the title when player_label changes."""
        try:
            title = self.query_one("#hand-title", Static)
            title.update(label)
        except Exception:  # noqa: BLE001, S110
            pass  # Widget may not be mounted yet

    def with_vertical(self) -> Vertical:
        """Wrap self in a Vertical container for layout convenience."""
        return Vertical(self)
