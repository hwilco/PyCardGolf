"""Entry point for the PyCardGolf application."""

import argparse

from pycardgolf.core.game import Game
from pycardgolf.interfaces.cli import CLIInterface
from pycardgolf.players.bots.random_bot import RandomBot
from pycardgolf.players.human import HumanPlayer


def main() -> None:
    """Run the main game loop."""
    parser = argparse.ArgumentParser(description="Play Card Golf")
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

    args = parser.parse_args()

    interface = CLIInterface()
    players = []

    for i in range(args.humans):
        name = interface.get_input(f"Enter name for Human {i + 1}: ")
        players.append(HumanPlayer(name, interface))

    players.extend(RandomBot(f"Bot {i + 1}", interface) for i in range(args.bots))

    game = Game(players, interface, num_rounds=args.rounds)
    game.start()


if __name__ == "__main__":
    main()
