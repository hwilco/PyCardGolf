"""Module containing GameEvent definitions for the game engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from pycardgolf.core.hand import Hand
    from pycardgolf.core.stats import PlayerStats
    from pycardgolf.players.player import BasePlayer
    from pycardgolf.utils.types import CardID

EventType = Literal[
    "ROUND_START",
    "TURN_START",
    "CARD_DRAWN_DECK",
    "CARD_DRAWN_DISCARD",
    "CARD_DISCARDED",
    "CARD_SWAPPED",
    "CARD_FLIPPED",
    "ROUND_END",
    "GAME_OVER",
    "SCORE_BOARD",
    "GAME_STATS",
    "GAME_STARTED",
    "DECK_RESHUFFLED",
    "ILLEGAL_ACTION",
]


@dataclass(frozen=True, kw_only=True)
class GameEvent:
    """Base class for all game events."""

    event_type: EventType


@dataclass(frozen=True, kw_only=True)
class GameStartedEvent(GameEvent):
    """Event triggered when the game starts."""

    players: list[BasePlayer]
    event_type: EventType = "GAME_STARTED"


@dataclass(frozen=True, kw_only=True)
class RoundStartEvent(GameEvent):
    """Event triggered when a round starts."""

    round_num: int
    event_type: EventType = "ROUND_START"


@dataclass(frozen=True, kw_only=True)
class TurnStartEvent(GameEvent):
    """Event triggered when a player's turn starts."""

    player_idx: int
    hands: dict[int, Hand]
    event_type: EventType = "TURN_START"


@dataclass(frozen=True, kw_only=True)
class CardDrawnDeckEvent(GameEvent):
    """Event triggered when a card is drawn from the deck."""

    player_idx: int
    card_id: CardID
    event_type: EventType = "CARD_DRAWN_DECK"


@dataclass(frozen=True, kw_only=True)
class CardDrawnDiscardEvent(GameEvent):
    """Event triggered when a card is drawn from the discard pile."""

    player_idx: int
    card_id: CardID
    event_type: EventType = "CARD_DRAWN_DISCARD"


@dataclass(frozen=True, kw_only=True)
class CardDiscardedEvent(GameEvent):
    """Event triggered when a card is discarded."""

    player_idx: int
    card_id: CardID
    event_type: EventType = "CARD_DISCARDED"


@dataclass(frozen=True, kw_only=True)
class CardSwappedEvent(GameEvent):
    """Event triggered when a card is swapped in hand."""

    player_idx: int
    hand_index: int
    new_card_id: CardID
    old_card_id: CardID
    event_type: EventType = "CARD_SWAPPED"


@dataclass(frozen=True, kw_only=True)
class CardFlippedEvent(GameEvent):
    """Event triggered when a card is flipped in hand."""

    player_idx: int
    hand_index: int
    card_id: CardID
    event_type: EventType = "CARD_FLIPPED"


@dataclass(frozen=True, kw_only=True)
class RoundEndEvent(GameEvent):
    """Event triggered when a round ends."""

    round_num: int
    scores: dict[BasePlayer, int]
    hands: dict[BasePlayer, Hand]
    event_type: EventType = "ROUND_END"


@dataclass(frozen=True, kw_only=True)
class GameOverEvent(GameEvent):
    """Event triggered when the entire game ends."""

    winner: BasePlayer
    winning_score: int
    event_type: EventType = "GAME_OVER"


@dataclass(frozen=True, kw_only=True)
class ScoreBoardEvent(GameEvent):
    """Event triggered to display the current scores or standings."""

    scores: dict[BasePlayer, int]
    standings: list[tuple[BasePlayer, int]] | None = None
    event_type: EventType = "SCORE_BOARD"


@dataclass(frozen=True, kw_only=True)
class GameStatsEvent(GameEvent):
    """Event triggered to display final game statistics."""

    stats: dict[BasePlayer, PlayerStats]
    event_type: EventType = "GAME_STATS"


@dataclass(frozen=True, kw_only=True)
class DeckReshuffledEvent(GameEvent):
    """Event triggered when the discard pile is shuffled to form a new draw pile."""

    event_type: EventType = "DECK_RESHUFFLED"


@dataclass(frozen=True, kw_only=True)
class IllegalActionEvent(GameEvent):
    """Event triggered when a player attempts an illegal action."""

    player_idx: int
    message: str
    event_type: EventType = "ILLEGAL_ACTION"
