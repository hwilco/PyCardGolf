from typing import List, Optional
from pycardgolf.utils.deck import Deck, DiscardStack
from pycardgolf.utils.card import Card
from pycardgolf.core.player import Player
from pycardgolf.core.scoring import calculate_score

class Round:
    def __init__(self, players: List[Player]):
        self.players = players
        self.deck = Deck(color="blue") # Default color
        self.discard_pile = DiscardStack()
        self.current_player_idx = 0
        self.round_over = False
        self.last_turn_player_idx: Optional[int] = None

    def setup(self):
        self.deck.shuffle()
        
        # Deal 6 cards to each player
        for player in self.players:
            player.hand = []
            for _ in range(6):
                card = self.deck.draw()
                card.face_up = False # Dealt face down
                player.hand.append(card)
        
        # Flip 2 cards for each player (standard rule variation, or let them choose? 
        # For simplicity, let's just deal them face down and let the game logic handle flipping later if needed, 
        # but standard golf usually starts with 2 random cards flipped up.
        # Let's implement the rule where players flip 2 cards at start.)
        for player in self.players:
            # Flip first two for now
            player.hand[0].face_up = True
            player.hand[1].face_up = True

        # Start discard pile
        self.discard_pile.add_card(self.deck.draw())
        self.discard_pile.peek().face_up = True

    def play(self):  # pragma: no cover
        self.setup()
        
        while not self.round_over:
            current_player = self.players[self.current_player_idx]
            current_player.take_turn(self)
            
            if self.check_round_end_condition(current_player):
                if self.last_turn_player_idx is None:
                    self.last_turn_player_idx = self.current_player_idx
                    # Everyone else gets one more turn
            
            self.advance_turn()

        self.calculate_scores()

    def advance_turn(self):
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        
        if self.last_turn_player_idx is not None and self.current_player_idx == self.last_turn_player_idx:
            self.round_over = True

    def check_round_end_condition(self, player: Player) -> bool:
        # Round ends when a player has all cards face up
        return all(card.face_up for card in player.hand)

    def calculate_scores(self):
        for player in self.players:
            # Flip all cards face up for scoring
            for card in player.hand:
                card.face_up = True
            player.score += calculate_score(player.hand)
