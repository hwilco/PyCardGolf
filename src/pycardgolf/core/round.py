"""Module containing the Round class."""

from __future__ import annotations

import random
import sys
from typing import TYPE_CHECKING

from pycardgolf.core.hand import Hand
from pycardgolf.core.scoring import calculate_score
from pycardgolf.exceptions import GameConfigError
from pycardgolf.utils.constants import HAND_SIZE, INITIAL_CARDS_TO_FLIP
from pycardgolf.utils.deck import CardStack, Deck

if TYPE_CHECKING:
    from pycardgolf.core.game import Game
    from pycardgolf.interfaces.base import GameInterface
    from pycardgolf.players.player import Player


class Round:
    """Class representing a single round of Golf."""

    def __init__(
        self,
        game: Game,
        players: list[Player],
        interface: GameInterface,
        seed: int = random.randrange(sys.maxsize),
    ) -> None:
        """Initialize a round with players."""
        self.game: Game = game
        self.players: list[Player] = players
        self.interface: GameInterface = interface
        self.seed: int = seed
        self._rng: random.Random = random.Random(self.seed)

        deck_color = "blue"
        self.interface.validate_color(deck_color)
        deck_seed = self._rng.randrange(sys.maxsize)
        self.deck: Deck = Deck(back_color=deck_color, seed=deck_seed)
        discard_seed = self._rng.randrange(sys.maxsize)
        self.discard_pile: CardStack = CardStack(seed=discard_seed)
        self.current_player_idx: int = 0
        self.round_over: bool = False
        self.last_turn_player_idx: int | None = None
        self.turn_count: int = 1

        cards_needed_for_hands = len(self.players) * HAND_SIZE
        if (
            cards_needed_for_hands >= self.deck.num_cards
        ):  # >= instead of > because we need one extra card for the discard pile
            msg = (
                f"Not enough cards for players. "
                f"{len(self.players)} players need {cards_needed_for_hands + 1} cards, "
                f"but deck only has {self.deck.num_cards} cards."
            )
            raise GameConfigError(msg)

    def setup(self) -> None:
        """Set up the round: shuffle, deal, and flip initial cards."""
        self.deck.shuffle()

        # Deal cards to each player
        for player in self.players:
            cards = [self.deck.draw() for _ in range(HAND_SIZE)]
            player.hand = Hand(cards)
            # Flip initial cards
            self.interface.display_initial_flip_prompt(player, INITIAL_CARDS_TO_FLIP)
            for _ in range(INITIAL_CARDS_TO_FLIP):
                # 1. Ask Player for choice (Decision)
                idx = player.choose_initial_card_to_flip(self)

                # 2. Round updates State (Mechanics)
                player.hand[idx].face_up = True

                # 3. Interface updates (Feedback)
                self.interface.display_flip_action(player, idx, player.hand[idx])

        # Start discard pile
        card = self.deck.draw()
        card.face_up = True
        self.discard_pile.add_card(card)

    def play(self) -> dict[Player, int]:  # pragma: no cover
        """Execute the game loop for the round.

        Returns:
            dict[Player, int]: A dictionary mapping players to their scores for this
                round.

        """
        self.setup()

        while not self.round_over:
            current_player = self.players[self.current_player_idx]
            current_player.take_turn(self.game)

            if (
                self.check_round_end_condition(current_player)
                and self.last_turn_player_idx is None
            ):
                self.last_turn_player_idx = self.current_player_idx
                self.interface.display_final_turn_notification(current_player)

            self.advance_turn()

        self.reveal_hands()
        self.interface.display_round_end(self.game)
        return self.get_scores()

    def advance_turn(self) -> None:
        """Advance the turn to the next player."""
        self.current_player_idx = (self.current_player_idx + 1) % len(
            self.players,
        )
        if self.current_player_idx == 0:
            self.turn_count += 1

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

    def __repr__(self) -> str:
        return f"Round(players={self.players}, interface={self.interface})"
