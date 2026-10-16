from __future__ import annotations

import argparse
import sys

from chess_arena_10x10.core.engine import GameEngine, discover_bots


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the custom 9x9 auto-chess arena.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("new", help="Initialize and print a fresh default game.")

    play = subparsers.add_parser("play", help="Run a bot-vs-bot match.")
    play.add_argument("--bot1", default="random_bot", help="White bot module name.")
    play.add_argument("--bot2", default="random_bot", help="Black bot module name.")
    play.add_argument("--max-actions", type=int, default=50, help="Maximum actions to execute.")
    play.add_argument("--seed", type=int, default=None, help="Random seed for reproducible bot play.")
    return parser


def create_default_engine() -> GameEngine:
    engine = GameEngine()
    engine.setup_default_position()
    return engine


def command_new(_: argparse.Namespace) -> int:
    engine = create_default_engine()
    print(engine.board.render_ascii())
    print(f"phase={engine.phase} active={engine.active_player} moves_left={engine.moves_left_this_turn}")
    return 0


def command_play(args: argparse.Namespace) -> int:
    if args.seed is not None:
        import random

        random.seed(args.seed)

    bots = discover_bots()
    if args.bot1 not in bots or args.bot2 not in bots:
        available = ", ".join(sorted(bots)) or "(none)"
        print(f"Unknown bot. Available bots: {available}", file=sys.stderr)
        return 2

    engine = create_default_engine()
    players = {
        "white": bots[args.bot1]("white"),
        "black": bots[args.bot2]("black"),
    }

    print(engine.board.render_ascii())
    for action_index in range(1, args.max_actions + 1):
        bot = players[engine.active_player]
        try:
            result = engine.run_bot_action(bot)
        except RuntimeError as exc:
            print(f"Match stopped: {exc}")
            return 0
        move = result.move
        capture_text = f", captured {result.captured}" if result.captured else ""
        print(
            f"\nAction {action_index}: {result.piece} "
            f"{move.from_pos} -> {move.to_pos}{capture_text}"
        )
        print(engine.board.render_ascii())
        print(
            f"active={engine.active_player} "
            f"moves_left={engine.moves_left_this_turn} turn={engine.turn_number}"
        )
        if result.winner:
            print(f"Game over: {result.winner} wins")
            return 0
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "new":
        return command_new(args)
    if args.command == "play":
        return command_play(args)
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
