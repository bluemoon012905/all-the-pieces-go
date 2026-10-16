"""Rogue enemy that advances pieces and pressures the opposing king."""

from chess_arena_10x10.bots.base import BaseBot
from chess_arena_10x10.bots.rogue_strategy import best_move, captured_value, forward_progress, nearest_enemy_king


class RusherBot(BaseBot):
    """Aggressive, readable baseline: advance, capture, and close distance."""

    def get_move(self, board_state):
        def score(engine, move, color):
            piece = engine.board.get(move.from_pos)
            return (
                captured_value(engine, move) * 20
                + forward_progress(color, move.to_pos) * 4
                - nearest_enemy_king(engine.board, color, move.to_pos)
                + (2 if piece and piece.name in {"Pawn", "Fuhyo / Pawn", "Xiangqi Soldier"} else 0)
            )

        return best_move(board_state, self.color, score)

