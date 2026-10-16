"""Rogue enemy that protects its king and holds the center."""

from chess_arena_10x10.bots.base import BaseBot
from chess_arena_10x10.bots.rogue_strategy import best_move, captured_value, forward_progress


class SentinelBot(BaseBot):
    """Defensive enemy with capture preference and conservative development."""

    def get_move(self, board_state):
        def score(engine, move, color):
            moving = engine.board.get(move.from_pos)
            center_distance = abs(move.to_pos[0] - 4) + abs(move.to_pos[1] - 4)
            retreat_from_edge = min(move.to_pos[0], 8 - move.to_pos[0])
            return (
                captured_value(engine, move) * 24
                - center_distance * 2
                + retreat_from_edge
                + forward_progress(color, move.to_pos)
                - (4 if moving and moving.name in {"King", "Shogi King", "Palace King"} else 0)
            )

        return best_move(board_state, self.color, score)

