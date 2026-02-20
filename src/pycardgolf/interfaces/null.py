"""Module containing the NullGameInterface class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pycardgolf.interfaces.base import (
    ActionChoice,
    DrawSource,
    FlipChoice,
    GameInterface,
)

if TYPE_CHECKING:
    from pycardgolf.core.game import Game
    from pycardgolf.core.hand import Hand
    from pycardgolf.core.stats import PlayerStats
    from pycardgolf.players import Player
    from pycardgolf.utils.card import Card


class NullGameInterface(GameInterface):
    """Null object implementation of GameInterface.

    This class provides no-op implementations for all methods, allowing it to be
    used as a default interface when no real interface is provided.
    """

    def display_state(self, game: Game) -> None:
        """Do nothing."""

    def display_round_end(self, game: Game) -> None:
        """Do nothing."""

    def get_input(self, prompt: str) -> str:
        """Raise NotImplementedError as null interface cannot provide input."""
        raise NotImplementedError

    def display_round_start(self, round_num: int) -> None:
        """Do nothing."""

    def display_scores(self, scores: dict[Player, int]) -> None:
        """Do nothing."""

    def display_game_over(self) -> None:
        """Do nothing."""

    def display_standings(self, standings: list[tuple[Player, int]]) -> None:
        """Do nothing."""

    def display_winner(self, winner: Player, score: int) -> None:
        """Do nothing."""

    def display_game_stats(self, stats: dict[Player, PlayerStats]) -> None:
        """Do nothing."""

    def display_error(self, message: str) -> None:
        """Do nothing."""

    def display_initial_flip_prompt(self, player: Player, num_to_flip: int) -> None:
        """Do nothing."""

    def display_initial_flip_selection_prompt(
        self, current_count: int, total_count: int
    ) -> None:
        """Do nothing."""

    def display_initial_flip_error_already_selected(self) -> None:
        """Do nothing."""

    def display_final_turn_notification(self, player: Player) -> None:
        """Do nothing."""

    def validate_color(self, color: str) -> None:
        """Do nothing."""

    def get_draw_choice(
        self, deck_card: Card | None, discard_card: Card | None
    ) -> DrawSource:
        """Raise NotImplementedError as null interface cannot provide input."""
        raise NotImplementedError

    def get_keep_or_discard_choice(self) -> ActionChoice:
        """Raise NotImplementedError as null interface cannot provide input."""
        raise NotImplementedError

    def get_flip_choice(self) -> FlipChoice:
        """Raise NotImplementedError as null interface cannot provide input."""
        raise NotImplementedError

    def get_index_to_replace(self) -> int:
        """Raise NotImplementedError as null interface cannot provide input."""
        raise NotImplementedError

    def get_index_to_flip(self) -> int:
        """Raise NotImplementedError as null interface cannot provide input."""
        raise NotImplementedError

    def display_drawn_card(self, player: Player, card: Card) -> None:
        """Do nothing."""

    def display_discard_draw(self, player: Player, card: Card) -> None:
        """Do nothing."""

    def display_replace_action(
        self, player: Player, index: int, new_card: Card, old_card: Card
    ) -> None:
        """Do nothing."""

    def display_flip_action(self, player: Player, index: int, card: Card) -> None:
        """Do nothing."""

    def display_turn_start(
        self, player: Player, next_player: Player | None = None
    ) -> None:
        """Do nothing."""

    def display_discard_action(self, player: Player, card: Card) -> None:
        """Do nothing."""

    def display_hand(self, player: Player, display_indices: bool = False) -> None:
        """Do nothing."""

    def get_initial_cards_to_flip(self, player: Player, num_to_flip: int) -> list[int]:
        """Raise NotImplementedError as null interface cannot provide input."""
        raise NotImplementedError

    def display_initial_flip_choices(self, player: Player, choices: list[int]) -> None:
        """Do nothing."""

    def get_valid_flip_index(self, hand: Hand) -> int:
        """Raise NotImplementedError as null interface cannot provide input."""
        raise NotImplementedError
