from pycardgolf.interfaces.base import GameInterface
from pycardgolf.core.round import Round

class CLIInterface(GameInterface):
    def display_state(self, game_round: Round) -> None:
        print("\n" + "="*20)
        print(f"Discard Pile Top: {game_round.discard_pile.peek()}")
        print("="*20)
        
        for player in game_round.players:
            print(f"\nPlayer: {player.name}")
            # Display hand as 2x3 grid
            for i in range(2):
                row_str = ""
                for j in range(3):
                    idx = i * 3 + j
                    if idx < len(player.hand):
                        row_str += str(player.hand[idx]) + "\t"
                print(row_str)

    def get_input(self, prompt: str) -> str:
        return input(prompt)

    def notify(self, message: str) -> None:
        print(message)
