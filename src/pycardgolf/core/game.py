"""Module containing the Game class."""

import random
import sys

from pycardgolf.core.player import Player
from pycardgolf.core.round import Round
from pycardgolf.interfaces.base import GameInterface


class Game:
    """Class representing the card game."""

    def __init__(
        self,
        players: list[Player],
        interface: GameInterface,
        num_rounds: int = 9,
        seed: int = random.randrange(sys.maxsize),
    ) -> None:
        self.players: list[Player] = players
        self.scores: dict[Player, int] = dict.fromkeys(players, 0)
        self.interface: GameInterface = interface
        self.num_rounds: int = num_rounds
        self.current_round_num: int = 0
        self.current_round: Round | None = None
        self.seed: int = seed

    def start(self) -> None:
        """Start the game loop."""
        for i in range(self.num_rounds):
            self.current_round_num = i + 1
            self.interface.display_round_start(self.current_round_num)
            self.current_round = Round(
                self, self.players, self.interface, seed=self.seed
            )
            round_scores = self.current_round.play()

            # Update total scores
            for player, score in round_scores.items():
                self.scores[player] += score

            self.display_scores()

        self.declare_winner()

    def display_scores(self) -> None:
        """Display current scores for all players."""
        self.interface.display_scores(self.scores)

    def get_standings(self) -> list[Player]:
        """Return players sorted by score (ascending)."""
        return sorted(self.players, key=lambda p: self.scores[p])

    def get_winner(self) -> Player:
        """Return the player with the lowest score."""
        return self.get_standings()[0]

    def declare_winner(self) -> None:
        """Notify the interface of the game winner and final standings."""
        self.interface.display_game_over()

        standings = self.get_standings()
        standings_tuples = [(p, self.scores[p]) for p in standings]
        self.interface.display_standings(standings_tuples)

        winner = standings[0]
        self.interface.display_winner(winner, self.scores[winner])

    def __repr__(self) -> str:
        return f"Game(players={self.players}, interface={self.interface})"
