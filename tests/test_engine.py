import pytest

from chess_arena_10x10.bots.random_bot import RandomBot
from chess_arena_10x10.core.board import Move
from chess_arena_10x10.core.engine import GameEngine, discover_bots
from chess_arena_10x10.pieces.standard import Pawn, Rook
from chess_arena_10x10.pieces.xiangqi import PalaceKing


def test_engine_switches_turn_after_five_actions():
    engine = GameEngine()
    engine.place_piece(Pawn("white"), (0, 1))
    engine.place_piece(Pawn("white"), (1, 1))
    engine.place_piece(Pawn("white"), (2, 1))
    engine.place_piece(Pawn("white"), (3, 1))
    engine.place_piece(Pawn("white"), (4, 1))
    engine.place_piece(Pawn("black"), (0, 8))
    engine.lock_setup()

    for x in range(5):
        engine.execute_action(Move(from_pos=(x, 1), to_pos=(x, 2)))

    assert engine.active_player == "black"
    assert engine.moves_left_this_turn == 5


def test_piece_can_only_move_once_per_turn():
    engine = GameEngine()
    engine.place_piece(Pawn("white"), (0, 1))
    engine.place_piece(Pawn("white"), (1, 1))
    engine.place_piece(Pawn("black"), (0, 8))
    engine.lock_setup()

    engine.execute_action(Move(from_pos=(0, 1), to_pos=(0, 2)))

    assert Move(from_pos=(0, 2), to_pos=(0, 3)) not in engine.legal_moves("white")
    with pytest.raises(ValueError, match="each piece can only move once"):
        engine.execute_action(Move(from_pos=(0, 2), to_pos=(0, 3)))


def test_pass_consumes_an_action_and_player_starts_first():
    engine = GameEngine()
    engine.place_piece(Pawn("white"), (0, 1))
    engine.place_piece(Pawn("black"), (0, 7))
    engine.lock_setup()

    assert engine.active_player == "white"
    engine.pass_action()
    assert engine.moves_left_this_turn == 4
    for _ in range(4):
        engine.pass_action()
    assert engine.active_player == "black"
    assert engine.moves_left_this_turn == 5


def test_drop_consumes_an_action_and_piece_cannot_move_again():
    engine = GameEngine()
    engine.place_piece(Pawn("white"), (0, 1))
    engine.place_piece(Pawn("black"), (0, 7))
    engine.lock_setup()
    dropped = Pawn("white")

    engine.execute_drop(dropped, (1, 2))
    assert engine.moves_left_this_turn == 4
    assert Move(from_pos=(1, 2), to_pos=(1, 3)) not in engine.legal_moves("white")


def test_game_ends_when_king_is_captured():
    engine = GameEngine()
    engine.place_piece(Rook("white"), (4, 1))
    engine.place_piece(PalaceKing("black"), (4, 8))
    engine.lock_setup()

    result = engine.execute_action(Move(from_pos=(4, 1), to_pos=(4, 8)))

    assert result.captured == "Palace King"
    assert result.winner == "white"
    assert engine.winner == "white"
    assert engine.phase == "game_over"
    assert engine.legal_moves("white") == []
    assert engine.legal_moves("black") == []

    with pytest.raises(ValueError, match="game is over"):
        engine.execute_action(Move(from_pos=(4, 8), to_pos=(4, 7)))


def test_default_position_has_legal_random_bot_move():
    engine = GameEngine()
    engine.setup_default_position()
    move = RandomBot("white").get_move(engine)
    assert move in engine.legal_moves("white")


def test_discovers_random_bot():
    assert "random_bot" in discover_bots()
