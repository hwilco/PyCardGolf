"""Module containing the CLI (command-line interface) implementation."""

from pycardgolf.core.player import Player
from pycardgolf.core.round import Round
from pycardgolf.core.scoring import calculate_visible_score
from pycardgolf.interfaces.base import GameInterface
from pycardgolf.utils.constants import HAND_SIZE

CARD_DISPLAY_WIDTH = 4  # Number of characters to display for each card position


class CLIInterface(GameInterface):
    """Command-line interface for the game."""

    def display_state(self, game_round: Round) -> None:
        """Display the current state of the game round."""
        self._display_discard_pile(game_round)

        for i, player in enumerate(game_round.players):
            marker = "*" if i == game_round.current_player_idx else " "
            visible_score = calculate_visible_score(player.hand)
            print(f"{marker} Player: {player.name} (Visible Score: {visible_score})")
            self._display_hand(player)

    def _display_discard_pile(self, game_round: Round) -> None:
        """Display the discard pile."""
        discard_pile_str = f"Discard Pile Top: {game_round.discard_pile.peek()}"
        print("\n" + "=" * len(discard_pile_str))
        print(discard_pile_str)
        print("-" * len(discard_pile_str))

    def _display_hand(self, player: Player) -> None:
        """Display a player's hand."""
        # Display hand in 2 rows with position indicators
        cols = HAND_SIZE // 2

        # Prepare card strings
        row1_cards = player.hand[0:cols]
        row2_cards = player.hand[cols:HAND_SIZE]

        card_strs_1 = [str(c).center(CARD_DISPLAY_WIDTH) for c in row1_cards]
        card_strs_2 = [str(c).center(CARD_DISPLAY_WIDTH) for c in row2_cards]

        content_row_1 = " ".join(card_strs_1)
        content_row_2 = " ".join(card_strs_2)

        # Prepare indices strings
        indices_1 = [str(i).center(CARD_DISPLAY_WIDTH) for i in range(1, cols + 1)]
        indices_2 = [
            str(i).center(CARD_DISPLAY_WIDTH) for i in range(cols + 1, HAND_SIZE + 1)
        ]

        indices_str_1 = " ".join(indices_1)
        indices_str_2 = " ".join(indices_2)

        # Border
        border = "+" + "-" * (len(content_row_1) + 2) + "+"

        # Print with indices aligned
        # Indent indices by 2 spaces to account for the box border "| "
        print("  " + indices_str_1)
        print(border)
        print(f"| {content_row_1} |")
        print(f"| {content_row_2} |")
        print(border)
        print("  " + indices_str_2)

    def get_input(self, prompt: str) -> str:
        """Get input from the user."""
        return input(prompt)

    def notify(self, message: str) -> None:
        """Notify the user of an event."""
        print(message)
