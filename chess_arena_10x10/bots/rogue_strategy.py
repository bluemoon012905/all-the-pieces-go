"""Shared scoring helpers for the first Rogue enemy archetypes."""

from __future__ import annotations

from chess_arena_10x10.core.board import Move


PIECE_VALUES = {
    "Pawn": 10,
    "Fuhyo / Pawn": 10,
    "Xiangqi Soldier": 10,
    "Shogi Knight": 24,
    "Knight": 30,
    "Silver General": 32,
    "Bishop": 33,
    "Shogi Bishop": 55,
    "Gold General": 34,
    "Rook": 40,
    "Shogi Rook": 65,
    "Cannon": 40,
    "Queen": 90,
    "King": 1000,
    "Shogi King": 1000,
    "Palace King": 1000,
}


def piece_value(piece) -> int:
    return PIECE_VALUES.get(piece.name, 20)


def forward_progress(color: str, coord: tuple[int, int]) -> int:
    return coord[1] if color == "white" else 8 - coord[1]


def nearest_enemy_king(board, color: str, coord: tuple[int, int]) -> int:
    kings = [
        position for position, piece in board.pieces_for("black" if color == "white" else "white")
        if piece.name in {"King", "Shogi King", "Palace King"}
    ]
    if not kings:
        return 0
    return min(abs(coord[0] - king[0]) + abs(coord[1] - king[1]) for king in kings)


def best_move(game_state, color: str, score_move):
    legal_moves = game_state.legal_moves(color)
    if not legal_moves:
        raise RuntimeError(f"{color} has no legal moves")
    return max(legal_moves, key=lambda move: score_move(game_state, move, color))


def captured_value(game_state, move: Move) -> int:
    target = game_state.board.get(move.to_pos)
    return piece_value(target) if target is not None and target.color != game_state.active_player else 0

