"""Module containing the Round class."""

from __future__ import annotations

import random
import sys
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
from pycardgolf.core.hand import Hand
from pycardgolf.core.scoring import calculate_score

if TYPE_CHECKING:
    from pycardgolf.utils.card import Card
from pycardgolf.exceptions import GameConfigError, IllegalActionError
from pycardgolf.utils.constants import HAND_SIZE, INITIAL_CARDS_TO_FLIP
from pycardgolf.utils.deck import CardStack, Deck


class RoundPhase(Enum):
    """Phases of a round."""

    SETUP = auto()  # Initial flipping of cards
    DRAW = auto()  # Waiting for player to draw
    ACTION = auto()  # Waiting for player to swap/discard
    FLIP = auto()  # Waiting for player to flip (optional after discard)
    FINISHED = auto()


class Round:
    """Class representing a single round of Golf (Engine Version)."""

    def __init__(
        self,
        player_names: list[str],
        seed: int = random.randrange(sys.maxsize),
    ) -> None:
        """Initialize a round with players."""
        self.player_names: list[str] = player_names
        self.num_players: int = len(player_names)
        self.seed: int = seed
        self._rng: random.Random = random.Random(self.seed)

        # Game State
        deck_color = "blue"
        deck_seed = self._rng.randrange(sys.maxsize)
        self.deck: Deck = Deck(back_color=deck_color, seed=deck_seed)

        discard_seed = self._rng.randrange(sys.maxsize)
        self.discard_pile: CardStack = CardStack(seed=discard_seed)

        self.current_player_idx: int = 0
        self.round_over: bool = False
        self.last_turn_player_idx: int | None = None
        self.turn_count: int = 1

        self.phase: RoundPhase = RoundPhase.SETUP
        self.drawn_card: Card | None = None
        self.drawn_from_deck: bool = False
        self.cards_flipped_in_setup: dict[int, int] = dict.fromkeys(
            range(self.num_players), 0
        )
        self.hands: list[Hand] = []

        # Validate configuration
        self.validate_config(self.num_players, self.deck.num_cards)

        # Initialize hands immediately
        self.deck.shuffle()
        for _ in range(self.num_players):
            cards = [self.deck.draw() for _ in range(HAND_SIZE)]
            self.hands.append(Hand(cards))

        # Start discard pile
        card = self.deck.draw()
        card.face_up = True
        self.discard_pile.add_card(card)

    def get_current_player_idx(self) -> int:
        """Return the index of the player whose turn it is."""
        return self.current_player_idx

    def get_valid_actions(self, player_idx: int) -> list[Action]:
        """Return a list of valid actions for the given player."""
        actions: list[Action] = []
        if self.phase == RoundPhase.SETUP:
            actions.extend(
                [
                    ActionFlipCard(hand_index=i)
                    for i, card in enumerate(self.hands[player_idx])
                    if not card.face_up
                ]
            )
        elif self.phase == RoundPhase.DRAW:
            actions.append(ActionDrawDeck())
            if self.discard_pile.num_cards > 0:
                actions.append(ActionDrawDiscard())
        elif self.phase == RoundPhase.ACTION:
            actions.extend([ActionSwapCard(hand_index=i) for i in range(HAND_SIZE)])
            if self.drawn_from_deck:
                actions.append(ActionDiscardDrawn())
        elif self.phase == RoundPhase.FLIP:
            actions.append(ActionPass())
            actions.extend(
                [
                    ActionFlipCard(hand_index=i)
                    for i, card in enumerate(self.hands[player_idx])
                    if not card.face_up
                ]
            )
        return actions

    @classmethod
    def validate_config(cls, num_players: int, deck_size: int = 52) -> None:
        """Validate game configuration before starting a round.

        Args:
            num_players: Number of players in the game.
            deck_size (optional): Number of cards in the deck. Defaults to 52.

        Raises:
            GameConfigError: If there are not enough cards for the number of players.

        """
        cards_needed_for_hands = num_players * HAND_SIZE
        if cards_needed_for_hands >= deck_size:
            msg = (
                f"Not enough cards for players. "
                f"{num_players} players need {cards_needed_for_hands + 1} cards, "
                f"but deck only has {deck_size} cards."
            )
            raise GameConfigError(msg)

    def step(self, action: Action) -> list[GameEvent]:
        """Advance the game state by one step based on the action."""
        if self.phase == RoundPhase.FINISHED:
            return []

        player_idx = self.current_player_idx
        events: list[GameEvent] = []

        if self.phase == RoundPhase.SETUP:
            events.extend(self._handle_setup_phase(player_idx, action))
        elif self.phase == RoundPhase.DRAW:
            events.extend(self._handle_draw_phase(player_idx, action))
        elif self.phase == RoundPhase.ACTION:
            events.extend(self._handle_action_phase(player_idx, action))
        elif self.phase == RoundPhase.FLIP:
            events.extend(self._handle_flip_phase(player_idx, action))

        return events

    def _handle_setup_phase(self, player_idx: int, action: Action) -> list[GameEvent]:
        if not isinstance(action, ActionFlipCard):
            msg = "Must flip a card in setup phase."
            raise IllegalActionError(msg)

        hand = self.hands[player_idx]
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
        self.cards_flipped_in_setup[player_idx] += 1

        if self.cards_flipped_in_setup[player_idx] >= INITIAL_CARDS_TO_FLIP:
            # Move to next player
            self.current_player_idx += 1
            if self.current_player_idx >= self.num_players:
                # All players done setup
                self.current_player_idx = 0
                self.phase = RoundPhase.DRAW
                events.append(TurnStartEvent(player_idx=0))
            else:
                pass

        return events

    def _handle_draw_phase(self, player_idx: int, action: Action) -> list[GameEvent]:
        events: list[GameEvent] = []
        if isinstance(action, ActionDrawDeck):
            card = self.deck.draw()
            card.face_up = True
            self.drawn_card = card
            self.drawn_from_deck = True
            self.phase = RoundPhase.ACTION
            events.append(CardDrawnDeckEvent(player_idx=player_idx, card=card))
        elif isinstance(action, ActionDrawDiscard):
            if self.discard_pile.num_cards == 0:
                msg = "Discard pile is empty."
                raise IllegalActionError(msg)
            card = self.discard_pile.draw()
            self.drawn_card = card
            self.drawn_from_deck = False
            self.phase = RoundPhase.ACTION
            events.append(CardDrawnDiscardEvent(player_idx=player_idx, card=card))
        else:
            msg = f"Invalid action for DRAW phase: {action}"
            raise IllegalActionError(msg)

        return events

    def _handle_action_phase(self, player_idx: int, action: Action) -> list[GameEvent]:
        events: list[GameEvent] = []
        if self.drawn_card is None:
            msg = "No card drawn."
            raise IllegalActionError(msg)

        hand = self.hands[player_idx]

        if isinstance(action, ActionSwapCard):
            old_card = hand.replace(action.hand_index, self.drawn_card)
            old_card.face_up = True
            self.discard_pile.add_card(old_card)
            events.append(
                CardSwappedEvent(
                    player_idx=player_idx,
                    hand_index=action.hand_index,
                    new_card=self.drawn_card,
                    old_card=old_card,
                )
            )
            self.drawn_card = None
            self._end_turn(events)
        elif isinstance(action, ActionDiscardDrawn):
            self.discard_pile.add_card(self.drawn_card)
            events.append(
                CardDiscardedEvent(player_idx=player_idx, card=self.drawn_card)
            )
            self.drawn_card = None
            self.phase = RoundPhase.FLIP
        else:
            msg = f"Invalid action for ACTION phase: {action}"
            raise IllegalActionError(msg)

        return events

    def _handle_flip_phase(self, player_idx: int, action: Action) -> list[GameEvent]:
        events: list[GameEvent] = []
        hand = self.hands[player_idx]
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
            self._end_turn(events)
        elif isinstance(action, ActionPass):
            self._end_turn(events)
        else:
            msg = f"Invalid action for FLIP phase: {action}"
            raise IllegalActionError(msg)
        return events

    def _end_turn(self, events: list[GameEvent]) -> None:
        """Finalize turn, check end conditions, and advance."""
        player_idx = self.current_player_idx

        # Check round end condition
        if (
            self.check_round_end_condition(player_idx)
            and self.last_turn_player_idx is None
        ):
            self.last_turn_player_idx = self.current_player_idx

        # Advance
        self.current_player_idx = (self.current_player_idx + 1) % self.num_players
        if self.current_player_idx == 0:
            self.turn_count += 1

        # Check if round is over
        if (
            self.last_turn_player_idx is not None
            and self.current_player_idx == self.last_turn_player_idx
        ):
            self.round_over = True
            self.phase = RoundPhase.FINISHED
            self.reveal_hands()  # Reveal hidden cards
            scores = self.get_scores()
            events.append(RoundEndEvent(scores=scores))
        else:
            self.phase = RoundPhase.DRAW
            events.append(TurnStartEvent(player_idx=self.current_player_idx))

    def check_round_end_condition(self, player_idx: int) -> bool:
        """Check if the round should end (player has all cards face up)."""
        return self.hands[player_idx].all_face_up()

    def reveal_hands(self) -> None:
        """Reveal all cards for all players."""
        for hand in self.hands:
            hand.reveal_all()

    def get_scores(self) -> dict[int, int]:
        """Calculate scores for all players."""
        return {i: calculate_score(hand) for i, hand in enumerate(self.hands)}

    def __repr__(self) -> str:
        return f"Round(phase={self.phase}, num_players={self.num_players})"
