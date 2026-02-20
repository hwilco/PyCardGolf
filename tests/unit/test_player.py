"""Tests for the abstract Player class."""

from unittest.mock import Mock

import pytest

from pycardgolf.core.actions import ActionPass
from pycardgolf.core.hand import Hand
from pycardgolf.core.state import Observation
from pycardgolf.interfaces.base import GameInterface
from pycardgolf.players.player import BasePlayer
from pycardgolf.utils.card import Card, Rank, Suit


class ConcretePlayer(BasePlayer):
    """Concrete implementation for testing."""

    def get_action(self, observation: Observation):
        return ActionPass()


def test_init():
    """Test initialization sets name, empty hand, and interface."""
    interface = Mock(spec=GameInterface)
    p = ConcretePlayer("Bob", interface)
    assert p.name == "Bob"
    assert isinstance(p.hand, Hand)
    assert len(p.hand) == 0
    assert p.interface == interface


def test_repr():
    """Test string representation."""
    interface = Mock(spec=GameInterface)
    player = ConcretePlayer("TestPlayer", interface)
    player.hand = Hand([Card(Rank.ACE, Suit.SPADES, "red")])
    assert "TestPlayer" in repr(player)
    assert "ACE" in repr(player)


def test_abstract_instantiation_raises():
    """Test that BasePlayer cannot be instantiated directly."""
    interface = Mock(spec=GameInterface)
    with pytest.raises(TypeError):
        BasePlayer("Abstract", interface)
