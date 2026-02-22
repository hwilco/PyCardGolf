"""Tests for the HumanPlayer class."""

from unittest.mock import MagicMock

import pytest

from pycardgolf.core.actions import ActionDrawDeck
from pycardgolf.core.observation import Observation
from pycardgolf.core.phases import RoundPhase
from pycardgolf.interfaces.base import GameInput
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


def test_get_action_delegation(player, mock_input_handler, obs):
    """Test that HumanPlayer.get_action delegates to its input handler."""
    expected_action = ActionDrawDeck()
    mock_input_handler.get_action.return_value = expected_action

    action = player.get_action(obs)

    assert action == expected_action
    mock_input_handler.get_action.assert_called_once_with(player, obs)
