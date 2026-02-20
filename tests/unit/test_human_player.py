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
    GameInterface,
)
from pycardgolf.players.human import HumanPlayer
from pycardgolf.utils.card import Card, Rank, Suit
from pycardgolf.utils.constants import HAND_SIZE


@pytest.fixture
def mock_interface():
    return MagicMock(spec=GameInterface)


@pytest.fixture
def player(mock_interface):
    p = HumanPlayer("Test Player", mock_interface)
    # Set up a dummy hand
    p.hand = [Card(Rank.ACE, Suit.SPADES, "blue") for _ in range(HAND_SIZE)]
    return p


@pytest.fixture
def obs():
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


def test_get_action_setup_phase(player, mock_interface, obs):
    obs.phase = RoundPhase.SETUP

    # Mock user input
    mock_interface.get_index_to_flip.return_value = 2

    action = player.get_action(obs)

    assert isinstance(action, ActionFlipCard)
    assert action.hand_index == 2
    mock_interface.display_hand.assert_called_once()


def test_get_action_draw_phase(player, mock_interface, obs):
    obs.phase = RoundPhase.DRAW

    # User chooses Deck
    mock_interface.get_draw_choice.return_value = DrawSource.DECK

    action = player.get_action(obs)
    assert isinstance(action, ActionDrawDeck)

    # User chooses Discard
    mock_interface.get_draw_choice.return_value = DrawSource.DISCARD
    action = player.get_action(obs)
    assert isinstance(action, ActionDrawDiscard)


def test_get_action_action_phase_keep_and_swap(player, mock_interface, obs):
    obs.phase = RoundPhase.ACTION
    obs.drawn_card = Card(Rank.KING, Suit.HEARTS, "blue")
    obs.can_discard_drawn = True

    # Choose to keep and swap
    mock_interface.get_keep_or_discard_choice.return_value = ActionChoice.KEEP
    mock_interface.get_index_to_replace.return_value = 1

    action = player.get_action(obs)
    assert isinstance(action, ActionSwapCard)
    assert action.hand_index == 1


def test_get_action_action_phase_discard_drawn(player, mock_interface, obs):
    obs.phase = RoundPhase.ACTION
    obs.drawn_card = Card(Rank.KING, Suit.HEARTS, "blue")
    obs.can_discard_drawn = True

    # Discard Drawn
    mock_interface.get_keep_or_discard_choice.return_value = ActionChoice.DISCARD

    action = player.get_action(obs)
    assert isinstance(action, ActionDiscardDrawn)


def test_get_action_flip_phase_yes(player, mock_interface, obs):
    obs.phase = RoundPhase.FLIP

    # Choose Yes and index 3
    mock_interface.get_flip_choice.return_value = FlipChoice.YES
    mock_interface.get_valid_flip_index.return_value = 3

    action = player.get_action(obs)
    assert isinstance(action, ActionFlipCard)
    assert action.hand_index == 3


def test_get_action_flip_phase_no(player, mock_interface, obs):
    obs.phase = RoundPhase.FLIP

    # Choose No
    mock_interface.get_flip_choice.return_value = FlipChoice.NO

    action = player.get_action(obs)
    assert isinstance(action, ActionPass)
