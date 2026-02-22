"""Tests for the CLI input handler."""

import pytest
from rich.console import Console

from pycardgolf.core.actions import (
    ActionDiscardDrawn,
    ActionDrawDeck,
    ActionFlipCard,
    ActionPass,
    ActionSwapCard,
)
from pycardgolf.core.hand import Hand
from pycardgolf.core.observation import Observation
from pycardgolf.core.phases import RoundPhase
from pycardgolf.exceptions import GameExitError
from pycardgolf.interfaces.cli import CLIInputHandler, CLIRenderer
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
def input_handler(mock_console, mock_renderer):
    """Create a CLI input handler with a mock console and renderer."""
    return CLIInputHandler(mock_console, mock_renderer)


@pytest.fixture
def mock_player(mocker):
    """Create a mock player."""
    player = mocker.Mock()
    player.name = "Test Player"
    player.hand = [mocker.Mock() for _ in range(6)]
    for card in player.hand:
        card.face_up = False
    return player


@pytest.fixture
def base_obs():
    """Create a base observation fixture."""
    return Observation(
        my_hand=Hand([Card(Rank.ACE, Suit.SPADES, "blue") for _ in range(6)]),
        other_hands={},
        discard_top=None,
        deck_size=52,
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
        # First return invalid, then valid
        mock_console.input.side_effect = ["invalid", "d"]

        result = input_handler.get_choice(
            "Choose: ", valid_options=["d", "p"], error_msg="Invalid input."
        )

        assert result == "d"
        # Check that error message was printed
        mock_console.print.assert_any_call("Invalid input.")

    @pytest.mark.parametrize(
        "quit_input",
        [
            pytest.param("q", id="q"),
            pytest.param("quit", id="quit"),
            pytest.param("Q", id="Q"),
            pytest.param("QUIT", id="QUIT"),
        ],
    )
    def test_get_choice_quit(self, input_handler, mock_console, quit_input):
        """Test that quit inputs raise GameExitError."""
        mock_console.input.return_value = quit_input
        with pytest.raises(GameExitError):
            input_handler.get_choice("Choose: ", valid_options=["a", "b"])

    def test_get_validated_input_quit(self, input_handler, mock_console):
        """Test that quit input in get_validated_input raises GameExitError."""
        mock_console.input.return_value = "q"
        with pytest.raises(GameExitError):
            input_handler.get_validated_input("Prompt: ", lambda x: x)


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
        # Inputs: 'k' for keep choice, then '2' for replacement index
        mock_console.input.side_effect = ["k", "2"]

        action = input_handler.get_action(mock_player, base_obs)

        assert isinstance(action, ActionSwapCard)
        assert action.hand_index == 1

    def test_get_action_action_phase_discard(
        self, input_handler, mock_console, mock_player, base_obs
    ):
        """Test action phase: discard drawn."""
        base_obs.phase = RoundPhase.ACTION
        base_obs.can_discard_drawn = True
        mock_console.input.return_value = "d"

        action = input_handler.get_action(mock_player, base_obs)

        assert isinstance(action, ActionDiscardDrawn)

    def test_get_action_flip_phase_yes(
        self, input_handler, mock_console, mock_player, base_obs
    ):
        """Test flip phase: yes and select index."""
        base_obs.phase = RoundPhase.FLIP
        # Inputs: 'y' for flip choice, then '3' for flip index
        mock_console.input.side_effect = ["y", "3"]

        action = input_handler.get_action(mock_player, base_obs)

        assert isinstance(action, ActionFlipCard)
        assert action.hand_index == 2

    def test_get_action_flip_phase_no(
        self, input_handler, mock_console, mock_player, base_obs
    ):
        """Test flip phase: no."""
        base_obs.phase = RoundPhase.FLIP
        mock_console.input.return_value = "n"

        action = input_handler.get_action(mock_player, base_obs)

        assert isinstance(action, ActionPass)

    def test_get_action_finished_phase(self, input_handler, mock_player, base_obs):
        """Test finished phase fallback."""
        base_obs.phase = RoundPhase.FINISHED
        action = input_handler.get_action(mock_player, base_obs)
        assert isinstance(action, ActionPass)


class TestInputHandlerHelpers:
    """Tests for private helper methods and card index validation."""

    def test_validate_card_index_valid(self, input_handler):
        """Test valid card index strings."""
        assert input_handler._validate_card_index("1") == 0
        assert input_handler._validate_card_index("6") == 5

    def test_validate_card_index_out_of_range(self, input_handler):
        """Test that out-of-range indices raise ValueError."""
        with pytest.raises(ValueError, match="Card index must be between"):
            input_handler._validate_card_index("0")
        with pytest.raises(ValueError, match="Card index must be between"):
            input_handler._validate_card_index("7")

    def test_validate_card_index_non_numeric(self, input_handler):
        """Test that non-numeric strings raise ValueError."""
        with pytest.raises(ValueError, match="Not a valid number"):
            input_handler._validate_card_index("abc")

    def test_get_valid_flip_index_filtering(
        self, input_handler, mock_console, mock_player, base_obs
    ):
        """Test filtration of face-up cards."""
        # Index 0, 1 are face up
        base_obs.my_hand[0].face_up = True
        base_obs.my_hand[1].face_up = True
        # User tries to pick '1', then picks '3'
        mock_console.input.side_effect = ["1", "3"]

        result = input_handler._get_valid_flip_index(mock_player, base_obs)

        assert result == 2
        # Should have printed error for '1'
        mock_console.print.assert_called()
