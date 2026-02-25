"""Unit tests for Action validation and ActionSpace."""

import pytest

from pycardgolf.core.actions import Action, ActionSpace, ActionType
from pycardgolf.utils.constants import HAND_SIZE


def test_action_validation_success():
    """Verify that valid combinations instantiate without error."""
    # Targeted actions with index
    Action(ActionType.FLIP, 0)
    Action(ActionType.SWAP, 5)

    # Non-targeted actions without index
    Action(ActionType.DRAW_DECK, None)
    Action(ActionType.DRAW_DISCARD, None)
    Action(ActionType.DISCARD_DRAWN, None)
    Action(ActionType.PASS, None)


def test_action_validation_fails():
    """Verify that invalid combinations trigger the assertion."""
    # Targeted action missing index
    with pytest.raises(AssertionError, match="must have a target_index"):
        Action(ActionType.FLIP, None)

    with pytest.raises(AssertionError, match="must have a target_index"):
        Action(ActionType.SWAP, None)

    # Non-targeted action with index
    with pytest.raises(AssertionError, match="must not have a target_index"):
        Action(ActionType.DRAW_DECK, 0)

    with pytest.raises(AssertionError, match="must not have a target_index"):
        Action(ActionType.PASS, 1)


def test_action_space_is_flyweight():
    """Verify that ActionSpace returns the same instances."""
    assert ActionSpace.DRAW_DECK is ActionSpace.DRAW_DECK
    assert ActionSpace.DRAW_DISCARD is ActionSpace.DRAW_DISCARD
    assert ActionSpace.DISCARD_DRAWN is ActionSpace.DISCARD_DRAWN
    assert ActionSpace.PASS is ActionSpace.PASS

    for i in range(HAND_SIZE):
        assert ActionSpace.FLIP[i] is ActionSpace.FLIP[i]
        assert ActionSpace.SWAP[i] is ActionSpace.SWAP[i]


def test_action_space_content():
    """Verify ActionSpace instances have correct data."""
    assert ActionSpace.DRAW_DECK.action_type == ActionType.DRAW_DECK
    assert ActionSpace.DRAW_DECK.target_index is None

    assert ActionSpace.FLIP[0].action_type == ActionType.FLIP
    assert ActionSpace.FLIP[0].target_index == 0

    assert ActionSpace.SWAP[HAND_SIZE - 1].action_type == ActionType.SWAP
    assert ActionSpace.SWAP[HAND_SIZE - 1].target_index == HAND_SIZE - 1
