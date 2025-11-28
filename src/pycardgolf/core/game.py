from typing import List
from pycardgolf.core.player import Player
from pycardgolf.core.round import Round

class Game:
    def __init__(self, players: List[Player], num_rounds: int = 9):
        self.players = players
        self.num_rounds = num_rounds
        self.current_round_num = 0

    def start(self):
        for i in range(self.num_rounds):
            self.current_round_num = i + 1
            print(f"--- Starting Round {self.current_round_num} ---")
            game_round = Round(self.players)
            game_round.play()
            self.display_scores()

        self.declare_winner()

    def display_scores(self):
        print("\nCurrent Scores:")
        for player in self.players:
            print(f"{player.name}: {player.score}")

    def declare_winner(self):
        print("\n--- Game Over ---")
        sorted_players = sorted(self.players, key=lambda p: p.score)
        winner = sorted_players[0]
        print(f"Winner: {winner.name} with score {winner.score}")
