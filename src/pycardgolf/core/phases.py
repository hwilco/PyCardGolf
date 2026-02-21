"""Module containing phase-specific logic for the Golf engine."""

from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING

from pycardgolf.core.actions import (
    Action,
    ActionDiscardDrawn,
    ActionDrawDeck,
    ActionDrawDiscard,
    ActionFlipCard,
    ActionPass,
    ActionSwapCard,
)
from pycardgolf.core.events import (
    CardDiscardedEvent,
    CardDrawnDeckEvent,
    CardDrawnDiscardEvent,
    CardFlippedEvent,
    CardSwappedEvent,
    GameEvent,
    RoundEndEvent,
    TurnStartEvent,
)
from pycardgolf.exceptions import IllegalActionError
from pycardgolf.utils.constants import HAND_SIZE, INITIAL_CARDS_TO_FLIP

if TYPE_CHECKING:
    from pycardgolf.core.round import Round


class RoundPhase(Enum):
    """Phases of a round."""

    SETUP = auto()  # Initial flipping of cards
    DRAW = auto()  # Waiting for player to draw
    ACTION = auto()  # Waiting for player to swap/discard
    FLIP = auto()  # Waiting for player to flip (optional after discard)
    FINISHED = auto()


def get_valid_actions(round_state: Round, player_idx: int) -> list[Action]:
    """Return a list of valid actions for the given player."""
    actions: list[Action] = []
    phase = round_state.phase

    if phase == RoundPhase.SETUP:
        actions.extend(
            [
                ActionFlipCard(hand_index=i)
                for i, card in enumerate(round_state.hands[player_idx])
                if not card.face_up
            ]
        )
    elif phase == RoundPhase.DRAW:
        actions.append(ActionDrawDeck())
        if round_state.discard_pile.num_cards > 0:
            actions.append(ActionDrawDiscard())
    elif phase == RoundPhase.ACTION:
        actions.extend([ActionSwapCard(hand_index=i) for i in range(HAND_SIZE)])
        if round_state.drawn_from_deck:
            actions.append(ActionDiscardDrawn())
    elif phase == RoundPhase.FLIP:
        actions.append(ActionPass())
        actions.extend(
            [
                ActionFlipCard(hand_index=i)
                for i, card in enumerate(round_state.hands[player_idx])
                if not card.face_up
            ]
        )
    return actions


def handle_step(round_state: Round, action: Action) -> list[GameEvent]:
    """Advance the round state based on the action and current phase."""
    if round_state.phase == RoundPhase.FINISHED:
        return []

    player_idx = round_state.current_player_idx

    if round_state.phase == RoundPhase.SETUP:
        return _handle_setup_phase(round_state, player_idx, action)
    if round_state.phase == RoundPhase.DRAW:
        return _handle_draw_phase(round_state, player_idx, action)
    if round_state.phase == RoundPhase.ACTION:
        return _handle_action_phase(round_state, player_idx, action)
    if round_state.phase == RoundPhase.FLIP:
        return _handle_flip_phase(round_state, player_idx, action)

    return []


def _handle_setup_phase(
    round_state: Round, player_idx: int, action: Action
) -> list[GameEvent]:
    if not isinstance(action, ActionFlipCard):
        msg = "Must flip a card in setup phase."
        raise IllegalActionError(msg)

    hand = round_state.hands[player_idx]
    if hand[action.hand_index].face_up:
        msg = "Card already face up."
        raise IllegalActionError(msg)

    hand.flip_card(action.hand_index)
    events: list[GameEvent] = [
        CardFlippedEvent(
            player_idx=player_idx,
            hand_index=action.hand_index,
            card=hand[action.hand_index],
        )
    ]
    round_state.cards_flipped_in_setup[player_idx] += 1

    if round_state.cards_flipped_in_setup[player_idx] >= INITIAL_CARDS_TO_FLIP:
        # Move to next player
        round_state.current_player_idx += 1
        if round_state.current_player_idx >= round_state.num_players:
            # All players done setup
            round_state.current_player_idx = 0
            round_state.phase = RoundPhase.DRAW
            events.append(TurnStartEvent(player_idx=0))

    return events


def _handle_draw_phase(
    round_state: Round, player_idx: int, action: Action
) -> list[GameEvent]:
    events: list[GameEvent] = []
    if isinstance(action, ActionDrawDeck):
        card = round_state.deck.draw()
        card.face_up = True
        round_state.drawn_card = card
        round_state.drawn_from_deck = True
        round_state.phase = RoundPhase.ACTION
        events.append(CardDrawnDeckEvent(player_idx=player_idx, card=card))
    elif isinstance(action, ActionDrawDiscard):
        if round_state.discard_pile.num_cards == 0:
            msg = "Discard pile is empty."
            raise IllegalActionError(msg)
        card = round_state.discard_pile.draw()
        round_state.drawn_card = card
        round_state.drawn_from_deck = False
        round_state.phase = RoundPhase.ACTION
        events.append(CardDrawnDiscardEvent(player_idx=player_idx, card=card))
    else:
        msg = f"Invalid action for DRAW phase: {action}"
        raise IllegalActionError(msg)

    return events


def _handle_action_phase(
    round_state: Round, player_idx: int, action: Action
) -> list[GameEvent]:
    events: list[GameEvent] = []
    if round_state.drawn_card is None:
        msg = "No card drawn."
        raise IllegalActionError(msg)

    hand = round_state.hands[player_idx]

    if isinstance(action, ActionSwapCard):
        old_card = hand.replace(action.hand_index, round_state.drawn_card)
        old_card.face_up = True
        round_state.discard_pile.add_card(old_card)
        events.append(
            CardSwappedEvent(
                player_idx=player_idx,
                hand_index=action.hand_index,
                new_card=round_state.drawn_card,
                old_card=old_card,
            )
        )
        round_state.drawn_card = None
        _end_turn(round_state, events)
    elif isinstance(action, ActionDiscardDrawn):
        round_state.discard_pile.add_card(round_state.drawn_card)
        events.append(
            CardDiscardedEvent(player_idx=player_idx, card=round_state.drawn_card)
        )
        round_state.drawn_card = None
        round_state.phase = RoundPhase.FLIP
    else:
        msg = f"Invalid action for ACTION phase: {action}"
        raise IllegalActionError(msg)

    return events


def _handle_flip_phase(
    round_state: Round, player_idx: int, action: Action
) -> list[GameEvent]:
    events: list[GameEvent] = []
    hand = round_state.hands[player_idx]
    if isinstance(action, ActionFlipCard):
        if hand[action.hand_index].face_up:
            msg = "Card already face up."
            raise IllegalActionError(msg)
        hand.flip_card(action.hand_index)
        events.append(
            CardFlippedEvent(
                player_idx=player_idx,
                hand_index=action.hand_index,
                card=hand[action.hand_index],
            )
        )
        _end_turn(round_state, events)
    elif isinstance(action, ActionPass):
        _end_turn(round_state, events)
    else:
        msg = f"Invalid action for FLIP phase: {action}"
        raise IllegalActionError(msg)
    return events


def _end_turn(round_state: Round, events: list[GameEvent]) -> None:
    """Finalize turn, check end conditions, and advance."""
    player_idx = round_state.current_player_idx

    # Check round end condition
    if (
        round_state.hands[player_idx].all_face_up()
        and round_state.last_turn_player_idx is None
    ):
        round_state.last_turn_player_idx = round_state.current_player_idx

    # Advance to the next player
    round_state.current_player_idx = (
        round_state.current_player_idx + 1
    ) % round_state.num_players
    if round_state.current_player_idx == 0:
        round_state.turn_count += 1

    # Check if round is over
    if (
        round_state.last_turn_player_idx is not None
        and round_state.current_player_idx == round_state.last_turn_player_idx
    ):
        round_state.phase = RoundPhase.FINISHED
        round_state.reveal_hands()  # Reveal hidden cards
        scores = round_state.get_scores()
        events.append(RoundEndEvent(scores=scores))
    else:
        round_state.phase = RoundPhase.DRAW
        events.append(TurnStartEvent(player_idx=round_state.current_player_idx))
