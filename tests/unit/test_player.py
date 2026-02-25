"""Tests for the abstract BasePlayer class."""

import pytest

from pycardgolf.core.actions import Action, ActionSpace
from pycardgolf.core.observation import Observation
from pycardgolf.players.player import BasePlayer


class ConcretePlayer(BasePlayer):
    """Concrete implementation for testing."""

    def get_action(self, observation: Observation) -> Action:
        return ActionSpace.PASS


def test_init() -> None:
    """Test initialization sets name (no interface required)."""
    p = ConcretePlayer("Bob")
    assert p.name == "Bob"


def test_repr() -> None:
    """Test string representation."""
    player = ConcretePlayer("TestPlayer")
    assert "TestPlayer" in repr(player)


def test_abstract_instantiation_raises() -> None:
    """Test that BasePlayer cannot be instantiated directly."""
    with pytest.raises(TypeError):
        BasePlayer("Abstract")  # type: ignore[abstract]
