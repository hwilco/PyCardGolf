"""Tests for the CLI renderer using primitives."""

import io

import pytest
from rich.color import ColorParseError
from rich.console import Console
from rich.text import Text

from pycardgolf.core.event_bus import EventBus
from pycardgolf.core.events import (
    CardDiscardedEvent,
    CardDrawnDeckEvent,
    CardDrawnDiscardEvent,
    CardFlippedEvent,
    CardSwappedEvent,
    DeckReshuffledEvent,
    GameOverEvent,
    GameStartedEvent,
    GameStatsEvent,
    RoundEndEvent,
    RoundStartEvent,
    ScoreBoardEvent,
    TurnStartEvent,
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

    def test_wait_for_enter_windows(self, captured_renderer, mocker):
        """Test wait_for_enter on Windows (mocked)."""
        renderer, _ = captured_renderer
        renderer.delay = 1.0

        mock_msvcrt = mocker.patch("pycardgolf.interfaces.cli.cli_renderer.msvcrt")
        mock_msvcrt.kbhit.side_effect = [False, True]
        mock_msvcrt.getch.return_value = b"\r"

        mock_time = mocker.patch("pycardgolf.interfaces.cli.cli_renderer.time.time")
        mock_time.side_effect = [0, 0.01, 0.06, 0.1, 0.15]

        mock_sleep = mocker.patch("pycardgolf.interfaces.cli.cli_renderer.time.sleep")

        renderer.wait_for_enter()
        assert mock_msvcrt.kbhit.called
        assert mock_msvcrt.getch.called
        assert mock_sleep.called


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

    def test_get_card_text_face_up(self, captured_renderer, sample_card_id):
        """Test that face-up cards are displayed correctly."""
        renderer, _ = captured_renderer
        card_text = renderer.get_card_text(sample_card_id)
        assert isinstance(card_text, Text)
        assert "A♠" in str(card_text)

    def test_get_card_text_face_down(self, captured_renderer):
        """Test that face-down cards show ?? with back color."""
        renderer, _ = captured_renderer
        # Masked ID for deck 0 is -1
        card_text = renderer.get_card_text(-1)
        assert isinstance(card_text, Text)
        assert "??" in str(card_text)

    def test_get_card_text_none_card(self, captured_renderer):
        """Test that None card shows ??."""
        renderer, _ = captured_renderer
        card_text = renderer.get_card_text(None)
        assert isinstance(card_text, Text)
        assert "??" in str(card_text)

    def test_get_card_text_color_error(self, captured_renderer, mocker):
        """Test ColorParseError handling in get_card_text."""
        renderer, _ = captured_renderer

        mocker.patch(
            "pycardgolf.interfaces.cli.cli_renderer.Style",
            side_effect=ColorParseError("Invalid color"),
        )

        with pytest.raises(GameConfigError, match="Invalid color"):
            renderer.get_card_text(0)


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
        assert "4" in result  # Bottom row indices

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

        player_stats = PlayerStats(round_scores=[1, 99])
        player_stats.best_score = 42
        player_stats.worst_score = 99
        player_stats.average_score = 12.3456
        player_stats.total_score = 1000

        stats = {mock_player: player_stats}
        event = GameStatsEvent(stats=stats)
        renderer.display_game_stats(event)

        result = output.getvalue()
        assert "Game Statistics:" in result
        assert "TestPlayer" in result
        assert "Best Score: 42" in result
        assert "Worst Score: 99" in result
        assert "Average Score: 12.35" in result

    def test_create_draw_choice_prompt(self, captured_renderer):
        renderer, _ = captured_renderer
        prompt = renderer.create_draw_choice_prompt(0, 1)
        assert isinstance(prompt, Text)
        assert "Draw from (d)eck" in str(prompt)
        assert "A♠" in str(prompt)
        assert "2♠" in str(prompt)

    def test_display_round_start(self, captured_renderer):
        renderer, output = captured_renderer
        event = RoundStartEvent(round_num=1)
        renderer.display_round_start(event)
        assert "Starting Round 1" in output.getvalue()

    def test_display_round_end(self, captured_renderer, mock_player, sample_hand):
        renderer, output = captured_renderer
        event = RoundEndEvent(
            round_num=1, scores={mock_player: 10}, hands={mock_player: sample_hand}
        )
        renderer.display_round_end(event)
        assert "Round 1 End" in output.getvalue()
        assert "TestPlayer (Round Score: 10)" in output.getvalue()

    def test_display_scoreboard(self, captured_renderer, mock_player):
        renderer, output = captured_renderer
        event = ScoreBoardEvent(scores={mock_player: 50})
        renderer.display_scoreboard(event)
        assert "Current Scores:" in output.getvalue()
        assert "TestPlayer: 50" in output.getvalue()

    def test_display_game_over(self, captured_renderer, mock_player):
        renderer, output = captured_renderer
        event = GameOverEvent(winner=mock_player, winning_score=5)
        renderer.display_game_over(event)
        assert "Game Over" in output.getvalue()
        assert "Winner: TestPlayer" in output.getvalue()

    def test_display_standings(self, captured_renderer, mock_player):
        renderer, output = captured_renderer
        renderer.display_standings([(mock_player, 5)])
        assert "Final Standings:" in output.getvalue()
        assert "1. TestPlayer: 5" in output.getvalue()

    def test_display_initial_flip_prompts(self, captured_renderer, mock_player):
        renderer, output = captured_renderer
        renderer.display_initial_flip_prompt(mock_player, 2)
        assert "TestPlayer, draw start!" in output.getvalue()

        renderer.display_initial_flip_selection_prompt(1, 2)
        assert "Select card 1 of 2 to flip." in output.getvalue()

        renderer.display_initial_flip_error_already_selected()
        assert "You already selected that card" in output.getvalue()

    def test_display_final_turn_notification(self, captured_renderer, mock_player):
        renderer, output = captured_renderer
        renderer.display_final_turn_notification(mock_player)
        assert "TestPlayer has revealed all their cards!" in output.getvalue()

    def test_display_turn_start(
        self, captured_renderer, mock_player, sample_hand, mocker
    ):
        renderer, output = captured_renderer
        # With multiple players set
        p2 = mocker.Mock(spec=BasePlayer)
        p2.name = "OpponentPlayer"
        renderer.players = [mock_player, p2]

        event = TurnStartEvent(player_idx=0, hands=[sample_hand, sample_hand])
        renderer.display_turn_start(event)

        result = output.getvalue()
        assert "It's TestPlayer's turn." in result
        assert "OpponentPlayer's Hand (Next Player):" in result

        # Test fallback without players
        # RE-CREATE StringIO to clear buffer
        renderer.console.file = io.StringIO()
        renderer.players = []
        renderer.display_turn_start(event)
        result_fallback = renderer.console.file.getvalue()
        assert "It's Player 0's turn." in result_fallback

    def test_display_discard_action(self, captured_renderer):
        renderer, output = captured_renderer
        event = CardDiscardedEvent(player_idx=0, card_id=0)
        renderer.display_discard_action(event)
        assert "Player 0 discarded" in output.getvalue()

    def test_validate_color_invalid(self, captured_renderer):
        renderer, _ = captured_renderer
        with pytest.raises(GameConfigError, match="Invalid color"):
            renderer.validate_color("not-a-color")


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

    def test_display_deck_reshuffled(self, captured_renderer):
        """Test displaying a deck reshuffled notification."""
        renderer, output = captured_renderer
        event = DeckReshuffledEvent()
        renderer.display_deck_reshuffled(event)
        assert "The draw deck is empty! Reshuffling" in output.getvalue()
