"""Rogue enemy that values captures and attacks valuable targets."""

from chess_arena_10x10.bots.base import BaseBot
from chess_arena_10x10.bots.rogue_strategy import best_move, captured_value, nearest_enemy_king, piece_value


class HunterBot(BaseBot):
    """Capture-first enemy with enough positional preference to avoid randomness."""

    def get_move(self, board_state):
        def score(engine, move, color):
            moving = engine.board.get(move.from_pos)
            target = engine.board.get(move.to_pos)
            target_score = captured_value(engine, move)
            if target is not None and target.name in {"King", "Shogi King", "Palace King"}:
                target_score += 10000
            return (
                target_score * 30
                - nearest_enemy_king(engine.board, color, move.to_pos)
                - piece_value(moving) * 0.04
            )

        return best_move(board_state, self.color, score)

