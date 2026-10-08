from __future__ import annotations

import importlib
import inspect
import pkgutil
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Type

from chess_arena_10x10.bots.base import BaseBot
from chess_arena_10x10.core.board import Board, Move, Palace
from chess_arena_10x10.pieces import (
    Bishop,
    Cannon,
    GoldGeneral,
    PalaceKing,
    Pawn,
    Queen,
    Rook,
    Servant,
    ShogiBishop,
    ShogiRook,
    SilverGeneral,
    XiangqiKnight,
)

Color = str


@dataclass
class ActionResult:
    move: Move
    piece: str
    captured: Optional[str]
    active_player: Color
    moves_left_this_turn: int


class GameEngine:
    """Game loop for setup and five-action battle turns."""

    def __init__(self) -> None:
        self.board = Board()
        self.phase = "setup"
        self.active_player: Color = "white"
        self.moves_left_this_turn = 5
        self.turn_number = 1

    def set_palace(self, color: Color, min_x: int, max_x: int, min_y: int, max_y: int) -> None:
        self.board.set_palace(color, Palace(min_x, max_x, min_y, max_y))

    def place_piece(self, piece: "Piece", coord: Tuple[int, int]) -> None:
        if self.phase != "setup":
            raise ValueError("pieces can only be placed during setup")
        self.board.place_piece(piece, coord, setup=True)

    def lock_setup(self) -> None:
        self.phase = "battle"
        self.active_player = "white"
        self.moves_left_this_turn = 5

    def setup_default_position(self) -> None:
        back_rank = [Rook, XiangqiKnight, Bishop, Queen, PalaceKing, Servant, GoldGeneral, SilverGeneral, Cannon, ShogiRook]
        for x, cls in enumerate(back_rank):
            self.place_piece(cls("white"), (x, 0))
            self.place_piece(cls("black"), (x, 9))
        for x in range(10):
            piece_cls = Pawn if x not in (2, 7) else ShogiBishop
            self.place_piece(piece_cls("white"), (x, 1))
            self.place_piece(piece_cls("black"), (x, 8))
        self.lock_setup()

    def legal_moves(self, color: Optional[Color] = None) -> List[Move]:
        return self.board.legal_moves_for_color(color or self.active_player)

    def execute_action(self, move: Move) -> ActionResult:
        if self.phase != "battle":
            raise ValueError("setup must be locked before actions can be executed")
        piece = self.board.get(move.from_pos)
        if piece is None:
            raise ValueError(f"no piece at {move.from_pos}")
        if piece.color != self.active_player:
            raise ValueError(f"it is {self.active_player}'s turn")
        if move.to_pos not in piece.legal_moves(self.board, move.from_pos):
            raise ValueError(f"illegal move: {move.from_pos} -> {move.to_pos}")

        moving_piece_name = piece.name
        captured_piece = self.board.get(move.to_pos)
        captured_name = captured_piece.name if captured_piece else None
        self.board.move_piece(move)
        self.moves_left_this_turn -= 1
        if self.moves_left_this_turn == 0:
            self._switch_turn()

        return ActionResult(
            move=move,
            piece=moving_piece_name,
            captured=captured_name,
            active_player=self.active_player,
            moves_left_this_turn=self.moves_left_this_turn,
        )

    def _switch_turn(self) -> None:
        self.active_player = "black" if self.active_player == "white" else "white"
        self.moves_left_this_turn = 5
        if self.active_player == "white":
            self.turn_number += 1

    def run_bot_action(self, bot: BaseBot) -> ActionResult:
        move = bot.get_move(self)
        if not isinstance(move, Move):
            move = Move.parse_obj(move)
        return self.execute_action(move)


def discover_bots() -> Dict[str, Type[BaseBot]]:
    """Import every bot module and return selectable BaseBot subclasses."""

    import chess_arena_10x10.bots as bots_package

    discovered: Dict[str, Type[BaseBot]] = {}
    for module_info in pkgutil.iter_modules(bots_package.__path__):
        if module_info.name.startswith("_") or module_info.name == "base":
            continue
        module = importlib.import_module(f"{bots_package.__name__}.{module_info.name}")
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if obj is not BaseBot and issubclass(obj, BaseBot):
                discovered[module_info.name] = obj
    return discovered


from chess_arena_10x10.pieces.base import Piece  # noqa: E402

