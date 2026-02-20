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
from pycardgolf.core.observation import ObservationBuilder
from pycardgolf.core.phases import RoundPhase
from pycardgolf.core.round import Round
from pycardgolf.core.stats import PlayerStats

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

    from pycardgolf.interfaces.base import GameRenderer
    from pycardgolf.players import Player


class Game:
    """Class representing the card game."""

    def __init__(
        self,
        players: list[Player],
        renderer: GameRenderer,
        num_rounds: int = 9,
        seed: int = random.randrange(sys.maxsize),
    ) -> None:
        self.players: list[Player] = players
        self.scores: dict[Player, int] = dict.fromkeys(players, 0)
        self.round_history: dict[Player, list[int]] = {p: [] for p in players}
        self.renderer: GameRenderer = renderer
        self.num_rounds: int = num_rounds
        self.current_round_num: int = 0
        self.current_round: Round | None = None
        self.seed: int = seed
        self._rng: random.Random = random.Random(self.seed)

        self._event_handlers: dict[type[GameEvent], Callable[[Any], None]] = {
            TurnStartEvent: self._on_turn_start,
            CardDrawnDeckEvent: self._on_card_drawn_deck,
            CardDrawnDiscardEvent: self._on_card_drawn_discard,
            CardDiscardedEvent: self._on_card_discarded,
            CardSwappedEvent: self._on_card_swapped,
            CardFlippedEvent: self._on_card_flipped,
            RoundEndEvent: self._on_round_end,
        }

    def start(self) -> None:
        """Start the game loop."""
        for i in range(self.num_rounds):
            self.current_round_num = i + 1
            self.renderer.display_round_start(self.current_round_num)
            round_seed = self._rng.randrange(sys.maxsize)

            player_names = [p.name for p in self.players]
            self.current_round = Round(
                player_names=player_names,
                seed=round_seed,
            )

            # Sync hands to players so they have the correct state
            for idx, player in enumerate(self.players):
                player.hand = self.current_round.hands[idx]

            self._run_round_loop()

            # Map round scores (by index) back to players
            round_scores_indices = self.current_round.get_scores()
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

        while (
            not round_instance.round_over
            and round_instance.phase != RoundPhase.FINISHED
        ):
            current_player_idx = round_instance.get_current_player_idx()
            current_player = self.players[current_player_idx]

            obs = ObservationBuilder.build(round_instance, current_player_idx)
            action = current_player.get_action(obs)
            events = round_instance.step(action)
            self.display_events(events)

    def display_events(self, events: list[GameEvent]) -> None:
        """Dispatch each game event to the appropriate renderer method."""
        for event in events:
            handler = self._event_handlers.get(type(event))
            if handler is None:
                msg = f"No handler registered for {type(event).__name__}"
                raise TypeError(msg)
            handler(event)

    def _on_turn_start(self, event: TurnStartEvent) -> None:
        self.renderer.display_turn_start(
            self.players[event.player_idx], self.players, event.player_idx
        )

    def _on_card_drawn_deck(self, event: CardDrawnDeckEvent) -> None:
        self.renderer.display_drawn_card(self.players[event.player_idx], event.card)

    def _on_card_drawn_discard(self, event: CardDrawnDiscardEvent) -> None:
        self.renderer.display_discard_draw(self.players[event.player_idx], event.card)

    def _on_card_discarded(self, event: CardDiscardedEvent) -> None:
        self.renderer.display_discard_action(self.players[event.player_idx], event.card)

    def _on_card_swapped(self, event: CardSwappedEvent) -> None:
        self.renderer.display_replace_action(
            self.players[event.player_idx],
            event.hand_index,
            event.new_card,
            event.old_card,
        )

    def _on_card_flipped(self, event: CardFlippedEvent) -> None:
        self.renderer.display_flip_action(
            self.players[event.player_idx], event.hand_index, event.card
        )

    def _on_round_end(self, _event: RoundEndEvent) -> None:
        self.renderer.display_round_end(self)

    def display_scores(self) -> None:
        """Display current scores for all players."""
        self.renderer.display_scores(self.scores)

    def get_standings(self) -> list[Player]:
        """Return players sorted by score (ascending — lowest score wins)."""
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
        """Notify the renderer of the game winner and final standings."""
        self.renderer.display_game_over()

        standings = self.get_standings()
        standings_tuples = [(p, self.scores[p]) for p in standings]

        self.renderer.display_game_stats(self.get_stats())
        self.renderer.display_standings(standings_tuples)

        winner = standings[0]
        self.renderer.display_winner(winner, self.scores[winner])

    def __repr__(self) -> str:
        return f"Game(players={self.players}, renderer={self.renderer})"
