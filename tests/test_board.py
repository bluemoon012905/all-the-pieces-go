import pytest

from chess_arena_10x10.core.board import Board, Move
from chess_arena_10x10.pieces.standard import Pawn, Rook
from chess_arena_10x10.pieces.xiangqi import (
    Cannon,
    PalaceKing,
    XiangqiElephant,
    XiangqiKnight,
    XiangqiSoldier,
)


def test_board_places_only_inside_setup_zone():
    board = Board()
    board.place_piece(Pawn("white"), (0, 1), setup=True)
    with pytest.raises(ValueError):
        board.place_piece(Pawn("white"), (0, 2), setup=True)


def test_rook_cannot_jump_over_piece():
    board = Board()
    board.place_piece(Rook("white"), (0, 0))
    board.place_piece(Pawn("white"), (0, 2))
    assert (0, 3) not in board.get((0, 0)).legal_moves(board, (0, 0))


def test_cannon_requires_one_screen_to_capture():
    board = Board()
    cannon = Cannon("white")
    board.place_piece(cannon, (0, 0))
    board.place_piece(Pawn("white"), (0, 2))
    board.place_piece(Pawn("black"), (0, 5))
    assert (0, 5) in cannon.legal_moves(board, (0, 0))
    assert (0, 2) not in cannon.legal_moves(board, (0, 0))


def test_xiangqi_knight_is_blocked_by_leg_piece():
    board = Board()
    knight = XiangqiKnight("white")
    board.place_piece(knight, (4, 4))
    board.place_piece(Pawn("white"), (4, 5))
    assert (5, 6) not in knight.legal_moves(board, (4, 4))


def test_palace_piece_cannot_leave_palace():
    board = Board()
    king = PalaceKing("white")
    board.place_piece(king, (4, 2))
    assert (4, 3) not in king.legal_moves(board, (4, 2))


def test_default_palaces_are_three_by_three():
    board = Board()
    assert board.in_palace("white", (3, 0))
    assert board.in_palace("white", (5, 2))
    assert not board.in_palace("white", (6, 2))
    assert board.in_palace("black", (3, 7))
    assert board.in_palace("black", (5, 8))
    assert not board.in_palace("black", (6, 8))


def test_xiangqi_elephant_is_blocked_and_stays_on_own_side():
    board = Board()
    elephant = XiangqiElephant("white")
    board.place_piece(elephant, (2, 2))
    board.place_piece(Pawn("white"), (3, 3))
    moves = elephant.legal_moves(board, (2, 2))
    assert (4, 4) not in moves
    assert (0, 4) in moves
    assert (4, 6) not in moves


def test_xiangqi_soldier_gains_sideways_moves_after_river():
    board = Board()
    soldier = XiangqiSoldier("white")
    board.place_piece(soldier, (4, 5))
    moves = soldier.legal_moves(board, (4, 5))
    assert (4, 6) in moves
    assert (5, 5) in moves
    assert (3, 5) in moves


def test_move_model_accepts_aliases():
    if hasattr(Move, "model_validate"):
        move = Move.model_validate({"from": (1, 1), "to": (1, 2)})
    else:
        move = Move.parse_obj({"from": (1, 1), "to": (1, 2)})
    assert move.from_pos == (1, 1)
    assert move.to_pos == (1, 2)
