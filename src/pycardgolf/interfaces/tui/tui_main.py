"""Entry point for the PyCardGolf TUI application."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from pycardgolf.core.event_bus import EventBus
from pycardgolf.core.game import Game
from pycardgolf.interfaces.tui.tui_app import PyCardGolfApp
from pycardgolf.interfaces.tui.tui_input import TUIInputHandler
from pycardgolf.interfaces.tui.tui_renderer import TUIRenderer
from pycardgolf.players.bots.random_bot import RandomBot
from pycardgolf.players.human import HumanPlayer

if TYPE_CHECKING:
    from pycardgolf.players.player import BasePlayer


def _display_rules() -> None:
    """Display the game rules and exit."""
    from rich.console import Console  # noqa: PLC0415
    from rich.markdown import Markdown  # noqa: PLC0415

    rules_path = Path(__file__).parents[2] / "RULES.md"
    console = Console()
    markdown = Markdown(rules_path.read_text(encoding="utf-8"))
    console.print(markdown)


def main() -> None:
    """Parse arguments and launch the Textual TUI."""
    parser = argparse.ArgumentParser(description="Play Card Golf (TUI)")
    parser.add_argument(
        "--rules",
        action="store_true",
        help="Display the game rules and exit",
    )
    parser.add_argument(
        "--humans",
        type=int,
        default=1,
        help="Number of human players",
    )
    parser.add_argument(
        "--bots",
        type=int,
        default=1,
        help="Number of bot players",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=9,
        help="Number of rounds to play",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for deterministic gameplay",
    )

    args = parser.parse_args()

    if args.rules:
        _display_rules()
        sys.exit(0)

    # Collect human names before launching the app
    event_bus = EventBus()
    renderer = TUIRenderer(event_bus)
    input_handler = TUIInputHandler()
    players: list[BasePlayer] = []

    for i in range(args.humans):
        name = input(f"Enter name for Human {i + 1}: ")
        players.append(HumanPlayer(name, input_handler))

    players.extend(RandomBot(f"Bot {i + 1}") for i in range(args.bots))

    game = Game(players, event_bus, num_rounds=args.rounds, seed=args.seed)

    app = PyCardGolfApp(game, renderer, input_handler)
    app.run()


if __name__ == "__main__":
    main()
