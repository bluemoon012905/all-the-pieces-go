from chess_arena_10x10.bots.random_bot import RandomBot
from chess_arena_10x10.core.board import Move
from chess_arena_10x10.core.engine import GameEngine, discover_bots
from chess_arena_10x10.pieces.standard import Pawn


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


def test_default_position_has_legal_random_bot_move():
    engine = GameEngine()
    engine.setup_default_position()
    move = RandomBot("white").get_move(engine)
    assert move in engine.legal_moves("white")


def test_discovers_random_bot():
    assert "random_bot" in discover_bots()
