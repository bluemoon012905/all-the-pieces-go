import pytest

from chess_arena_10x10.core.modes import (
    MODE_DEFINITIONS,
    GameMode,
    PvPVariant,
    create_mode_engine,
    get_mode_definition,
)
from chess_arena_10x10.web.server import ArenaSession
from chess_arena_10x10.pieces.catalog import CATALOG


def test_registry_contains_three_top_level_modes():
    assert [definition.key for definition in MODE_DEFINITIONS] == [
        GameMode.PVP,
        GameMode.BOT_MAKER,
        GameMode.ROGUE,
    ]


def test_pvp_exposes_sandbox_variant():
    definition = get_mode_definition(GameMode.PVP)
    assert PvPVariant.SANDBOX.value in definition.variants


@pytest.mark.parametrize("mode", list(GameMode))
def test_every_mode_has_a_board_backed_engine(mode):
    engine = create_mode_engine(mode)
    assert engine.phase == "battle"
    assert len(engine.board.grid) == 36


def test_invalid_variant_is_rejected():
    with pytest.raises(ValueError, match="not a valid variant"):
        create_mode_engine(GameMode.PVP, "rogue")


def test_web_session_switches_modes_without_losing_board_surface():
    session = ArenaSession()
    state = session.set_mode(GameMode.PVP, PvPVariant.SANDBOX.value)

    assert state["mode"] == "pvp"
    assert state["variant"] == "sandbox"
    assert len(state["pieces"]) == 36

    state = session.set_mode(GameMode.ROGUE)
    assert state["modeStatus"] == "scaffold"
    assert len(state["pieces"]) == 36


def test_piece_catalog_has_previewable_records():
    assert len(CATALOG) == 21
    assert {piece.game for piece in CATALOG} == {"Chess", "Xiangqi", "Shogi"}
    assert all(piece.name and piece.game and piece.movement and piece.preview for piece in CATALOG)
