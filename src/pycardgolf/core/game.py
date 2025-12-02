"""Module containing the Game class."""

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
    ) -> None:
        self.players = players
        self.interface = interface
        self.num_rounds = num_rounds
        self.current_round_num = 0

    def start(self) -> None:
        """Start the game loop."""
        for i in range(self.num_rounds):
            self.current_round_num = i + 1
            self.interface.notify(
                f"--- Starting Round {self.current_round_num} ---",
            )
            game_round = Round(self.players)
            round_scores = game_round.play()

            # Update total scores
            for player, score in round_scores.items():
                player.score += score

            self.display_scores()

        self.declare_winner()

    def display_scores(self) -> None:
        """Display current scores for all players."""
        self.interface.notify("\nCurrent Scores:")
        for player in self.players:
            self.interface.notify(f"{player.name}: {player.score}")

    def get_standings(self) -> list[Player]:
        """Return players sorted by score (ascending)."""
        return sorted(self.players, key=lambda p: p.score)

    def get_winner(self) -> Player:
        """Return the player with the lowest score."""
        return self.get_standings()[0]

    def declare_winner(self) -> None:
        """Notify the interface of the game winner."""
        self.interface.notify("\n--- Game Over ---")
        winner = self.get_winner()
        self.interface.notify(
            f"Winner: {winner.name} with score {winner.score}",
        )
