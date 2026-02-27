"""Module containing the OpponentGrid widget for rendering opponent hands."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from pycardgolf.interfaces.tui.components.card_widget import CardWidget
from pycardgolf.utils.constants import HAND_SIZE

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from pycardgolf.utils.types import CardID


class OpponentHandWidget(Widget):
    """A compact display of a single opponent's hand."""

    DEFAULT_CSS = """
    OpponentHandWidget {
        height: auto;
        width: auto;
        padding: 0 1;
    }

    OpponentHandWidget .opp-name {
        text-align: center;
        text-style: bold;
        width: 100%;
        color: $text;
    }

    OpponentHandWidget .opp-card-row {
        height: auto;
        width: auto;
        align: center middle;
    }
    """

    def __init__(
        self,
        opponent_name: str = "Opponent",
        *,
        opp_index: int = 0,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        """Initialize with the opponent's name and index."""
        super().__init__(id=id, classes=classes)
        self.opponent_name = opponent_name
        self._opp_index = opp_index

    opponent_name: reactive[str] = reactive("Opponent")  # type: ignore[type-arg]
    is_next: reactive[bool] = reactive(False)  # type: ignore[type-arg]

    def compose(self) -> ComposeResult:
        """Build a compact 2-row card grid for this opponent."""
        cols = HAND_SIZE // 2
        label = (
            f"{self.opponent_name} [bold cyan](Next)[/bold cyan]"
            if self.is_next
            else self.opponent_name
        )
        yield Static(label, id="opp-name-label", classes="opp-name")

        with Horizontal(classes="opp-card-row"):
            for i in range(cols):
                yield CardWidget(
                    id=f"opp-{self._opp_index}-card-{i}",
                )

        with Horizontal(classes="opp-card-row"):
            for i in range(cols, HAND_SIZE):
                yield CardWidget(
                    id=f"opp-{self._opp_index}-card-{i}",
                )

    def update_hand(self, cards: list[CardID]) -> None:
        """Update the opponent's cards."""
        for i in range(min(len(cards), HAND_SIZE)):
            card_widget = self.query_one(f"#opp-{self._opp_index}-card-{i}", CardWidget)
            card_widget.card_id = cards[i]

    def watch_is_next(self, is_next: bool) -> None:
        """Update the name label when is_next changes."""
        try:
            label_widget = self.query_one("#opp-name-label", Static)
            if is_next:
                label_widget.update(
                    f"{self.opponent_name} [bold cyan](Next)[/bold cyan]"
                )
            else:
                label_widget.update(self.opponent_name)
        except Exception:  # noqa: BLE001, S110
            pass

    def watch_opponent_name(self, name: str) -> None:
        """Update the name label when opponent_name changes."""
        try:
            label_widget = self.query_one("#opp-name-label", Static)
            # Re-check if we are the next player whenever our name changes
            if (
                self.parent is not None
                and hasattr(self.parent, "parent")
                and isinstance(self.parent.parent, OpponentGrid)
            ):
                self.is_next = self.parent.parent.next_player_name == name

            if self.is_next:
                label_widget.update(f"{name} [bold cyan](Next)[/bold cyan]")
            else:
                label_widget.update(name)
        except Exception:  # noqa: BLE001, S110
            pass


class OpponentGrid(Widget):
    """Widget displaying up to MAX_OPPONENTS opponent hands in a horizontal row."""

    MAX_OPPONENTS: ClassVar[int] = 3

    DEFAULT_CSS = """
    OpponentGrid {
        height: auto;
        width: 100%;
        align: center middle;
    }

    OpponentGrid .opp-grid-title {
        text-align: center;
        text-style: bold;
        width: 100%;
        color: $text-muted;
    }

    OpponentGrid .opp-row {
        height: auto;
        width: auto;
        align: center middle;
    }
    """

    def __init__(
        self,
        num_slots: int = 1,
        *,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        """Initialize with a number of opponent slots."""
        super().__init__(id=id, classes=classes)
        self._num_slots = min(max(num_slots, 0), self.MAX_OPPONENTS)

    next_player_name: reactive[str] = reactive("")  # type: ignore[type-arg]

    def compose(self) -> ComposeResult:
        """Build horizontal row of opponent slots."""
        if self._num_slots <= 0:
            return

        yield Static("─── Opponents ───", classes="opp-grid-title")
        with Horizontal(classes="opp-row"):
            for i in range(self._num_slots):
                yield OpponentHandWidget(opp_index=i, id=f"opponent-{i}")

    def update_opponent(self, opp_index: int, name: str, cards: list[CardID]) -> None:
        """Update a specific opponent's slot with name and hand."""
        try:
            opp_widget = self.query_one(f"#opponent-{opp_index}", OpponentHandWidget)
            opp_widget.opponent_name = name
            opp_widget.update_hand(cards)
        except Exception:  # noqa: BLE001, S110
            pass  # Opponent slot may not exist

    def mark_next_player(self, player_name: str) -> None:
        """Mark the named opponent as the next player to act."""
        self.next_player_name = player_name

    def watch_next_player_name(self, next_player_name: str) -> None:
        """Update all opponent widgets when the next player changes."""
        for widget in self.query(OpponentHandWidget):
            widget.is_next = widget.opponent_name == next_player_name
