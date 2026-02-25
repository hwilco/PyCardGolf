"""Tests for the ObservationBuilder class using primitives."""

import pytest

from pycardgolf.core.actions import Action, ActionType
from pycardgolf.core.hand import Hand
from pycardgolf.core.observation import ObservationBuilder
from pycardgolf.core.phases import ActionPhaseState, RoundPhase
from pycardgolf.core.round import Round
from pycardgolf.utils.card import get_masked_id


@pytest.fixture
def sample_card_ids():
    """Create a list of sample CardIDs."""
    # Card IDs: 0 is Ace Spades, 1 is 2 Spades, etc., up to 5 (6 Spades)
    return [0, 1, 2, 3, 4, 5]


@pytest.fixture
def mock_round(sample_card_ids, mocker):
    """Create a mock round state."""
    names = ["Player1", "Player2"]
    round_state = mocker.Mock(spec=Round)
    round_state.player_names = names
    round_state.num_players = 2

    # Hand 0: cards 0, 2, 4 are face up (mask 0b010101 = 21)
    # Hand 1: all face down (mask 0)
    round_state.hands = [
        Hand(list(sample_card_ids), 0b010101),
        Hand(list(sample_card_ids), 0),
    ]
    round_state.current_player_idx = 0
    round_state.phase = RoundPhase.DRAW
    round_state.drawn_card = None
    round_state.drawn_from_deck = False

    # Mock deck
    round_state.deck = mocker.Mock()
    round_state.deck.num_cards = 40
    round_state.deck.peek.return_value = 51  # King of Clubs

    # Mock discard
    round_state.discard_pile = mocker.Mock()
    round_state.discard_pile.num_cards = 1
    round_state.discard_pile.peek.return_value = 25  # Jack of Hearts

    # Mock get_valid_actions
    round_state.get_valid_actions.return_value = [
        Action(action_type=ActionType.DRAW_DECK)
    ]

    return round_state


def test_mask_card():
    """Test the secure masking logic."""
    # deck 0: 0-51. Mask is -1.
    assert get_masked_id(0) == -1
    assert get_masked_id(51) == -1
    # deck 1: 52-103. Mask is -2.
    assert get_masked_id(52) == -2
    assert get_masked_id(103) == -2


def test_sanitize_hand():
    """Test sanitizing a hand with a mix of face-up and face-down cards."""
    # Hand: [0, 1, 2], face_up_mask: 0b101 (0 and 2 are face up)
    hand = Hand([0, 1, 2], 0b101)
    sanitized = ObservationBuilder.sanitize_hand(hand)
    assert sanitized == [0, -1, 2]


def test_build_observation(mock_round):
    """Test building a full observation for a player."""
    obs = ObservationBuilder.build(mock_round, 0)

    # My hand cards are 0-5. With the mask 0b010101, indices 0, 2, 4 are face up.
    # Expected visibility result: [0, -1, 2, -1, 4, -1]
    assert obs.my_hand == [0, -1, 2, -1, 4, -1]

    # Other hands
    assert "Player2" in obs.other_hands
    # Player 2 has mask 0, all should be -1
    assert obs.other_hands["Player2"] == [-1, -1, -1, -1, -1, -1]

    # Deck
    assert obs.deck_size == 40
    # Deck top is ALWAYS masked in observation
    assert obs.deck_top == -1

    # Discard
    assert obs.discard_top == 25

    # Phase/Actions
    assert obs.phase == RoundPhase.DRAW
    assert obs.valid_actions[0].action_type == ActionType.DRAW_DECK
    assert obs.current_player_name == "Player1"


def test_observation_drawn_card_leak(mock_round):
    """Test that drawn_card is only visible to the current player."""
    mock_round.drawn_card_id = 42
    mock_round.current_player_idx = 0

    # Current player sees it
    obs0 = ObservationBuilder.build(mock_round, 0)
    assert obs0.drawn_card_id == 42

    # Other player doesn't
    obs1 = ObservationBuilder.build(mock_round, 1)
    assert obs1.drawn_card_id is None


def test_build_observation_empty_deck(mock_round):
    """Test building observation when deck is empty."""
    mock_round.deck.num_cards = 0
    obs = ObservationBuilder.build(mock_round, 0)
    assert obs.deck_size == 0
    assert obs.deck_top is None


def test_observation_can_discard_drawn(mock_round):
    """Test that can_discard_drawn is correctly set in ACTION phase."""
    mock_round.current_player_idx = 1
    mock_round.phase_state = ActionPhaseState(drawn_from_deck=True)
    mock_round.phase = RoundPhase.ACTION

    # Observation for player 1 (current player)
    obs1 = ObservationBuilder.build(mock_round, 1)
    assert obs1.can_discard_drawn is True

    # Observation for player 0 (not current player)
    obs0 = ObservationBuilder.build(mock_round, 0)
    assert obs0.can_discard_drawn is False

    # ActionPhaseState with drawn_from_deck=False
    mock_round.phase_state = ActionPhaseState(drawn_from_deck=False)
    obs1_no_discard = ObservationBuilder.build(mock_round, 1)
    assert obs1_no_discard.can_discard_drawn is False
