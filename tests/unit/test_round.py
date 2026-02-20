import pytest

from pycardgolf.core.actions import (
    ActionDiscardDrawn,
    ActionDrawDeck,
    ActionFlipCard,
    ActionPass,
    ActionSwapCard,
)
from pycardgolf.core.events import (
    CardDiscardedEvent,
    CardDrawnDeckEvent,
    CardFlippedEvent,
    CardSwappedEvent,
    TurnStartEvent,
)
from pycardgolf.core.round import Round
from pycardgolf.core.state import RoundPhase
from pycardgolf.exceptions import GameConfigError, IllegalActionError
from pycardgolf.utils.card import Card
from pycardgolf.utils.constants import HAND_SIZE
from pycardgolf.utils.enums import Rank, Suit


def test_validate_config_success():
    """Test that validate_config passes for valid configuration."""
    # 2 players * 6 cards = 12 cards needed. Deck has 52. OK.
    Round.validate_config(num_players=2, deck_size=52)


def test_validate_config_failure():
    """Test that validate_config raises GameConfigError for invalid configuration."""
    # 10 players * 6 cards = 60 cards needed. Deck has 52. Fail.
    with pytest.raises(GameConfigError, match="Not enough cards"):
        Round.validate_config(num_players=10, deck_size=52)


def test_round_initialization():
    player_names = ["P1", "P2"]

    round_instance = Round(player_names=player_names)

    assert round_instance.phase == RoundPhase.SETUP
    assert len(round_instance.hands) == 2
    assert len(round_instance.hands[0]) == HAND_SIZE
    assert len(round_instance.hands[1]) == HAND_SIZE
    # Discard pile should have 1 card
    assert round_instance.discard_pile.num_cards == 1
    assert round_instance.discard_pile.peek().face_up


def test_round_step_setup_phase():
    player_names = ["P1"]
    round_instance = Round(player_names=player_names)

    # Needs to flip 2 cards to finish setup
    assert round_instance.phase == RoundPhase.SETUP
    assert round_instance.get_current_player_idx() == 0

    # Action 1: Flip index 0
    events = round_instance.step(ActionFlipCard(hand_index=0))
    assert len(events) == 1
    assert isinstance(events[0], CardFlippedEvent)
    assert round_instance.hands[0][0].face_up
    assert round_instance.phase == RoundPhase.SETUP  # Still setup

    # Action 2: Flip index 1
    events = round_instance.step(ActionFlipCard(hand_index=1))
    # Should transition to DRAW phase
    assert round_instance.hands[0][1].face_up
    assert round_instance.phase == RoundPhase.DRAW
    # Should yield CardFlippedEvent AND TurnStartEvent
    assert isinstance(events[0], CardFlippedEvent)
    assert isinstance(events[-1], TurnStartEvent)


def test_round_step_illegal_setup_action():
    round_instance = Round(player_names=["P1"])

    with pytest.raises(IllegalActionError):
        round_instance.step(ActionPass())  # Pass is not valid in SETUP


def test_round_step_draw_phase():
    round_instance = Round(player_names=["P1"])

    # Skip setup
    round_instance.phase = RoundPhase.DRAW

    # Draw from Deck
    events = round_instance.step(ActionDrawDeck())
    assert isinstance(events[0], CardDrawnDeckEvent)
    assert round_instance.phase == RoundPhase.ACTION
    assert round_instance.drawn_card is not None
    assert round_instance.drawn_from_deck is True


def test_round_step_action_phase_swap():
    round_instance = Round(player_names=["P1"])
    round_instance.phase = RoundPhase.ACTION
    drawn = Card(Rank.ACE, Suit.SPADES, "blue")
    round_instance.drawn_card = drawn

    initial_hand_card = round_instance.hands[0][0]

    events = round_instance.step(ActionSwapCard(hand_index=0))

    assert isinstance(events[0], CardSwappedEvent)
    assert round_instance.hands[0][0] == drawn
    # Replaced card goes to discard
    assert round_instance.discard_pile.peek() == initial_hand_card
    # Turn should end (back to DRAW or next player)
    assert round_instance.phase == RoundPhase.DRAW
    assert isinstance(events[-1], TurnStartEvent)


def test_round_step_action_phase_discard_drawn():
    round_instance = Round(player_names=["P1"])
    round_instance.phase = RoundPhase.ACTION
    drawn = Card(Rank.ACE, Suit.SPADES, "blue")
    round_instance.drawn_card = drawn
    # Must be from deck to discard
    round_instance.drawn_from_deck = True

    events = round_instance.step(ActionDiscardDrawn())

    assert isinstance(events[0], CardDiscardedEvent)
    assert round_instance.discard_pile.peek() == drawn
    # Should transition to FLIP phase
    assert round_instance.phase == RoundPhase.FLIP


def test_round_step_flip_phase():
    round_instance = Round(player_names=["P1"])
    round_instance.phase = RoundPhase.FLIP

    # Flip index 2
    events = round_instance.step(ActionFlipCard(hand_index=2))

    assert isinstance(events[0], CardFlippedEvent)
    assert round_instance.hands[0][2].face_up
    assert round_instance.phase == RoundPhase.DRAW
