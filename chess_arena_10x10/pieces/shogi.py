from __future__ import annotations

from typing import List, Tuple

from chess_arena_10x10.pieces.base import DIAGONAL, ORTHOGONAL, Piece
from chess_arena_10x10.pieces.standard import Bishop, Rook

Coord = Tuple[int, int]


def in_promotion_zone(color: str, coord: Coord) -> bool:
    _, y = coord
    return y >= 6 if color == "white" else y <= 2


class ShogiKing(Piece):
    name = "Shogi King"
    code = "K"
    asset_family = "lishogi"
    asset_name = "KI"

    def legal_moves(self, board: "Board", start: Coord) -> List[Coord]:
        return self.step_moves(board, start, DIAGONAL + ORTHOGONAL)


class ShogiPawn(Piece):
    name = "Fuhyo / Pawn"
    code = "P"
    asset_family = "lishogi"
    asset_name = "FU"

    def legal_moves(self, board: "Board", start: Coord) -> List[Coord]:
        if self.promoted:
            return GoldGeneral(self.color, promoted=True).legal_moves(board, start)
        return self.step_moves(board, start, ((0, self.direction),))

    def can_promote_at(self, coord: Coord) -> bool:
        return in_promotion_zone(self.color, coord)


class GoldGeneral(Piece):
    name = "Gold General"
    code = "G"
    asset_family = "lishogi"
    asset_name = "KI"

    def legal_moves(self, board: "Board", start: Coord) -> List[Coord]:
        forward = self.direction
        deltas = ((0, forward), (1, forward), (-1, forward), (1, 0), (-1, 0), (0, -forward))
        return self.step_moves(board, start, deltas)


class SilverGeneral(Piece):
    name = "Silver General"
    code = "V"
    asset_family = "lishogi"
    asset_name = "GI"

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
    asset_family = "lishogi"
    asset_name = "HI"

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
    asset_family = "lishogi"
    asset_name = "KA"

    def legal_moves(self, board: "Board", start: Coord) -> List[Coord]:
        moves = super().legal_moves(board, start)
        if self.promoted:
            moves.extend(coord for coord in self.step_moves(board, start, ORTHOGONAL) if coord not in moves)
        return moves

    def can_promote_at(self, coord: Coord) -> bool:
        return in_promotion_zone(self.color, coord)


class ShogiLance(Piece):
    name = "Shogi Lance"
    code = "L"
    asset_family = "lishogi"
    asset_name = "KY"

    def legal_moves(self, board: "Board", start: Coord) -> List[Coord]:
        if self.promoted:
            return GoldGeneral(self.color, promoted=True).legal_moves(board, start)
        return self.sliding_moves(board, start, ((0, self.direction),))

    def can_promote_at(self, coord: Coord) -> bool:
        return in_promotion_zone(self.color, coord)


class ShogiKnight(Piece):
    name = "Shogi Knight"
    code = "J"
    asset_family = "lishogi"
    asset_name = "KE"

    def legal_moves(self, board: "Board", start: Coord) -> List[Coord]:
        if self.promoted:
            return GoldGeneral(self.color, promoted=True).legal_moves(board, start)
        forward = self.direction
        return self.step_moves(board, start, ((1, 2 * forward), (-1, 2 * forward)))

    def can_promote_at(self, coord: Coord) -> bool:
        return in_promotion_zone(self.color, coord)


from chess_arena_10x10.core.board import Board  # noqa: E402
