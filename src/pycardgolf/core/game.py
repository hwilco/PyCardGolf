"""Module containing the Game class."""

from __future__ import annotations

import random
import sys
from typing import TYPE_CHECKING
import time

from pycardgolf.core.events import (
    CardDiscardedEvent,
    CardDrawnDeckEvent,
    CardDrawnDiscardEvent,
    CardFlippedEvent,
    CardSwappedEvent,
    GameEvent,
    MessageEvent,
    RoundEndEvent,
    TurnStartEvent,
)
from pycardgolf.core.round import Round
from pycardgolf.core.state import RoundPhase
from pycardgolf.core.stats import PlayerStats
from pycardgolf.exceptions import GameExitError
from pycardgolf.interfaces.base import GameInterface
from pycardgolf.players.player import Player

if TYPE_CHECKING:
    pass


class Game:
    """Class representing the card game."""

    def __init__(
        self,
        players: list[Player],
        interface: GameInterface,
        num_rounds: int = 9,
        seed: int = random.randrange(sys.maxsize),
    ) -> None:
        self.players: list[Player] = players
        self.scores: dict[Player, int] = dict.fromkeys(players, 0)
        self.round_history: dict[Player, list[int]] = {p: [] for p in players}
        self.interface: GameInterface = interface
        self.num_rounds: int = num_rounds
        self.current_round_num: int = 0
        self.current_round: Round | None = None
        self.seed: int = seed
        self._rng: random.Random = random.Random(self.seed)

    def start(self) -> None:
        """Start the game loop."""
        try:
            for i in range(self.num_rounds):
                self.current_round_num = i + 1
                self.interface.display_round_start(self.current_round_num)
                round_seed = self._rng.randrange(sys.maxsize)
                # Note: Round signature changed (removed interface)
                self.current_round = Round(self, self.players, seed=round_seed)

                # New Loop
                self._run_round_loop()

                # Update total scores
                # Round.get_scores() is available but we need latest state.
                # RoundEndEvent provides scores too.
                # Logic: _run_round_loop returns scores? or we read from round.

                round_scores = self.current_round.get_scores()

                for player, score in round_scores.items():
                    self.scores[player] += score
                    self.round_history[player].append(score)

                self.display_scores()

            self.declare_winner()
        except GameExitError:
            self.interface.display_message("\nGame exited by user.")
        except KeyboardInterrupt:
            self.interface.display_message("\nGame interrupted.")

    def _run_round_loop(self) -> None:
        """Execute the engine loop for the current round."""
        if self.current_round is None:
            return

        round_instance = self.current_round

        # Initial setup phase prompt or turn?
        # Round starts in SETUP phase for player 0.
        # We should display turn start logic manually for the very first action?
        # Or rely on loop?

        # Display initial state
        # round_instance.setup() # setup is now implicit in init

        # Loop
        while (
            not round_instance.round_over
            and round_instance.phase != RoundPhase.FINISHED
        ):
            current_player = round_instance.get_current_player()

            # Display update?
            # Interface typically clears screen or updates board.
            # We can call display_state here?
            # But Display State required 'Game' object.
            # We are inside 'Game'.
            # self.interface.display_state(self)
            # Note: display_state(self) might be heavy.
            # But the old loop called `interface.display_state(game)` inside `HumanPlayer.take_turn`.
            # We mimic that behavior by calling it if current player is human?
            # Or just call it always to keep UI fresh.
            if hasattr(current_player, "get_action"):  # It is a Player
                # Optimization for bots: maybe don't render full board every step?
                # But for Human spectator we want to see.
                # self.interface.display_state(self)
                pass

            obs = round_instance.get_observation(current_player)

            # Get Action
            # If Human, this might block on input
            try:
                action = current_player.get_action(obs)
            except GameExitError:
                raise
            except Exception as e:
                # If bot crashes or logic error
                # We should probably catch/log
                raise e

            # Step
            events = round_instance.step(action)

            # Process Events (Update UI)
            self.process_events(events)

            # Optional: Add small delay for bot moves if viewing?
            # time.sleep(0.5)

    def process_events(self, events: list[GameEvent]) -> None:
        """Update interface based on events."""
        for event in events:
            if isinstance(event, TurnStartEvent):
                self.interface.display_turn_start(event.player)
            elif isinstance(event, CardDrawnDeckEvent):
                self.interface.display_drawn_card(event.player, event.card)
            elif isinstance(event, CardDrawnDiscardEvent):
                self.interface.display_discard_draw(event.player, event.card)
            elif isinstance(event, CardDiscardedEvent):
                self.interface.display_discard_action(event.player, event.card)
            elif isinstance(event, CardSwappedEvent):
                self.interface.display_replace_action(
                    event.player, event.hand_index, event.new_card, event.old_card
                )
            elif isinstance(event, CardFlippedEvent):
                self.interface.display_flip_action(
                    event.player, event.hand_index, event.card
                )
            elif isinstance(event, RoundEndEvent):
                self.interface.display_round_end(self)
            elif isinstance(event, MessageEvent):
                self.interface.display_message(event.message)

    def display_scores(self) -> None:
        """Display current scores for all players."""
        self.interface.display_scores(self.scores)

    def get_standings(self) -> list[Player]:
        """Return players sorted by score (ascending)."""
        return sorted(self.players, key=lambda p: self.scores[p])

    def get_winner(self) -> Player:
        """Return the player with the lowest score."""
        return self.get_standings()[0]

    def get_stats(self) -> dict[Player, PlayerStats]:
        """Calculate game statistics for each player."""
        return {
            player: PlayerStats(self.round_history[player]) for player in self.players
        }

    def declare_winner(self) -> None:
        """Notify the interface of the game winner and final standings."""
        self.interface.display_game_over()

        standings = self.get_standings()
        standings_tuples = [(p, self.scores[p]) for p in standings]

        self.interface.display_game_stats(self.get_stats())
        self.interface.display_standings(standings_tuples)

        winner = standings[0]
        self.interface.display_winner(winner, self.scores[winner])

    def __repr__(self) -> str:
        return f"Game(players={self.players}, interface={self.interface})"
