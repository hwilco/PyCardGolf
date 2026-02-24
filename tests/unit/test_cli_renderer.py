"""Tests for the CLI renderer using primitives."""

import io

import pytest
from rich.console import Console
from rich.text import Text

from pycardgolf.core.event_bus import EventBus
from pycardgolf.core.events import (
    CardDrawnDeckEvent,
    CardDrawnDiscardEvent,
    CardFlippedEvent,
    CardSwappedEvent,
    GameStartedEvent,
    GameStatsEvent,
)
from pycardgolf.core.hand import Hand
from pycardgolf.core.round import Round
from pycardgolf.core.stats import PlayerStats
from pycardgolf.exceptions import GameConfigError
from pycardgolf.interfaces.cli.cli_renderer import CLIRenderer
from pycardgolf.players.player import BasePlayer


@pytest.fixture
def captured_renderer():
    """Create a renderer that captures output to a string buffer."""
    string_io = io.StringIO()
    console = Console(file=string_io, force_terminal=False)
    event_bus = EventBus()
    renderer = CLIRenderer(event_bus, console)
    return renderer, string_io


class TestRendererWait:
    """Tests for wait_for_enter functionality."""

    def test_init_negative_delay(self):
        """Test that negative delay raises GameConfigError."""
        console = Console()
        event_bus = EventBus()
        renderer = CLIRenderer(event_bus, console, delay=-1.0)
        with pytest.raises(GameConfigError, match="Delay cannot be negative"):
            renderer.wait_for_enter()


@pytest.fixture
def sample_card_id():
    """Create a sample CardID (Ace of Spades)."""
    return 0


@pytest.fixture
def sample_hand():
    """Create a sample hand with mix of face-up and face-down."""
    # IDs: 0, 1, 2, 3, 4, 5. Face up indices: 0, 1, 3, 5.
    return Hand([0, 1, 2, 3, 4, 5], 0b101011)


@pytest.fixture
def mock_player(mocker):
    """Create a mock player with a hand."""
    player = mocker.Mock(spec=BasePlayer)
    player.name = "TestPlayer"
    return player


@pytest.fixture
def mock_round(sample_hand, mocker):
    """Create a fully populated mock round."""
    game_round = mocker.Mock(spec=Round)
    game_round.turn_count = 5

    # Mock deck
    game_round.deck = mocker.Mock()
    game_round.deck.num_cards = 40
    game_round.deck.peek.return_value = 51  # King of Clubs

    # Mock discard pile
    game_round.discard_pile = mocker.Mock()
    game_round.discard_pile.num_cards = 1
    game_round.discard_pile.peek.return_value = 4  # 5 of Spades

    # Mock players
    game_round.player_names = ["TestPlayer"]
    game_round.current_player_idx = 0
    game_round.hands = [sample_hand]

    return game_round


class TestCardDisplay:
    """Tests for card display functionality."""

    def test_get_card_string_face_up(self, captured_renderer, sample_card_id):
        """Test that face-up cards are displayed correctly."""
        renderer, _ = captured_renderer
        card_text = renderer.get_card_string(sample_card_id)
        assert isinstance(card_text, Text)
        assert "A♠" in str(card_text)

    def test_get_card_string_face_down(self, captured_renderer):
        """Test that face-down cards show ?? with back color."""
        renderer, _ = captured_renderer
        # Masked ID for deck 0 is -1
        card_text = renderer.get_card_string(-1)
        assert isinstance(card_text, Text)
        assert "??" in str(card_text)

    def test_get_card_string_none_card(self, captured_renderer):
        """Test that None card shows ??."""
        renderer, _ = captured_renderer
        card_text = renderer.get_card_string(None)
        assert isinstance(card_text, Text)
        assert "??" in str(card_text)


class TestRendererDisplay:
    """Tests for display methods using captured output."""

    def test_display_drawn_card(self, captured_renderer):
        """Test displaying a drawn card."""
        renderer, output = captured_renderer
        event = CardDrawnDeckEvent(player_idx=0, card_id=0)
        renderer.display_drawn_card(event)
        assert "Player 0 drew:" in output.getvalue()
        assert "A♠" in output.getvalue()

    def test_display_discard_draw(self, captured_renderer):
        """Test displaying a discard pile draw."""
        renderer, output = captured_renderer
        event = CardDrawnDiscardEvent(player_idx=0, card_id=0)
        renderer.display_discard_draw(event)
        assert "Player 0 drew" in output.getvalue()
        assert "A♠" in output.getvalue()

    def test_display_replace_action(self, captured_renderer):
        """Test displaying a replace action."""
        renderer, output = captured_renderer
        event = CardSwappedEvent(
            player_idx=0, hand_index=2, new_card_id=0, old_card_id=1
        )
        renderer.display_replace_action(event)

        result = output.getvalue()
        assert "Player 0 replaced card" in result
        assert "A♠" in result
        assert "2♠" in result

    def test_display_flip_action(self, captured_renderer):
        """Test displaying a flip action."""
        renderer, output = captured_renderer
        event = CardFlippedEvent(player_idx=0, hand_index=1, card_id=0)
        renderer.display_flip_action(event)

        result = output.getvalue()
        assert "Player 0 flipped card" in result
        assert "A♠" in result

    def test_display_hand_output(self, captured_renderer, sample_hand):
        """Test that display_hand produces output with borders."""
        renderer, output = captured_renderer
        renderer.display_hand(sample_hand, display_indices=True)

        result = output.getvalue()
        assert "+" in result
        assert "|" in result
        assert "1" in result

    def test_display_discard_pile(self, captured_renderer, mock_round):
        """Test _display_discard_pile method."""
        renderer, output = captured_renderer
        renderer._display_discard_pile(mock_round)

        result = output.getvalue()
        assert "Discard Pile Top Card:" in result
        assert "5♠" in result

    def test_display_game_stats(self, captured_renderer, mock_player):
        """Test display_game_stats method formatting."""
        renderer, output = captured_renderer

        player_stats = PlayerStats(round_scores=[])
        player_stats.best_score = 42
        player_stats.worst_score = 99
        player_stats.average_score = 12.3456
        player_stats.total_score = 1000
        player_stats.round_scores = [1, 99]

        stats = {mock_player: player_stats}
        event = GameStatsEvent(stats=stats)
        renderer.display_game_stats(event)

        result = output.getvalue()
        assert "Game Statistics:" in result
        assert "TestPlayer" in result
        assert "Best Score: 42" in result
        assert "Worst Score: 99" in result


class TestColorValidation:
    """Tests for color validation."""

    @pytest.mark.parametrize(
        "valid_color",
        [
            pytest.param("red", id="simple_color"),
            pytest.param("#FF0000", id="hex_color"),
        ],
    )
    def test_validate_color_valid(self, captured_renderer, valid_color):
        """Test that valid colors pass validation."""
        renderer, _ = captured_renderer
        renderer.validate_color(valid_color)

    def test_handle_game_started(self, captured_renderer, mocker):
        """Test handle_game_started stores the list of players on the base class."""
        renderer, _ = captured_renderer
        player1 = mocker.Mock(spec=BasePlayer)
        player1.name = "Player 1"
        player2 = mocker.Mock(spec=BasePlayer)
        player2.name = "Player 2"
        event = GameStartedEvent(players=[player1, player2])

        renderer.handle_game_started(event)
        assert renderer.players == [player1, player2]
