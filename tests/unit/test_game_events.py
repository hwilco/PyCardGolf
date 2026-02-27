"""Tests for events published by the Game class."""

from unittest.mock import MagicMock

from pycardgolf.core.event_bus import EventBus
from pycardgolf.core.events import GameStartedEvent, RoundStartEvent, TurnStartEvent
from pycardgolf.core.game import Game
from pycardgolf.players.human import HumanPlayer


def test_game_start_events():
    """Test that start() and round initialization publish the expected events."""
    event_bus = EventBus()
    publisher = MagicMock()
    event_bus.subscribe(GameStartedEvent, publisher)
    event_bus.subscribe(RoundStartEvent, publisher)
    event_bus.subscribe(TurnStartEvent, publisher)

    player = HumanPlayer("Test Player", MagicMock())
    game = Game(players=[player], event_bus=event_bus, num_rounds=1, seed=42)

    game.start()

    # Should have published:
    # 1. GameStartedEvent
    # 2. RoundStartEvent
    # 3. TurnStartEvent (the new one we added)
    assert publisher.call_count == 3

    calls = publisher.call_args_list
    assert isinstance(calls[0][0][0], GameStartedEvent)
    assert isinstance(calls[1][0][0], RoundStartEvent)
    assert isinstance(calls[2][0][0], TurnStartEvent)

    # Verify TurnStartEvent has the correct hands
    turn_start_event = calls[2][0][0]
    assert turn_start_event.player_idx == 0
    assert len(turn_start_event.hands) == 1
    assert 0 in turn_start_event.hands
