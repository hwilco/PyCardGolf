"""Tests for the CLI input handler using primitives."""

import pytest
from rich.console import Console

from pycardgolf.core.actions import (
    ActionDrawDeck,
    ActionFlipCard,
    ActionPass,
    ActionSwapCard,
)
from pycardgolf.core.observation import Observation
from pycardgolf.core.phases import RoundPhase
from pycardgolf.exceptions import GameExitError
from pycardgolf.interfaces.cli import CLIInputHandler, CLIRenderer
from pycardgolf.utils.constants import HAND_SIZE
from pycardgolf.utils.deck import CARDS_PER_DECK


@pytest.fixture
def mock_console(mocker):
    """Create a mock console."""
    return mocker.Mock(spec=Console)


@pytest.fixture
def mock_renderer(mocker):
    """Create a mock renderer."""
    return mocker.Mock(spec=CLIRenderer)


@pytest.fixture
def input_handler(mock_console, mock_renderer):
    """Create a CLI input handler with a mock console and renderer."""
    return CLIInputHandler(mock_console, mock_renderer)


@pytest.fixture
def mock_player(mocker):
    """Create a mock player."""
    player = mocker.Mock()
    player.name = "Test Player"
    return player


@pytest.fixture
def base_obs():
    """Create a base observation fixture."""
    return Observation(
        my_hand=[-1] * HAND_SIZE,
        other_hands={},
        discard_top=None,
        deck_size=CARDS_PER_DECK,
        deck_top=None,
        current_player_name="Test Player",
        phase=RoundPhase.SETUP,
        valid_actions=[],
    )


class TestInputHandlerValidation:
    """Tests for user input validation in CLIInputHandler."""

    def test_get_input(self, input_handler, mock_console):
        """Test basic input retrieval."""
        mock_console.input.return_value = "test"
        result = input_handler.get_input("Prompt: ")
        assert result == "test"
        mock_console.input.assert_called_once_with("Prompt: ")

    def test_get_choice_with_valid_options(self, input_handler, mock_console):
        """Test that valid options are accepted."""
        mock_console.input.return_value = "d"
        result = input_handler.get_choice(
            "Choose: ", valid_options=["d", "p"], error_msg="Invalid"
        )
        assert result == "d"

    def test_get_choice_retries_on_invalid(self, input_handler, mock_console):
        """Test that invalid input causes retry."""
        mock_console.input.side_effect = ["invalid", "d"]
        result = input_handler.get_choice(
            "Choose: ", valid_options=["d", "p"], error_msg="Invalid input."
        )
        assert result == "d"
        mock_console.print.assert_any_call("Invalid input.")

    @pytest.mark.parametrize(
        "quit_input",
        ["q", "quit", "Q", "QUIT"],
    )
    def test_get_choice_quit(self, input_handler, mock_console, quit_input):
        """Test that quit inputs raise GameExitError."""
        mock_console.input.return_value = quit_input
        with pytest.raises(GameExitError):
            input_handler.get_choice("Choose: ", valid_options=["a", "b"])


class TestInputHandlerGetAction:
    """Tests for the consolidated get_action method."""

    def test_get_action_setup_phase(
        self, input_handler, mock_console, mock_player, base_obs
    ):
        """Test setup phase routing."""
        base_obs.phase = RoundPhase.SETUP
        mock_console.input.return_value = "1"
        action = input_handler.get_action(mock_player, base_obs)
        assert isinstance(action, ActionFlipCard)
        assert action.hand_index == 0

    def test_get_action_draw_phase(
        self, input_handler, mock_console, mock_player, base_obs
    ):
        """Test draw phase routing."""
        base_obs.phase = RoundPhase.DRAW
        mock_console.input.return_value = "d"
        action = input_handler.get_action(mock_player, base_obs)
        assert isinstance(action, ActionDrawDeck)

    def test_get_action_action_phase_keep_and_swap(
        self, input_handler, mock_console, mock_player, base_obs
    ):
        """Test action phase: keep and swap."""
        base_obs.phase = RoundPhase.ACTION
        base_obs.can_discard_drawn = True
        mock_console.input.side_effect = ["k", "2"]
        action = input_handler.get_action(mock_player, base_obs)
        assert isinstance(action, ActionSwapCard)
        assert action.hand_index == 1

    def test_get_action_flip_phase_no(
        self, input_handler, mock_console, mock_player, base_obs
    ):
        """Test flip phase: no."""
        base_obs.phase = RoundPhase.FLIP
        mock_console.input.return_value = "n"
        action = input_handler.get_action(mock_player, base_obs)
        assert isinstance(action, ActionPass)


class TestInputHandlerHelpers:
    """Tests for private helper methods and card index validation."""

    def test_validate_card_index_valid(self, input_handler):
        """Test valid card index strings."""
        assert input_handler._validate_card_index("1") == 0
        assert input_handler._validate_card_index("6") == 5

    def test_get_valid_flip_index_filtering(
        self, input_handler, mock_console, mock_player, base_obs
    ):
        """Test filtration of face-up cards."""
        # Index 0 is face up (-1 is bitmask for ID 0 but in observation it's filtered)
        # The visibility is encoded in the ID (negative for hidden).
        base_obs.my_hand[0] = 0  # Face up
        base_obs.my_hand[1] = -1  # Face down

        # User tries to pick '1' (already face up), then picks '2'
        mock_console.input.side_effect = ["1", "2"]
        result = input_handler._get_valid_flip_index(mock_player, base_obs)
        assert result == 1
