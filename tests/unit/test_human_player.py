"""Tests for HumanPlayer class."""

from unittest.mock import MagicMock, Mock

import pytest

from pycardgolf.core.game import Game
from pycardgolf.core.hand import Hand
from pycardgolf.core.round import Round
from pycardgolf.interfaces.base import (
    ActionChoice,
    DrawSource,
    FlipChoice,
    GameInterface,
)
from pycardgolf.players.human import HumanPlayer
from pycardgolf.utils.card import Card
from pycardgolf.utils.enums import Rank, Suit


@pytest.fixture
def mock_interface():
    return MagicMock(spec=GameInterface)


@pytest.fixture
def player(mock_interface):
    hand = Hand(
        [
            Card(Rank.ACE, Suit.SPADES, back_color="blue"),
            Card(Rank.TWO, Suit.SPADES, back_color="blue"),
        ]
    )
    p = HumanPlayer("Test Player", mock_interface)
    p.hand = hand
    return p


@pytest.fixture
def mock_game():
    game = Mock(spec=Game)
    game.current_round = Mock()
    game.current_round.deck.peek.return_value = Card(
        Rank.THREE, Suit.HEARTS, back_color="blue"
    )
    game.current_round.discard_pile.peek.return_value = Card(
        Rank.FOUR, Suit.HEARTS, back_color="blue", face_up=True
    )
    game.current_round.deck.draw.return_value = Card(
        Rank.THREE, Suit.HEARTS, back_color="blue"
    )
    game.current_round.discard_pile.draw.return_value = Card(
        Rank.FOUR, Suit.HEARTS, back_color="blue", face_up=True
    )
    return game


def test_choose_initial_card_to_flip(player, mock_interface):
    """Test choosing a single initial card."""
    mock_interface.get_index_to_flip.return_value = 0
    # Setup hand so card 0 is face down
    player.hand[0].face_up = False

    result = player.choose_initial_card_to_flip(None)

    assert result == 0
    # Should display hand
    mock_interface.display_hand.assert_called_once_with(player, display_indices=True)
    # Should NOT flip the card (it's Round's job now)
    assert player.hand[0].face_up is False


def test_choose_initial_card_to_flip_retry_if_face_up(player, mock_interface):
    """Test retry logic if selecting a face-up card."""
    # First call 0 (which we set to face up), Second call 1 (face down)
    mock_interface.get_index_to_flip.side_effect = [0, 1]

    player.hand[0].face_up = True
    player.hand[1].face_up = False

    result = player.choose_initial_card_to_flip(None)

    assert result == 1
    assert result == 1
    assert mock_interface.display_initial_flip_error_already_selected.call_count >= 1


def test_take_turn_deck_draw_keep(player, mock_interface, mock_game):
    """Test taking a turn: draw from deck, keep card, replace index 0."""
    # Setup interface responses
    mock_interface.get_draw_choice.return_value = DrawSource.DECK
    mock_interface.get_keep_or_discard_choice.return_value = ActionChoice.KEEP
    mock_interface.get_index_to_replace.return_value = 0

    player.take_turn(mock_game)

    # Verify display state called
    mock_interface.display_state.assert_called_once_with(mock_game)

    # Verify deck draw
    mock_game.current_round.deck.draw.assert_called_once()
    # Verify display called
    mock_interface.display_drawn_card.assert_called_once()

    # Verify replacement logic (check if hand updated)
    assert player.hand[0].rank == Rank.THREE
    assert player.hand[0].face_up is True
    # Verify display called
    mock_interface.display_replace_action.assert_called_once()


def test_take_turn_deck_draw_discard_flip(player, mock_interface, mock_game):
    """Test takng a turn: draw from deck, discard, flip index 1."""
    mock_interface.get_draw_choice.return_value = DrawSource.DECK
    mock_interface.get_keep_or_discard_choice.return_value = ActionChoice.DISCARD
    mock_interface.get_flip_choice.return_value = FlipChoice.YES
    mock_interface.get_valid_flip_index.return_value = 1

    player.take_turn(mock_game)

    # Verify discard pile add
    mock_game.current_round.discard_pile.add_card.assert_called()
    # Verify flip
    assert player.hand[1].face_up is True
    # Verify displays
    mock_interface.display_discard_action.assert_called_once()
    mock_interface.display_flip_action.assert_called_once()


def test_take_turn_discard_pile_draw(player, mock_interface, mock_game):
    """Test taking a turn: draw from discard pile, replace index 0."""
    mock_interface.get_draw_choice.return_value = DrawSource.DISCARD
    mock_interface.get_index_to_replace.return_value = 0

    player.take_turn(mock_game)

    # Verify discard pile draw
    mock_game.current_round.discard_pile.draw.assert_called_once()
    # Verify display
    mock_interface.display_discard_draw.assert_called_once()
    # Verify replacement
    assert player.hand[0].rank == Rank.FOUR
    assert player.hand[0].face_up is True
    # Verify display
    mock_interface.display_replace_action.assert_called_once()


def test_choose_card_to_flip_after_discard_no():
    """Test choosing NOT to flip a card after discard."""
    interface = Mock()
    player = HumanPlayer("TestHuman", interface)

    # Determine behavior: FlipChoice.NO
    interface.get_flip_choice.return_value = FlipChoice.NO

    mock_round = Mock(spec=Round)

    result = player._choose_card_to_flip_after_discard(mock_round)
    assert result is None

    # Verify get_valid_flip_index was NOT called
    interface.get_valid_flip_index.assert_not_called()
