"""Module containing abstract interface classes for the game.

Defines two focused ABCs following the Interface Segregation Principle:

- ``GameRenderer`` — all display/output methods (no user interaction).
- ``GameInput``    — all input/decision methods (returns player choices).

``CLIRenderer`` implements the former, and ``CLIInputHandler`` implements
the latter.  ``HumanPlayer`` accepts a ``GameInput``; ``Game`` accepts a
``GameRenderer``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pycardgolf.core.events import (
    CardDiscardedEvent,
    CardDrawnDeckEvent,
    CardDrawnDiscardEvent,
    CardFlippedEvent,
    CardSwappedEvent,
    DeckReshuffledEvent,
    GameOverEvent,
    GameStartedEvent,
    GameStatsEvent,
    IllegalActionEvent,
    RoundEndEvent,
    RoundStartEvent,
    ScoreBoardEvent,
    TurnStartEvent,
)

if TYPE_CHECKING:
    from pycardgolf.core.actions import Action
    from pycardgolf.core.event_bus import EventBus
    from pycardgolf.core.hand import Hand
    from pycardgolf.core.observation import Observation
    from pycardgolf.players.player import BasePlayer


# ---------------------------------------------------------------------------
# GameRenderer — pure display / output
# ---------------------------------------------------------------------------


class GameRenderer(ABC):
    """Abstract base class for rendering game state to the user.

    All methods are output-only and return ``None``.  Implementations
    are free to render to a terminal, GUI, log file, or discard output
    entirely.
    """

    def __init__(self, event_bus: EventBus) -> None:
        """Initialize the renderer and subscribe to game events."""
        self.event_bus = event_bus
        self.players: list[BasePlayer] = []
        self._subscribe_to_events()

    def handle_game_started(self, event: GameStartedEvent) -> None:
        """Store the list of players for use in rendering names and hands."""
        self.players = event.players

    def _subscribe_to_events(self) -> None:
        """Register renderer methods to the event bus."""
        self.event_bus.subscribe(GameStartedEvent, self.handle_game_started)
        self.event_bus.subscribe(RoundStartEvent, self.display_round_start)
        self.event_bus.subscribe(TurnStartEvent, self.display_turn_start)
        self.event_bus.subscribe(CardDrawnDeckEvent, self.display_drawn_card)
        self.event_bus.subscribe(CardDrawnDiscardEvent, self.display_discard_draw)
        self.event_bus.subscribe(CardDiscardedEvent, self.display_discard_action)
        self.event_bus.subscribe(CardSwappedEvent, self.display_replace_action)
        self.event_bus.subscribe(CardFlippedEvent, self.display_flip_action)
        self.event_bus.subscribe(DeckReshuffledEvent, self.display_deck_reshuffled)
        self.event_bus.subscribe(RoundEndEvent, self.display_round_end)
        self.event_bus.subscribe(GameOverEvent, self.display_game_over)
        self.event_bus.subscribe(ScoreBoardEvent, self.display_scoreboard)
        self.event_bus.subscribe(GameStatsEvent, self.display_game_stats)
        self.event_bus.subscribe(IllegalActionEvent, self.display_illegal_action)

    @abstractmethod
    def display_round_end(self, event: RoundEndEvent) -> None:
        """Display the state of the game at the end of a round."""

    @abstractmethod
    def display_round_start(self, event: RoundStartEvent) -> None:
        """Display a message indicating the start of a new round."""

    @abstractmethod
    def display_scoreboard(self, event: ScoreBoardEvent) -> None:
        """Display scores and optional standings."""

    @abstractmethod
    def display_game_over(self, event: GameOverEvent) -> None:
        """Display a game-over message and the winner."""

    @abstractmethod
    def display_game_stats(self, event: GameStatsEvent) -> None:
        """Display per-player game statistics."""

    @abstractmethod
    def display_drawn_card(self, event: CardDrawnDeckEvent) -> None:
        """Display the card drawn from the deck."""

    @abstractmethod
    def display_discard_draw(self, event: CardDrawnDiscardEvent) -> None:
        """Display the card drawn from the discard pile."""

    @abstractmethod
    def display_replace_action(self, event: CardSwappedEvent) -> None:
        """Display the action of replacing a card in hand."""

    @abstractmethod
    def display_flip_action(self, event: CardFlippedEvent) -> None:
        """Display the action of flipping a card face-up."""

    @abstractmethod
    def display_turn_start(self, event: TurnStartEvent) -> None:
        """Display the start of a turn."""

    @abstractmethod
    def display_discard_action(self, event: CardDiscardedEvent) -> None:
        """Display the action of discarding a drawn card."""

    @abstractmethod
    def display_hand(self, hand: Hand, display_indices: bool = False) -> None:
        """Display a hand."""

    @abstractmethod
    def display_deck_reshuffled(self, event: DeckReshuffledEvent) -> None:
        """Display a notification that the draw pile was replenished from discard."""

    @abstractmethod
    def display_illegal_action(self, event: IllegalActionEvent) -> None:
        """Display an error message for an illegal action."""


# ---------------------------------------------------------------------------
# NullGameRenderer — no-op base for testing and stub implementations
# ---------------------------------------------------------------------------


class NullGameRenderer(GameRenderer):
    """GameRenderer that silently discards all output.

    Suitable as a base class for test doubles or partial implementations
    where only a subset of display methods needs to be overridden.
    """

    def display_round_end(self, event: RoundEndEvent) -> None:  # pragma: no cover
        """No-op."""

    def display_round_start(self, event: RoundStartEvent) -> None:  # pragma: no cover
        """No-op."""

    def display_scoreboard(self, event: ScoreBoardEvent) -> None:  # pragma: no cover
        """No-op."""

    def display_game_over(self, event: GameOverEvent) -> None:  # pragma: no cover
        """No-op."""

    def display_game_stats(self, event: GameStatsEvent) -> None:  # pragma: no cover
        """No-op."""

    def display_drawn_card(self, event: CardDrawnDeckEvent) -> None:  # pragma: no cover
        """No-op."""

    def display_discard_draw(
        self, event: CardDrawnDiscardEvent
    ) -> None:  # pragma: no cover
        """No-op."""

    def display_replace_action(
        self, event: CardSwappedEvent
    ) -> None:  # pragma: no cover
        """No-op."""

    def display_flip_action(self, event: CardFlippedEvent) -> None:  # pragma: no cover
        """No-op."""

    def display_turn_start(self, event: TurnStartEvent) -> None:  # pragma: no cover
        """No-op."""

    def display_discard_action(
        self, event: CardDiscardedEvent
    ) -> None:  # pragma: no cover
        """No-op."""

    def display_hand(
        self, hand: Hand, display_indices: bool = False
    ) -> None:  # pragma: no cover
        """No-op."""

    def display_deck_reshuffled(
        self, event: DeckReshuffledEvent
    ) -> None:  # pragma: no cover
        """No-op."""

    def display_illegal_action(
        self, event: IllegalActionEvent
    ) -> None:  # pragma: no cover
        """No-op."""


# ---------------------------------------------------------------------------
# GameInput — user input / player decisions
# ---------------------------------------------------------------------------


class GameInput(ABC):
    """Abstract base class for obtaining player decisions.

    All methods return a value representing the player's choice.
    Implementations may read from stdin, a GUI, an AI model, etc.

    Implementations are responsible for displaying any necessary context
    (e.g., showing the player's hand) before or during these prompts.
    """

    @abstractmethod
    def get_input(self, prompt: str) -> str:
        """Return a raw string response to an arbitrary prompt."""

    @abstractmethod
    def get_action(self, player: BasePlayer, observation: Observation) -> Action:
        """Ask the player to choose an action based on the current observation.

        Args:
            player: The player making the move.
            observation: The current view of the game state.

        Returns:
            The selected Action.

        """
