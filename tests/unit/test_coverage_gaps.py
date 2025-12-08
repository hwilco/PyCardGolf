"""Tests to fill specific coverage gaps."""

import pytest

from pycardgolf.interfaces.base import GameInterface
from pycardgolf.interfaces.null import NullGameInterface
from pycardgolf.players.bots.random_bot import RandomBot
from pycardgolf.utils.card import Card, Rank, Suit
from pycardgolf.utils.deck import Deck


class TestRandomBotCoverage:
    """Coverage tests for RandomBot."""

    def test_init_default_interface(self):
        """Test initialization with default interface."""
        bot = RandomBot("TestBot")
        assert isinstance(bot.interface, NullGameInterface)


class TestDeckCoverage:
    """Coverage tests for Deck."""

    def test_add_card_wrong_color(self):
        """Test error when adding card with mismatching back color."""
        deck = Deck(back_color="red")
        # Remove a card so we can theoretically add one
        _ = deck.draw()

        blue_card = Card(Rank.ACE, Suit.SPADES, back_color="blue")

        with pytest.raises(ValueError, match="does not match"):
            deck.add_card(blue_card)

    def test_add_card_duplicate(self):
        """Test error when adding a duplicate card."""
        deck = Deck(back_color="red")
        # Peek top card
        top_card = deck.peek()

        with pytest.raises(ValueError, match="duplicate"):
            deck.add_card(top_card)

    def test_add_card_success(self):
        """Test successfully adding a valid card to the deck."""
        deck = Deck(back_color="red")
        # Draw a card to make space (and have a valid card to add back)
        card = deck.draw()

        # Verify card is gone
        assert card not in deck.cards

        # Add it back
        deck.add_card(card)

        # Verify it's back
        assert card in deck.cards
        assert deck.peek() == card
