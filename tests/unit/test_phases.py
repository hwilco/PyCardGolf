"""Unit tests for the PhaseHandler class."""

import pytest

from pycardgolf.core.actions import (
    ActionDiscardDrawn,
    ActionDrawDeck,
    ActionDrawDiscard,
    ActionFlipCard,
    ActionPass,
    ActionSwapCard,
)
from pycardgolf.core.events import (
    CardDiscardedEvent,
    CardDrawnDeckEvent,
    CardFlippedEvent,
    CardSwappedEvent,
    RoundEndEvent,
    TurnStartEvent,
)
from pycardgolf.core.phases import PhaseHandler
from pycardgolf.core.round import Round, RoundPhase


@pytest.fixture
def round_state():
    """Create a 2-player round state."""
    return Round(player_names=["Player1", "Player2"])


def test_get_valid_actions_setup(round_state):
    """Test valid actions in SETUP phase."""
    round_state.phase = RoundPhase.SETUP
    actions = PhaseHandler.get_valid_actions(round_state, 0)
    assert len(actions) == 6
    assert all(isinstance(a, ActionFlipCard) for a in actions)


def test_get_valid_actions_draw(round_state):
    """Test valid actions in DRAW phase."""
    round_state.phase = RoundPhase.DRAW
    actions = PhaseHandler.get_valid_actions(round_state, 0)
    assert any(isinstance(a, ActionDrawDeck) for a in actions)
    assert any(isinstance(a, ActionDrawDiscard) for a in actions)


def test_get_valid_actions_action(round_state):
    """Test valid actions in ACTION phase."""
    round_state.phase = RoundPhase.ACTION
    round_state.drawn_from_deck = True
    actions = PhaseHandler.get_valid_actions(round_state, 0)
    assert any(isinstance(a, ActionSwapCard) for a in actions)
    assert any(isinstance(a, ActionDiscardDrawn) for a in actions)


def test_get_valid_actions_flip(round_state):
    """Test valid actions in FLIP phase."""
    round_state.phase = RoundPhase.FLIP
    actions = PhaseHandler.get_valid_actions(round_state, 0)
    assert any(isinstance(a, ActionPass) for a in actions)
    assert any(isinstance(a, ActionFlipCard) for a in actions)


def test_handle_setup_phase(round_state):
    """Test that flipping cards in setup advances the round."""
    round_state.phase = RoundPhase.SETUP
    events = PhaseHandler.handle_step(round_state, ActionFlipCard(hand_index=0))
    assert any(isinstance(e, CardFlippedEvent) for e in events)
    assert round_state.cards_flipped_in_setup[0] == 1


def test_setup_to_draw_transition(round_state):
    """Test that finishing setup moves to DRAW phase."""
    round_state.phase = RoundPhase.SETUP
    # Flip 2 cards for Player1
    PhaseHandler.handle_step(round_state, ActionFlipCard(hand_index=0))
    PhaseHandler.handle_step(round_state, ActionFlipCard(hand_index=1))
    # Flip 2 cards for Player2
    PhaseHandler.handle_step(round_state, ActionFlipCard(hand_index=0))
    events = PhaseHandler.handle_step(round_state, ActionFlipCard(hand_index=1))

    assert round_state.phase == RoundPhase.DRAW
    assert any(isinstance(e, TurnStartEvent) for e in events)


def test_handle_draw_deck(round_state):
    """Test drawing from deck."""
    round_state.phase = RoundPhase.DRAW
    events = PhaseHandler.handle_step(round_state, ActionDrawDeck())
    assert round_state.phase == RoundPhase.ACTION
    assert round_state.drawn_card is not None
    assert round_state.drawn_from_deck is True
    assert any(isinstance(e, CardDrawnDeckEvent) for e in events)


def test_handle_swap_card(round_state):
    """Test swapping a card."""
    round_state.phase = RoundPhase.ACTION
    round_state.drawn_card = round_state.deck.draw()
    events = PhaseHandler.handle_step(round_state, ActionSwapCard(hand_index=0))

    assert round_state.phase == RoundPhase.DRAW  # Moved to next player
    assert round_state.current_player_idx == 1
    assert any(isinstance(e, CardSwappedEvent) for e in events)
    assert any(isinstance(e, TurnStartEvent) for e in events)


def test_handle_discard_drawn(round_state):
    """Test discarding a drawn card."""
    round_state.phase = RoundPhase.ACTION
    round_state.drawn_card = round_state.deck.draw()
    round_state.drawn_from_deck = True
    events = PhaseHandler.handle_step(round_state, ActionDiscardDrawn())

    assert round_state.phase == RoundPhase.FLIP
    assert any(isinstance(e, CardDiscardedEvent) for e in events)


def test_round_end(round_state):
    """Test that the round ends when all players have cards up."""
    # Setup: one card hidden for player 2
    for i in range(5):
        round_state.hands[0][i].face_up = True
        round_state.hands[1][i].face_up = True

    round_state.hands[0][5].face_up = True  # Player 1 finished!
    round_state.current_player_idx = 0
    round_state.phase = RoundPhase.FLIP

    # Player 1 is current player, just finished their turn
    events = PhaseHandler.handle_step(round_state, ActionPass())

    # Should flag last turn
    assert round_state.last_turn_player_idx == 0
    assert round_state.current_player_idx == 1
    assert round_state.phase == RoundPhase.DRAW

    # Player 2 turn
    round_state.hands[1][5].face_up = True
    round_state.phase = RoundPhase.FLIP
    events = PhaseHandler.handle_step(round_state, ActionPass())

    assert round_state.round_over is True
    assert round_state.phase == RoundPhase.FINISHED
    assert any(isinstance(e, RoundEndEvent) for e in events)
