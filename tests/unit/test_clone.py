from pycardgolf.core.actions import ActionFlipCard
from pycardgolf.core.round import RoundFactory


def test_round_clone_state_independence():
    """Test that cloning a round does not share object references."""
    r = RoundFactory.create_standard_round(["P1", "P2"], seed=42)
    # The first action in SETUP phase is to flip cards
    r.step(ActionFlipCard(hand_index=0))

    cloned = r.clone()

    # Assert state matches
    assert cloned.phase == r.phase
    assert cloned.turn_count == r.turn_count
    assert cloned.hands[0][0].face_up == r.hands[0][0].face_up

    # Modify original
    r.step(ActionFlipCard(hand_index=1))

    # Assert clone is unaffected
    assert not cloned.hands[0][1].face_up
    assert r.hands[0][1].face_up


def test_round_clone_preserve_rng(mocker):
    """Test that preserve_rng correctly maintains or randomized the PRNG state."""
    # Patch randrange so the original and the clone get known, different seeds
    mock_randrange = mocker.patch("pycardgolf.core.round.random.randrange")
    mock_randrange.side_effect = [42, 100, 200, 300, 400, 500]

    r = RoundFactory.create_standard_round(["P1", "P2"], seed=42)

    # Clone with default (preserve_rng=False)
    cloned_random = r.clone()
    # Clone with preserve_rng=True
    cloned_preserved = r.clone(preserve_rng=True)

    # Draw a card from each deck to advance their respective PRNGs
    # (Deck uses the same RNG implementation logic for shuffling)

    # The underlying Round _rng should be different for the default clone
    val1 = r.rng.random()
    val2 = cloned_random.rng.random()
    val3 = cloned_preserved.rng.random()

    assert val1 != val2, "Default clone should have a new RNG state/seed"
    assert val1 == val3, "Preserved clone should produce identical RNG output"
