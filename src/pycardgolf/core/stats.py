"""Module containing statistics related classes."""

from dataclasses import dataclass, field


@dataclass
class PlayerStats:
    """Class representing a player's statistics."""

    round_scores: list[int]
    best_score: int = field(init=False)
    worst_score: int = field(init=False)
    average_score: float = field(init=False)
    total_score: int = field(init=False)

    def __post_init__(self) -> None:
        """Calculate derived statistics."""
        if not self.round_scores:
            self.best_score = 0
            self.worst_score = 0
            self.average_score = 0.0
            self.total_score = 0
            return

        self.best_score = min(self.round_scores)
        self.worst_score = max(self.round_scores)
        self.average_score = sum(self.round_scores) / len(self.round_scores)
        self.total_score = sum(self.round_scores)
