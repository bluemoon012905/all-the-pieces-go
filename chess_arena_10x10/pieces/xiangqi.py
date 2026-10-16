from __future__ import annotations

from typing import List, Tuple

from chess_arena_10x10.pieces.base import DIAGONAL, ORTHOGONAL, Piece
from chess_arena_10x10.pieces.standard import King

Coord = Tuple[int, int]


class Cannon(Piece):
    name = "Cannon"
    code = "C"
    asset_family = "xiangqi"
    asset_name = "cannon"

    def legal_moves(self, board: "Board", start: Coord) -> List[Coord]:
        sx, sy = start
        moves = []
        for dx, dy in ORTHOGONAL:
            coord = (sx + dx, sy + dy)
            screens = 0
            while board.in_bounds(coord):
                target = board.get(coord)
                if target is None:
                    if screens == 0:
                        moves.append(coord)
                else:
                    screens += 1
                    if screens == 2:
                        if target.color != self.color:
                            moves.append(coord)
                        break
                coord = (coord[0] + dx, coord[1] + dy)
        return moves


class XiangqiKnight(Piece):
    name = "Xiangqi Knight"
    code = "H"
    asset_family = "xiangqi"
    asset_name = "horse"

    LEGS_AND_DESTS = (
        ((0, 1), (1, 2)),
        ((0, 1), (-1, 2)),
        ((1, 0), (2, 1)),
        ((1, 0), (2, -1)),
        ((0, -1), (1, -2)),
        ((0, -1), (-1, -2)),
        ((-1, 0), (-2, 1)),
        ((-1, 0), (-2, -1)),
    )

    def legal_moves(self, board: "Board", start: Coord) -> List[Coord]:
        sx, sy = start
        moves = []
        for leg, dest in self.LEGS_AND_DESTS:
            leg_coord = (sx + leg[0], sy + leg[1])
            dest_coord = (sx + dest[0], sy + dest[1])
            if board.in_bounds(leg_coord) and board.is_empty(leg_coord) and self.can_land_on(board, dest_coord):
                moves.append(dest_coord)
        return moves


class PalaceKing(King):
    name = "Palace King"
    code = "K"
    asset_family = "xiangqi"
    asset_name = "general"
    must_stay_in_palace = True


class Servant(Piece):
    name = "Servant"
    code = "S"
    asset_family = "xiangqi"
    asset_name = "advisor"
    must_stay_in_palace = True

    def legal_moves(self, board: "Board", start: Coord) -> List[Coord]:
        return self.step_moves(board, start, DIAGONAL)


class XiangqiElephant(Piece):
    name = "Xiangqi Elephant"
    code = "E"
    asset_family = "xiangqi"
    asset_name = "elephant"

    def legal_moves(self, board: "Board", start: Coord) -> List[Coord]:
        sx, sy = start
        moves = []
        for dx, dy in ((2, 2), (2, -2), (-2, 2), (-2, -2)):
            block = (sx + dx // 2, sy + dy // 2)
            dest = (sx + dx, sy + dy)
            if not board.in_bounds(block) or not board.is_empty(block):
                continue
            if not self._stays_on_own_side(dest):
                continue
            if self.can_land_on(board, dest):
                moves.append(dest)
        return moves

    def _stays_on_own_side(self, coord: Coord) -> bool:
        _, y = coord
        return y <= 4 if self.color == "white" else y >= 5


class XiangqiSoldier(Piece):
    name = "Xiangqi Soldier"
    code = "D"
    asset_family = "xiangqi"
    asset_name = "soldier"

    def legal_moves(self, board: "Board", start: Coord) -> List[Coord]:
        sx, sy = start
        deltas = [(0, self.direction)]
        if self._crossed_river(start):
            deltas.extend([(1, 0), (-1, 0)])
        return self.step_moves(board, start, deltas)

    def _crossed_river(self, coord: Coord) -> bool:
        _, y = coord
        return y >= 5 if self.color == "white" else y <= 3


from chess_arena_10x10.core.board import Board  # noqa: E402
