"""Module containing the Hand class."""

from __future__ import annotations

from typing import TYPE_CHECKING, overload

if TYPE_CHECKING:
    from collections.abc import Iterator

    from pycardgolf.utils.types import CardID, FaceUpMask


class Hand:
    """Class representing a player's hand in Golf using primitive types."""

    __slots__ = ("card_ids", "cols", "face_up_mask", "rows")
    __hash__ = None  # type: ignore[assignment]

    def __init__(self, card_ids: list[CardID], face_up_mask: FaceUpMask = 0) -> None:
        """Initialize a hand with a list of cards and visibility mask."""
        self.card_ids: list[CardID] = card_ids
        self.face_up_mask: FaceUpMask = face_up_mask
        self.rows: int = 2
        self.cols: int = len(card_ids) // self.rows

    def get_column(self, col_index: int) -> tuple[CardID, ...]:
        """Return the cards in a specific column."""
        if not 0 <= col_index < self.cols:
            msg = f"Column index out of range: {col_index}"
            raise IndexError(msg)
        return tuple(self.card_ids[col_index :: self.cols])

    def get_row(self, row_index: int) -> tuple[CardID, ...]:
        """Return the cards in a specific row."""
        if not 0 <= row_index < self.rows:
            msg = f"Row index out of range: {row_index}"
            raise IndexError(msg)
        start_index = row_index * self.cols
        end_index = start_index + self.cols
        return tuple(self.card_ids[start_index:end_index])

    def is_face_up(self, index: int) -> bool:
        """Return True if the card at the given index is face up."""
        return (self.face_up_mask & (1 << index)) != 0

    def all_face_up(self) -> bool:
        """Return True if all cards in the hand are face up."""
        return self.face_up_mask == (1 << len(self.card_ids)) - 1

    def replace(self, index: int, new_card_id: CardID) -> CardID:
        """Replace card at index and return the old one."""
        if not 0 <= index < len(self.card_ids):
            msg = f"Card index out of range: {index}"
            raise IndexError(msg)
        old_card_id = self.card_ids[index]
        self.card_ids[index] = new_card_id
        # When a card is replaced, it becomes face up
        self.face_up_mask |= 1 << index
        return old_card_id

    def flip_card(self, index: int) -> None:
        """Flip the card at the specified index face up."""
        if not 0 <= index < len(self.card_ids):
            msg = f"Card index out of range: {index}"
            raise IndexError(msg)
        self.face_up_mask |= 1 << index

    def reveal_all(self) -> None:
        """Reveal all cards in the hand."""
        self.face_up_mask = (1 << len(self.card_ids)) - 1

    def clone(self) -> Hand:
        """Return a copy of the hand."""
        return Hand(list(self.card_ids), self.face_up_mask)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Hand):
            return NotImplemented
        return (
            self.card_ids == other.card_ids and self.face_up_mask == other.face_up_mask
        )

    def __repr__(self) -> str:
        return f"Hand(card_ids={self.card_ids}, face_up_mask={self.face_up_mask})"

    # --- Type Checker Signatures ---
    @overload
    def __getitem__(self, index: int) -> CardID: ...  # pragma: no cover

    @overload
    def __getitem__(self, index: slice) -> list[CardID]: ...  # pragma: no cover

    # --- Implementation ---
    def __getitem__(self, index: int | slice) -> CardID | list[CardID]:
        """Get card ID at index."""
        return self.card_ids[index]

    def __len__(self) -> int:
        """Return number of cards in hand."""
        return len(self.card_ids)

    def __iter__(self) -> Iterator[CardID]:
        """Iterate over cards in hand."""
        return iter(self.card_ids)
