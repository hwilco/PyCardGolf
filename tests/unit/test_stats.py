"""Tests for the PlayerStats class."""

from pycardgolf.core.stats import PlayerStats


def test_player_stats_calculation() -> None:
    """Test that derived statistics are calculated correctly."""
    scores = [10, 20, 5, 15]
    stats = PlayerStats(round_scores=scores)

    assert stats.best_score == 5
    assert stats.worst_score == 20
    assert stats.average_score == 12.5
    assert stats.total_score == 50
    assert stats.round_scores == scores


def test_player_stats_empty() -> None:
    """Test that empty scores result in zeroed statistics."""
    stats = PlayerStats(round_scores=[])

    assert stats.best_score == 0
    assert stats.worst_score == 0
    assert stats.average_score == 0.0
    assert stats.total_score == 0
    assert stats.round_scores == []
