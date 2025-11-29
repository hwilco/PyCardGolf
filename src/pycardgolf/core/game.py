from typing import List
from pycardgolf.core.player import Player
from pycardgolf.core.round import Round
from pycardgolf.interfaces.base import GameInterface


class Game:
    def __init__(
        self,
        players: List[Player],
        interface: GameInterface,
        num_rounds: int = 9,
    ):
        self.players = players
        self.interface = interface
        self.num_rounds = num_rounds
        self.current_round_num = 0

    def start(self):
        for i in range(self.num_rounds):
            self.current_round_num = i + 1
            self.interface.notify(
                f"--- Starting Round {self.current_round_num} ---"
            )
            game_round = Round(self.players)
            game_round.play()
            self.display_scores()

        self.declare_winner()

    def display_scores(self):
        self.interface.notify("\nCurrent Scores:")
        for player in self.players:
            self.interface.notify(f"{player.name}: {player.score}")

    def get_standings(self) -> List[Player]:
        return sorted(self.players, key=lambda p: p.score)

    def get_winner(self) -> Player:
        return self.get_standings()[0]

    def declare_winner(self):
        self.interface.notify("\n--- Game Over ---")
        winner = self.get_winner()
        self.interface.notify(
            f"Winner: {winner.name} with score {winner.score}"
        )
