"""Module containing GameEvent definitions for the game engine."""

from dataclasses import dataclass
from typing import Literal

from pycardgolf.players.player import Player
from pycardgolf.utils.card import Card

EventType = Literal[
    "ROUND_START",
    "TURN_START",
    "CARD_DRAWN_DECK",
    "CARD_DRAWN_DISCARD",
    "CARD_DISCARDED",
    "CARD_SWAPPED",
    "CARD_FLIPPED",
    "ROUND_END",
    "MESSAGE",
]


@dataclass(frozen=True, kw_only=True)
class GameEvent:
    """Base class for all game events."""

    event_type: EventType


@dataclass(frozen=True, kw_only=True)
class RoundStartEvent(GameEvent):
    """Event triggered when a round starts."""

    round_num: int
    event_type: EventType = "ROUND_START"


@dataclass(frozen=True, kw_only=True)
class TurnStartEvent(GameEvent):
    """Event triggered when a player's turn starts."""

    player: Player
    event_type: EventType = "TURN_START"


@dataclass(frozen=True, kw_only=True)
class CardDrawnDeckEvent(GameEvent):
    """Event triggered when a card is drawn from the deck."""

    player: Player
    card: Card
    event_type: EventType = "CARD_DRAWN_DECK"


@dataclass(frozen=True, kw_only=True)
class CardDrawnDiscardEvent(GameEvent):
    """Event triggered when a card is drawn from the discard pile."""

    player: Player
    card: Card
    event_type: EventType = "CARD_DRAWN_DISCARD"


@dataclass(frozen=True, kw_only=True)
class CardDiscardedEvent(GameEvent):
    """Event triggered when a card is discarded."""

    player: Player
    card: Card
    event_type: EventType = "CARD_DISCARDED"


@dataclass(frozen=True, kw_only=True)
class CardSwappedEvent(GameEvent):
    """Event triggered when a card is swapped in hand."""

    player: Player
    hand_index: int
    new_card: Card
    old_card: Card
    event_type: EventType = "CARD_SWAPPED"


@dataclass(frozen=True, kw_only=True)
class CardFlippedEvent(GameEvent):
    """Event triggered when a card is flipped in hand."""

    player: Player
    hand_index: int
    card: Card
    event_type: EventType = "CARD_FLIPPED"


@dataclass(frozen=True, kw_only=True)
class RoundEndEvent(GameEvent):
    """Event triggered when a round ends."""

    scores: dict[Player, int]
    event_type: EventType = "ROUND_END"


@dataclass(frozen=True, kw_only=True)
class MessageEvent(GameEvent):
    """Event triggered to display a generic message."""

    message: str
    event_type: EventType = "MESSAGE"
