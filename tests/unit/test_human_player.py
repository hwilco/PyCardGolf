"""Tests for the HumanPlayer class."""

from unittest.mock import MagicMock

import pytest

from pycardgolf.core.actions import (
    ActionDiscardDrawn,
    ActionDrawDeck,
    ActionDrawDiscard,
    ActionFlipCard,
    ActionPass,
    ActionSwapCard,
)
from pycardgolf.core.observation import Observation
from pycardgolf.core.phases import RoundPhase
from pycardgolf.interfaces.base import GameInput
from pycardgolf.players.human import HumanPlayer
from pycardgolf.utils.card import Card, Rank, Suit
from pycardgolf.utils.constants import HAND_SIZE
from pycardgolf.utils.enums import DrawSourceChoice, KeepOrDiscardChoice


@pytest.fixture
def mock_input_handler():
    """Create a mock GameInput handler."""
    return MagicMock(spec=GameInput)


@pytest.fixture
def player(mock_input_handler):
    """Create a HumanPlayer with a mocked input handler."""
    p = HumanPlayer("Test Player", mock_input_handler)
    # Provide a dummy hand
    p.hand = [Card(Rank.ACE, Suit.SPADES, "blue") for _ in range(HAND_SIZE)]
    return p


@pytest.fixture
def obs():
    """Create a minimal Observation for testing."""
    return Observation(
        my_hand=[Card(Rank.ACE, Suit.SPADES, "blue") for _ in range(HAND_SIZE)],
        other_hands={},
        discard_top=Card(Rank.ACE, Suit.SPADES, "blue"),
        deck_size=50,
        deck_top=None,
        current_player_name="Test Player",
        phase=RoundPhase.SETUP,
        valid_actions=[],
    )


def test_get_action_setup_phase(player, mock_input_handler, obs):
    """Setup phase: player flips a face-down card."""
    obs.phase = RoundPhase.SETUP
    mock_input_handler.get_valid_flip_index.return_value = 2

    action = player.get_action(obs)

    assert isinstance(action, ActionFlipCard)
    assert action.hand_index == 2
    mock_input_handler.get_valid_flip_index.assert_called_once_with(player)


def test_get_action_draw_phase(player, mock_input_handler, obs):
    """Draw phase: player draws from deck or discard."""
    obs.phase = RoundPhase.DRAW
    obs.deck_top = Card(Rank.KING, Suit.HEARTS, "blue")
    obs.discard_top = Card(Rank.ACE, Suit.SPADES, "blue")

    mock_input_handler.get_draw_choice.return_value = DrawSourceChoice.DECK
    action = player.get_action(obs)
    assert isinstance(action, ActionDrawDeck)
    mock_input_handler.get_draw_choice.assert_called_with(
        player, obs.deck_top, obs.discard_top
    )

    mock_input_handler.get_draw_choice.return_value = DrawSourceChoice.DISCARD_PILE
    action = player.get_action(obs)
    assert isinstance(action, ActionDrawDiscard)


def test_get_action_action_phase_keep_and_swap(player, mock_input_handler, obs):
    """Action phase: player keeps and swaps a card."""
    obs.phase = RoundPhase.ACTION
    obs.drawn_card = Card(Rank.KING, Suit.HEARTS, "blue")
    obs.can_discard_drawn = True

    mock_input_handler.get_keep_or_discard_choice.return_value = (
        KeepOrDiscardChoice.KEEP
    )
    mock_input_handler.get_index_to_replace.return_value = 1

    action = player.get_action(obs)
    assert isinstance(action, ActionSwapCard)
    assert action.hand_index == 1
    mock_input_handler.get_keep_or_discard_choice.assert_called_once_with(player)
    mock_input_handler.get_index_to_replace.assert_called_once_with(player)


def test_get_action_action_phase_discard_drawn(player, mock_input_handler, obs):
    """Action phase: player discards the drawn card."""
    obs.phase = RoundPhase.ACTION
    obs.drawn_card = Card(Rank.KING, Suit.HEARTS, "blue")
    obs.can_discard_drawn = True

    mock_input_handler.get_keep_or_discard_choice.return_value = (
        KeepOrDiscardChoice.DISCARD
    )

    action = player.get_action(obs)
    assert isinstance(action, ActionDiscardDrawn)


def test_get_action_flip_phase_yes(player, mock_input_handler, obs):
    """Flip phase: player flips a card."""
    obs.phase = RoundPhase.FLIP

    mock_input_handler.get_flip_choice.return_value = True
    mock_input_handler.get_valid_flip_index.return_value = 3

    action = player.get_action(obs)
    assert isinstance(action, ActionFlipCard)
    assert action.hand_index == 3
    mock_input_handler.get_flip_choice.assert_called_once_with(player)
    mock_input_handler.get_valid_flip_index.assert_called_once_with(player)


def test_get_action_flip_phase_no(player, mock_input_handler, obs):
    """Flip phase: player passes."""
    obs.phase = RoundPhase.FLIP

    mock_input_handler.get_flip_choice.return_value = False

    action = player.get_action(obs)
    assert isinstance(action, ActionPass)


def test_get_action_finished_phase_fallback(player, obs):
    """Test that get_action returns ActionPass for FINISHED phase."""
    obs.phase = RoundPhase.FINISHED
    action = player.get_action(obs)
    assert isinstance(action, ActionPass)


def test_get_action_action_phase_no_discard(player, mock_input_handler, obs):
    """Action phase: can_discard_drawn=False skips discard prompt."""
    obs.phase = RoundPhase.ACTION
    obs.drawn_card = Card(Rank.KING, Suit.HEARTS, "blue")
    obs.can_discard_drawn = False

    mock_input_handler.get_index_to_replace.return_value = 1

    action = player.get_action(obs)
    assert isinstance(action, ActionSwapCard)
    assert action.hand_index == 1
    mock_input_handler.get_keep_or_discard_choice.assert_not_called()
    mock_input_handler.get_index_to_replace.assert_called_once_with(player)
