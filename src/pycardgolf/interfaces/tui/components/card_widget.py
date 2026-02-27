"""Module containing the CardWidget for rendering a single card."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from color_contrast import ModulationMode, modulate
from rich.style import Style
from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget

from pycardgolf.utils.card import card_to_string, get_card_colors, is_face_up

if TYPE_CHECKING:
    from rich.console import RenderableType

    from pycardgolf.utils.types import CardID


class CardWidget(Widget):
    """A widget that renders a single playing card using Rich styling.

    Reuses the same color and display logic as CLIRenderer.get_card_text().
    """

    CARD_DISPLAY_WIDTH: ClassVar[int] = 4
    FACE_BACKGROUND_COLOR: ClassVar[str] = "white"

    DEFAULT_CSS = """
    CardWidget {
        width: 8;
        height: 3;
        content-align: center middle;
    }
    """

    card_id: reactive[int | None] = reactive(None)  # type: ignore[type-arg]

    def __init__(
        self,
        card_id: CardID | None = None,
        *,
        label: str = "",
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        """Initialize the card widget with an optional card ID and label."""
        super().__init__(id=id, classes=classes)
        self._label = label
        self.card_id = card_id

    def render(self) -> RenderableType:
        """Render the card as a Rich Text object with appropriate coloring."""
        return self._build_card_text(self.card_id)

    def _build_card_text(self, card_id: CardID | None) -> Text:
        """Build a Rich Text representation of a card.

        Uses the same styling logic as CLIRenderer.get_card_text():
        face-up cards show rank+suit on white background, face-down
        cards show '??' with the deck-back color.
        """
        if card_id is not None and is_face_up(card_id):
            text = card_to_string(card_id).center(self.CARD_DISPLAY_WIDTH)
            text_color, _ = get_card_colors(card_id)
            background_color = self.FACE_BACKGROUND_COLOR
        else:
            text = "??".center(self.CARD_DISPLAY_WIDTH)
            text_color = "black"
            _, background_color = get_card_colors(
                card_id if card_id is not None else -1
            )
            text_color, background_color = (
                str(color)
                for color in modulate(
                    text_color, background_color, mode=ModulationMode.FOREGROUND
                )[:2]
            )

        label_line = ""
        if self._label:
            label_line = self._label.center(self.CARD_DISPLAY_WIDTH)

        style = Style(color=text_color, bgcolor=background_color, bold=True)
        result = Text()
        if label_line:
            result.append(f"{label_line}\n")
        result.append(text, style=style)
        return result

    def watch_card_id(self) -> None:
        """React to card_id changes by refreshing the widget."""
        self.refresh()
