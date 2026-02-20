"""Entry point for the PyCardGolf application."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from rich.console import Console
from rich.markdown import Markdown

from pycardgolf.core.game import Game
from pycardgolf.exceptions import GameExitError
from pycardgolf.interfaces.cli_input import CLIInputHandler
from pycardgolf.interfaces.cli_renderer import CLIRenderer
from pycardgolf.players.bots.random_bot import RandomBot
from pycardgolf.players.human import HumanPlayer

if TYPE_CHECKING:
    from pycardgolf.players import Player


def _display_rules() -> None:
    """Display the game rules."""
    rules_path = Path(__file__).parent / "RULES.md"
    console = Console()
    markdown = Markdown(rules_path.read_text(encoding="utf-8"))
    console.print(markdown)


def main() -> None:
    """Run the main game loop."""
    parser = argparse.ArgumentParser(description="Play Card Golf")
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
        "--delay",
        type=float,
        default=0.0,
        help="Delay in seconds between actions (for animations)",
    )

    args = parser.parse_args()

    if args.rules:
        _display_rules()
        sys.exit(0)

    # Instantiate renderer (for Game) and input handler (for HumanPlayer).
    renderer = CLIRenderer(Console(), delay=args.delay)
    input_handler = CLIInputHandler(renderer.console, renderer)
    players: list[Player] = []

    for i in range(args.humans):
        name = input_handler.get_input(f"Enter name for Human {i + 1}: ")
        players.append(HumanPlayer(name, input_handler))

    players.extend(RandomBot(f"Bot {i + 1}") for i in range(args.bots))

    game = Game(players, renderer, num_rounds=args.rounds)
    try:
        game.start()
    except GameExitError:
        console = Console()
        console.print("\n[bold red][ERROR] Game exited by user.[/bold red]\n")
    except KeyboardInterrupt:
        console = Console()
        console.print("\n[bold red][ERROR] Game interrupted.[/bold red]\n")


if __name__ == "__main__":
    main()
