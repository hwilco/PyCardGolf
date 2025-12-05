"""Module containing the abstract BotPlayer class."""

from abc import ABC, abstractmethod

from pycardgolf.core.player import Player
from pycardgolf.core.round import Round
from pycardgolf.interfaces.base import GameInterface
from pycardgolf.utils.card import Card


class BotPlayer(Player, ABC):
    """Abstract base class for bot players."""

    def __init__(self, name: str, interface: GameInterface | None = None) -> None:
        """Initialize the bot with a name and optional interface."""
        super().__init__(name)
        self.interface: GameInterface | None = interface

    def _notify(self, message: str) -> None:
        if self.interface:
            self.interface.notify(message)

    def take_turn(self, game_round: Round) -> None:
        """Execute the bot's turn using the template method pattern."""
        self._notify(f"It's {self.name}'s turn.")

        # 1. Decide where to draw from
        draw_source = self.choose_draw_source(game_round)

        if draw_source == "p":
            self._handle_pile_draw(game_round)
        else:
            self._handle_deck_draw(game_round)

    def _handle_pile_draw(self, game_round: Round) -> None:
        """Handle drawing from the discard pile."""
        drawn_card = game_round.discard_pile.draw()
        if self.interface:
            self.interface.display_discard_draw(self.name, drawn_card)

        # Must replace a card
        idx = self.choose_card_to_replace(drawn_card, game_round)
        self._replace_card(idx, drawn_card, game_round)

    def _handle_deck_draw(self, game_round: Round) -> None:
        """Handle drawing from the deck."""
        drawn_card = game_round.deck.draw()
        drawn_card.face_up = True
        if self.interface:
            self.interface.display_drawn_card(self.name, drawn_card)

        if self.should_keep_drawn_card(drawn_card, game_round):
            idx = self.choose_card_to_replace(drawn_card, game_round)
            self._replace_card(idx, drawn_card, game_round)
        else:
            # Discard the drawn card
            game_round.discard_pile.add_card(drawn_card)
            self._notify(f"{self.name} discarded {drawn_card}.")

            # Optionally flip a card
            flip_idx = self.choose_card_to_flip(game_round)
            if flip_idx is not None:
                self.hand.flip_card(flip_idx)
                if self.interface:
                    self.interface.display_flip_action(
                        self.name, flip_idx, self.hand[flip_idx]
                    )

    def _replace_card(self, idx: int, new_card: Card, game_round: Round) -> None:
        """Replace a card in hand and handle display."""
        old_card = self.hand.replace(idx, new_card)
        old_card.face_up = True
        game_round.discard_pile.add_card(old_card)
        if self.interface:
            self.interface.display_replace_action(self.name, idx, new_card, old_card)

    @abstractmethod
    def choose_draw_source(self, game_round: Round) -> str:
        """Decide whether to draw from deck ('d') or discard pile ('p')."""

    @abstractmethod
    def should_keep_drawn_card(self, card: Card, game_round: Round) -> bool:
        """Decide whether to keep a card drawn from the deck."""

    @abstractmethod
    def choose_card_to_replace(self, new_card: Card, game_round: Round) -> int:
        """Choose which card index (0-based) to replace with the new card."""

    @abstractmethod
    def choose_card_to_flip(self, game_round: Round) -> int | None:
        """Choose which card index (0-based) to flip, or None to skip."""
