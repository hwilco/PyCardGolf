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
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pycardgolf.core.hand import Hand
    from pycardgolf.core.stats import PlayerStats
    from pycardgolf.players.player import BasePlayer
    from pycardgolf.utils.card import Card


# ---------------------------------------------------------------------------
# Choice enums (shared by GameInput implementations and callers)
# ---------------------------------------------------------------------------


class DrawSource(Enum):
    """Source to draw a card from."""

    DECK = auto()
    DISCARD = auto()


class ActionChoice(Enum):
    """Choice to keep or discard a drawn card."""

    KEEP = auto()
    DISCARD = auto()


class FlipChoice(Enum):
    """Choice to flip a card or not."""

    YES = auto()
    NO = auto()


# ---------------------------------------------------------------------------
# GameRenderer — pure display / output
# ---------------------------------------------------------------------------


class GameRenderer(ABC):
    """Abstract base class for rendering game state to the user.

    All methods are output-only and return ``None``.  Implementations
    are free to render to a terminal, GUI, log file, or discard output
    entirely.
    """

    @abstractmethod
    def display_round_end(self, round_num: int, players: list[BasePlayer]) -> None:
        """Display the state of the game at the end of a round."""

    @abstractmethod
    def display_round_start(self, round_num: int) -> None:
        """Display a message indicating the start of a new round."""

    @abstractmethod
    def display_scores(self, scores: dict[BasePlayer, int]) -> None:
        """Display scores.  ``scores`` maps each player to their total score."""

    @abstractmethod
    def display_game_over(self) -> None:
        """Display a game-over message."""

    @abstractmethod
    def display_standings(self, standings: list[tuple[BasePlayer, int]]) -> None:
        """Display standings as a ``(player, score)`` list sorted by rank."""

    @abstractmethod
    def display_winner(self, winner: BasePlayer, score: int) -> None:
        """Display the winner of the game."""

    @abstractmethod
    def display_game_stats(self, stats: dict[BasePlayer, PlayerStats]) -> None:
        """Display per-player game statistics."""

    @abstractmethod
    def display_final_turn_notification(self, player: BasePlayer) -> None:
        """Notify that ``player`` triggered the final turn."""

    @abstractmethod
    def display_drawn_card(self, player: BasePlayer, card: Card) -> None:
        """Display the card ``player`` drew from the deck."""

    @abstractmethod
    def display_discard_draw(self, player: BasePlayer, card: Card) -> None:
        """Display the card ``player`` drew from the discard pile."""

    @abstractmethod
    def display_replace_action(
        self, player: BasePlayer, index: int, new_card: Card, old_card: Card
    ) -> None:
        """Display the action of replacing a card in hand."""

    @abstractmethod
    def display_flip_action(self, player: BasePlayer, index: int, card: Card) -> None:
        """Display the action of flipping a card face-up."""

    @abstractmethod
    def display_turn_start(
        self, player: BasePlayer, players: list[BasePlayer], current_idx: int
    ) -> None:
        """Display the start of ``player``'s turn."""

    @abstractmethod
    def display_discard_action(self, player: BasePlayer, card: Card) -> None:
        """Display the action of discarding a drawn card."""


# ---------------------------------------------------------------------------
# NullGameRenderer — no-op base for testing and stub implementations
# ---------------------------------------------------------------------------


class NullGameRenderer(GameRenderer):
    """GameRenderer that silently discards all output.

    Suitable as a base class for test doubles or partial implementations
    where only a subset of display methods needs to be overridden.
    """

    def display_round_end(
        self, round_num: int, players: list[BasePlayer]
    ) -> None:  # pragma: no cover
        """No-op."""

    def display_round_start(self, round_num: int) -> None:  # pragma: no cover
        """No-op."""

    def display_scores(self, scores: dict[BasePlayer, int]) -> None:  # pragma: no cover
        """No-op."""

    def display_game_over(self) -> None:  # pragma: no cover
        """No-op."""

    def display_standings(
        self, standings: list[tuple[BasePlayer, int]]
    ) -> None:  # pragma: no cover
        """No-op."""

    def display_winner(
        self, winner: BasePlayer, score: int
    ) -> None:  # pragma: no cover
        """No-op."""

    def display_game_stats(
        self, stats: dict[BasePlayer, PlayerStats]
    ) -> None:  # pragma: no cover
        """No-op."""

    def display_final_turn_notification(
        self, player: BasePlayer
    ) -> None:  # pragma: no cover
        """No-op."""

    def display_drawn_card(
        self, player: BasePlayer, card: Card
    ) -> None:  # pragma: no cover
        """No-op."""

    def display_discard_draw(
        self, player: BasePlayer, card: Card
    ) -> None:  # pragma: no cover
        """No-op."""

    def display_replace_action(
        self, player: BasePlayer, index: int, new_card: Card, old_card: Card
    ) -> None:  # pragma: no cover
        """No-op."""

    def display_flip_action(
        self, player: BasePlayer, index: int, card: Card
    ) -> None:  # pragma: no cover
        """No-op."""

    def display_turn_start(
        self, player: BasePlayer, players: list[BasePlayer], current_idx: int
    ) -> None:  # pragma: no cover
        """No-op."""

    def display_discard_action(
        self, player: BasePlayer, card: Card
    ) -> None:  # pragma: no cover
        """No-op."""


# ---------------------------------------------------------------------------
# GameInput — user input / player decisions
# ---------------------------------------------------------------------------


class GameInput(ABC):
    """Abstract base class for obtaining player decisions.

    All methods return a value representing the player's choice.
    Implementations may read from stdin, a GUI, an AI model, etc.

    Two display methods — ``display_hand`` and
    ``display_initial_flip_error_already_selected`` — are placed here rather
    than on ``GameRenderer`` because they are intrinsically part of the
    human-input decision loop; a player must see their hand before deciding
    which card to act on.
    """

    @abstractmethod
    def get_input(self, prompt: str) -> str:
        """Return a raw string response to an arbitrary prompt."""

    @abstractmethod
    def get_draw_choice(
        self, deck_card: Card | None, discard_card: Card | None
    ) -> DrawSource:
        """Ask the player whether to draw from the deck or the discard pile.

        Returns:
            ``DrawSource.DECK`` or ``DrawSource.DISCARD``.

        """

    @abstractmethod
    def get_keep_or_discard_choice(self) -> ActionChoice:
        """Ask the player whether to keep the drawn card or discard it.

        Returns:
            ``ActionChoice.KEEP`` or ``ActionChoice.DISCARD``.

        """

    @abstractmethod
    def get_flip_choice(self) -> FlipChoice:
        """Ask the player whether they want to flip a card this turn.

        Returns:
            ``FlipChoice.YES`` or ``FlipChoice.NO``.

        """

    @abstractmethod
    def get_index_to_replace(self) -> int:
        """Ask the player which card in their hand to replace.

        Returns:
            Zero-based index of the card to replace.

        """

    @abstractmethod
    def get_index_to_flip(self) -> int:
        """Ask the player which card in their hand to flip.

        Returns:
            Zero-based index of the card to flip.

        """

    @abstractmethod
    def get_initial_cards_to_flip(
        self, player: BasePlayer, num_to_flip: int
    ) -> list[int]:
        """Ask the player to select cards for the initial flip at round start.

        Args:
            player: The player who needs to flip cards.
            num_to_flip: How many cards they must flip.

        Returns:
            A list of zero-based indices of the chosen cards.

        """

    @abstractmethod
    def get_valid_flip_index(self, hand: Hand) -> int:
        """Ask the player to choose a face-down card in their hand to flip.

        Returns:
            Zero-based index of a face-down card.

        """

    @abstractmethod
    def display_hand(self, player: BasePlayer, display_indices: bool = False) -> None:
        """Display a player's hand as part of an interactive input decision.

        Placed on ``GameInput`` (rather than ``GameRenderer``) because
        human players must see their hand in order to decide which card to
        act on during interactive prompts.

        Args:
            player: The player whose hand to display.
            display_indices: Whether to show position indices alongside cards.

        """

    @abstractmethod
    def display_initial_flip_error_already_selected(self) -> None:
        """Notify the player that the card they selected is already face-up."""
