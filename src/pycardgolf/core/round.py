"""Module containing the Round class."""

import random
import sys

from pycardgolf.core.hand import Hand
from pycardgolf.core.player import Player
from pycardgolf.core.scoring import calculate_score
from pycardgolf.utils.constants import HAND_SIZE
from pycardgolf.utils.deck import Deck, DiscardStack


class Round:
    """Class representing a single round of Golf."""

    def __init__(self, players: list[Player], seed: int | None = None) -> None:
        """Initialize a round with players."""
        self.players: list[Player] = players
        self.seed: int = random.randrange(sys.maxsize) if seed is None else seed
        self.deck: Deck = Deck(color="blue", seed=self.seed)  # Default color
        self.discard_pile: DiscardStack = DiscardStack(seed=self.seed)
        self.current_player_idx: int = 0
        self.round_over: bool = False
        self.last_turn_player_idx: int | None = None

    def setup(self) -> None:
        """Set up the round: shuffle, deal, and flip initial cards."""
        self.deck.shuffle()

        # Deal cards to each player
        for player in self.players:
            cards = [self.deck.draw() for _ in range(HAND_SIZE)]
            player.hand = Hand(cards)

            # Flip 2 cards for each player
            # Simple approach: flip first two for now (can be random)
            # TODO: allow player to choose
            player.hand.flip_card(0)
            player.hand.flip_card(1)

        # Start discard pile
        self.discard_pile.add_card(self.deck.draw())
        self.discard_pile.peek().face_up = True

    def play(self) -> dict[Player, int]:  # pragma: no cover
        """Execute the game loop for the round.

        Returns:
            dict[Player, int]: A dictionary mapping players to their scores for this
            round.

        """
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

        self.reveal_hands()
        return self.get_scores()

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
        return player.hand.all_face_up()

    def reveal_hands(self) -> None:
        """Reveal all cards for all players."""
        for player in self.players:
            player.hand.reveal_all()

    def get_scores(self) -> dict[Player, int]:
        """Calculate scores for all players.

        Returns:
            dict[Player, int]: A dictionary mapping players to their scores for this
            round.

        Raises:
            ValueError: If a player has no hand.

        """
        return {player: calculate_score(player.hand) for player in self.players}
