"""Game-mode definitions and engine factories."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from chess_arena_10x10.core.engine import GameEngine


class GameMode(str, Enum):
    PVP = "pvp"
    BOT_MAKER = "bot_maker"
    ROGUE = "rogue"


class PvPVariant(str, Enum):
    STANDARD = "standard"
    SANDBOX = "sandbox"


@dataclass(frozen=True)
class ModeDefinition:
    key: GameMode
    name: str
    description: str
    status: str
    variants: tuple[str, ...] = ()


MODE_DEFINITIONS = (
    ModeDefinition(
        GameMode.PVP,
        "Player vs Player",
        "Two players share the board and take alternating five-action turns.",
        "active",
        (PvPVariant.STANDARD.value, PvPVariant.SANDBOX.value),
    ),
    ModeDefinition(
        GameMode.BOT_MAKER,
        "Bot Maker",
        "A board-backed workspace for building and testing Python bots.",
        "on_hold",
    ),
    ModeDefinition(
        GameMode.ROGUE,
        "Rogue Run",
        "A single-player run with encounters, upgrades, and persistent progress.",
        "scaffold",
    ),
)


def get_mode_definition(mode: GameMode | str) -> ModeDefinition:
    selected = GameMode(mode)
    return next(definition for definition in MODE_DEFINITIONS if definition.key == selected)


def create_mode_engine(mode: GameMode | str, variant: Optional[str] = None) -> GameEngine:
    """Create the shared board engine for any registered mode."""

    selected = GameMode(mode)
    definition = get_mode_definition(selected)
    if variant is not None and variant not in definition.variants:
        raise ValueError(f"{variant!r} is not a valid variant for {selected.value}")

    engine = GameEngine()
    engine.setup_default_position()
    return engine
