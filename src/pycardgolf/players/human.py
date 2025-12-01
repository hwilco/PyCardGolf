"""Module containing the HumanPlayer class."""

from pycardgolf.core.player import Player
from pycardgolf.core.round import Round
from pycardgolf.interfaces.base import GameInterface
from pycardgolf.utils.card import Card
from pycardgolf.utils.constants import HAND_SIZE


class HumanPlayer(Player):
    """A human player that interacts via the game interface."""

    def __init__(self, name: str, interface: GameInterface) -> None:
        """Initialize the human player with a name and interface."""
        super().__init__(name)
        self.interface: GameInterface = interface

    def take_turn(self, game_round: Round) -> None:
        """Execute the human player's turn."""
        self.interface.display_state(game_round)
        self.interface.notify(f"It's {self.name}'s turn.")

        while True:
            action = self.interface.get_input(
                "Draw from (d)eck or ()ile? ",
            ).lower()
            if action in ["d", "p"]:
                break
            self.interface.notify("Invalid input. Please enter 'd' or 'p'.")

        if action == "d":
            drawn_card = game_round.deck.draw()
            drawn_card.face_up = True
            self.interface.notify(f"You drew: {drawn_card}")

            while True:
                choice = self.interface.get_input(
                    "Action: (k)eep or (d)iscard? ",
                ).lower()
                if choice in ["k", "d"]:
                    break
                self.interface.notify(
                    "Invalid input. Please enter 'k' or 'd'.",
                )

            if choice == "k":
                idx = self._choose_index_to_replace()
                old_card = self._replace_card(idx, drawn_card)
                game_round.discard_pile.add_card(old_card)
                self.interface.notify(
                    f"Replaced card at {idx} with {drawn_card}. Discarded {old_card}.",
                )
            else:
                game_round.discard_pile.add_card(drawn_card)
                # If discarded, you can optionally flip a card.
                while True:
                    flip_choice = self.interface.get_input(
                        "Flip a card? (y/n) ",
                    ).lower()
                    if flip_choice in ["y", "n"]:
                        break
                    self.interface.notify(
                        "Invalid input. Please enter 'y' or 'n'.",
                    )
                if flip_choice == "y":
                    self._flip_card()

        else:  # action == 'p'
            drawn_card = game_round.discard_pile.draw()
            self.interface.notify(f"You took from pile: {drawn_card}")
            idx = self._choose_index_to_replace()
            old_card = self._replace_card(idx, drawn_card)
            game_round.discard_pile.add_card(old_card)
            self.interface.notify(
                f"Replaced card at {idx} with {drawn_card}. Discarded {old_card}.",
            )

    def _replace_card(self, idx: int, new_card: Card) -> Card:
        old_card = self.hand[idx]
        self.hand[idx] = new_card
        self.hand[idx].face_up = True
        return old_card

    def _choose_index_to_replace(self) -> int:
        while True:
            try:
                idx = int(
                    self.interface.get_input("Which card to replace (0-5)? "),
                )
                if 0 <= idx < HAND_SIZE:
                    break
                self.interface.notify("Invalid index. Please enter 0-5.")
            except ValueError:
                self.interface.notify("Invalid input. Please enter a number.")
        return idx

    def _flip_card(self) -> None:
        while True:
            try:
                idx = int(
                    self.interface.get_input("Which card to flip (0-5)? "),
                )
                if 0 <= idx < HAND_SIZE:
                    if not self.hand[idx].face_up:
                        self.hand[idx].flip()
                        self.interface.notify(
                            f"Flipped card at {idx}: {self.hand[idx]}",
                        )
                        break
                    self.interface.notify("Card is already face up.")
                else:
                    self.interface.notify("Invalid index. Please enter 0-5.")
            except ValueError:
                self.interface.notify("Invalid input. Please enter a number.")
