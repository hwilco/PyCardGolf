"""Module containing the Game class."""

from __future__ import annotations

import random
import sys
from typing import TYPE_CHECKING

from pycardgolf.core.events import (
    CardDiscardedEvent,
    CardDrawnDeckEvent,
    CardDrawnDiscardEvent,
    CardFlippedEvent,
    CardSwappedEvent,
    GameEvent,
    RoundEndEvent,
    TurnStartEvent,
)
from pycardgolf.core.round import Round
from pycardgolf.core.state import RoundPhase
from pycardgolf.core.stats import PlayerStats

if TYPE_CHECKING:
    from pycardgolf.interfaces.base import GameInterface
    from pycardgolf.players import Player


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
        for i in range(self.num_rounds):
            self.current_round_num = i + 1
            self.interface.display_round_start(self.current_round_num)
            round_seed = self._rng.randrange(sys.maxsize)

            # Update: Initialize Round with num_players and names
            player_names = [p.name for p in self.players]
            self.current_round = Round(
                player_names=player_names,
                seed=round_seed,
            )

            # Sync hands to players so they have the correct state
            for idx, player in enumerate(self.players):
                player.hand = self.current_round.hands[idx]

            # New Loop
            self._run_round_loop()

            # Update total scores
            round_scores_indices = self.current_round.get_scores()

            # Map indices back to players
            round_scores = {
                self.players[idx]: score for idx, score in round_scores_indices.items()
            }

            for player, score in round_scores.items():
                self.scores[player] += score
                self.round_history[player].append(score)

            self.display_scores()

        self.declare_winner()

    def _run_round_loop(self) -> None:
        """Execute the engine loop for the current round."""
        if self.current_round is None:
            return

        round_instance = self.current_round

        # Loop
        while (
            not round_instance.round_over
            and round_instance.phase != RoundPhase.FINISHED
        ):
            current_player_idx = round_instance.get_current_player_idx()
            current_player = self.players[current_player_idx]

            if hasattr(current_player, "get_action"):
                # Optional: display state for humans
                pass

            obs = round_instance.get_observation(current_player_idx)

            # Get Action
            action = current_player.get_action(obs)

            # Step
            events = round_instance.step(action)

            # Display Events (Update UI)
            self.display_events(events)

    def display_events(self, events: list[GameEvent]) -> None:
        """Update interface based on events."""
        for event in events:
            match event:
                case TurnStartEvent(player_idx=pid):
                    next_player = self.players[(pid + 1) % len(self.players)]
                    self.interface.display_turn_start(self.players[pid], next_player)
                case CardDrawnDeckEvent(player_idx=pid, card=card):
                    self.interface.display_drawn_card(self.players[pid], card)
                case CardDrawnDiscardEvent(player_idx=pid, card=card):
                    self.interface.display_discard_draw(self.players[pid], card)
                case CardDiscardedEvent(player_idx=pid, card=card):
                    self.interface.display_discard_action(self.players[pid], card)
                case CardSwappedEvent(
                    player_idx=pid, hand_index=idx, new_card=new, old_card=old
                ):
                    self.interface.display_replace_action(
                        self.players[pid], idx, new, old
                    )
                case CardFlippedEvent(player_idx=pid, hand_index=idx, card=card):
                    self.interface.display_flip_action(self.players[pid], idx, card)
                case RoundEndEvent():
                    self.interface.display_round_end(self)

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
