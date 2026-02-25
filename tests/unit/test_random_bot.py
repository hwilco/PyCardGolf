"""Tests for the RandomBot player class."""

import pytest

from pycardgolf.core.actions import ActionSpace, ActionType
from pycardgolf.core.observation import Observation
from pycardgolf.core.phases import RoundPhase
from pycardgolf.players.bots.random_bot import RandomBot
from pycardgolf.utils.constants import HAND_SIZE


def test_random_bot_no_actions(mocker):
    """Test that RandomBot raises RuntimeError if no valid actions are found."""
    bot = RandomBot("Bot")
    mock_observation = mocker.Mock(spec=Observation)
    mock_observation.valid_actions = ()

    with pytest.raises(RuntimeError, match=r"No valid actions found."):
        bot.get_action(mock_observation)


def test_bots_have_unique_default_seeds(mocker):
    """Test that multiple bots instantiated without seeds get unique seeds."""
    mock_randrange = mocker.patch("pycardgolf.utils.mixins.random.randrange")
    mock_randrange.side_effect = [100, 200, 300]

    bot1 = RandomBot("Bot 1")
    bot2 = RandomBot("Bot 2")
    bot3 = RandomBot("Bot 3")

    assert bot1.seed == 100
    assert bot2.seed == 200
    assert bot3.seed == 300


@pytest.fixture
def bot():
    """Create a RandomBot with a fixed seed (no interface required)."""
    return RandomBot("Bot", seed=42)


@pytest.fixture
def empty_obs():
    """Create a minimal Observation for testing."""
    return Observation(
        my_hand=[0] * HAND_SIZE,
        other_hands={},
        discard_top=25,
        deck_size=50,
        deck_top=None,
        current_player_name="Bot",
        phase=RoundPhase.SETUP,
        valid_actions=(),
    )


def test_get_action_setup_phase(bot, empty_obs):
    """Setup phase: bot flips a random face-down card."""
    empty_obs.phase = RoundPhase.SETUP
    empty_obs.valid_actions = ActionSpace.FLIP

    action = bot.get_action(empty_obs)

    assert action.action_type == ActionType.FLIP
    assert action in empty_obs.valid_actions


def test_get_action_draw_phase(bot, empty_obs):
    """Draw phase: bot draws from deck or discard pile."""
    empty_obs.phase = RoundPhase.DRAW
    empty_obs.valid_actions = (
        ActionSpace.DRAW_DECK,
        ActionSpace.DRAW_DISCARD,
    )

    action = bot.get_action(empty_obs)

    assert action.action_type in (ActionType.DRAW_DECK, ActionType.DRAW_DISCARD)
    assert action in empty_obs.valid_actions


def test_get_action_action_phase(bot, empty_obs):
    """Action phase: bot swaps or discards a drawn card."""
    empty_obs.phase = RoundPhase.ACTION
    empty_obs.drawn_card_id = 99

    actions = (*ActionSpace.SWAP, ActionSpace.DISCARD_DRAWN)
    empty_obs.valid_actions = actions

    action = bot.get_action(empty_obs)
    assert action.action_type in (ActionType.SWAP, ActionType.DISCARD_DRAWN)
    assert action in empty_obs.valid_actions


def test_get_action_flip_phase(bot, empty_obs):
    """Flip phase: bot passes or flips a random face-down card."""
    empty_obs.phase = RoundPhase.FLIP

    actions = (ActionSpace.PASS, *ActionSpace.FLIP)
    empty_obs.valid_actions = actions

    action = bot.get_action(empty_obs)
    assert action.action_type in (ActionType.FLIP, ActionType.PASS)
    assert action in empty_obs.valid_actions
