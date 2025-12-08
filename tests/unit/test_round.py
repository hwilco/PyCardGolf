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
    CardDrawnDiscardEvent,
    CardFlippedEvent,
    CardSwappedEvent,
    RoundEndEvent,
    TurnStartEvent,
)
from pycardgolf.core.hand import Hand
from pycardgolf.core.round import Round
from pycardgolf.core.state import Observation, RoundPhase
from pycardgolf.exceptions import IllegalActionError
from pycardgolf.players.player import Player
from pycardgolf.utils.card import Card
from pycardgolf.utils.constants import HAND_SIZE, INITIAL_CARDS_TO_FLIP
from pycardgolf.utils.enums import Rank, Suit


class MockAgent(Player):
    """A minimal concrete player for testing."""

    def get_action(self, observation: Observation):
        return ActionPass()


def test_round_initialization(mocker):
    mock_game = mocker.Mock()
    p1 = MockAgent("P1", mocker.Mock())
    p2 = MockAgent("P2", mocker.Mock())

    round_instance = Round(mock_game, [p1, p2])

    assert round_instance.phase == RoundPhase.SETUP
    assert len(p1.hand) == HAND_SIZE
    assert len(p2.hand) == HAND_SIZE
    # Discard pile should have 1 card
    assert round_instance.discard_pile.num_cards == 1
    assert round_instance.discard_pile.peek().face_up


def test_round_step_setup_phase(mocker):
    mock_game = mocker.Mock()
    p1 = MockAgent("P1", mocker.Mock())
    round_instance = Round(mock_game, [p1])

    # Needs to flip 2 cards to finish setup
    assert round_instance.phase == RoundPhase.SETUP
    assert round_instance.get_current_player() == p1

    # Action 1: Flip index 0
    events = round_instance.step(ActionFlipCard(hand_index=0))
    assert len(events) == 1
    assert isinstance(events[0], CardFlippedEvent)
    assert p1.hand[0].face_up
    assert round_instance.phase == RoundPhase.SETUP  # Still setup

    # Action 2: Flip index 1
    events = round_instance.step(ActionFlipCard(hand_index=1))
    # Should transition to DRAW phase
    assert p1.hand[1].face_up
    assert round_instance.phase == RoundPhase.DRAW
    # Should yield CardFlippedEvent AND TurnStartEvent
    assert isinstance(events[0], CardFlippedEvent)
    assert isinstance(events[-1], TurnStartEvent)


def test_round_step_illegal_setup_action(mocker):
    mock_game = mocker.Mock()
    p1 = MockAgent("P1", mocker.Mock())
    round_instance = Round(mock_game, [p1])

    with pytest.raises(IllegalActionError):
        round_instance.step(ActionPass())  # Pass is not valid in SETUP


def test_round_step_draw_phase(mocker):
    mock_game = mocker.Mock()
    p1 = MockAgent("P1", mocker.Mock())
    round_instance = Round(mock_game, [p1])

    # Skip setup
    round_instance.phase = RoundPhase.DRAW

    # Draw from Deck
    events = round_instance.step(ActionDrawDeck())
    assert isinstance(events[0], CardDrawnDeckEvent)
    assert round_instance.phase == RoundPhase.ACTION
    assert round_instance.drawn_card is not None
    assert round_instance.drawn_from_deck is True


def test_round_step_action_phase_swap(mocker):
    mock_game = mocker.Mock()
    p1 = MockAgent("P1", mocker.Mock())
    round_instance = Round(mock_game, [p1])
    round_instance.phase = RoundPhase.ACTION
    drawn = Card(Rank.ACE, Suit.SPADES, "blue")
    round_instance.drawn_card = drawn

    initial_hand_card = p1.hand[0]

    events = round_instance.step(ActionSwapCard(hand_index=0))

    assert isinstance(events[0], CardSwappedEvent)
    assert p1.hand[0] == drawn
    # Replaced card goes to discard
    assert round_instance.discard_pile.peek() == initial_hand_card
    # Turn should end (back to DRAW or next player)
    assert round_instance.phase == RoundPhase.DRAW
    assert isinstance(events[-1], TurnStartEvent)


def test_round_step_action_phase_discard_drawn(mocker):
    mock_game = mocker.Mock()
    p1 = MockAgent("P1", mocker.Mock())
    round_instance = Round(mock_game, [p1])
    round_instance.phase = RoundPhase.ACTION
    drawn = Card(Rank.ACE, Suit.SPADES, "blue")
    round_instance.drawn_card = drawn
    # Must be from deck to discard
    round_instance.drawn_from_deck = True

    events = round_instance.step(ActionDiscardDrawn())

    assert isinstance(events[0], CardDiscardedEvent)
    assert round_instance.discard_pile.peek() == drawn
    assert round_instance.phase == RoundPhase.FLIP


def test_round_step_flip_phase(mocker):
    mock_game = mocker.Mock()
    p1 = MockAgent("P1", mocker.Mock())
    round_instance = Round(mock_game, [p1])
    round_instance.phase = RoundPhase.FLIP

    # Flip index 2
    events = round_instance.step(ActionFlipCard(hand_index=2))

    assert isinstance(events[0], CardFlippedEvent)
    assert p1.hand[2].face_up
    assert round_instance.phase == RoundPhase.DRAW
