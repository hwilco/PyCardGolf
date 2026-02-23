"""Module containing the Game class."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from pycardgolf.core.events import (
    GameEvent,
    GameOverEvent,
    GameStartedEvent,
    GameStatsEvent,
    RoundEndEvent,
    RoundStartEvent,
    ScoreBoardEvent,
)
from pycardgolf.core.observation import ObservationBuilder
from pycardgolf.core.phases import RoundPhase
from pycardgolf.core.round import Round, RoundFactory
from pycardgolf.core.stats import PlayerStats
from pycardgolf.utils.mixins import RNGMixin

if TYPE_CHECKING:
    from pycardgolf.core.event_bus import EventBus
    from pycardgolf.players import BasePlayer


class Game(RNGMixin):
    """Class representing the card game."""

    def __init__(
        self,
        players: list[BasePlayer],
        event_bus: EventBus,
        num_rounds: int = 9,
        seed: int | None = None,
    ) -> None:
        self.players: list[BasePlayer] = players
        self.scores: dict[BasePlayer, int] = dict.fromkeys(players, 0)
        self.round_history: dict[BasePlayer, list[int]] = {p: [] for p in players}
        self.event_bus: EventBus = event_bus
        self.num_rounds: int = num_rounds
        self.current_round_num: int = 0
        self.current_round: Round | None = None
        super().__init__(seed=seed)

        # Re-initialize player RNG if they support it
        for player in self.players:
            if isinstance(player, RNGMixin):
                new_seed = self.rng.randrange(sys.maxsize)
                player.reseed(new_seed)

    def start(self) -> None:
        """Start the game loop."""
        self.event_bus.publish(GameStartedEvent(players=self.players))

        for i in range(self.num_rounds):
            self.current_round_num = i + 1
            self.event_bus.publish(RoundStartEvent(round_num=self.current_round_num))
            round_seed = self.rng.randrange(sys.maxsize)

            player_names = [p.name for p in self.players]
            self.current_round = RoundFactory.create_standard_round(
                player_names=player_names,
                seed=round_seed,
            )

            # Syncing hands to players is no longer needed as they access it via
            # Observation
            self._run_round_loop()

            # Map round scores (by index) back to players
            round_scores_indices = self.current_round.get_scores()
            round_scores = {
                self.players[idx]: score for idx, score in round_scores_indices.items()
            }
            round_hands = {
                self.players[idx]: self.current_round.hands[idx]
                for idx in range(len(self.players))
            }

            for player, score in round_scores.items():
                self.scores[player] += score
                self.round_history[player].append(score)

            self.event_bus.publish(
                RoundEndEvent(
                    scores=round_scores.copy(),
                    hands=round_hands,
                    round_num=self.current_round_num,
                )
            )

            self.publish_scores()

        self.declare_winner()

    def _run_round_loop(self) -> None:
        """Execute the engine loop for the current round."""
        if self.current_round is None:
            return

        round_instance = self.current_round

        while round_instance.phase != RoundPhase.FINISHED:
            current_player_idx = round_instance.get_current_player_idx()
            current_player = self.players[current_player_idx]

            obs = ObservationBuilder.build(round_instance, current_player_idx)
            action = current_player.get_action(obs)
            events = round_instance.step(action)
            self.publish_events(events)

    def publish_events(self, events: list[GameEvent]) -> None:
        """Publish each game event to the event bus."""
        for event in events:
            self.event_bus.publish(event)

    def publish_scores(self) -> None:
        """Publish current scores for all players."""
        self.event_bus.publish(ScoreBoardEvent(scores=self.scores.copy()))

    def get_standings(self) -> list[tuple[BasePlayer, int]]:
        """Return (player, score) pairs sorted by score (ascending — lowest wins)."""
        pairs = [(p, self.scores[p]) for p in self.players]
        return sorted(pairs, key=lambda x: x[1])

    def get_winner(self) -> BasePlayer:
        """Return the player with the lowest score."""
        return self.get_standings()[0][0]

    def get_stats(self) -> dict[BasePlayer, PlayerStats]:
        """Calculate game statistics for each player."""
        return {
            player: PlayerStats(self.round_history[player]) for player in self.players
        }

    def declare_winner(self) -> None:
        """Publish the game winner and final standings."""
        standings = self.get_standings()
        stats = self.get_stats()

        self.event_bus.publish(GameStatsEvent(stats=stats))
        self.event_bus.publish(
            ScoreBoardEvent(scores=self.scores.copy(), standings=standings)
        )

        winner, score = standings[0]
        self.event_bus.publish(GameOverEvent(winner=winner, winning_score=score))

    def __repr__(self) -> str:
        return f"Game(players={self.players}, event_bus={self.event_bus})"
