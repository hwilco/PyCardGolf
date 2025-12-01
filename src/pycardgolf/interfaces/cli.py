"""Module containing the CLI interface implementation."""

from pycardgolf.core.round import Round
from pycardgolf.interfaces.base import GameInterface
from pycardgolf.utils.constants import HAND_SIZE


class CLIInterface(GameInterface):
    """Command-line interface for the game."""

    def display_state(self, game_round: Round) -> None:
        """Display the current state of the game round."""
        print("\n" + "=" * 20)
        print(f"Discard Pile Top: {game_round.discard_pile.peek()}")
        print("-" * 20)

        for i, player in enumerate(game_round.players):
            marker = "*" if i == game_round.current_player_idx else " "
            print(f"{marker} Player: {player.name}")
            # Display hand in 2 rows
            # Indices: 0 1 2
            #          3 4 5
            for row in range(2):
                row_cards = player.hand[
                    (row * (HAND_SIZE // 2)) : ((row + 1) * (HAND_SIZE // 2))
                ]
                row_str = " ".join(str(c) for c in row_cards)
                print(row_str)

    def get_input(self, prompt: str) -> str:
        """Get input from the user."""
        return input(prompt)

    def notify(self, message: str) -> None:
        """Notify the user of an event."""
        print(message)
