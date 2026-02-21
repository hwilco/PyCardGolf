"""Tests for the CLI renderer."""

import io

import pytest
from rich.console import Console
from rich.text import Text

from pycardgolf.core.event_bus import EventBus
from pycardgolf.core.events import (
    CardDiscardedEvent,
    CardDrawnDeckEvent,
    CardDrawnDiscardEvent,
    CardFlippedEvent,
    CardSwappedEvent,
    GameOverEvent,
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
from pycardgolf.utils.card import Card, Rank, Suit
from pycardgolf.utils.deck import CardStack, Deck


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

    def test_wait_for_enter_windows_kbhit(self, mocker):
        """Test wait_for_enter logic when msvcrt is present (Windows)."""
        mock_msvcrt = mocker.patch("pycardgolf.interfaces.cli.cli_renderer.msvcrt")
        mock_time = mocker.patch("pycardgolf.interfaces.cli.cli_renderer.time")

        mock_time.time.side_effect = [0, 0.5, 0.9, 1.5]
        console = Console()
        event_bus = EventBus()
        renderer = CLIRenderer(event_bus, console, delay=1.0)

        mock_msvcrt.kbhit.side_effect = [False, True]
        renderer.wait_for_enter()
        assert mock_msvcrt.getch.called is True


@pytest.fixture
def sample_card():
    """Create a sample card for testing."""
    return Card(Rank.ACE, Suit.SPADES, "red", face_up=True)


@pytest.fixture
def sample_face_down_card():
    """Create a sample face-down card for testing."""
    return Card(Rank.KING, Suit.HEARTS, "blue", face_up=False)


@pytest.fixture
def sample_hand_cards():
    """Create a list of cards for a hand."""
    return [
        Card(Rank.ACE, Suit.SPADES, "red", face_up=True),
        Card(Rank.TWO, Suit.HEARTS, "red", face_up=True),
        Card(Rank.THREE, Suit.CLUBS, "red", face_up=False),
        Card(Rank.FOUR, Suit.DIAMONDS, "red", face_up=True),
        Card(Rank.FIVE, Suit.SPADES, "red", face_up=False),
        Card(Rank.SIX, Suit.HEARTS, "red", face_up=True),
    ]


@pytest.fixture
def mock_player(sample_hand_cards, mocker):
    """Create a mock player with a hand."""
    player = mocker.Mock(spec=BasePlayer)
    player.name = "TestPlayer"
    player.hand = Hand(sample_hand_cards)
    return player


@pytest.fixture
def mock_round(mock_player, mocker):
    """Create a fully populated mock round."""
    game_round = mocker.Mock(spec=Round)
    game_round.turn_count = 5

    # Mock deck
    deck = mocker.Mock(spec=Deck)
    deck.num_cards = 40
    top_deck_card = Card(Rank.KING, Suit.HEARTS, "red", face_up=False)
    deck.peek.return_value = top_deck_card
    game_round.deck = deck

    # Mock discard pile
    discard = mocker.Mock(spec=CardStack)
    discard_card = Card(Rank.FIVE, Suit.CLUBS, "red", face_up=True)
    discard.peek.return_value = discard_card
    game_round.discard_pile = discard

    # Mock players - create a list of players
    game_round.players = [mock_player]
    game_round.current_player_idx = 0

    return game_round


class TestCardDisplay:
    """Tests for card display functionality."""

    def test_get_card_string_face_up(self, captured_renderer, sample_card):
        """Test that face-up cards are displayed correctly."""
        renderer, _ = captured_renderer
        card_text = renderer.get_card_string(sample_card)
        assert isinstance(card_text, Text)
        assert "A♤" in str(card_text)

    def test_get_card_string_face_down(self, captured_renderer, sample_face_down_card):
        """Test that face-down cards show ?? with back color."""
        renderer, _ = captured_renderer
        card_text = renderer.get_card_string(sample_face_down_card)
        assert isinstance(card_text, Text)
        assert "??" in str(card_text)

    def test_get_card_string_none_card(self, captured_renderer):
        """Test that None card shows ?? with default blue back."""
        renderer, _ = captured_renderer
        card_text = renderer.get_card_string(None)
        assert isinstance(card_text, Text)
        assert "??" in str(card_text)
        # Default back color is blue, which is black text on blue background usually
        # but we just check it doesn't crash and returns Text.

    def test_get_card_string_invalid_color_raises(self, captured_renderer, mocker):
        """Test that invalid card colors raise GameConfigError."""
        renderer, _ = captured_renderer
        mock_card = mocker.Mock(spec=Card)
        mock_card.face_up = True
        mock_card.face_color = "invalid_color"
        with pytest.raises(GameConfigError, match="Invalid color"):
            renderer.get_card_string(mock_card)


class TestRendererDisplay:
    """Tests for display methods using captured output."""

    def test_display_drawn_card(self, captured_renderer, sample_card, mock_player):
        """Test displaying a drawn card."""
        renderer, output = captured_renderer
        event = CardDrawnDeckEvent(player_idx=0, card=sample_card)
        renderer.display_drawn_card(event)
        assert "Player 0 drew:" in output.getvalue()
        assert "A♤" in output.getvalue()

    def test_display_discard_draw(self, captured_renderer, sample_card, mock_player):
        """Test displaying a discard pile draw."""
        renderer, output = captured_renderer
        event = CardDrawnDiscardEvent(player_idx=0, card=sample_card)
        renderer.display_discard_draw(event)
        assert "Player 0 drew" in output.getvalue()
        assert "A♤" in output.getvalue()

    def test_display_replace_action(self, captured_renderer, mock_player):
        """Test displaying a replace action."""
        renderer, output = captured_renderer
        new_card = Card(Rank.ACE, Suit.SPADES, "red", face_up=True)
        old_card = Card(Rank.TWO, Suit.HEARTS, "red", face_up=True)

        event = CardSwappedEvent(
            player_idx=0, hand_index=2, new_card=new_card, old_card=old_card
        )
        renderer.display_replace_action(event)

        result = output.getvalue()
        assert "Player 0 replaced card" in result
        assert "A♤" in result
        assert "2♡" in result

    def test_display_flip_action(self, captured_renderer, sample_card, mock_player):
        """Test displaying a flip action."""
        renderer, output = captured_renderer
        event = CardFlippedEvent(player_idx=0, hand_index=1, card=sample_card)
        renderer.display_flip_action(event)

        result = output.getvalue()
        assert "Player 0 flipped card" in result
        assert "A♤" in result

    def test_display_hand_output(self, captured_renderer, mock_player):
        """Test that display_hand produces output with borders."""
        renderer, output = captured_renderer
        renderer.display_hand(mock_player, display_indices=True)

        result = output.getvalue()
        assert "+" in result
        assert "|" in result
        # Should contain indices since display_indices=True
        assert "1" in result

    def test_display_hand_without_indices(self, captured_renderer, mock_player):
        """Test display_hand without indices."""
        renderer, output = captured_renderer
        renderer.display_hand(mock_player, display_indices=False)

        result = output.getvalue()
        assert "+" in result
        assert "|" in result

    def test_display_discard_pile(self, captured_renderer, mocker):
        """Test _display_discard_pile method."""
        renderer, output = captured_renderer

        # Create mock Round object with discard pile
        game_round = mocker.Mock(spec=Round)
        discard = mocker.Mock(spec=CardStack)
        discard_card = Card(Rank.QUEEN, Suit.DIAMONDS, "red", face_up=True)
        discard.peek.return_value = discard_card
        game_round.discard_pile = discard

        renderer._display_discard_pile(game_round)

        result = output.getvalue()
        assert "Discard Pile Top Card:" in result
        assert "Q♢" in result

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
        assert "Average Score: 12.35" in result
        assert "Total Score: 1000" in result
        assert "Round Scores: 1, 99" in result


class TestColorValidation:
    """Tests for color validation."""

    @pytest.mark.parametrize(
        "valid_color",
        [
            pytest.param("red", id="simple_color"),
            pytest.param("blue", id="another_color"),
            pytest.param("green", id="third_color"),
            pytest.param("#FF0000", id="hex_color"),
            pytest.param("rgb(255,0,0)", id="rgb_color"),
        ],
    )
    def test_validate_color_valid(self, captured_renderer, valid_color):
        """Test that valid colors pass validation."""
        renderer, _ = captured_renderer
        renderer.validate_color(valid_color)

    def test_validate_color_invalid(self, captured_renderer):
        """Test that invalid colors raise GameConfigError."""
        renderer, _ = captured_renderer
        with pytest.raises(GameConfigError, match="Invalid color"):
            renderer.validate_color("notacolorstring")


class TestRendererGameFlow:
    """Tests for game lifecycle display methods in CLIRenderer."""

    def test_display_round_end(self, captured_renderer, mock_player):
        renderer, output = captured_renderer
        # Ensure all cards are face up for calculate_score
        for card in mock_player.hand:
            card.face_up = True
        scores = {mock_player: 10}
        event = RoundEndEvent(scores=scores, round_num=1)
        renderer.display_round_end(event)
        result = output.getvalue()
        assert "Round 1 End" in result
        assert "TestPlayer" in result

    def test_create_draw_choice_prompt(self, captured_renderer, sample_card):
        renderer, _ = captured_renderer
        prompt = renderer.create_draw_choice_prompt(sample_card, sample_card)
        assert isinstance(prompt, Text)
        assert "Draw from (d)eck" in str(prompt)
        assert "or (p)ile" in str(prompt)

    def test_display_turn_start(self, captured_renderer, mock_player):
        renderer, output = captured_renderer
        event = TurnStartEvent(player_idx=0)
        renderer.display_turn_start(event)
        result = output.getvalue()
        assert "It's Player 0's turn" in result

    def test_display_turn_start_with_next(self, captured_renderer, mock_player, mocker):
        renderer, output = captured_renderer

        mock_player2 = mocker.Mock(spec=BasePlayer)
        mock_player2.name = "Opponent"
        mock_player2.hand = Hand([])

        renderer.players = [mock_player, mock_player2]

        event = TurnStartEvent(player_idx=0)
        renderer.display_turn_start(event)

        result = output.getvalue()
        assert "It's TestPlayer's turn." in result
        assert "Opponent's Hand (Next Player):" in result
        assert "TestPlayer's Hand (Current Player):" in result

    def test_display_discard_action(self, captured_renderer, mock_player, sample_card):
        renderer, output = captured_renderer
        event = CardDiscardedEvent(player_idx=0, card=sample_card)
        renderer.display_discard_action(event)
        assert "Player 0 discarded" in output.getvalue()

    def test_display_round_start(self, captured_renderer):
        renderer, output = captured_renderer
        event = RoundStartEvent(round_num=1)
        renderer.display_round_start(event)
        assert "Starting Round 1" in output.getvalue()

    def test_display_scores(self, captured_renderer, mock_player):
        renderer, output = captured_renderer
        event = ScoreBoardEvent(scores={mock_player: 10})
        renderer.display_scoreboard(event)
        result = output.getvalue()
        assert "Current Scores:" in result
        assert "TestPlayer: 10" in result

    def test_display_game_over(self, captured_renderer):
        renderer, output = captured_renderer
        event = GameOverEvent(winner=mock_player, winning_score=10)
        renderer.display_game_over(event)
        assert "Game Over" in output.getvalue()

    def test_display_standings(self, captured_renderer, mock_player):
        renderer, output = captured_renderer
        event = ScoreBoardEvent(scores={}, standings=[(mock_player, 10)])
        renderer.display_standings(event.standings)
        result = output.getvalue()
        assert "Final Standings:" in result
        assert "1. TestPlayer: 10" in result

    def test_display_initial_flip_prompt(self, captured_renderer, mock_player):
        renderer, output = captured_renderer
        renderer.display_initial_flip_prompt(mock_player, 2)
        result = output.getvalue()
        assert "TestPlayer, draw start!" in result
        assert "Select 2 cards to flip." in result

    def test_display_initial_flip_selection_prompt(self, captured_renderer):
        renderer, output = captured_renderer
        renderer.display_initial_flip_selection_prompt(1, 2)
        assert "Select card 1 of 2 to flip." in output.getvalue()

    def test_display_initial_flip_error_already_selected(self, captured_renderer):
        renderer, output = captured_renderer
        renderer.display_initial_flip_error_already_selected()
        assert "You already selected that card." in output.getvalue()

    def test_display_final_turn_notification(self, captured_renderer, mock_player):
        renderer, output = captured_renderer
        renderer.display_final_turn_notification(mock_player)
        result = output.getvalue()
        assert "TestPlayer has revealed all their cards!" in result

    def test_display_initial_flip_choices(self, captured_renderer, mock_player):
        renderer, output = captured_renderer
        renderer.display_initial_flip_choices(mock_player, [0, 1])
        result = output.getvalue()
        assert "TestPlayer flipped initial cards:" in result
