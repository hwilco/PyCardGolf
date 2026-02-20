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
from pycardgolf.core.state import Observation, RoundPhase
from pycardgolf.interfaces.base import (
    ActionChoice,
    DrawSource,
    FlipChoice,
    GameInput,
)
from pycardgolf.players.human import HumanPlayer
from pycardgolf.utils.card import Card, Rank, Suit
from pycardgolf.utils.constants import HAND_SIZE


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
    mock_input_handler.get_index_to_flip.return_value = 2

    action = player.get_action(obs)

    assert isinstance(action, ActionFlipCard)
    assert action.hand_index == 2
    mock_input_handler.display_hand.assert_called_once()


def test_get_action_draw_phase(player, mock_input_handler, obs):
    """Draw phase: player draws from deck or discard."""
    obs.phase = RoundPhase.DRAW

    mock_input_handler.get_draw_choice.return_value = DrawSource.DECK
    action = player.get_action(obs)
    assert isinstance(action, ActionDrawDeck)

    mock_input_handler.get_draw_choice.return_value = DrawSource.DISCARD
    action = player.get_action(obs)
    assert isinstance(action, ActionDrawDiscard)


def test_get_action_action_phase_keep_and_swap(player, mock_input_handler, obs):
    """Action phase: player keeps and swaps a card."""
    obs.phase = RoundPhase.ACTION
    obs.drawn_card = Card(Rank.KING, Suit.HEARTS, "blue")
    obs.can_discard_drawn = True

    mock_input_handler.get_keep_or_discard_choice.return_value = ActionChoice.KEEP
    mock_input_handler.get_index_to_replace.return_value = 1

    action = player.get_action(obs)
    assert isinstance(action, ActionSwapCard)
    assert action.hand_index == 1


def test_get_action_action_phase_discard_drawn(player, mock_input_handler, obs):
    """Action phase: player discards the drawn card."""
    obs.phase = RoundPhase.ACTION
    obs.drawn_card = Card(Rank.KING, Suit.HEARTS, "blue")
    obs.can_discard_drawn = True

    mock_input_handler.get_keep_or_discard_choice.return_value = ActionChoice.DISCARD

    action = player.get_action(obs)
    assert isinstance(action, ActionDiscardDrawn)


def test_get_action_flip_phase_yes(player, mock_input_handler, obs):
    """Flip phase: player flips a card."""
    obs.phase = RoundPhase.FLIP

    mock_input_handler.get_flip_choice.return_value = FlipChoice.YES
    mock_input_handler.get_valid_flip_index.return_value = 3

    action = player.get_action(obs)
    assert isinstance(action, ActionFlipCard)
    assert action.hand_index == 3


def test_get_action_flip_phase_no(player, mock_input_handler, obs):
    """Flip phase: player passes."""
    obs.phase = RoundPhase.FLIP

    mock_input_handler.get_flip_choice.return_value = FlipChoice.NO

    action = player.get_action(obs)
    assert isinstance(action, ActionPass)
