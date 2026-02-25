"""Unit tests for the PhaseHandler class using primitives."""

import pytest

from pycardgolf.core.actions import Action, ActionType
from pycardgolf.core.events import (
    CardDiscardedEvent,
    CardDrawnDeckEvent,
    CardFlippedEvent,
    CardSwappedEvent,
    TurnStartEvent,
)
from pycardgolf.core.phases import (
    ActionPhaseState,
    DrawPhaseState,
    FinishedPhaseState,
    FlipPhaseState,
    RoundPhase,
    SetupPhaseState,
)
from pycardgolf.core.round import RoundFactory
from pycardgolf.exceptions import IllegalActionError


@pytest.fixture
def round_state():
    """Create a 2-player round state."""
    return RoundFactory.create_standard_round(player_names=["P1", "P2"])


def test_get_valid_actions_setup(round_state):
    """Test valid actions in SETUP phase."""
    round_state.phase_state = SetupPhaseState()
    actions = round_state.get_valid_actions(0)
    assert len(actions) == 6
    assert all(a.action_type == ActionType.FLIP for a in actions)


def test_get_valid_actions_draw(round_state):
    """Test valid actions in DRAW phase."""
    round_state.phase_state = DrawPhaseState()
    actions = round_state.get_valid_actions(0)
    assert any(a.action_type == ActionType.DRAW_DECK for a in actions)
    assert any(a.action_type == ActionType.DRAW_DISCARD for a in actions)


def test_get_valid_actions_action(round_state):
    """Test valid actions in ACTION phase."""
    round_state.phase_state = ActionPhaseState(drawn_from_deck=True)
    actions = round_state.get_valid_actions(0)
    assert any(a.action_type == ActionType.SWAP for a in actions)
    assert any(a.action_type == ActionType.DISCARD_DRAWN for a in actions)


def test_get_valid_actions_flip(round_state):
    """Test valid actions in FLIP phase."""
    round_state.phase_state = FlipPhaseState()
    actions = round_state.get_valid_actions(0)
    assert any(a.action_type == ActionType.PASS for a in actions)
    assert any(a.action_type == ActionType.FLIP for a in actions)


def test_handle_setup_phase(round_state):
    """Test that flipping cards in setup advances the round."""
    round_state.phase_state = SetupPhaseState()
    events = round_state.step(Action(action_type=ActionType.FLIP, target_index=0))
    assert any(isinstance(e, CardFlippedEvent) for e in events)
    assert round_state.cards_flipped_in_setup[0] == 1


def test_setup_to_draw_transition(round_state):
    """Test that finishing setup moves to DRAW phase."""
    round_state.phase_state = SetupPhaseState()
    # Flip 2 cards for Player 1
    round_state.step(Action(action_type=ActionType.FLIP, target_index=0))
    round_state.step(Action(action_type=ActionType.FLIP, target_index=1))
    # Flip 2 cards for Player 2
    round_state.step(Action(action_type=ActionType.FLIP, target_index=0))
    events = round_state.step(Action(action_type=ActionType.FLIP, target_index=1))

    assert round_state.phase == RoundPhase.DRAW
    assert any(isinstance(e, TurnStartEvent) for e in events)


def test_handle_draw_deck(round_state):
    """Test drawing from deck."""
    round_state.phase_state = DrawPhaseState()
    events = round_state.step(Action(action_type=ActionType.DRAW_DECK))
    assert round_state.phase == RoundPhase.ACTION
    assert round_state.drawn_card_id is not None
    assert isinstance(round_state.phase_state, ActionPhaseState)
    assert round_state.phase_state.drawn_from_deck is True
    assert any(isinstance(e, CardDrawnDeckEvent) for e in events)


def test_handle_swap_card(round_state):
    """Test swapping a card."""
    round_state.phase_state = ActionPhaseState(drawn_from_deck=False)
    round_state.drawn_card_id = round_state.deck.draw()
    events = round_state.step(Action(action_type=ActionType.SWAP, target_index=0))

    assert round_state.phase == RoundPhase.DRAW  # Moved to next player
    assert round_state.current_player_idx == 1
    assert any(isinstance(e, CardSwappedEvent) for e in events)
    assert any(isinstance(e, TurnStartEvent) for e in events)


def test_handle_discard_drawn(round_state):
    """Test discarding a drawn card."""
    round_state.phase_state = ActionPhaseState(drawn_from_deck=True)
    round_state.drawn_card_id = round_state.deck.draw()
    events = round_state.step(Action(action_type=ActionType.DISCARD_DRAWN))

    assert round_state.phase == RoundPhase.FLIP
    assert any(isinstance(e, CardDiscardedEvent) for e in events)


def test_round_end(round_state):
    """Test that the round ends when all players have cards up."""
    # Setup: one card hidden for player 2
    for i in range(5):
        round_state.hands[0].flip_card(i)
        round_state.hands[1].flip_card(i)

    round_state.hands[0].flip_card(5)  # Player 1 finished!
    round_state.phase_state = FlipPhaseState()

    # Player 1 is current player, just finished their turn
    round_state.step(Action(action_type=ActionType.PASS))

    # Should flag last turn
    assert round_state.last_turn_player_idx == 0
    assert round_state.current_player_idx == 1
    assert round_state.phase == RoundPhase.DRAW

    # Player 2 turn
    round_state.hands[1].flip_card(5)
    round_state.phase_state = FlipPhaseState()
    round_state.step(Action(action_type=ActionType.PASS))

    assert round_state.phase == RoundPhase.FINISHED


def test_handle_step_finished_phase(round_state):
    """Test that step returns empty list for FINISHED phase."""
    round_state.phase_state = FinishedPhaseState()
    events = round_state.step(Action(action_type=ActionType.PASS))
    assert events == []


def test_setup_flip_face_up_card_raises(round_state):
    """Test that flipping already face-up card in SETUP raises error."""
    round_state.phase_state = SetupPhaseState()
    round_state.hands[0].flip_card(0)

    with pytest.raises(IllegalActionError, match="Card already face up"):
        round_state.step(Action(action_type=ActionType.FLIP, target_index=0))


def test_draw_from_empty_discard_raises(round_state, mocker):
    """Test that drawing from empty discard raises error."""
    round_state.phase_state = DrawPhaseState()
    round_state.discard_pile = mocker.Mock()
    round_state.discard_pile.num_cards = 0

    with pytest.raises(IllegalActionError, match="Discard pile is empty"):
        round_state.step(Action(action_type=ActionType.DRAW_DISCARD))


def test_draw_invalid_action_raises(round_state):
    """Test that invalid action in DRAW phase raises error."""
    round_state.phase_state = DrawPhaseState()

    with pytest.raises(IllegalActionError, match="Invalid action for DRAW phase"):
        round_state.step(Action(action_type=ActionType.PASS))


def test_action_no_drawn_card_raises(round_state):
    """Test that ACTION phase without drawn card raises error."""
    round_state.phase_state = ActionPhaseState(drawn_from_deck=True)
    round_state.drawn_card_id = None

    with pytest.raises(IllegalActionError, match="No card drawn"):
        round_state.step(Action(action_type=ActionType.SWAP, target_index=0))


def test_flip_face_up_card_raises(round_state):
    """Test that flipping already face-up card in FLIP phase raises error."""
    round_state.phase_state = FlipPhaseState()
    round_state.hands[0].flip_card(0)

    with pytest.raises(IllegalActionError, match="Card already face up"):
        round_state.step(Action(action_type=ActionType.FLIP, target_index=0))


def test_flip_invalid_action_raises(round_state):
    """Test that invalid action in FLIP phase raises error."""
    round_state.phase_state = FlipPhaseState()

    with pytest.raises(IllegalActionError, match="Invalid action for FLIP phase"):
        round_state.step(Action(action_type=ActionType.DRAW_DECK))


def test_finished_phase_handle_action(round_state):
    """Test FinishedPhaseState returns empty list for handle_action."""
    round_state.phase_state = FinishedPhaseState()
    events = round_state.step(Action(action_type=ActionType.PASS))
    assert not events
    assert round_state.phase == RoundPhase.FINISHED


def test_get_valid_actions_finished(round_state):
    """Test that FINISHED phase returns no valid actions."""
    round_state.phase_state = FinishedPhaseState()
    actions = round_state.get_valid_actions(0)
    assert actions == []


def test_get_valid_actions_draw_empty_discard(round_state):
    """Test DRAW phase actions when discard pile is empty."""
    round_state.phase_state = DrawPhaseState()
    # Round initializes with 1 discard card, so we must clear it
    while round_state.discard_pile.num_cards > 0:
        round_state.discard_pile.draw()

    actions = round_state.get_valid_actions(0)
    assert len(actions) == 1
    assert actions[0].action_type == ActionType.DRAW_DECK
    assert not any(a.action_type == ActionType.DRAW_DISCARD for a in actions)
