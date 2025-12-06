"""Module containing the abstract Player class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pycardgolf.core.hand import Hand
from pycardgolf.exceptions import GameConfigError
from pycardgolf.interfaces.base import DrawSource, GameInterface

if TYPE_CHECKING:
    from pycardgolf.core.game import Game
    from pycardgolf.core.round import Round
    from pycardgolf.utils.card import Card


class Player(ABC):
    """Abstract base class for a game player."""

    def __init__(self, name: str, interface: GameInterface) -> None:
        """Initialize a player with a name."""
        self.name: str = name
        self.hand: Hand = Hand([])
        self.interface: GameInterface = interface

    def take_turn(self, game: Game) -> None:
        """Execute the player's turn using the template method pattern."""
        if game.current_round is None:
            msg = "Game round is None."
            raise GameConfigError(msg)
        game_round: Round = game.current_round

        # Optional display hook
        self.interface.display_turn_start(self)

        # 1. Decide where to draw from
        draw_source = self._choose_draw_source(game_round)

        if draw_source == DrawSource.DISCARD:
            self._handle_pile_draw(game_round)
        elif draw_source == DrawSource.DECK:
            self._handle_deck_draw(game_round)
        else:
            msg = f"Invalid draw source: {draw_source}"
            raise GameConfigError(msg)

    def _handle_pile_draw(self, game_round: Round) -> None:
        """Handle drawing from the discard pile."""
        drawn_card = game_round.discard_pile.draw()
        self.interface.display_discard_draw(self, drawn_card)

        # Must replace a card
        idx = self._choose_card_to_replace(drawn_card, game_round)
        self._replace_card(idx, drawn_card, game_round)

    def _handle_deck_draw(self, game_round: Round) -> None:
        """Handle drawing from the deck."""
        drawn_card = game_round.deck.draw()
        drawn_card.face_up = True
        self.interface.display_drawn_card(self, drawn_card)

        if self._should_keep_drawn_card(drawn_card, game_round):
            idx = self._choose_card_to_replace(drawn_card, game_round)
            self._replace_card(idx, drawn_card, game_round)
        else:
            # Discard the drawn card
            game_round.discard_pile.add_card(drawn_card)
            self.interface.display_discard_action(self, drawn_card)

            # Optionally flip a card
            flip_idx = self._choose_card_to_flip_after_discard(game_round)
            if flip_idx is not None:
                self.hand.flip_card(flip_idx)
                self.interface.display_flip_action(self, flip_idx, self.hand[flip_idx])

    def _replace_card(self, idx: int, new_card: Card, game_round: Round) -> None:
        """Replace a card in hand and handle display."""
        old_card = self.hand.replace(idx, new_card)
        old_card.face_up = True
        game_round.discard_pile.add_card(old_card)
        self.interface.display_replace_action(self, idx, new_card, old_card)

    def __repr__(self) -> str:
        return f"Player(name={self.name}, hand={self.hand})"

    # --- Abstract Decision Hooks ---

    @abstractmethod
    def _choose_draw_source(self, game_round: Round) -> DrawSource:
        """Decide whether to draw from deck or discard pile."""

    @abstractmethod
    def _should_keep_drawn_card(self, card: Card, game_round: Round) -> bool:
        """Decide whether to keep a card drawn from the deck."""

    @abstractmethod
    def _choose_card_to_replace(self, new_card: Card, game_round: Round) -> int:
        """Choose which card index (0-based) to replace with the new card."""

    @abstractmethod
    def _choose_card_to_flip_after_discard(self, game_round: Round) -> int | None:
        """Choose card index (0-based) to flip after discarding, or None."""

    @abstractmethod
    def choose_initial_card_to_flip(self, game_round: Round) -> int:
        """Select one card to flip at the start of the round."""
