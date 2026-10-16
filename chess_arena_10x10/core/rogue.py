"""Rogue Run characters, shops, rewards, and run-level state.

The board engine owns action legality. This module owns the economy and the
player's faction-specific starting rules described in ``character design``.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Type

from chess_arena_10x10.core.engine import GameEngine
from chess_arena_10x10.pieces import (
    Bishop,
    Cannon,
    GoldGeneral,
    King,
    Knight,
    PalaceKing,
    Pawn,
    Queen,
    Rook,
    Servant,
    ShogiBishop,
    ShogiKing,
    ShogiKnight,
    ShogiLance,
    ShogiRook,
    ShogiPawn,
    SilverGeneral,
    XiangqiElephant,
    XiangqiKnight,
    XiangqiSoldier,
)
from chess_arena_10x10.pieces.base import Piece


@dataclass(frozen=True)
class ShopPiece:
    key: str
    name: str
    cost: int
    piece_class: Type[Piece]


@dataclass(frozen=True)
class CharacterDefinition:
    key: str
    name: str
    starting_material: int
    starting_piece_classes: tuple[Type[Piece], ...]
    shop: tuple[ShopPiece, ...]
    ability: str


CHESS_SHOP = (
    ShopPiece("pawn", "Pawn", 10, Pawn),
    ShopPiece("knight", "Knight", 30, Knight),
    ShopPiece("bishop", "Bishop", 33, Bishop),
    ShopPiece("rook", "Rook", 5, Rook),
    ShopPiece("queen", "Queen", 9, Queen),
)

XIANGQI_SHOP = (
    ShopPiece("pawn", "Soldier", 10, XiangqiSoldier),
    ShopPiece("advisor", "Advisor", 15, Servant),
    ShopPiece("elephant", "Elephant", 18, XiangqiElephant),
    ShopPiece("horse", "Horse", 26, XiangqiKnight),
    ShopPiece("cannon", "Cannon", 40, Cannon),
    ShopPiece("rook", "Rook", 50, Rook),
)

SHOGI_SHOP = (
    ShopPiece("pawn", "Pawn", 10, ShogiPawn),
    ShopPiece("lance", "Lance", 22, ShogiLance),
    ShopPiece("shogi_knight", "Shogi Knight", 24, ShogiKnight),
    ShopPiece("silver", "Silver General", 32, SilverGeneral),
    ShopPiece("gold", "Gold General", 34, GoldGeneral),
    ShopPiece("kaku", "Kaku / Bishop", 55, ShogiBishop),
    ShopPiece("hisha", "Hisha / Rook", 65, ShogiRook),
)

CHARACTERS: Dict[str, CharacterDefinition] = {
    "chess": CharacterDefinition(
        "chess", "Chess", 250, (King,), CHESS_SHOP,
        "No special ability.",
    ),
    "shogi": CharacterDefinition(
        "shogi", "Shogi", 200, (ShogiKing,), SHOGI_SHOP,
        "When this character captures, gain half the captured piece's shop cost.",
    ),
    "xiangqi": CharacterDefinition(
        "xiangqi", "Xiangqi", 200, (PalaceKing, Servant, Servant), XIANGQI_SHOP,
        "No special ability.",
    ),
}


@dataclass(frozen=True)
class RewardOffer:
    kind: str
    material: int
    choices: tuple[str, ...]


@dataclass
class RogueRunState:
    """Economy and player state for one Rogue Run."""

    character: CharacterDefinition
    engine: GameEngine
    material: int
    shop_keys: List[str]
    reserve: List[Piece] = field(default_factory=list)
    bank: List[Piece] = field(default_factory=list)
    wave_number: int = 1
    pending_reward: Optional[RewardOffer] = None

    @classmethod
    def new(cls, character_key: str) -> "RogueRunState":
        character = get_character(character_key)
        engine = GameEngine()
        for index, piece_class in enumerate(character.starting_piece_classes):
            x = 4 if piece_class not in (Servant,) else (3 if index == 1 else 5)
            engine.place_piece(piece_class("white"), (x, 0))
        engine.lock_setup()
        return cls(
            character=character,
            engine=engine,
            material=character.starting_material,
            shop_keys=[item.key for item in character.shop],
        )

    def shop_items(self) -> List[ShopPiece]:
        by_key = {item.key: item for item in self.character.shop}
        return [by_key[key] for key in self.shop_keys if key in by_key]

    def buy(self, piece_key: str) -> Piece:
        item = next((item for item in self.shop_items() if item.key == piece_key), None)
        if item is None:
            raise ValueError(f"{piece_key!r} is not available in the shop")
        if self.material < item.cost:
            raise ValueError("not enough material")
        self.material -= item.cost
        piece = item.piece_class("white")
        self.reserve.append(piece)
        return piece

    def drop(self, piece: Piece, coord: tuple[int, int]):
        if piece not in self.reserve:
            raise ValueError("piece is not in the reserve")
        result = self.engine.execute_drop(piece, coord)
        self.reserve.remove(piece)
        return result

    def drop_from_bank(self, bank_index: int, coord: tuple[int, int]):
        try:
            piece = self.bank[bank_index]
        except IndexError as exc:
            raise ValueError("bank piece does not exist") from exc
        result = self.engine.execute_drop(piece, coord)
        self.bank.pop(bank_index)
        return result

    def execute_action(self, move):
        """Execute a player move and apply any character-specific bonus."""

        captured_piece = self.engine.board.get(move.to_pos)
        result = self.engine.execute_action(move)
        if result.captured:
            if captured_piece is not None:
                captured_piece.color = "white"
                self.bank.append(captured_piece)
            self.capture_material(result.captured)
        return result

    def start_wave(self, enemies) -> None:
        """Keep the player's formation and install a fresh enemy formation."""

        for coord, piece in list(self.engine.board.grid.items()):
            if piece.color == "black":
                self.engine.board.remove_piece(coord)
        for piece, coord in enemies:
            self.engine.board.place_piece(piece, coord)
        self.engine.phase = "battle"
        self.engine.active_player = "white"
        self.engine.moves_left_this_turn = 5
        self.engine.winner = None
        self.engine._moved_piece_ids_this_turn.clear()

    def capture_material(self, captured_name: str) -> int:
        """Apply Shogi's half-value capture bonus and return the amount gained."""

        if self.character.key != "shogi":
            return 0
        all_items = [item for character in CHARACTERS.values() for item in character.shop]
        aliases = {
            "Pawn": {"Pawn", "Fuhyo / Pawn"},
            "Fuhyo / Pawn": {"Pawn", "Fuhyo / Pawn"},
            "Soldier": {"Soldier", "Xiangqi Soldier"},
            "Xiangqi Soldier": {"Soldier", "Xiangqi Soldier"},
        }
        names = aliases.get(captured_name, {captured_name})
        item = next((item for item in all_items if item.name in names), None)
        if item is None:
            return 0
        gained = item.cost // 2
        self.material += gained
        return gained

    def offer_reward(self, kind: str, rng: Optional[random.Random] = None) -> RewardOffer:
        if kind not in {"major", "minor"}:
            raise ValueError("reward kind must be 'major' or 'minor'")
        picker = rng or random
        choices = tuple(item.key for item in picker.sample(self.character.shop, min(3, len(self.character.shop))))
        self.pending_reward = RewardOffer(kind, 200 if kind == "major" else 60, choices)
        return self.pending_reward

    def choose_reward(self, piece_key: str) -> RewardOffer:
        if self.pending_reward is None:
            raise ValueError("there is no pending reward")
        if piece_key not in self.pending_reward.choices:
            raise ValueError("piece is not one of the offered rewards")
        reward = self.pending_reward
        self.material += reward.material
        if reward.kind == "major" and piece_key not in self.shop_keys:
            self.shop_keys.append(piece_key)
        self.pending_reward = None
        self.wave_number += 1
        return reward


def get_character(key: str) -> CharacterDefinition:
    try:
        return CHARACTERS[key]
    except KeyError as exc:
        raise ValueError(f"unknown Rogue character: {key}") from exc

