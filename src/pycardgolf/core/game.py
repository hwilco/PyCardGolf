"""Module containing the Game class."""

from __future__ import annotations

import random
import sys
from functools import singledispatchmethod
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
    from pycardgolf.interfaces.base import GameRenderer
    from pycardgolf.players import BasePlayer


class Game:
    """Class representing the card game."""

    def __init__(
        self,
        players: list[BasePlayer],
        renderer: GameRenderer,
        num_rounds: int = 9,
        seed: int | None = None,
    ) -> None:
        self.players: list[BasePlayer] = players
        self.scores: dict[BasePlayer, int] = dict.fromkeys(players, 0)
        self.round_history: dict[BasePlayer, list[int]] = {p: [] for p in players}
        self.renderer: GameRenderer = renderer
        self.num_rounds: int = num_rounds
        self.current_round_num: int = 0
        self.current_round: Round | None = None
        self.seed: int = seed if seed is not None else random.randrange(sys.maxsize)
        self._rng: random.Random = random.Random(self.seed)

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

        while round_instance.phase != RoundPhase.FINISHED:
            current_player_idx = round_instance.get_current_player_idx()
            current_player = self.players[current_player_idx]

            obs = ObservationBuilder.build(round_instance, current_player_idx)
            action = current_player.get_action(obs)
            events = round_instance.step(action)
            self.display_events(events)

    def display_events(self, events: list[GameEvent]) -> None:
        """Dispatch each game event to the appropriate renderer method."""
        for event in events:
            self._handle_event(event)

    @singledispatchmethod
    def _handle_event(self, event: GameEvent) -> None:
        """Fallback handler if an unknown event is passed."""
        msg = f"No handler registered for {type(event).__name__}"
        raise TypeError(msg)

    @_handle_event.register
    def _on_turn_start(self, event: TurnStartEvent) -> None:
        """Handle start of turn."""
        self.renderer.display_turn_start(
            self.players[event.player_idx], self.players, event.player_idx
        )

    @_handle_event.register
    def _on_card_drawn_deck(self, event: CardDrawnDeckEvent) -> None:
        """Handle card drawn from deck."""
        self.renderer.display_drawn_card(self.players[event.player_idx], event.card)

    @_handle_event.register
    def _on_card_drawn_discard(self, event: CardDrawnDiscardEvent) -> None:
        """Handle card drawn from discard pile."""
        self.renderer.display_discard_draw(self.players[event.player_idx], event.card)

    @_handle_event.register
    def _on_card_discarded(self, event: CardDiscardedEvent) -> None:
        """Handle card discarded."""
        self.renderer.display_discard_action(self.players[event.player_idx], event.card)

    @_handle_event.register
    def _on_card_swapped(self, event: CardSwappedEvent) -> None:
        """Handle card swapped in hand."""
        self.renderer.display_replace_action(
            self.players[event.player_idx],
            event.hand_index,
            event.new_card,
            event.old_card,
        )

    @_handle_event.register
    def _on_card_flipped(self, event: CardFlippedEvent) -> None:
        """Handle card flipped in hand."""
        self.renderer.display_flip_action(
            self.players[event.player_idx], event.hand_index, event.card
        )

    @_handle_event.register
    def _on_round_end(self, _event: RoundEndEvent) -> None:
        """Handle end of round."""
        self.renderer.display_round_end(self.current_round_num, self.players)

    def display_scores(self) -> None:
        """Display current scores for all players."""
        self.renderer.display_scores(self.scores)

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
        """Notify the renderer of the game winner and final standings."""
        self.renderer.display_game_over()

        standings = self.get_standings()

        self.renderer.display_game_stats(self.get_stats())
        self.renderer.display_standings(standings)

        winner, score = standings[0]
        self.renderer.display_winner(winner, score)

    def __repr__(self) -> str:
        return f"Game(players={self.players}, renderer={self.renderer})"
