"""Module containing the Round class."""

from pycardgolf.core.player import Player
from pycardgolf.core.scoring import calculate_score
from pycardgolf.utils.constants import Constants
from pycardgolf.utils.deck import Deck, DiscardStack


class Round:
    """Class representing a single round of Golf."""

    def __init__(self, players: list[Player]) -> None:
        """Initialize a round with players."""
        self.players: list[Player] = players
        self.deck: Deck = Deck(color="blue")  # Default color
        self.discard_pile: DiscardStack = DiscardStack()
        self.current_player_idx: int = 0
        self.round_over: bool = False
        self.last_turn_player_idx: int | None = None

    def setup(self) -> None:
        """Set up the round: shuffle, deal, and flip initial cards."""
        self.deck.shuffle()

        # Deal cards to each player
        for player in self.players:
            player.hand = []  # Clear hand before dealing
            for _ in range(Constants.HAND_SIZE):
                player.hand.append(self.deck.draw())

        # Flip 2 random cards for each player
        for player in self.players:
            # Simple approach: flip first two for now (can be random)
            # TODO: allow player to choose
            player.hand[0].face_up = True
            player.hand[1].face_up = True

        # Start discard pile
        self.discard_pile.add_card(self.deck.draw())
        self.discard_pile.peek().face_up = True

    def play(self) -> None:  # pragma: no cover
        """Execute the game loop for the round."""
        self.setup()

        while not self.round_over:
            current_player = self.players[self.current_player_idx]
            current_player.take_turn(self)

            if (
                self.check_round_end_condition(current_player)
                and self.last_turn_player_idx is None
            ):
                self.last_turn_player_idx = self.current_player_idx
                # Notify players?

            self.advance_turn()

        self.calculate_scores()

    def advance_turn(self) -> None:
        """Advance the turn to the next player."""
        self.current_player_idx = (self.current_player_idx + 1) % len(
            self.players,
        )

        if (
            self.last_turn_player_idx is not None
            and self.current_player_idx == self.last_turn_player_idx
        ):
            self.round_over = True

    def check_round_end_condition(self, player: Player) -> bool:
        """Check if the round should end (player has all cards face up)."""
        # Round ends when a player has all cards face up
        return all(card.face_up for card in player.hand)

    def calculate_scores(self) -> None:
        """Calculate and update scores for all players."""
        for player in self.players:
            # Flip all cards face up for scoring
            for card in player.hand:
                card.face_up = True
            player.score += calculate_score(player.hand)
