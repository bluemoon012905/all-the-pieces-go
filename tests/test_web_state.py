from chess_arena_10x10.pieces.shogi import ShogiBishop, ShogiKnight, ShogiLance, ShogiRook, SilverGeneral
from chess_arena_10x10.pieces.standard import Pawn
from chess_arena_10x10.web.server import ArenaSession


def test_promoted_assets_use_promoted_visual_names():
    assert ArenaSession._visual_asset_name(Pawn("white", promoted=True)) == "Q"
    assert ArenaSession._visual_asset_name(SilverGeneral("white", promoted=True)) == "NG"
    assert ArenaSession._visual_asset_name(ShogiLance("white", promoted=True)) == "NY"
    assert ArenaSession._visual_asset_name(ShogiKnight("white", promoted=True)) == "NK"
    assert ArenaSession._visual_asset_name(ShogiRook("white", promoted=True)) == "RY"
    assert ArenaSession._visual_asset_name(ShogiBishop("white", promoted=True)) == "UM"
