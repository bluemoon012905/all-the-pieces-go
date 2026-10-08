from __future__ import annotations

from typing import List, Tuple

from chess_arena_10x10.pieces.base import DIAGONAL, KING_STEPS, ORTHOGONAL, Piece

Coord = Tuple[int, int]


class Pawn(Piece):
    name = "Pawn"
    code = "P"

    def legal_moves(self, board: "Board", start: Coord) -> List[Coord]:
        if self.promoted:
            return Queen(self.color, promoted=True).legal_moves(board, start)

        sx, sy = start
        moves = []
        forward = (sx, sy + self.direction)
        if board.in_bounds(forward) and board.is_empty(forward):
            moves.append(forward)

        for dx in (-1, 1):
            coord = (sx + dx, sy + self.direction)
            target = board.get(coord)
            if board.in_bounds(coord) and target is not None and target.color != self.color:
                moves.append(coord)
        return moves

    def can_promote_at(self, coord: Coord) -> bool:
        return coord[1] == (9 if self.color == "white" else 0)


class Rook(Piece):
    name = "Rook"
    code = "R"

    def legal_moves(self, board: "Board", start: Coord) -> List[Coord]:
        return self.sliding_moves(board, start, ORTHOGONAL)


class Knight(Piece):
    name = "Knight"
    code = "N"

    def legal_moves(self, board: "Board", start: Coord) -> List[Coord]:
        deltas = ((1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2))
        return self.step_moves(board, start, deltas)


class Bishop(Piece):
    name = "Bishop"
    code = "B"

    def legal_moves(self, board: "Board", start: Coord) -> List[Coord]:
        return self.sliding_moves(board, start, DIAGONAL)


class Queen(Piece):
    name = "Queen"
    code = "Q"

    def legal_moves(self, board: "Board", start: Coord) -> List[Coord]:
        return self.sliding_moves(board, start, ORTHOGONAL + DIAGONAL)


class King(Piece):
    name = "King"
    code = "K"

    def legal_moves(self, board: "Board", start: Coord) -> List[Coord]:
        return self.step_moves(board, start, KING_STEPS)


from chess_arena_10x10.core.board import Board  # noqa: E402

