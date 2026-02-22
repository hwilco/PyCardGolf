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
    GameOverEvent,
    GameStartedEvent,
    GameStatsEvent,
    RoundEndEvent,
    RoundStartEvent,
    ScoreBoardEvent,
    TurnStartEvent,
)

if TYPE_CHECKING:
    from pycardgolf.core.event_bus import EventBus
    from pycardgolf.players.player import BasePlayer
    from pycardgolf.utils.card import Card
    from pycardgolf.utils.enums import DrawSourceChoice, KeepOrDiscardChoice


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
        self.event_bus.subscribe(RoundEndEvent, self.display_round_end)
        self.event_bus.subscribe(GameOverEvent, self.display_game_over)
        self.event_bus.subscribe(ScoreBoardEvent, self.display_scoreboard)
        self.event_bus.subscribe(GameStatsEvent, self.display_game_stats)

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
    def get_draw_choice(
        self, player: BasePlayer, deck_card: Card | None, discard_card: Card | None
    ) -> DrawSourceChoice:
        """Ask the player whether to draw from the deck or the discard pile.

        Returns:
            ``DrawSourceChoice.DECK`` or ``DrawSourceChoice.DISCARD_PILE``.

        """

    @abstractmethod
    def get_keep_or_discard_choice(self, player: BasePlayer) -> KeepOrDiscardChoice:
        """Ask the player whether to keep the drawn card or discard it.

        Returns:
            ``KeepOrDiscardChoice.KEEP`` or ``KeepOrDiscardChoice.DISCARD``.

        """

    @abstractmethod
    def get_flip_choice(self, player: BasePlayer) -> bool:
        """Ask the player whether they want to flip a card this turn.

        Returns:
            ``True`` if flipping a card, otherwise ``False``.

        """

    @abstractmethod
    def get_index_to_replace(self, player: BasePlayer) -> int:
        """Ask the player which card in their hand to replace.

        Returns:
            Zero-based index of the card to replace.

        """

    @abstractmethod
    def get_index_to_flip(self, player: BasePlayer) -> int:
        """Ask the player which card in their hand to flip.

        Returns:
            Zero-based index of the card to flip.

        """

    @abstractmethod
    def get_valid_flip_index(self, player: BasePlayer) -> int:
        """Ask the player to choose a face-down card in their hand to flip.

        Returns:
            Zero-based index of a face-down card.

        """
