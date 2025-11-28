import random
from pycardgolf.core.player import Player
from pycardgolf.core.round import Round

class RandomBot(Player):
    def take_turn(self, game_round: Round) -> None:
        # Simple random strategy
        if random.choice([True, False]):
            # Draw from deck
            drawn_card = game_round.deck.draw()
            drawn_card.face_up = True
            
            if random.choice([True, False]):
                # Keep
                idx = random.randint(0, 5)
                old_card = self.hand[idx]
                old_card.face_up = True
                self.hand[idx] = drawn_card
                game_round.discard_pile.add_card(old_card)
            else:
                # Discard
                game_round.discard_pile.add_card(drawn_card)
                # Maybe flip
                if random.choice([True, False]):
                     # Find face down cards
                    face_down_indices = [i for i, c in enumerate(self.hand) if not c.face_up]
                    if face_down_indices:
                        idx = random.choice(face_down_indices)
                        self.hand[idx].face_up = True
        else:
            # Draw from pile (if available)
            # Check if pile has cards (it should, but good to be safe)
            if game_round.discard_pile.num_cards > 0:
                drawn_card = game_round.discard_pile.draw()
                idx = random.randint(0, 5)
                old_card = self.hand[idx]
                old_card.face_up = True
                self.hand[idx] = drawn_card
                game_round.discard_pile.add_card(old_card)
            else:
                # Fallback to deck if pile empty (shouldn't happen with setup)
                drawn_card = game_round.deck.draw()
                game_round.discard_pile.add_card(drawn_card)
