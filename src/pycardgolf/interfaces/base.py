"""Module containing the abstract GameInterface class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pycardgolf.core.game import Game
    from pycardgolf.utils.card import Card


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
    def notify(self, message: str) -> None:
        """Notify the user of an event."""

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
    def get_draw_choice(self, deck_card: Card, discard_card: Card) -> str:
        """Get the user's choice to draw from the deck or discard pile.

        Args:
            deck_card: The top card of the deck.
            discard_card: The top card of the discard pile.

        Returns:
            'd' for deck or 'p' for pile.

        """

    @abstractmethod
    def get_keep_or_discard_choice(self) -> str:
        """Get the user's choice to keep the drawn card or discard it.

        Returns:
            'k' to keep or 'd' to discard.

        """

    @abstractmethod
    def get_flip_choice(self) -> str:
        """Get the user's choice to flip a card.

        Returns:
            'y' to flip or 'n' to not flip.

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
    def display_drawn_card(self, player_name: str, card: Card) -> None:
        """Display the card drawn from the deck.

        Args:
            player_name: The name of the player who drew the card.
            card: The card that was drawn.

        """

    @abstractmethod
    def display_discard_draw(self, player_name: str, card: Card) -> None:
        """Display the card drawn from the discard pile.

        Args:
            player_name: The name of the player who drew the card.
            card: The card that was drawn.

        """

    @abstractmethod
    def display_replace_action(
        self, player_name: str, index: int, new_card: Card, old_card: Card
    ) -> None:
        """Display the action of replacing a card in hand.

        Args:
            player_name: The name of the player who replaced the card.
            index: The 0-based index of the card being replaced.
            new_card: The new card being placed in the hand.
            old_card: The old card being discarded.

        """

    @abstractmethod
    def display_flip_action(self, player_name: str, index: int, card: Card) -> None:
        """Display the action of flipping a card in hand.

        Args:
            player_name: The name of the player who flipped the card.
            index: The 0-based index of the card being flipped.
            card: The card that was flipped (now face up).

        """
