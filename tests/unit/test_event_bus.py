"""Tests for the event bus publisher-subscriber system."""

from pycardgolf.core.event_bus import EventBus
from pycardgolf.core.events import GameEvent


class DummyEvent(GameEvent):
    """A dummy event for testing purposes."""

    event_type: str = "DUMMY"  # type: ignore[assignment]


class AnotherDummyEvent(GameEvent):
    """Another dummy event to test type differentiation."""

    event_type: str = "ANOTHER_DUMMY"  # type: ignore[assignment]


def test_event_bus_subscribe_and_publish() -> None:
    """Test that basic subscription and publishing works."""
    bus = EventBus()
    received_events = []

    def callback(event: DummyEvent) -> None:
        received_events.append(event)

    bus.subscribe(DummyEvent, callback)

    event1 = DummyEvent(event_type="DUMMY")  # type: ignore[arg-type]
    bus.publish(event1)

    assert len(received_events) == 1
    assert received_events[0] is event1


def test_event_bus_filters_by_type() -> None:
    """Test that events are only routed to their specific subscribers."""
    bus = EventBus()
    dummy_hits = []
    another_hits = []

    def dummy_callback(event: DummyEvent) -> None:  # noqa: ARG001
        dummy_hits.append(True)

    def another_callback(event: AnotherDummyEvent) -> None:  # noqa: ARG001
        another_hits.append(True)

    bus.subscribe(DummyEvent, dummy_callback)
    bus.subscribe(AnotherDummyEvent, another_callback)

    bus.publish(DummyEvent(event_type="DUMMY"))  # type: ignore[arg-type]

    assert len(dummy_hits) == 1
    assert len(another_hits) == 0


def test_event_bus_multiple_subscribers() -> None:
    """Test that multiple subscribers to the same event both fire."""
    bus = EventBus()
    hits = []

    def callback1(event: DummyEvent) -> None:  # noqa: ARG001
        hits.append(1)

    def callback2(event: DummyEvent) -> None:  # noqa: ARG001
        hits.append(2)

    bus.subscribe(DummyEvent, callback1)
    bus.subscribe(DummyEvent, callback2)

    bus.publish(DummyEvent(event_type="DUMMY"))  # type: ignore[arg-type]

    assert len(hits) == 2
    assert 1 in hits
    assert 2 in hits


def test_event_bus_publish_no_subscribers() -> None:
    """Test that publishing an event with no subscribers doesn't crash."""
    bus = EventBus()
    bus.publish(DummyEvent(event_type="DUMMY"))  # type: ignore[arg-type]
    # Should not raise an exception
