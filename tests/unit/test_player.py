"""Tests for the abstract BasePlayer class."""

import pytest

from pycardgolf.core.actions import ActionPass
from pycardgolf.core.hand import Hand
from pycardgolf.core.observation import Observation
from pycardgolf.players.player import BasePlayer
from pycardgolf.utils.card import Card, Rank, Suit


class ConcretePlayer(BasePlayer):
    """Concrete implementation for testing."""

    def get_action(self, observation: Observation) -> ActionPass:
        return ActionPass()


def test_init() -> None:
    """Test initialization sets name and empty hand (no interface required)."""
    p = ConcretePlayer("Bob")
    assert p.name == "Bob"
    assert isinstance(p.hand, Hand)
    assert len(p.hand) == 0


def test_repr() -> None:
    """Test string representation."""
    player = ConcretePlayer("TestPlayer")
    player.hand = Hand([Card(Rank.ACE, Suit.SPADES, "red")])
    assert "TestPlayer" in repr(player)
    assert "ACE" in repr(player)


def test_abstract_instantiation_raises() -> None:
    """Test that BasePlayer cannot be instantiated directly."""
    with pytest.raises(TypeError):
        BasePlayer("Abstract")  # type: ignore[abstract]
