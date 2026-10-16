"""Piece implementations for the 9x9 arena."""

from chess_arena_10x10.pieces.shogi import (
    GoldGeneral,
    ShogiBishop,
    ShogiKing,
    ShogiKnight,
    ShogiLance,
    ShogiPawn,
    ShogiRook,
    SilverGeneral,
)
from chess_arena_10x10.pieces.standard import Bishop, King, Knight, Pawn, Queen, Rook
from chess_arena_10x10.pieces.xiangqi import (
    Cannon,
    PalaceKing,
    Servant,
    XiangqiElephant,
    XiangqiKnight,
    XiangqiSoldier,
)

__all__ = [
    "Bishop",
    "Cannon",
    "GoldGeneral",
    "King",
    "Knight",
    "PalaceKing",
    "Pawn",
    "Queen",
    "Rook",
    "Servant",
    "ShogiBishop",
    "ShogiKing",
    "ShogiKnight",
    "ShogiLance",
    "ShogiPawn",
    "ShogiRook",
    "SilverGeneral",
    "XiangqiElephant",
    "XiangqiKnight",
    "XiangqiSoldier",
]
