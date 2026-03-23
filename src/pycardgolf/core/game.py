"""Module containing the Game class."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from pycardgolf.core.events import (
    GameEvent,
    GameOverEvent,
    GameStartedEvent,
    GameStatsEvent,
    IllegalActionEvent,
    RoundEndEvent,
    RoundStartEvent,
    ScoreBoardEvent,
    TurnStartEvent,
)
from pycardgolf.core.observation import ObservationBuilder
from pycardgolf.core.phases import RoundPhase
from pycardgolf.core.round import Round, RoundFactory
from pycardgolf.core.stats import PlayerStats
from pycardgolf.exceptions import IllegalActionError
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
        self.is_game_over: bool = False
        super().__init__(seed=seed)

        # Re-initialize player RNG if they support it
        for player in self.players:
            if isinstance(player, RNGMixin):
                new_seed = self.rng.randrange(sys.maxsize)
                player.reseed(new_seed)

    def start(self) -> None:
        """Initialize the game state and start the first round."""
        self.event_bus.publish(GameStartedEvent(players=self.players))
        self._start_next_round()

    def _start_next_round(self) -> None:
        """Prepare and start the next round."""
        self.current_round_num += 1
        self.event_bus.publish(RoundStartEvent(round_num=self.current_round_num))
        round_seed = self.rng.randrange(sys.maxsize)

        player_names = [p.name for p in self.players]
        self.current_round = RoundFactory.create_standard_round(
            player_names=player_names,
            seed=round_seed,
        )

        # Publish initial turn start event for UI to refresh hands
        self.event_bus.publish(
            TurnStartEvent(
                player_idx=self.current_round.current_player_idx,
                hands=dict(enumerate(self.current_round.hands)),
            )
        )

    def _handle_round_end(self) -> None:
        """Process scoring and events at the end of a round."""
        if self.current_round is None:
            return

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

    def tick(self) -> bool:
        """Advance the game by a single player action or state transition.

        Returns:
            bool: True if the game is still active, False if the game is over.

        """
        if self.is_game_over:
            return False

        if self.current_round is None:
            # Game hasn't been started properly; start it now
            self.start()
            return True

        if self.current_round.phase == RoundPhase.FINISHED:
            self._handle_round_end()

            if self.current_round_num >= self.num_rounds:
                self.declare_winner()
                self.is_game_over = True
                return False

            self._start_next_round()
            return True

        # Process exactly ONE player's turn
        current_player_idx = self.current_round.get_current_player_idx()
        current_player = self.players[current_player_idx]

        obs = ObservationBuilder.build(self.current_round, current_player_idx)
        action = current_player.get_action(obs)

        try:
            events = self.current_round.step(action)
            self.publish_events(events)
        except IllegalActionError as exc:
            # Publish illegal action event but return True to keep game loop running
            # and allow the same player to try a different move.
            self.event_bus.publish(
                IllegalActionEvent(
                    player_idx=current_player_idx,
                    message=str(exc),
                )
            )

        return True

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
