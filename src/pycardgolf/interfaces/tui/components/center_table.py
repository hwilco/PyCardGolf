"""Module containing the CenterTable widget for draw/discard piles."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from pycardgolf.interfaces.tui.components.card_widget import CardWidget

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from pycardgolf.utils.types import CardID


class CenterTable(Widget):
    """Widget displaying the draw pile, discard pile, and drawn card."""

    DEFAULT_CSS = """
    CenterTable {
        height: auto;
        width: 100%;
        align: center middle;
        padding: 1 0;
    }

    CenterTable .table-title {
        text-align: center;
        text-style: bold;
        width: 100%;
        color: $text-muted;
    }

    CenterTable .table-row {
        height: auto;
        width: auto;
        align: center middle;
    }

    CenterTable .pile-container {
        height: auto;
        width: auto;
        padding: 0 2;
        align: center middle;
    }

    CenterTable .pile-label {
        text-align: center;
        width: 100%;
        color: $text;
    }
    """

    discard_top: reactive[int | None] = reactive(None)  # type: ignore[type-arg]
    drawn_card: reactive[int | None] = reactive(None)  # type: ignore[type-arg]
    deck_size: reactive[int] = reactive(0)  # type: ignore[type-arg]

    def compose(self) -> ComposeResult:
        """Build the center table with draw pile, discard pile, and drawn card."""
        yield Static("─── Table ───", classes="table-title")
        with Horizontal(classes="table-row"):
            # Draw pile
            with Widget(classes="pile-container"):
                yield Static("Draw", classes="pile-label")
                yield CardWidget(card_id=-1, id="draw-pile-card")
                yield Static("", id="deck-count-label", classes="pile-label")

            # Drawn card (shown when a card has been drawn)
            with Widget(classes="pile-container"):
                yield Static("Drawn", classes="pile-label")
                yield CardWidget(id="drawn-card-display")

            # Discard pile
            with Widget(classes="pile-container"):
                yield Static("Discard", classes="pile-label")
                yield CardWidget(id="discard-pile-card")

    def watch_discard_top(self, card_id: CardID | None) -> None:
        """Update the discard pile display."""
        try:
            discard_widget = self.query_one("#discard-pile-card", CardWidget)
            discard_widget.card_id = card_id
        except Exception:  # noqa: BLE001, S110
            pass  # Widget may not be mounted yet

    def watch_drawn_card(self, card_id: CardID | None) -> None:
        """Update the drawn card display."""
        try:
            drawn_widget = self.query_one("#drawn-card-display", CardWidget)
            drawn_widget.card_id = card_id
        except Exception:  # noqa: BLE001, S110
            pass  # Widget may not be mounted yet

    def watch_deck_size(self, size: int) -> None:
        """Update the deck count label."""
        try:
            label = self.query_one("#deck-count-label", Static)
            label.update(f"({size})")
        except Exception:  # noqa: BLE001, S110
            pass  # Widget may not be mounted yet
