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
from pycardgolf.core.phases import RoundPhase
from pycardgolf.core.round import Round, RoundFactory
from pycardgolf.exceptions import GameConfigError, IllegalActionError
from pycardgolf.utils.constants import HAND_SIZE


def test_validate_config_success():
    """Test that validate_config passes for valid configuration."""
    Round.validate_config(num_players=2)


def test_validate_config_failure():
    """Test that validate_config raises GameConfigError for invalid configuration."""
    with pytest.raises(GameConfigError, match="Not enough cards"):
        Round.validate_config(num_players=10)


def test_round_initialization():
    player_names = ["P1", "P2"]
    round_instance = RoundFactory.create_standard_round(player_names=player_names)

    assert round_instance.phase == RoundPhase.SETUP
    assert len(round_instance.hands) == 2
    assert len(round_instance.hands[0]) == HAND_SIZE
    assert len(round_instance.hands[1]) == HAND_SIZE
    assert round_instance.discard_pile.num_cards == 1


def test_rounds_have_unique_default_seeds(mocker):
    """Test that multiple rounds instantiated without seeds get unique seeds."""
    mock_randrange = mocker.patch("pycardgolf.utils.mixins.random.randrange")
    mock_randrange.side_effect = [100, 200, 300, 400, 500, 600]

    r1 = RoundFactory.create_standard_round(["P1", "P2"])
    r2 = RoundFactory.create_standard_round(["P1", "P2"])

    assert r1.seed is not None
    assert r2.seed is not None
    assert r1.seed != r2.seed


def test_round_step_setup_phase():
    player_names = ["P1"]
    round_instance = RoundFactory.create_standard_round(player_names=player_names)

    assert round_instance.phase == RoundPhase.SETUP
    assert round_instance.get_current_player_idx() == 0

    # Action 1: Flip index 0
    events = round_instance.step(ActionFlipCard(hand_index=0))
    assert len(events) == 1
    assert isinstance(events[0], CardFlippedEvent)
    assert round_instance.hands[0].is_face_up(0)
    assert round_instance.phase == RoundPhase.SETUP

    # Action 2: Flip index 1
    events = round_instance.step(ActionFlipCard(hand_index=1))
    assert round_instance.hands[0].is_face_up(1)
    assert round_instance.phase == RoundPhase.DRAW
    assert isinstance(events[0], CardFlippedEvent)
    assert isinstance(events[-1], TurnStartEvent)


def test_round_step_illegal_setup_action():
    round_instance = RoundFactory.create_standard_round(player_names=["P1"])
    with pytest.raises(IllegalActionError):
        round_instance.step(ActionPass())


def test_round_step_draw_phase():
    round_instance = RoundFactory.create_standard_round(player_names=["P1"])
    round_instance.phase = RoundPhase.DRAW
    events = round_instance.step(ActionDrawDeck())
    assert isinstance(events[0], CardDrawnDeckEvent)
    assert round_instance.phase == RoundPhase.ACTION
    assert round_instance.drawn_card_id is not None
    assert round_instance.drawn_from_deck is True


def test_round_step_action_phase_swap():
    round_instance = RoundFactory.create_standard_round(player_names=["P1"])
    round_instance.phase = RoundPhase.ACTION
    drawn = 99
    round_instance.drawn_card_id = drawn

    initial_hand_card = round_instance.hands[0][0]
    events = round_instance.step(ActionSwapCard(hand_index=0))

    assert isinstance(events[0], CardSwappedEvent)
    assert round_instance.hands[0][0] == drawn
    assert round_instance.discard_pile.peek() == initial_hand_card
    assert round_instance.phase == RoundPhase.DRAW


def test_round_step_action_phase_discard_drawn():
    round_instance = RoundFactory.create_standard_round(player_names=["P1"])
    round_instance.phase = RoundPhase.ACTION
    drawn = 99
    round_instance.drawn_card_id = drawn
    round_instance.drawn_from_deck = True

    events = round_instance.step(ActionDiscardDrawn())
    assert isinstance(events[0], CardDiscardedEvent)
    assert round_instance.discard_pile.peek() == drawn
    assert round_instance.phase == RoundPhase.FLIP


def test_round_step_flip_phase():
    round_instance = RoundFactory.create_standard_round(player_names=["P1"])
    round_instance.phase = RoundPhase.FLIP
    events = round_instance.step(ActionFlipCard(hand_index=2))
    assert isinstance(events[0], CardFlippedEvent)
    assert round_instance.hands[0].is_face_up(2)
    assert round_instance.phase == RoundPhase.DRAW


def get_all_slots(obj):
    """Gather all slots from class hierarchy."""
    slots = set()
    for cls in type(obj).__mro__:
        dict_slots = getattr(cls, "__slots__", None)
        if dict_slots:
            if isinstance(dict_slots, str):
                slots.add(dict_slots)
            else:
                slots.update(dict_slots)
    return slots


def test_round_clone_copies_all_attributes():
    """Verify that Round.clone() correctly copies all attributes."""
    player_names = ["P1", "P2"]
    original = RoundFactory.create_standard_round(player_names=player_names)
    original.drawn_card_id = 42
    original.drawn_from_deck = True

    clone = original.clone(preserve_rng=True)

    slots = get_all_slots(original)

    # Check all slots are present and values match
    for slot in slots:
        assert hasattr(clone, slot), f"Clone missing slot: {slot}"

        # Skip RNG comparison as random.Random doesn't support state-based equality
        if slot in ("rng", "_rng"):
            continue

        orig_val = getattr(original, slot)
        clone_val = getattr(clone, slot)

        assert orig_val == clone_val, (
            f"Value mismatch for slot {slot}: {orig_val} != {clone_val}"
        )

        # For mutable collections, ensure deep copy (different IDs)
        if isinstance(orig_val, (list, dict)):
            assert id(orig_val) != id(clone_val), (
                f"Shallow copy detected for slot {slot}"
            )

    # Specifically check hands (list of Hand objects)
    assert len(original.hands) == len(clone.hands)
    for h1, h2 in zip(original.hands, clone.hands, strict=True):
        assert h1 is not h2
        assert h1.card_ids == h2.card_ids
        assert h1.face_up_mask == h2.face_up_mask
