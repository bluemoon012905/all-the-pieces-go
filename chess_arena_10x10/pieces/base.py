from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

Coord = Tuple[int, int]
Color = str


@dataclass
class Piece:
    color: Color
    promoted: bool = False

    name = "Piece"
    code = "?"
    must_stay_in_palace = False

    @property
    def direction(self) -> int:
        return 1 if self.color == "white" else -1

    @property
    def symbol(self) -> str:
        symbol = self.code
        if self.promoted:
            symbol = f"+{symbol}"[-1]
        return symbol.upper() if self.color == "white" else symbol.lower()

    def legal_moves(self, board: "Board", start: Coord) -> List[Coord]:
        raise NotImplementedError

    def after_move(self, coord: Coord) -> None:
        if self.can_promote_at(coord):
            self.promoted = True

    def can_promote_at(self, coord: Coord) -> bool:
        return False

    def can_land_on(self, board: "Board", coord: Coord) -> bool:
        if not board.in_bounds(coord):
            return False
        if self.must_stay_in_palace and not board.in_palace(self.color, coord):
            return False
        target = board.get(coord)
        return target is None or target.color != self.color

    def step_moves(self, board: "Board", start: Coord, deltas: Iterable[Coord]) -> List[Coord]:
        sx, sy = start
        moves = []
        for dx, dy in deltas:
            coord = (sx + dx, sy + dy)
            if self.can_land_on(board, coord):
                moves.append(coord)
        return moves

    def sliding_moves(self, board: "Board", start: Coord, deltas: Iterable[Coord]) -> List[Coord]:
        sx, sy = start
        moves = []
        for dx, dy in deltas:
            coord = (sx + dx, sy + dy)
            while board.in_bounds(coord):
                if self.must_stay_in_palace and not board.in_palace(self.color, coord):
                    break
                target = board.get(coord)
                if target is None:
                    moves.append(coord)
                else:
                    if target.color != self.color:
                        moves.append(coord)
                    break
                coord = (coord[0] + dx, coord[1] + dy)
        return moves


ORTHOGONAL = ((1, 0), (-1, 0), (0, 1), (0, -1))
DIAGONAL = ((1, 1), (1, -1), (-1, 1), (-1, -1))
KING_STEPS = ORTHOGONAL + DIAGONAL


from chess_arena_10x10.core.board import Board  # noqa: E402

