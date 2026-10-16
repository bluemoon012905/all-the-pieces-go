from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

Coord = Tuple[int, int]
Color = str
BOARD_SIZE = 9


try:
    from pydantic import BaseModel, Field

    try:
        from pydantic import ConfigDict, field_validator
    except ImportError:
        ConfigDict = None
        field_validator = None
except ModuleNotFoundError:
    BaseModel = None


def _validate_coord(value: Coord) -> Coord:
    x, y = value
    if not (0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE):
        raise ValueError(f"coordinates must be between 0 and {BOARD_SIZE - 1}")
    return value


if BaseModel is not None:

    class Move(BaseModel):
        """A single movement or capture action."""

        if ConfigDict is not None:
            model_config = ConfigDict(populate_by_name=True)

        from_pos: Coord = Field(..., alias="from")
        to_pos: Coord = Field(..., alias="to")

        if field_validator is not None:

            @field_validator("from_pos", "to_pos")
            @classmethod
            def coordinates_are_on_board(cls, value: Coord) -> Coord:
                return _validate_coord(value)

        else:
            from pydantic import validator

            @validator("from_pos", "to_pos")
            def coordinates_are_on_board(cls, value: Coord) -> Coord:
                return _validate_coord(value)

            class Config:
                allow_population_by_field_name = True

else:

    class Move:
        """Fallback Move model used when pydantic is not installed."""

        def __init__(self, from_pos: Coord = None, to_pos: Coord = None, **data) -> None:
            if from_pos is None:
                from_pos = data.get("from")
            if to_pos is None:
                to_pos = data.get("to")
            if from_pos is None or to_pos is None:
                raise ValueError("Move requires from/from_pos and to/to_pos")
            self.from_pos = _validate_coord(tuple(from_pos))
            self.to_pos = _validate_coord(tuple(to_pos))

        @classmethod
        def parse_obj(cls, data) -> "Move":
            if isinstance(data, cls):
                return data
            return cls(**data)

        def __eq__(self, other) -> bool:
            return (
                isinstance(other, Move)
                and self.from_pos == other.from_pos
                and self.to_pos == other.to_pos
            )

        def __repr__(self) -> str:
            return f"Move(from_pos={self.from_pos!r}, to_pos={self.to_pos!r})"

        def dict(self) -> Dict[str, Coord]:
            return {"from_pos": self.from_pos, "to_pos": self.to_pos}


@dataclass(frozen=True)
class Palace:
    min_x: int
    max_x: int
    min_y: int
    max_y: int

    def contains(self, coord: Coord) -> bool:
        x, y = coord
        return self.min_x <= x <= self.max_x and self.min_y <= y <= self.max_y


class Board:
    """9x9 board backed by a coordinate-to-piece dictionary."""

    width = BOARD_SIZE
    height = BOARD_SIZE

    def __init__(self) -> None:
        self.grid: Dict[Coord, "Piece"] = {}
        self.palaces: Dict[Color, Palace] = {
            "white": Palace(3, 5, 0, 2),
            "black": Palace(3, 5, 6, 8),
        }

    def in_bounds(self, coord: Coord) -> bool:
        x, y = coord
        return 0 <= x < self.width and 0 <= y < self.height

    def get(self, coord: Coord) -> Optional["Piece"]:
        return self.grid.get(coord)

    def is_empty(self, coord: Coord) -> bool:
        return self.get(coord) is None

    def place_piece(self, piece: "Piece", coord: Coord, setup: bool = False) -> None:
        if not self.in_bounds(coord):
            raise ValueError(f"{coord} is outside the board")
        if coord in self.grid:
            raise ValueError(f"{coord} is already occupied")
        if setup and not self.is_setup_zone(piece.color, coord):
            raise ValueError(f"{piece.color} cannot set up at {coord}")
        if piece.must_stay_in_palace and not self.in_palace(piece.color, coord):
            raise ValueError(f"{piece.name} must be placed in {piece.color}'s palace")
        self.grid[coord] = piece

    def remove_piece(self, coord: Coord) -> Optional["Piece"]:
        return self.grid.pop(coord, None)

    def move_piece(self, move: Move) -> Optional["Piece"]:
        piece = self.get(move.from_pos)
        if piece is None:
            raise ValueError(f"no piece at {move.from_pos}")
        target = self.get(move.to_pos)
        if target is not None and target.color == piece.color:
            raise ValueError("cannot capture your own piece")
        self.grid.pop(move.from_pos)
        captured = self.grid.pop(move.to_pos, None)
        piece.after_move(move.to_pos)
        self.grid[move.to_pos] = piece
        return captured

    def is_setup_zone(self, color: Color, coord: Coord) -> bool:
        _, y = coord
        if color == "white":
            return y in (0, 1)
        if color == "black":
            return y in (7, 8)
        raise ValueError(f"unknown color {color}")

    def set_palace(self, color: Color, palace: Palace) -> None:
        self.palaces[color] = palace

    def in_palace(self, color: Color, coord: Coord) -> bool:
        palace = self.palaces.get(color)
        return palace.contains(coord) if palace else True

    def path_between(self, start: Coord, end: Coord) -> List[Coord]:
        sx, sy = start
        ex, ey = end
        dx = (ex > sx) - (ex < sx)
        dy = (ey > sy) - (ey < sy)
        if sx != ex and sy != ey and abs(ex - sx) != abs(ey - sy):
            return []

        coords: List[Coord] = []
        current = (sx + dx, sy + dy)
        while current != end:
            coords.append(current)
            current = (current[0] + dx, current[1] + dy)
        return coords

    def clear_path(self, start: Coord, end: Coord) -> bool:
        return all(self.is_empty(coord) for coord in self.path_between(start, end))

    def pieces_for(self, color: Color) -> Iterable[Tuple[Coord, "Piece"]]:
        for coord, piece in self.grid.items():
            if piece.color == color:
                yield coord, piece

    def legal_moves_for_color(self, color: Color) -> List[Move]:
        moves: List[Move] = []
        for coord, piece in self.pieces_for(color):
            for to_pos in piece.legal_moves(self, coord):
                moves.append(Move(from_pos=coord, to_pos=to_pos))
        return moves

    def render_ascii(self) -> str:
        rows = ["   " + " ".join(str(x) for x in range(self.width))]
        for y in range(self.height - 1, -1, -1):
            cells = []
            for x in range(self.width):
                piece = self.get((x, y))
                cells.append(piece.symbol if piece else ".")
            rows.append(f"{y:>2} " + " ".join(cells))
        return "\n".join(rows)

    def snapshot(self) -> Dict[Coord, str]:
        return {coord: piece.code for coord, piece in self.grid.items()}


from chess_arena_10x10.pieces.base import Piece  # noqa: E402
