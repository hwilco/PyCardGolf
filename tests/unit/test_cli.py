"""Tests for the CLI interface coordination."""

import pytest
from rich.console import Console

from pycardgolf.core.player import Player
from pycardgolf.interfaces.base import ActionChoice, DrawSource, FlipChoice
from pycardgolf.interfaces.cli import CLIInterface
from pycardgolf.interfaces.cli_input import CLIInputHandler
from pycardgolf.interfaces.cli_renderer import CLIRenderer
from pycardgolf.utils.card import Card, Rank, Suit


@pytest.fixture
def mock_console(mocker):
    """Create a mock console."""
    return mocker.Mock(spec=Console)


@pytest.fixture
def mock_renderer(mocker):
    """Create a mock renderer."""
    return mocker.Mock(spec=CLIRenderer)


@pytest.fixture
def mock_input_handler(mocker):
    """Create a mock input handler."""
    return mocker.Mock(spec=CLIInputHandler)


@pytest.fixture
def cli(mock_console, mock_renderer, mock_input_handler, mocker):
    """Create a CLI interface with mocked components."""
    mocker.patch("pycardgolf.interfaces.cli.Console", return_value=mock_console)
    mocker.patch("pycardgolf.interfaces.cli.CLIRenderer", return_value=mock_renderer)
    mocker.patch(
        "pycardgolf.interfaces.cli.CLIInputHandler", return_value=mock_input_handler
    )

    return CLIInterface()


@pytest.fixture
def sample_card():
    """Create a sample card for testing."""
    return Card(Rank.ACE, Suit.SPADES, "red", face_up=True)


@pytest.fixture
def mock_player(mocker):
    """Create a mock player."""
    player = mocker.Mock(spec=Player)
    player.name = "TestPlayer"
    return player


class TestCLIInterfaceCoordination:
    """Tests that CLIInterface delegates correctly to its components."""

    def test_init(self, mock_console, mocker):
        """Test initialization creates components."""
        mock_cons_cls = mocker.patch(
            "pycardgolf.interfaces.cli.Console", return_value=mock_console
        )
        mock_rend_cls = mocker.patch("pycardgolf.interfaces.cli.CLIRenderer")
        mock_inp_cls = mocker.patch("pycardgolf.interfaces.cli.CLIInputHandler")

        interface = CLIInterface(delay=1.5)

        mock_cons_cls.assert_called_once()
        mock_rend_cls.assert_called_once_with(mock_console)
        mock_inp_cls.assert_called_once_with(mock_console, 1.5)
        assert interface.console == mock_console

    def test_wait_for_enter(self, cli):
        """Test wait_for_enter delegation."""
        cli.wait_for_enter()
        cli.input_handler.wait_for_enter.assert_called_once()

    def test_display_state(self, cli, mocker):
        """Test display_state delegation."""
        game = mocker.Mock()
        cli.display_state(game)
        cli.renderer.display_state.assert_called_once_with(game)

    def test_display_round_end(self, cli, mocker):
        """Test display_round_end delegation."""
        game = mocker.Mock()
        cli.display_round_end(game)
        cli.renderer.display_round_end.assert_called_once_with(game)

    def test_display_hand(self, cli, mock_player):
        """Test display_hand delegation."""
        cli.display_hand(mock_player, display_indices=True)
        cli.renderer.display_hand.assert_called_once_with(mock_player, True)

    def test_get_input(self, cli):
        """Test get_input delegation."""
        cli.input_handler.get_input.return_value = "foo"
        result = cli.get_input("prompt")
        assert result == "foo"
        cli.input_handler.get_input.assert_called_once_with("prompt")

    def test_validate_color(self, cli):
        """Test validate_color delegation."""
        cli.validate_color("red")
        cli.renderer.validate_color.assert_called_once_with("red")


class TestGameChoices:
    """Tests for game-specific user choice logic in CLIInterface."""

    @pytest.mark.parametrize(
        ("input_char", "expected_source"),
        [
            pytest.param("d", DrawSource.DECK, id="deck"),
            pytest.param("p", DrawSource.DISCARD, id="discard"),
        ],
    )
    def test_get_draw_choice(self, cli, sample_card, input_char, expected_source):
        """Test choosing draw source delegates and returns enum."""
        # Setup mock to return input_char
        cli.input_handler.get_valid_input.return_value = input_char
        deck_card = sample_card
        discard_card = sample_card  # Reuse for simplicity

        result = cli.get_draw_choice(deck_card, discard_card)

        assert result == expected_source
        cli.renderer.create_draw_choice_prompt.assert_called_once_with(
            deck_card, discard_card
        )
        cli.input_handler.get_valid_input.assert_called_once()

    @pytest.mark.parametrize(
        ("input_char", "expected_choice"),
        [
            pytest.param("k", ActionChoice.KEEP, id="keep"),
            pytest.param("d", ActionChoice.DISCARD, id="discard"),
        ],
    )
    def test_get_keep_or_discard_choice(self, cli, input_char, expected_choice):
        """Test keep/discard choice."""
        cli.input_handler.get_valid_input.return_value = input_char
        assert cli.get_keep_or_discard_choice() == expected_choice

    @pytest.mark.parametrize(
        ("input_char", "expected_choice"),
        [
            pytest.param("y", FlipChoice.YES, id="yes"),
            pytest.param("n", FlipChoice.NO, id="no"),
        ],
    )
    def test_get_flip_choice(self, cli, input_char, expected_choice):
        """Test flip choice."""
        cli.input_handler.get_valid_input.return_value = input_char
        assert cli.get_flip_choice() == expected_choice

    def test_get_index_to_replace(self, cli):
        """Test getting index to replace."""
        cli.input_handler.get_valid_input.return_value = 4
        result = cli.get_index_to_replace()
        assert result == 4
        cli.input_handler.get_valid_input.assert_called_once()

    def test_get_index_to_flip(self, cli):
        """Test getting index to flip."""
        cli.input_handler.get_valid_input.return_value = 2
        result = cli.get_index_to_flip()
        assert result == 2
        cli.input_handler.get_valid_input.assert_called_once()

    def test_get_initial_cards_to_flip(self, cli, mock_player, mocker):
        """Test initial card flip loop logic."""
        # Mock get_index_to_flip to return 0, 0, 1
        # We need to patch the method on the instance
        cli.get_index_to_flip = mocker.Mock(side_effect=[0, 0, 1])

        # Mock player hand items so we can set face_up
        card0 = mocker.Mock(face_up=False)
        card1 = mocker.Mock(face_up=False)
        mock_player.hand = [card0, card1, mocker.Mock(), mocker.Mock()]

        result = cli.get_initial_cards_to_flip(mock_player, 2)

        assert result == [0, 1]
        assert card0.face_up is True
        assert card1.face_up is True

        # Verify calls
        cli.renderer.display_initial_flip_prompt.assert_called_once()
        cli.renderer.display_initial_flip_error_already_selected.assert_called_once()
        # display_hand called initially + once per successful flip (2) = 3 times
        assert cli.renderer.display_hand.call_count == 3
