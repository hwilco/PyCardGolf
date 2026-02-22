"""Module containing the Hand class."""

from __future__ import annotations

from typing import TYPE_CHECKING, overload

if TYPE_CHECKING:
    from collections.abc import Iterator

    from pycardgolf.utils.card import Card


class Hand:
    """Class representing a player's hand in Golf."""

    def __init__(self, cards: list[Card]) -> None:
        """Initialize a hand with a list of cards."""
        self._cards: list[Card] = cards
        self.rows: int = 2
        self.cols: int = len(cards) // self.rows

    def get_column(self, col_index: int) -> tuple[Card, Card]:
        """Return the two cards in a specific column."""
        if not 0 <= col_index < self.cols:
            msg = f"Column index out of range: {col_index}"
            raise IndexError(msg)
        return self._cards[col_index], self._cards[col_index + self.cols]

    def all_face_up(self) -> bool:
        """Return True if all cards in the hand are face up."""
        return all(card.face_up for card in self._cards)

    def replace(self, index: int, new_card: Card) -> Card:
        """Replace card at index and return the old one."""
        if not 0 <= index < len(self._cards):
            msg = f"Card index out of range: {index}"
            raise IndexError(msg)
        old_card = self._cards[index]
        self._cards[index] = new_card
        return old_card

    def flip_card(self, index: int) -> None:
        """Flip the card at the specified index."""
        if not 0 <= index < len(self._cards):
            msg = f"Card index out of range: {index}"
            raise IndexError(msg)
        self._cards[index].flip()

    def reveal_all(self) -> None:
        """Reveal all cards in the hand (set face_up to True)."""
        for card in self._cards:
            card.face_up = True

    def clone(self) -> Hand:
        """Return a deep copy of the hand."""
        return Hand([c.clone() for c in self._cards])

    def __repr__(self) -> str:
        return f"Hand(cards={self._cards})"

    # --- Type Checker Signatures ---
    @overload
    def __getitem__(self, index: int) -> Card: ...  # pragma: no cover

    @overload
    def __getitem__(self, index: slice) -> list[Card]: ...  # pragma: no cover

    # --- Implementation ---
    def __getitem__(self, index: int | slice) -> Card | list[Card]:
        """Get card at index."""
        return self._cards[index]

    def __len__(self) -> int:
        """Return number of cards in hand."""
        return len(self._cards)

    def __iter__(self) -> Iterator[Card]:
        """Iterate over cards in hand."""
        return iter(self._cards)
