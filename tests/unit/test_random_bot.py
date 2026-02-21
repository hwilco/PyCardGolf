"""Tests for the RandomBot player class."""

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
from pycardgolf.players.bots.random_bot import RandomBot
from pycardgolf.utils.card import Card, Rank, Suit
from pycardgolf.utils.constants import HAND_SIZE


def test_random_bot_no_actions(mocker):
    """Test that RandomBot raises RuntimeError if no valid actions are found."""
    bot = RandomBot("Bot")
    mock_observation = mocker.Mock(spec=Observation)
    mock_observation.valid_actions = []

    with pytest.raises(RuntimeError, match=r"No valid actions found."):
        bot.get_action(mock_observation)


@pytest.fixture
def bot():
    """Create a RandomBot with a fixed seed (no interface required)."""
    return RandomBot("Bot", seed=42)


@pytest.fixture
def empty_obs():
    """Create a minimal Observation for testing."""
    return Observation(
        my_hand=[Card(Rank.ACE, Suit.SPADES, "blue") for _ in range(HAND_SIZE)],
        other_hands={},
        discard_top=Card(Rank.ACE, Suit.SPADES, "blue"),
        deck_size=50,
        deck_top=None,
        current_player_name="Bot",
        phase=RoundPhase.SETUP,
        valid_actions=[],
    )


def test_get_action_setup_phase(bot, empty_obs):
    """Setup phase: bot flips a random face-down card."""
    empty_obs.phase = RoundPhase.SETUP
    empty_obs.valid_actions = [ActionFlipCard(hand_index=i) for i in range(HAND_SIZE)]

    action = bot.get_action(empty_obs)

    assert isinstance(action, ActionFlipCard)
    assert action in empty_obs.valid_actions


def test_get_action_draw_phase(bot, empty_obs):
    """Draw phase: bot draws from deck or discard pile."""
    empty_obs.phase = RoundPhase.DRAW
    empty_obs.valid_actions = [ActionDrawDeck(), ActionDrawDiscard()]

    action = bot.get_action(empty_obs)

    assert isinstance(action, (ActionDrawDeck, ActionDrawDiscard))
    assert action in empty_obs.valid_actions


def test_get_action_action_phase(bot, empty_obs):
    """Action phase: bot swaps or discards a drawn card."""
    empty_obs.phase = RoundPhase.ACTION
    empty_obs.drawn_card = Card(Rank.KING, Suit.HEARTS, "blue")

    actions = [ActionSwapCard(hand_index=i) for i in range(HAND_SIZE)]
    actions.append(ActionDiscardDrawn())
    empty_obs.valid_actions = actions

    action = bot.get_action(empty_obs)
    assert isinstance(action, (ActionSwapCard, ActionDiscardDrawn))
    assert action in empty_obs.valid_actions


def test_get_action_flip_phase(bot, empty_obs):
    """Flip phase: bot passes or flips a random face-down card."""
    empty_obs.phase = RoundPhase.FLIP

    bot.hand = [Card(Rank.ACE, Suit.HEARTS, "blue") for _ in range(HAND_SIZE)]
    bot.hand[0].face_up = True

    actions = [ActionPass()]
    actions.extend(ActionFlipCard(hand_index=i) for i in range(1, HAND_SIZE))
    empty_obs.valid_actions = actions

    action = bot.get_action(empty_obs)
    assert isinstance(action, (ActionFlipCard, ActionPass))
    assert action in empty_obs.valid_actions
