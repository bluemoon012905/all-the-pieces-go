from __future__ import annotations

from typing import List, Tuple

from chess_arena_10x10.pieces.base import DIAGONAL, ORTHOGONAL, Piece
from chess_arena_10x10.pieces.standard import Bishop, Rook

Coord = Tuple[int, int]


def in_promotion_zone(color: str, coord: Coord) -> bool:
    _, y = coord
    return y >= 7 if color == "white" else y <= 2


class GoldGeneral(Piece):
    name = "Gold General"
    code = "G"

    def legal_moves(self, board: "Board", start: Coord) -> List[Coord]:
        forward = self.direction
        deltas = ((0, forward), (1, forward), (-1, forward), (1, 0), (-1, 0), (0, -forward))
        return self.step_moves(board, start, deltas)


class SilverGeneral(Piece):
    name = "Silver General"
    code = "V"

    def legal_moves(self, board: "Board", start: Coord) -> List[Coord]:
        if self.promoted:
            return GoldGeneral(self.color, promoted=True).legal_moves(board, start)
        forward = self.direction
        deltas = ((0, forward), (1, forward), (-1, forward), (1, -forward), (-1, -forward))
        return self.step_moves(board, start, deltas)

    def can_promote_at(self, coord: Coord) -> bool:
        return in_promotion_zone(self.color, coord)


class ShogiRook(Rook):
    name = "Shogi Rook"
    code = "T"

    def legal_moves(self, board: "Board", start: Coord) -> List[Coord]:
        moves = super().legal_moves(board, start)
        if self.promoted:
            moves.extend(coord for coord in self.step_moves(board, start, DIAGONAL) if coord not in moves)
        return moves

    def can_promote_at(self, coord: Coord) -> bool:
        return in_promotion_zone(self.color, coord)


class ShogiBishop(Bishop):
    name = "Shogi Bishop"
    code = "M"

    def legal_moves(self, board: "Board", start: Coord) -> List[Coord]:
        moves = super().legal_moves(board, start)
        if self.promoted:
            moves.extend(coord for coord in self.step_moves(board, start, ORTHOGONAL) if coord not in moves)
        return moves

    def can_promote_at(self, coord: Coord) -> bool:
        return in_promotion_zone(self.color, coord)


from chess_arena_10x10.core.board import Board  # noqa: E402

