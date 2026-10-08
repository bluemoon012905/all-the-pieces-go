import random

from chess_arena_10x10.bots.base import BaseBot


class RandomBot(BaseBot):
    """Baseline bot that chooses uniformly from legal moves."""

    def get_move(self, board_state):
        legal_moves = board_state.legal_moves(self.color)
        if not legal_moves:
            raise RuntimeError(f"{self.color} has no legal moves")
        return random.choice(legal_moves)

