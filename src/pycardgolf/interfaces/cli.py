"""Module containing the CLI (command-line interface) implementation."""

from pycardgolf.core.round import Round
from pycardgolf.core.scoring import calculate_visible_score
from pycardgolf.interfaces.base import GameInterface
from pycardgolf.utils.constants import HAND_SIZE

CARD_DISPLAY_WIDTH = 2  # Number of characters to display for each card position


class CLIInterface(GameInterface):
    """Command-line interface for the game."""

    def display_state(self, game_round: Round) -> None:
        """Display the current state of the game round."""
        discard_pile_str = f"Discard Pile Top: {game_round.discard_pile.peek()}"
        print("\n" + "=" * len(discard_pile_str))
        print(discard_pile_str)
        print("-" * len(discard_pile_str))

        for i, player in enumerate(game_round.players):
            marker = "*" if i == game_round.current_player_idx else " "
            visible_score = calculate_visible_score(player.hand)
            print(f"{marker} Player: {player.name} (Visible Score: {visible_score})")
            # Display hand in 2 rows with position indicators
            # Indices: 1 2 3
            #          4 5 6
            for row in range(2):
                row_cards = player.hand[
                    (row * (HAND_SIZE // 2)) : ((row + 1) * (HAND_SIZE // 2))
                ]
                row_str = " ".join(str(c) for c in row_cards)
                print(row_str)
                # Print position indices below cards
                start_idx = row * (HAND_SIZE // 2) + 1  # 1-indexed
                indices = " ".join(
                    self._format_index(i)
                    for i in range(start_idx, start_idx + HAND_SIZE // 2)
                )
                print(indices)

    def get_input(self, prompt: str) -> str:
        """Get input from the user."""
        return input(prompt)

    def notify(self, message: str) -> None:
        """Notify the user of an event."""
        print(message)

    def _format_index(self, idx: int) -> str:
        """Format an index for display by adding proper padding."""
        idx_str = str(idx)
        return idx_str + (CARD_DISPLAY_WIDTH - len(idx_str)) * " "
