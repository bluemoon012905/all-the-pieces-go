from __future__ import annotations

import importlib
import inspect
import pkgutil
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple, Type, Union

from chess_arena_10x10.bots.base import BaseBot
from chess_arena_10x10.core.board import Board, Move, Palace
from chess_arena_10x10.pieces import (
    Bishop,
    Cannon,
    GoldGeneral,
    PalaceKing,
    Pawn,
    Queen,
    Servant,
    ShogiBishop,
    ShogiKing,
    ShogiKnight,
    ShogiLance,
    ShogiRook,
    SilverGeneral,
    XiangqiElephant,
    XiangqiKnight,
    XiangqiSoldier,
)

Color = str


@dataclass
class ActionResult:
    move: Optional[Move]
    piece: str
    captured: Optional[str]
    active_player: Color
    moves_left_this_turn: int
    winner: Optional[Color] = None
    action_type: str = "move"


@dataclass(frozen=True)
class PassAction:
    """Spend one action without moving or deploying a piece."""


@dataclass(frozen=True)
class DropAction:
    """Deploy a purchased piece as one action."""

    piece: "Piece"
    to_pos: Tuple[int, int]


BotAction = Union[Move, PassAction, DropAction]


class GameEngine:
    """Game loop for setup and five-action battle turns."""

    def __init__(self) -> None:
        self.board = Board()
        self.phase = "setup"
        self.active_player: Color = "white"
        self.moves_left_this_turn = 5
        self.turn_number = 1
        self.winner: Optional[Color] = None
        self._moved_piece_ids_this_turn: Set[int] = set()

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
        self.winner = None
        self._moved_piece_ids_this_turn.clear()

    def setup_default_position(self) -> None:
        back_rank = [
            ShogiLance,
            XiangqiKnight,
            XiangqiElephant,
            Queen,
            PalaceKing,
            Servant,
            GoldGeneral,
            SilverGeneral,
            ShogiRook,
        ]
        for x, cls in enumerate(back_rank):
            self.place_piece(cls("white"), (x, 0))
            self.place_piece(cls("black"), (x, 8))
        for x in range(self.board.width):
            if x in (0, self.board.width - 1):
                piece_cls = XiangqiSoldier
            elif x in (1, self.board.width - 2):
                piece_cls = ShogiKnight
            elif x in (2, self.board.width - 3):
                piece_cls = ShogiBishop
            else:
                piece_cls = Pawn
            self.place_piece(piece_cls("white"), (x, 1))
            self.place_piece(piece_cls("black"), (x, 7))
        self.lock_setup()

    def legal_moves(self, color: Optional[Color] = None) -> List[Move]:
        if self.phase == "game_over":
            return []
        selected_color = color or self.active_player
        if self.phase != "battle" or selected_color != self.active_player:
            return self.board.legal_moves_for_color(selected_color)

        moves: List[Move] = []
        for coord, piece in self.board.pieces_for(selected_color):
            if id(piece) in self._moved_piece_ids_this_turn:
                continue
            for to_pos in piece.legal_moves(self.board, coord):
                moves.append(Move(from_pos=coord, to_pos=to_pos))
        return moves

    def execute_action(self, move: Move) -> ActionResult:
        if self.phase == "game_over":
            raise ValueError("game is over")
        if self.phase != "battle":
            raise ValueError("setup must be locked before actions can be executed")
        piece = self.board.get(move.from_pos)
        if piece is None:
            raise ValueError(f"no piece at {move.from_pos}")
        if piece.color != self.active_player:
            raise ValueError(f"it is {self.active_player}'s turn")
        if id(piece) in self._moved_piece_ids_this_turn:
            raise ValueError("each piece can only move once per turn")
        if move.to_pos not in piece.legal_moves(self.board, move.from_pos):
            raise ValueError(f"illegal move: {move.from_pos} -> {move.to_pos}")

        moving_piece_name = piece.name
        moving_piece_id = id(piece)
        captured_piece = self.board.get(move.to_pos)
        captured_name = captured_piece.name if captured_piece else None
        self.board.move_piece(move)
        self._moved_piece_ids_this_turn.add(moving_piece_id)
        self.moves_left_this_turn -= 1

        if captured_piece is not None and self._is_king(captured_piece):
            self.phase = "game_over"
            self.winner = piece.color
            self.moves_left_this_turn = 0
        elif self.moves_left_this_turn == 0:
            self._switch_turn()

        return ActionResult(
            move=move,
            piece=moving_piece_name,
            captured=captured_name,
            active_player=self.active_player,
            moves_left_this_turn=self.moves_left_this_turn,
            winner=self.winner,
        )

    def execute_drop(self, piece: "Piece", coord: Tuple[int, int]) -> ActionResult:
        """Deploy a piece for the active player and spend one action."""

        self._require_battle_action()
        if piece.color != self.active_player:
            raise ValueError(f"it is {self.active_player}'s turn")
        if not self.board.in_bounds(coord):
            raise ValueError(f"{coord} is outside the board")
        if not self.board.is_empty(coord):
            raise ValueError(f"{coord} is already occupied")
        if piece.must_stay_in_palace and not self.board.in_palace(piece.color, coord):
            raise ValueError(f"{piece.name} must be placed in {piece.color}'s palace")

        self.board.place_piece(piece, coord)
        self._moved_piece_ids_this_turn.add(id(piece))
        return self._consume_action(piece.name, None, action_type="drop")

    def pass_action(self) -> ActionResult:
        """Spend one action while leaving the board unchanged."""

        self._require_battle_action()
        return self._consume_action("Pass", None, action_type="pass")

    def _require_battle_action(self) -> None:
        if self.phase == "game_over":
            raise ValueError("game is over")
        if self.phase != "battle":
            raise ValueError("setup must be locked before actions can be executed")

    def _consume_action(
        self,
        piece: str,
        captured: Optional[str],
        action_type: str = "move",
    ) -> ActionResult:
        self.moves_left_this_turn -= 1
        if self.moves_left_this_turn == 0 and self.phase != "game_over":
            self._switch_turn()
        return ActionResult(
            move=None,
            piece=piece,
            captured=captured,
            active_player=self.active_player,
            moves_left_this_turn=self.moves_left_this_turn,
            winner=self.winner,
            action_type=action_type,
        )

    def _is_king(self, piece: "Piece") -> bool:
        return piece.name in {"King", "Palace King", "Shogi King"}

    def _switch_turn(self) -> None:
        self.active_player = "black" if self.active_player == "white" else "white"
        self.moves_left_this_turn = 5
        self._moved_piece_ids_this_turn.clear()
        if self.active_player == "white":
            self.turn_number += 1

    def run_bot_action(self, bot: BaseBot) -> ActionResult:
        try:
            action = bot.get_action(self)
        except RuntimeError as exc:
            if "no legal moves" not in str(exc):
                raise
            return self.pass_action()
        if isinstance(action, DropAction):
            return self.execute_drop(action.piece, action.to_pos)
        if isinstance(action, PassAction):
            return self.pass_action()
        if not isinstance(action, Move):
            action = Move.parse_obj(action)
        return self.execute_action(action)


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
