"""Module containing the EventBus for publisher-subscriber communication."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

    from pycardgolf.core.events import GameEvent

    # Type variable bound to GameEvent for proper typing of subscriber callbacks
    E = TypeVar("E", bound=GameEvent)


class EventBus:
    """A synchronous event bus for decoupling game logic from interfaces."""

    def __init__(self) -> None:
        """Initialize an empty EventBus."""
        self._subscribers: dict[type[GameEvent], list[Callable[[Any], None]]] = {}

    def subscribe(self, event_type: type[E], callback: Callable[[E], None]) -> None:
        """Register a callback to be invoked when a specific GameEvent is published.

        Args:
            event_type: The class of the GameEvent to subscribe to.
            callback: The function to call when the event is published.

        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def publish(self, event: GameEvent) -> None:
        """Publish an event to all registered subscribers.

        Args:
            event: The GameEvent instance to publish.

        """
        event_type = type(event)
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                callback(event)
