"""Module containing the Round class."""

from __future__ import annotations

import random
import sys
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
from pycardgolf.core.state import Observation, RoundPhase
from pycardgolf.exceptions import GameConfigError, IllegalActionError
from pycardgolf.utils.card import Card
from pycardgolf.utils.constants import HAND_SIZE, INITIAL_CARDS_TO_FLIP
from pycardgolf.utils.deck import CardStack, Deck

if TYPE_CHECKING:
    from pycardgolf.core.game import Game
    from pycardgolf.players.player import Player


class Round:
    """Class representing a single round of Golf (Engine Version)."""

    def __init__(
        self,
        game: Game,
        players: list[Player],
        seed: int = random.randrange(sys.maxsize),
    ) -> None:
        """Initialize a round with players."""
        self.game: Game = game
        self.players: list[Player] = players
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
        self.cards_flipped_in_setup: dict[Player, int] = {p: 0 for p in players}

        cards_needed_for_hands = len(self.players) * HAND_SIZE
        if cards_needed_for_hands >= self.deck.num_cards:
            msg = (
                f"Not enough cards for players. "
                f"{len(self.players)} players need {cards_needed_for_hands + 1} cards, "
                f"but deck only has {self.deck.num_cards} cards."
            )
            raise GameConfigError(msg)

        # Initialize hands immediately
        self.deck.shuffle()
        for player in self.players:
            cards = [self.deck.draw() for _ in range(HAND_SIZE)]
            player.hand = Hand(cards)

        # Start discard pile
        card = self.deck.draw()
        card.face_up = True
        self.discard_pile.add_card(card)

    def get_current_player(self) -> Player:
        """Return the player whose turn it is."""
        return self.players[self.current_player_idx]

    def get_valid_actions(self, player: Player) -> list[Action]:
        actions: list[Action] = []
        if self.phase == RoundPhase.SETUP:
            for i, card in enumerate(player.hand):
                if not card.face_up:
                    actions.append(ActionFlipCard(hand_index=i))
        elif self.phase == RoundPhase.DRAW:
            actions.append(ActionDrawDeck())
            if self.discard_pile.num_cards > 0:
                actions.append(ActionDrawDiscard())
        elif self.phase == RoundPhase.ACTION:
            for i in range(HAND_SIZE):
                actions.append(ActionSwapCard(hand_index=i))
            if self.drawn_from_deck:
                actions.append(ActionDiscardDrawn())
        elif self.phase == RoundPhase.FLIP:
            actions.append(ActionPass())
            for i, card in enumerate(player.hand):
                if not card.face_up:
                    actions.append(ActionFlipCard(hand_index=i))
        return actions

    def get_observation(self, player: Player) -> Observation:
        """Return a sanitized observation for the given player."""
        # My hand: direct reference
        # Note: We rely on Card protecting its data if face_up=False.
        my_hand_view: list[Card] = list(player.hand)

        # Other hands
        other_hands_view = {}
        for p in self.players:
            if p != player:
                other_hands_view[p.name] = list(p.hand)

        return Observation(
            my_hand=my_hand_view,
            other_hands=other_hands_view,
            discard_top=None
            if self.discard_pile.num_cards == 0
            else self.discard_pile.peek(),
            deck_size=self.deck.num_cards,
            current_player_name=self.get_current_player().name,
            phase=self.phase,
            valid_actions=self.get_valid_actions(player),
            drawn_card=self.drawn_card if self.get_current_player() == player else None,
            can_discard_drawn=self.drawn_from_deck
            if self.get_current_player() == player
            else False,
        )

    def step(self, action: Action) -> list[GameEvent]:
        """Advance the game state by one step based on the action."""
        if self.phase == RoundPhase.FINISHED:
            return []

        player = self.get_current_player()
        events: list[GameEvent] = []

        if self.phase == RoundPhase.SETUP:
            events.extend(self._handle_setup_phase(player, action))
        elif self.phase == RoundPhase.DRAW:
            events.extend(self._handle_draw_phase(player, action))
        elif self.phase == RoundPhase.ACTION:
            events.extend(self._handle_action_phase(player, action))
        elif self.phase == RoundPhase.FLIP:
            events.extend(self._handle_flip_phase(player, action))

        # Check round end condition if we just finished a turn (went back to DRAW)
        # Actually logic is: if turn ended, check update round over.
        # But we need to know IF turn ended.
        # I'll let the handlers call advance_turn which checks conditions.

        return events

    def _handle_setup_phase(self, player: Player, action: Action) -> list[GameEvent]:
        if not isinstance(action, ActionFlipCard):
            raise IllegalActionError("Must flip a card in setup phase.")

        if player.hand[action.hand_index].face_up:
            raise IllegalActionError("Card already face up.")

        player.hand.flip_card(action.hand_index)
        events = [
            CardFlippedEvent(
                player=player,
                hand_index=action.hand_index,
                card=player.hand[action.hand_index],
            )
        ]
        self.cards_flipped_in_setup[player] += 1

        if self.cards_flipped_in_setup[player] >= INITIAL_CARDS_TO_FLIP:
            # Move to next player
            self.current_player_idx += 1
            if self.current_player_idx >= len(self.players):
                # All players done setup
                self.current_player_idx = 0
                self.phase = RoundPhase.DRAW
                events.append(TurnStartEvent(player=self.players[0]))
            else:
                # Next player setup
                # events.append(MessageEvent(f"{self.players[self.current_player_idx].name}'s turn to set up."))
                pass

        return events

    def _handle_draw_phase(self, player: Player, action: Action) -> list[GameEvent]:
        events = []
        if isinstance(action, ActionDrawDeck):
            card = self.deck.draw()
            card.face_up = True
            self.drawn_card = card
            self.drawn_from_deck = True
            self.phase = RoundPhase.ACTION
            events.append(CardDrawnDeckEvent(player=player, card=card))
        elif isinstance(action, ActionDrawDiscard):
            if self.discard_pile.num_cards == 0:
                raise IllegalActionError("Discard pile is empty.")
            card = self.discard_pile.draw()
            self.drawn_card = card
            self.drawn_from_deck = False
            # Drawing from discard forces a swap.
            # But we can reuse ACTION phase if we track that valid actions are only SWAP.
            self.phase = RoundPhase.ACTION
            events.append(CardDrawnDiscardEvent(player=player, card=card))
        else:
            raise IllegalActionError(f"Invalid action for DRAW phase: {action}")

        return events

    def _handle_action_phase(self, player: Player, action: Action) -> list[GameEvent]:
        events = []
        if self.drawn_card is None:
            raise IllegalActionError("No card drawn.")

        # Check if we drew from discard (which restricts actions)
        # We can implement this simply: if last event was DrawDiscard...
        # Or check logic: Discard draw MUST swap.
        # But here we just process the action. If they try to discard the drawn card
        # but they drew from discard, that is illegal.
        # Ideally we track source of drawn card.
        # For now let's assume the player/logic knows.

        # Improvement: Track `drawn_source` in state.

        if isinstance(action, ActionSwapCard):
            old_card = player.hand.replace(action.hand_index, self.drawn_card)
            old_card.face_up = True
            self.discard_pile.add_card(old_card)
            events.append(
                CardSwappedEvent(
                    player=player,
                    hand_index=action.hand_index,
                    new_card=self.drawn_card,
                    old_card=old_card,
                )
            )
            self.drawn_card = None
            self._end_turn(events)
        elif isinstance(action, ActionDiscardDrawn):
            # Validate: Can only discard drawn if it came from deck.
            # We need to know where it came from.
            # Hack: Check if drawn card was previously top of discard? No, it's already drawn.
            # Let's assume for now this action is legal only if Deck was source.
            # I SHOULD add `drawn_from_deck`
            self.discard_pile.add_card(self.drawn_card)
            events.append(CardDiscardedEvent(player=player, card=self.drawn_card))
            self.drawn_card = None
            self.phase = RoundPhase.FLIP
        else:
            raise IllegalActionError(f"Invalid action for ACTION phase: {action}")

        return events

    def _handle_flip_phase(self, player: Player, action: Action) -> list[GameEvent]:
        events = []
        if isinstance(action, ActionFlipCard):
            if player.hand[action.hand_index].face_up:
                raise IllegalActionError("Card already face up.")
            player.hand.flip_card(action.hand_index)
            events.append(
                CardFlippedEvent(
                    player=player,
                    hand_index=action.hand_index,
                    card=player.hand[action.hand_index],
                )
            )
            self._end_turn(events)
        elif isinstance(action, ActionPass):
            # Choose not to flip
            self._end_turn(events)
        else:
            raise IllegalActionError(f"Invalid action for FLIP phase: {action}")
        return events

    def _end_turn(self, events: list[GameEvent]) -> None:
        """Finalize turn, check end conditions, and advance."""
        player = self.get_current_player()

        # Check round end condition
        if self.check_round_end_condition(player) and self.last_turn_player_idx is None:
            self.last_turn_player_idx = self.current_player_idx
            # Notify final turn start for others?
            # events.append(MessageEvent(f"{player.name} triggered the final round!"))

        # Advance
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
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
            events.append(TurnStartEvent(player=self.players[self.current_player_idx]))

    def check_round_end_condition(self, player: Player) -> bool:
        """Check if the round should end (player has all cards face up)."""
        return player.hand.all_face_up()

    def reveal_hands(self) -> None:
        """Reveal all cards for all players."""
        for player in self.players:
            player.hand.reveal_all()

    def get_scores(self) -> dict[Player, int]:
        """Calculate scores for all players."""
        return {player: calculate_score(player.hand) for player in self.players}

    def __repr__(self) -> str:
        return f"Round(phase={self.phase}, players={self.players})"
