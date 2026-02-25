"""Module defining card-related constants and display functions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pycardgolf.utils.deck import (
    _RANK_ORDER,
    _SUIT_ORDER,
    CARDS_PER_DECK,
    CARDS_PER_SUIT,
    Rank,
    Suit,
)

if TYPE_CHECKING:
    from pycardgolf.utils.types import CardID

_CARD_NAMES: dict[int, str] = {}
for s_idx, suit in enumerate(_SUIT_ORDER):
    for r_idx, rank in enumerate(_RANK_ORDER):
        card_id = s_idx * CARDS_PER_SUIT + r_idx
        _CARD_NAMES[card_id] = f"{rank} of {suit.name.capitalize()}"

_DECK_COLORS: dict[int, str] = {
    0: "blue",
    1: "red",
    2: "green",
}

_SUIT_COLORS = {
    Suit.SPADES: "black",
    Suit.HEARTS: "red",
    Suit.DIAMONDS: "red",
    Suit.CLUBS: "black",
}


def is_face_up(card_id: CardID | None) -> bool:
    """Return True if the card is face up (ID >= 0)."""
    return card_id is not None and card_id >= 0


def is_face_down(card_id: CardID | None) -> bool:
    """Return True if the card is face down (ID < 0)."""
    return card_id is not None and card_id < 0


def get_masked_id(card_id: CardID) -> CardID:
    """Return the masked ID for a card (encoding only the deck index)."""
    return -(card_id // CARDS_PER_DECK + 1)


def card_to_string(card_id: CardID) -> str:
    """Return a short string representation (e.g., 'A\u2660')."""
    if card_id < 0:
        return "??"
    rank = get_rank(card_id)
    suit = get_suit(card_id)
    # Use short suit symbol
    suit_sym = {
        Suit.SPADES: "♠",
        Suit.HEARTS: "♥",
        Suit.DIAMONDS: "♦",
        Suit.CLUBS: "♣",
    }.get(suit, "?")
    return f"{rank}{suit_sym}"


def card_back_to_string(card_id: CardID) -> str:
    """Return a string for the back of the card."""
    deck_index = abs(card_id) - 1 if card_id < 0 else card_id // CARDS_PER_DECK
    color = _DECK_COLORS.get(deck_index, "Unknown")
    return f"[Hidden {color} Card]"


def get_card_colors(card_id: CardID) -> tuple[str, str]:
    """Return (foreground_color, background_color) for a card."""
    deck_index = abs(card_id) - 1 if card_id < 0 else card_id // CARDS_PER_DECK
    background = _DECK_COLORS.get(deck_index, "blue").lower()
    if card_id < 0:
        return ("black", background)

    suit = get_suit(card_id)
    foreground = _SUIT_COLORS.get(suit, "black")
    return (foreground, background)


def get_card_display(card_id: CardID) -> str:
    """Return a human-readable string for a card ID."""
    if card_id < 0:
        return card_back_to_string(card_id)

    deck_index = card_id // CARDS_PER_DECK
    value = card_id % CARDS_PER_DECK
    card_name = _CARD_NAMES.get(value, "Unknown Card")
    color = _DECK_COLORS.get(deck_index, "Unknown")
    return f"{card_name} ({color} back)"


def get_rank(card_id: CardID) -> Rank:
    """Return the Rank enum for a given card ID."""
    if card_id < 0:
        return Rank.HIDDEN
    value = card_id % CARDS_PER_DECK
    rank_idx = value % CARDS_PER_SUIT
    return _RANK_ORDER[rank_idx]


def get_suit(card_id: CardID) -> Suit:
    """Return the Suit enum for a given card ID."""
    if card_id < 0:
        return Suit.HIDDEN
    value = card_id % CARDS_PER_DECK
    suit_idx = value // CARDS_PER_SUIT
    return _SUIT_ORDER[suit_idx]
