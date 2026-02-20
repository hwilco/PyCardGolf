"""Module containing the abstract GameInterface class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pycardgolf.core.game import Game
    from pycardgolf.core.hand import Hand
    from pycardgolf.core.stats import PlayerStats
    from pycardgolf.players import Player
    from pycardgolf.utils.card import Card


class DrawSource(Enum):
    """Source to draw a card from."""

    DECK = auto()
    DISCARD = auto()


class ActionChoice(Enum):
    """Choice to keep or discard a card."""

    KEEP = auto()
    DISCARD = auto()


class FlipChoice(Enum):
    """Choice to flip a card or not."""

    YES = auto()
    NO = auto()


class GameInterface(ABC):
    """Abstract base class for game interfaces."""

    @abstractmethod
    def display_state(self, game: Game) -> None:
        """Display the current state of the game (cards, scores, etc.)."""

    @abstractmethod
    def display_round_end(self, game: Game) -> None:
        """Display the state of the game at the end of a round."""

    @abstractmethod
    def get_input(self, prompt: str) -> str:
        """Get input from the user."""

    @abstractmethod
    def display_round_start(self, round_num: int) -> None:
        """Display the start of a round."""

    @abstractmethod
    def display_scores(self, scores: dict[Player, int]) -> None:
        """Display scores. scores is a map of player -> score."""

    @abstractmethod
    def display_game_over(self) -> None:
        """Display game over message."""

    @abstractmethod
    def display_standings(self, standings: list[tuple[Player, int]]) -> None:
        """Display standings. List of (player, score) tuples, sorted by rank."""

    @abstractmethod
    def display_winner(self, winner: Player, score: int) -> None:
        """Display the winner."""

    @abstractmethod
    def display_game_stats(self, stats: dict[Player, PlayerStats]) -> None:
        """Display game statistics.

        Args:
            stats: A dictionary mapping players to their statistics.

        """

    @abstractmethod
    def display_error(self, message: str) -> None:
        """Display an error message.

        Args:
            message: The error message to display.

        """

    @abstractmethod
    def display_initial_flip_prompt(self, player: Player, num_to_flip: int) -> None:
        """Prompt player to select initial cards to flip."""

    @abstractmethod
    def display_initial_flip_selection_prompt(
        self, current_count: int, total_count: int
    ) -> None:
        """Prompt to select a specific card during initial flip."""

    @abstractmethod
    def display_initial_flip_error_already_selected(self) -> None:
        """Error when selecting an already selected card during initial flip."""

    @abstractmethod
    def display_final_turn_notification(self, player: Player) -> None:
        """Notify that a player triggered the final turn."""

    @abstractmethod
    def validate_color(self, color: str) -> None:
        """Validate that a color string is supported by the interface.

        Args:
            color: The color string to validate. Either a name or a hex code starting
            with #.

        Raises:
            GameConfigError: If the color is invalid.

        """

    @abstractmethod
    def get_draw_choice(
        self, deck_card: Card | None, discard_card: Card | None
    ) -> DrawSource:
        """Get the user's choice to draw from the deck or discard pile.

        Args:
            deck_card: The top card of the deck.
            discard_card: The top card of the discard pile.

        Returns:
            The chosen source to draw from (DECK or DISCARD).

        """

    @abstractmethod
    def get_keep_or_discard_choice(self) -> ActionChoice:
        """Get the user's choice to keep the drawn card or discard it.

        Returns:
            The choice to KEEP or DISCARD.

        """

    @abstractmethod
    def get_flip_choice(self) -> FlipChoice:
        """Get the user's choice to flip a card.

        Returns:
            The choice to YES (flip) or NO (don't flip).

        """

    @abstractmethod
    def get_index_to_replace(self) -> int:
        """Get the index of the card to replace in the hand.

        Returns:
            The 0-based index of the card to replace.

        """

    @abstractmethod
    def get_index_to_flip(self) -> int:
        """Get the index of the card to flip in the hand.

        Returns:
            The 0-based index of the card to flip.

        """

    @abstractmethod
    def display_drawn_card(self, player: Player, card: Card) -> None:
        """Display the card drawn from the deck.

        Args:
            player: The player who drew the card.
            card: The card that was drawn.

        """

    @abstractmethod
    def display_discard_draw(self, player: Player, card: Card) -> None:
        """Display the card drawn from the discard pile.

        Args:
            player: The player who drew the card.
            card: The card that was drawn.

        """

    @abstractmethod
    def display_replace_action(
        self, player: Player, index: int, new_card: Card, old_card: Card
    ) -> None:
        """Display the action of replacing a card in hand.

        Args:
            player: The player who replaced the card.
            index: The 0-based index of the card being replaced.
            new_card: The new card being placed in the hand.
            old_card: The old card being discarded.

        """

    @abstractmethod
    def display_flip_action(self, player: Player, index: int, card: Card) -> None:
        """Display the action of flipping a card in hand.

        Args:
            player: The player who flipped the card.
            index: The 0-based index of the card being flipped.
            card: The card that was flipped (now face up).

        """

    @abstractmethod
    def display_turn_start(
        self, player: Player, next_player: Player | None = None
    ) -> None:
        """Display the start of a player's turn.

        Args:
            player: The player whose turn it is.
            next_player: The next player in the turn order (optional).

        """

    @abstractmethod
    def display_discard_action(self, player: Player, card: Card) -> None:
        """Display the action of discarding a card.

        Args:
            player: The player who discarded.
            card: The card that was discarded.

        """

    @abstractmethod
    def display_hand(self, player: Player, display_indices: bool = False) -> None:
        """Display a player's hand.

        Args:
            player: The player whose hand to display.
            display_indices: Whether to display the position indices of the cards.

        """

    @abstractmethod
    def get_initial_cards_to_flip(self, player: Player, num_to_flip: int) -> list[int]:
        """Get the indices of cards to flip at the start of the round.

        Args:
            player: The player who needs to flip cards.
            num_to_flip: The number of cards to flip.

        Returns:
            A list of 0-based indices of cards to flip.

        """

    @abstractmethod
    def display_initial_flip_choices(self, player: Player, choices: list[int]) -> None:
        """Display the choices made for initial cards to flip.

        Args:
            player: The player who made the choices.
            choices: The indices of the cards flipped.

        """

    @abstractmethod
    def get_valid_flip_index(self, hand: Hand) -> int:
        """Get a valid index of a face-down card to flip.

        Args:
            hand: The hand containing the cards.

        Returns:
            The 0-based index of the card to flip.

        """
