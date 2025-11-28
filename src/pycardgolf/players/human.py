from pycardgolf.core.player import Player
from pycardgolf.interfaces.base import GameInterface
from pycardgolf.core.round import Round
from pycardgolf.utils.card import Card

class HumanPlayer(Player):
    def __init__(self, name: str, interface: GameInterface):
        super().__init__(name)
        self.interface = interface

    def take_turn(self, game_round: Round) -> None:
        self.interface.display_state(game_round)
        self.interface.notify(f"It's {self.name}'s turn.")
        
        while True:
            action = self.interface.get_input("Draw from (D)eck or (P)ile? ").lower()
            if action in ['d', 'p']:
                break
            self.interface.notify("Invalid input. Please enter 'D' or 'P'.")

        if action == 'd':
            drawn_card = game_round.deck.draw()
            drawn_card.face_up = True
            self.interface.notify(f"You drew: {drawn_card}")
            
            while True:
                choice = self.interface.get_input("Action: (K)eep or (D)iscard? ").lower()
                if choice in ['k', 'd']:
                    break
                self.interface.notify("Invalid input. Please enter 'K' or 'D'.")
            
            if choice == 'k':
                self._replace_card(game_round, drawn_card)
            else:
                game_round.discard_pile.add_card(drawn_card)
                # If discarded, you can optionally flip a card (depending on rules).
                # Standard golf often allows flipping a card if you discard the drawn card.
                # Let's implement that.
                flip_choice = self.interface.get_input("Flip a card? (y/n) ").lower()
                if flip_choice == 'y':
                    self._flip_card(game_round)

        else: # action == 'p'
            drawn_card = game_round.discard_pile.draw() # Wait, DiscardStack.draw() is not implemented in original deck.py?
            # Let's check deck.py again. It has draw() but it inherits from CardStack.
            # DiscardStack inherits from CardStack.
            # But we need to make sure we are taking the top card.
            # CardStack.draw() pops from end, which is top. Correct.
            self.interface.notify(f"You took from pile: {drawn_card}")
            self._replace_card(game_round, drawn_card)

    def _replace_card(self, game_round: Round, new_card: Card) -> None:
        while True:
            try:
                idx = int(self.interface.get_input("Which card to replace (0-5)? "))
                if 0 <= idx < 6:
                    break
                self.interface.notify("Invalid index. Please enter 0-5.")
            except ValueError:
                self.interface.notify("Invalid input. Please enter a number.")
        
        old_card = self.hand[idx]
        old_card.face_up = True # Ensure it's face up when discarded
        self.hand[idx] = new_card
        game_round.discard_pile.add_card(old_card)
        self.interface.notify(f"Replaced card at {idx} with {new_card}. Discarded {old_card}.")

    def _flip_card(self, game_round: Round) -> None:
         while True:
            try:
                idx = int(self.interface.get_input("Which card to flip (0-5)? "))
                if 0 <= idx < 6:
                    if not self.hand[idx].face_up:
                        self.hand[idx].face_up = True
                        self.interface.notify(f"Flipped card at {idx}: {self.hand[idx]}")
                        break
                    else:
                        self.interface.notify("Card is already face up.")
                else:
                    self.interface.notify("Invalid index. Please enter 0-5.")
            except ValueError:
                self.interface.notify("Invalid input. Please enter a number.")
