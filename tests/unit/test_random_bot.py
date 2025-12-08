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
from pycardgolf.players.bots.random_bot import RandomBot
from pycardgolf.utils.card import Card, Rank, Suit
from pycardgolf.utils.constants import HAND_SIZE


@pytest.fixture
def bot():
    mock_interface = MagicMock()
    return RandomBot("Bot", mock_interface, seed=42)


@pytest.fixture
def empty_obs():
    return Observation(
        my_hand=[Card(Rank.ACE, Suit.SPADES, "blue") for _ in range(HAND_SIZE)],
        other_hands={},
        discard_top=Card(Rank.ACE, Suit.SPADES, "blue"),
        deck_size=50,
        current_player_name="Bot",
        phase=RoundPhase.SETUP,
        valid_actions=[],
    )


def test_get_action_setup_phase(bot, empty_obs):
    empty_obs.phase = RoundPhase.SETUP
    empty_obs.valid_actions = [ActionFlipCard(hand_index=i) for i in range(HAND_SIZE)]

    action = bot.get_action(empty_obs)

    assert isinstance(action, ActionFlipCard)
    assert action in empty_obs.valid_actions


def test_get_action_draw_phase(bot, empty_obs):
    empty_obs.phase = RoundPhase.DRAW
    empty_obs.valid_actions = [ActionDrawDeck(), ActionDrawDiscard()]

    action = bot.get_action(empty_obs)

    assert isinstance(action, (ActionDrawDeck, ActionDrawDiscard))
    assert action in empty_obs.valid_actions


def test_get_action_action_phase(bot, empty_obs):
    empty_obs.phase = RoundPhase.ACTION
    empty_obs.drawn_card = Card(Rank.KING, Suit.HEARTS, "blue")

    actions = [ActionSwapCard(hand_index=i) for i in range(HAND_SIZE)]
    actions.append(ActionDiscardDrawn())
    empty_obs.valid_actions = actions

    action = bot.get_action(empty_obs)
    assert isinstance(action, (ActionSwapCard, ActionDiscardDrawn))
    assert action in empty_obs.valid_actions


def test_get_action_flip_phase(bot, empty_obs):
    empty_obs.phase = RoundPhase.FLIP

    # Setup bot hand with some face down cards
    bot.hand = [Card(Rank.ACE, Suit.HEARTS, "blue") for _ in range(HAND_SIZE)]
    # All handled internally by bot using its own hand reference or observing it?
    # RandomBot uses 'self.hand', which is updated by referencing Observation?
    # No, Player.hand is updated by Round/Game externally?
    # Wait, RandomBot logic uses `self.hand`. The Round logic updates `player.hand`.
    # So we need to ensure bot.hand matches what we expect.

    # Flip index 0
    bot.hand[0].face_up = True

    # Valid actions: Pass + Flip face down
    actions = [ActionPass()]
    # Index 0 is face up, so valid flips are 1..HAND_SIZE-1
    for i in range(1, HAND_SIZE):
        actions.append(ActionFlipCard(hand_index=i))
    empty_obs.valid_actions = actions

    action = bot.get_action(empty_obs)
    assert isinstance(action, (ActionFlipCard, ActionPass))
    assert action in empty_obs.valid_actions
