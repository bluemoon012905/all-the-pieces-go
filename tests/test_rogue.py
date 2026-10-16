from chess_arena_10x10.bots.hunter_bot import HunterBot
from chess_arena_10x10.bots.rusher_bot import RusherBot
from chess_arena_10x10.bots.sentinel_bot import SentinelBot
from chess_arena_10x10.core.engine import GameEngine
from chess_arena_10x10.core.rogue import RogueRunState


def test_rogue_characters_match_design_sheet():
    chess = RogueRunState.new("chess")
    shogi = RogueRunState.new("shogi")
    xiangqi = RogueRunState.new("xiangqi")

    assert chess.material == 250
    assert shogi.material == 200
    assert xiangqi.material == 200
    assert [piece.name for piece in xiangqi.engine.board.grid.values()] == [
        "Palace King", "Servant", "Servant"
    ]


def test_rogue_shop_buy_and_drop():
    run = RogueRunState.new("chess")
    pawn = run.buy("pawn")
    assert run.material == 240
    run.drop(pawn, (0, 2))
    assert run.engine.board.get((0, 2)) is pawn
    assert run.engine.moves_left_this_turn == 4


def test_rogue_bots_produce_legal_actions():
    engine = GameEngine()
    engine.setup_default_position()
    for bot in (RusherBot("white"), HunterBot("white"), SentinelBot("white")):
        move = bot.get_move(engine)
        assert move in engine.legal_moves("white")

