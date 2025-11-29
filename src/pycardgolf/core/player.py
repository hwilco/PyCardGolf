from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pycardgolf.core.round import Round


class Player(ABC):
    def __init__(self, name: str):
        self.name = name
        self.hand = []
        self.score = 0

    @abstractmethod
    def take_turn(self, game_round: "Round") -> None:
        """
        Execute the player's turn.
        """
        pass

    def notify(self, event: str, data: Any = None) -> None:
        """
        Notify the player of an event (e.g., another player's move).
        """
        pass
