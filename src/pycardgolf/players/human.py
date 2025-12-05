"""Module containing the HumanPlayer class."""

from typing import TYPE_CHECKING

from pycardgolf.core.game import Game
from pycardgolf.core.player import Player
from pycardgolf.exceptions import GameConfigError
from pycardgolf.interfaces.base import GameInterface

if TYPE_CHECKING:
    from pycardgolf.core.round import Round


class HumanPlayer(Player):
    """A human player that interacts via the game interface."""

    def __init__(self, name: str, interface: GameInterface) -> None:
        """Initialize the human player with a name and interface."""
        super().__init__(name)
        self.interface: GameInterface = interface

    def take_turn(self, game: Game) -> None:
        """Execute the human player's turn."""
        if game.current_round is None:
            msg = "Game round is None."
            raise GameConfigError(msg)
        game_round: Round = game.current_round
        self.interface.display_state(game)
        self.interface.notify(f"It's {self.name}'s turn.")

        deck_card = game.current_round.deck.peek()
        discard_card = game.current_round.discard_pile.peek()
        action = self.interface.get_draw_choice(deck_card, discard_card)

        if action == "d":
            drawn_card = game_round.deck.draw()
            drawn_card.face_up = True
            self.interface.display_drawn_card(self.name, drawn_card)

            choice = self.interface.get_keep_or_discard_choice()

            if choice == "k":
                idx = self._choose_index_to_replace()
                old_card = self.hand.replace(idx, drawn_card)
                old_card.face_up = True
                game_round.discard_pile.add_card(old_card)
                self.interface.display_replace_action(
                    self.name, idx, drawn_card, old_card
                )
            else:
                game_round.discard_pile.add_card(drawn_card)
                # If discarded, you can optionally flip a card.
                flip_choice = self.interface.get_flip_choice()
                if flip_choice == "y":
                    self._flip_card()

        else:  # action == 'p'
            drawn_card = game_round.discard_pile.draw()
            self.interface.display_discard_draw(self.name, drawn_card)
            idx = self._choose_index_to_replace()
            old_card = self.hand.replace(idx, drawn_card)
            old_card.face_up = True
            game_round.discard_pile.add_card(old_card)
            self.interface.display_replace_action(self.name, idx, drawn_card, old_card)

    def _choose_index_to_replace(self) -> int:
        """Prompt user to choose a card position to replace.

        Returns 0-indexed position for internal use.
        """
        return self.interface.get_index_to_replace()

    def _flip_card(self) -> None:
        """Prompt user to choose a card to flip."""
        while True:
            idx_internal = self.interface.get_index_to_flip()
            if not self.hand[idx_internal].face_up:
                self.hand.flip_card(idx_internal)
                self.interface.display_flip_action(
                    self.name, idx_internal, self.hand[idx_internal]
                )
                break
            self.interface.notify("Card is already face up.")
