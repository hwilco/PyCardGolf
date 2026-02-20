"""Tests for the ObservationBuilder class."""

import pytest

from pycardgolf.core.actions import ActionDrawDeck
from pycardgolf.core.hand import Hand
from pycardgolf.core.observation import ObservationBuilder
from pycardgolf.core.round import Round, RoundPhase
from pycardgolf.utils.card import Card
from pycardgolf.utils.enums import Rank, Suit


@pytest.fixture
def sample_cards():
    """Create a list of sample cards."""
    return [
        Card(Rank.ACE, Suit.SPADES, "red", face_up=True),
        Card(Rank.TWO, Suit.HEARTS, "red", face_up=False),
        Card(Rank.THREE, Suit.CLUBS, "red", face_up=True),
        Card(Rank.FOUR, Suit.DIAMONDS, "red", face_up=False),
        Card(Rank.FIVE, Suit.SPADES, "red", face_up=True),
        Card(Rank.SIX, Suit.HEARTS, "red", face_up=False),
    ]


@pytest.fixture
def mock_round(sample_cards, mocker):
    """Create a mock round state."""
    names = ["Player1", "Player2"]
    round_state = mocker.Mock(spec=Round)
    round_state.player_names = names
    round_state.num_players = 2
    round_state.hands = [Hand(sample_cards), Hand(sample_cards)]
    round_state.current_player_idx = 0
    round_state.phase = RoundPhase.DRAW
    round_state.drawn_card = None
    round_state.drawn_from_deck = False

    # Mock deck
    round_state.deck = mocker.Mock()
    round_state.deck.num_cards = 40
    round_state.deck.peek.return_value = Card(
        Rank.KING, Suit.SPADES, "blue", face_up=False
    )

    # Mock discard
    round_state.discard_pile = mocker.Mock()
    round_state.discard_pile.num_cards = 1
    discard_card = Card(Rank.JACK, Suit.HEARTS, "red", face_up=True)
    round_state.discard_pile.peek.return_value = discard_card

    # Mock get_valid_actions
    round_state.get_valid_actions.return_value = [ActionDrawDeck()]

    return round_state


def test_sanitize_card_face_up():
    """Test that face-up cards are copied as-is."""
    card = Card(Rank.ACE, Suit.SPADES, "red", face_up=True)
    sanitized = ObservationBuilder._sanitize_card(card)
    assert sanitized is not card
    assert sanitized.rank == Rank.ACE
    assert sanitized.suit == Suit.SPADES
    assert sanitized.face_up is True


def test_sanitize_card_face_down():
    """Test that face-down cards are hidden."""
    card = Card(Rank.KING, Suit.HEARTS, "blue", face_up=False)
    sanitized = ObservationBuilder._sanitize_card(card)
    # Should hide rank/suit
    sanitized.face_up = True
    assert sanitized.rank == Rank.HIDDEN
    assert sanitized.suit == Suit.HIDDEN
    assert sanitized.face_up is True
    assert sanitized.back_color == "blue"


def test_build_observation(mock_round):
    """Test building a full observation for a player."""
    obs = ObservationBuilder.build(mock_round, 0)

    # My hand
    assert len(obs.my_hand) == 6
    assert obs.my_hand[0].rank == Rank.ACE  # Was face up

    obs.my_hand[1].face_up = True
    assert obs.my_hand[1].rank == Rank.HIDDEN  # Was face down

    # Other hands
    assert "Player2" in obs.other_hands
    assert len(obs.other_hands["Player2"]) == 6
    assert obs.other_hands["Player2"][0].rank == Rank.ACE

    obs.other_hands["Player2"][1].face_up = True
    assert obs.other_hands["Player2"][1].rank == Rank.HIDDEN

    # Deck
    assert obs.deck_size == 40
    obs.deck_top.face_up = True
    assert obs.deck_top.rank == Rank.HIDDEN

    # Discard
    assert obs.discard_top.rank == Rank.JACK

    # Phase/Actions
    assert obs.phase == RoundPhase.DRAW
    assert isinstance(obs.valid_actions[0], ActionDrawDeck)


def test_observation_drawn_card_leak(mock_round):
    """Test that drawn_card is only visible to the current player."""
    drawn = Card(Rank.TEN, Suit.DIAMONDS, "red", face_up=True)
    mock_round.drawn_card = drawn
    mock_round.current_player_idx = 0

    # Current player sees it
    obs0 = ObservationBuilder.build(mock_round, 0)
    assert obs0.drawn_card is drawn

    # Other player doesn't
    obs1 = ObservationBuilder.build(mock_round, 1)
    assert obs1.drawn_card is None
