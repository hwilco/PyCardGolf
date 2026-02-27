import pytest
from textual.app import App, ComposeResult

from pycardgolf.interfaces.tui.components.center_table import CenterTable
from pycardgolf.interfaces.tui.components.opponents import (
    OpponentGrid,
    OpponentHandWidget,
)
from pycardgolf.interfaces.tui.components.status_bar import StatusBar


# A simple wrapper app to test individual widgets in a real Textual environment
class WidgetTestApp(App):
    def __init__(self, widget):
        super().__init__()
        self._test_widget = widget

    def compose(self) -> ComposeResult:
        yield self._test_widget


@pytest.mark.asyncio
async def test_status_bar_rendering():
    """Test that the StatusBar reactively updates its rendered text."""
    status_bar = StatusBar()
    app = WidgetTestApp(status_bar)

    async with app.run_test() as pilot:
        # Initial state (no data)
        assert status_bar.render() == "PyCardGolf"

        # Update reactive properties
        status_bar.round_num = 5
        status_bar.current_player = "TestPlayer"
        status_bar.phase_name = "ACTION"

        await pilot.pause()

        rendered = status_bar.render()
        assert "Round 5" in rendered
        assert "TestPlayer" in rendered
        assert "ACTION" in rendered
        assert " │ " in rendered


@pytest.mark.asyncio
async def test_center_table_updates():
    """Test that CenterTable correctly updates its sub-widgets."""
    center_table = CenterTable()
    app = WidgetTestApp(center_table)

    async with app.run_test() as pilot:
        # Test deck size update
        center_table.deck_size = 52
        await pilot.pause()
        deck_label = app.query_one("#deck-count-label")
        assert "(52)" in str(deck_label.render())

        # Test drawn card update
        # Using a hypothetical card ID
        center_table.drawn_card = 10
        await pilot.pause()
        drawn_card_widget = app.query_one("#drawn-card-display")
        assert drawn_card_widget.card_id == 10

        # Test discard top update
        center_table.discard_top = 20
        await pilot.pause()
        discard_card_widget = app.query_one("#discard-pile-card")
        assert discard_card_widget.card_id == 20


@pytest.mark.asyncio
async def test_opponent_hand_widget():
    """Test the OpponentHandWidget reactive behavior."""
    opp_widget = OpponentHandWidget(opponent_name="Bot 1", opp_index=0)
    app = WidgetTestApp(opp_widget)

    async with app.run_test() as pilot:
        label_widget = app.query_one("#opp-name-label")

        # Initial name
        assert "Bot 1" in str(label_widget.render())
        assert "(Next)" not in str(label_widget.render())

        # Test is_next highlight
        opp_widget.is_next = True
        await pilot.pause()
        assert "(Next)" in str(label_widget.render())

        # Test name change
        opp_widget.opponent_name = "NewName"
        await pilot.pause()
        assert "NewName" in str(label_widget.render())
        assert "(Next)" in str(
            label_widget.render()
        )  # Should persist if is_next is True


@pytest.mark.asyncio
async def test_opponent_grid_management():
    """Test that OpponentGrid manages multiple slots and 'next player' logic."""
    grid = OpponentGrid(num_slots=2)
    app = WidgetTestApp(grid)

    async with app.run_test() as pilot:
        # Verify slots exist
        opp0 = app.query_one("#opponent-0", OpponentHandWidget)
        opp1 = app.query_one("#opponent-1", OpponentHandWidget)

        # Update one opponent
        grid.update_opponent(0, "Alice", [1, 2, 3, 4, 5, 6])
        await pilot.pause()
        assert opp0.opponent_name == "Alice"

        # Mark Alice as next
        grid.mark_next_player("Alice")
        await pilot.pause()
        assert opp0.is_next is True
        assert opp1.is_next is False

        # Mark Bob as next (Bob is not in the list yet, but check if Alice is cleared)
        grid.mark_next_player("Bob")
        await pilot.pause()
        assert opp0.is_next is False
