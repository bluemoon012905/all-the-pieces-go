from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional

from chess_arena_10x10.bots.random_bot import RandomBot
from chess_arena_10x10.bots.hunter_bot import HunterBot
from chess_arena_10x10.bots.rusher_bot import RusherBot
from chess_arena_10x10.bots.sentinel_bot import SentinelBot
from chess_arena_10x10.core.engine import GameEngine
from chess_arena_10x10.core.board import Move
from chess_arena_10x10.core.modes import (
    MODE_DEFINITIONS,
    GameMode,
    PvPVariant,
    create_mode_engine,
    get_mode_definition,
)
from chess_arena_10x10.core.rogue import RogueRunState, get_character
from chess_arena_10x10.pieces import (
    Bishop,
    Cannon,
    King,
    Pawn,
    Rook,
    Servant,
    ShogiBishop,
    ShogiLance,
    SilverGeneral,
    XiangqiSoldier,
)
from chess_arena_10x10.pieces.catalog import catalog_as_dicts

STATIC_DIR = Path(__file__).with_name("static")


class ArenaSession:
    def __init__(self, mode: GameMode | str = GameMode.PVP, variant: str | None = None) -> None:
        self.mode = GameMode(mode)
        self.variant = variant or self._default_variant(self.mode)
        self.engine = self._new_engine()
        self.bots = {
            "white": RandomBot("white"),
            "black": RandomBot("black"),
        }
        self.action_count = 0
        self.last_action: Optional[Dict[str, Any]] = None

    def reset(self) -> Dict[str, Any]:
        self.engine = self._new_engine()
        self.action_count = 0
        self.last_action = None
        return self.state()

    def set_mode(self, mode: GameMode | str, variant: str | None = None) -> Dict[str, Any]:
        self.mode = GameMode(mode)
        self.variant = variant or self._default_variant(self.mode)
        get_mode_definition(self.mode)
        return self.reset()

    def step(self) -> Dict[str, Any]:
        if self.mode != GameMode.BOT_MAKER:
            raise RuntimeError(f"{self.mode.value} does not have bot stepping enabled")
        if self.engine.phase == "game_over":
            return self.state()
        bot = self.bots[self.engine.active_player]
        result = self.engine.run_bot_action(bot)
        self.action_count += 1
        self.last_action = {
            "number": self.action_count,
            "piece": result.piece,
            "from": result.move.from_pos if result.move else None,
            "to": result.move.to_pos if result.move else None,
            "captured": result.captured,
            "winner": result.winner,
            "actionType": result.action_type,
        }
        return self.state()

    def state(self) -> Dict[str, Any]:
        pieces = []
        for (x, y), piece in sorted(self.engine.board.grid.items()):
            pieces.append(
                {
                    "x": x,
                    "y": y,
                    "code": piece.code,
                    "symbol": piece.symbol,
                    "name": piece.name,
                    "color": piece.color,
                    "promoted": piece.promoted,
                    "assetFamily": piece.asset_family,
                    "assetName": self._visual_asset_name(piece),
                }
            )
        return {
            "mode": self.mode.value,
            "modeName": get_mode_definition(self.mode).name,
            "modeStatus": get_mode_definition(self.mode).status,
            "variant": self.variant,
            "phase": self.engine.phase,
            "activePlayer": self.engine.active_player,
            "movesLeft": self.engine.moves_left_this_turn,
            "turn": self.engine.turn_number,
            "winner": self.engine.winner,
            "actionCount": self.action_count,
            "lastAction": self.last_action,
            "pieces": pieces,
        }

    @staticmethod
    def _visual_asset_name(piece) -> str:
        if not piece.promoted:
            return piece.asset_name
        if piece.asset_family == "lichess" and piece.code == "P":
            return "Q"
        if piece.asset_family == "lishogi":
            return {
                "GI": "NG",
                "KY": "NY",
                "KE": "NK",
                "HI": "RY",
                "KA": "UM",
            }.get(piece.asset_name, piece.asset_name)
        return piece.asset_name

    def _new_engine(self) -> GameEngine:
        return create_mode_engine(self.mode, self.variant)

    @staticmethod
    def _default_variant(mode: GameMode) -> str | None:
        if mode == GameMode.PVP:
            return PvPVariant.STANDARD.value
        return None


SESSION = ArenaSession()


ROGUE_WAVES = (
    {
        "name": "Scout Line", "kind": "minor", "reward": "minor", "bot": RusherBot,
        "pieces": [(Pawn, (2, 7)), (Pawn, (3, 7)), (Pawn, (4, 7)), (Pawn, (5, 7))],
    },
    {
        "name": "Horse Ambush", "kind": "minor", "reward": "minor", "bot": HunterBot,
        "pieces": [(Pawn, (2, 7)), (Pawn, (6, 7)), (Rook, (3, 8)), (Rook, (5, 8))],
    },
    {
        "name": "Cannon Test", "kind": "minor", "reward": "minor", "bot": SentinelBot,
        "pieces": [(XiangqiSoldier, (2, 7)), (XiangqiSoldier, (4, 7)), (XiangqiSoldier, (6, 7)), (Cannon, (4, 8))],
    },
    {
        "name": "Shogi Screen", "kind": "minor", "reward": "minor", "bot": RusherBot,
        "pieces": [(Pawn, (3, 7)), (Pawn, (5, 7)), (ShogiLance, (2, 8)), (SilverGeneral, (6, 8))],
    },
    {
        "name": "The Captain", "kind": "major", "reward": "major", "bot": HunterBot,
        "pieces": [(King, (4, 8)), (Rook, (3, 8)), (Bishop, (5, 8)), (Pawn, (2, 7)), (Pawn, (6, 7))],
    },
)


class RogueSession:
    """Small server-backed playable Rogue loop for the first vertical slice."""

    def __init__(self) -> None:
        self.run: Optional[RogueRunState] = None
        self.wave_index = 0
        self.wave_complete = False
        self.last_actions = []
        self.action_frames = []

    def choose_character(self, character_key: str) -> Dict[str, Any]:
        self.run = RogueRunState.new(character_key)
        self.wave_index = 0
        self.wave_complete = False
        self.last_actions = []
        self.action_frames = []
        self._load_wave()
        return self.state()

    def reset(self) -> Dict[str, Any]:
        self.run = None
        self.wave_index = 0
        self.wave_complete = False
        self.last_actions = []
        self.action_frames = []
        return self.state()

    def _load_wave(self) -> None:
        wave = ROGUE_WAVES[self.wave_index]
        enemies = [(piece_class("black"), coord) for piece_class, coord in wave["pieces"]]
        self.run.start_wave(enemies)

    def _current_wave(self) -> Dict[str, Any]:
        return ROGUE_WAVES[self.wave_index]

    def _run_enemy_turn(self) -> None:
        wave = self._current_wave()
        bot = wave["bot"]("black")
        while self.run.engine.active_player == "black" and self.run.engine.phase != "game_over":
            result = self.run.engine.run_bot_action(bot)
            self.last_actions.append(self._action_dict(result))
            self.action_frames.append({"action": self._action_dict(result), "pieces": self._piece_snapshot()})

    def player_action(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._require_run()
        if self.wave_complete:
            raise ValueError("choose a reward before taking another action")
        self.action_frames = [{"action": {"actionType": "before"}, "pieces": self._piece_snapshot()}]
        action_type = payload.get("action", "move")
        if action_type == "pass":
            result = self.run.engine.pass_action()
        elif action_type == "drop":
            raise ValueError("use the buy-and-drop action for reserve pieces")
        else:
            move = Move(from_pos=tuple(payload["from"]), to_pos=tuple(payload["to"]))
            result = self.run.execute_action(move)
        self.last_actions = [self._action_dict(result)]
        self.action_frames.append({"action": self._action_dict(result), "pieces": self._piece_snapshot()})
        if self.run.engine.active_player == "black" and self.run.engine.phase != "game_over":
            self._run_enemy_turn()
        self._check_wave_complete()
        return self.state()

    def buy_and_drop(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._require_run()
        if self.wave_complete:
            raise ValueError("choose a reward before buying")
        self.action_frames = [{"action": {"actionType": "before"}, "pieces": self._piece_snapshot()}]
        piece = self.run.buy(payload["piece"])
        try:
            result = self.run.drop(piece, tuple(payload["to"]))
        except Exception:
            self.run.reserve.remove(piece)
            item = next(item for item in self.run.shop_items() if item.key == payload["piece"])
            self.run.material += item.cost
            raise
        self.last_actions = [self._action_dict(result)]
        self.action_frames.append({"action": self._action_dict(result), "pieces": self._piece_snapshot()})
        if self.run.engine.active_player == "black":
            self._run_enemy_turn()
        self._check_wave_complete()
        return self.state()

    def bank_drop(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self._require_run()
        if self.wave_complete:
            raise ValueError("choose a reward before deploying a banked piece")
        self.action_frames = [{"action": {"actionType": "before"}, "pieces": self._piece_snapshot()}]
        result = self.run.drop_from_bank(int(payload["bankIndex"]), tuple(payload["to"]))
        self.last_actions = [self._action_dict(result)]
        self.action_frames.append({"action": self._action_dict(result), "pieces": self._piece_snapshot()})
        if self.run.engine.active_player == "black":
            self._run_enemy_turn()
        self._check_wave_complete()
        return self.state()

    def choose_reward(self, piece_key: str) -> Dict[str, Any]:
        self._require_run()
        if self.run.pending_reward is None:
            raise ValueError("there is no reward to choose")
        self.run.choose_reward(piece_key)
        self.action_frames = []
        if self.wave_index + 1 < len(ROGUE_WAVES):
            self.wave_index += 1
            self.wave_complete = False
            self._load_wave()
        else:
            self.wave_complete = False
            self.run.engine.phase = "victory"
        return self.state()

    def _check_wave_complete(self) -> None:
        if self.run.engine.phase == "game_over" and self.run.engine.winner != "white":
            return
        if not any(piece.color == "black" for piece in self.run.engine.board.grid.values()):
            self.wave_complete = True
            self.run.offer_reward(self._current_wave()["reward"])

    def _require_run(self) -> None:
        if self.run is None:
            raise ValueError("choose a character first")

    @staticmethod
    def _action_dict(result) -> Dict[str, Any]:
        return {
            "piece": result.piece,
            "from": result.move.from_pos if result.move else None,
            "to": result.move.to_pos if result.move else None,
            "captured": result.captured,
            "actionType": result.action_type,
        }

    def _piece_snapshot(self) -> list[Dict[str, Any]]:
        return [
            {
                "x": x, "y": y, "name": piece.name, "color": piece.color,
                "code": piece.code, "symbol": piece.symbol, "promoted": piece.promoted,
                "assetFamily": piece.asset_family, "assetName": ArenaSession._visual_asset_name(piece),
            }
            for (x, y), piece in sorted(self.run.engine.board.grid.items())
        ]

    def state(self) -> Dict[str, Any]:
        if self.run is None:
            return {"phase": "character_select", "characters": [
                {"key": key, "name": character.name, "material": character.starting_material, "ability": character.ability}
                for key, character in ((key, get_character(key)) for key in ("chess", "shogi", "xiangqi"))
            ]}
        pieces = self._piece_snapshot()
        wave = self._current_wave()
        reward = self.run.pending_reward
        movable = []
        if self.run.engine.active_player == "white" and self.run.engine.phase == "battle":
            movable = [list(move.from_pos) for move in self.run.engine.legal_moves("white")]
            movable = [list(coord) for coord in sorted({tuple(coord) for coord in movable})]
        return {
            "phase": self.run.engine.phase,
            "character": {"key": self.run.character.key, "name": self.run.character.name, "ability": self.run.character.ability},
            "material": self.run.material,
            "reserve": [{"name": piece.name, "code": piece.code, "assetFamily": piece.asset_family, "assetName": piece.asset_name} for piece in self.run.reserve],
            "bank": [{"index": index, "name": piece.name, "code": piece.code, "assetFamily": piece.asset_family, "assetName": piece.asset_name} for index, piece in enumerate(self.run.bank)],
            "wave": {"number": self.wave_index + 1, "total": len(ROGUE_WAVES), "name": wave["name"], "kind": wave["kind"]},
            "activePlayer": self.run.engine.active_player,
            "movesLeft": self.run.engine.moves_left_this_turn,
            "turn": self.run.engine.turn_number,
            "pieces": pieces,
            "movablePieces": movable,
            "lastActions": self.last_actions[-10:],
            "actionFrames": self.action_frames,
            "waveComplete": self.wave_complete,
            "victory": self.run.engine.phase == "victory",
            "reward": {"kind": reward.kind, "material": reward.material, "choices": list(reward.choices)} if reward else None,
            "shop": [{"key": item.key, "name": item.name, "cost": item.cost} for item in self.run.shop_items()],
        }


ROGUE_SESSION = RogueSession()


class ArenaRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self) -> None:
        if self.path == "/api/pieces":
            self._send_json({"pieces": catalog_as_dicts()})
            return
        if self.path == "/api/modes":
            self._send_json({
                "modes": [
                    {
                        "id": definition.key.value,
                        "name": definition.name,
                        "description": definition.description,
                        "status": definition.status,
                        "variants": list(definition.variants),
                    }
                    for definition in MODE_DEFINITIONS
                ]
            })
            return
        if self.path == "/api/state":
            self._send_json(SESSION.state())
            return
        if self.path == "/api/rogue/state":
            self._send_json(ROGUE_SESSION.state())
            return
        if self.path == "/almanac":
            self.path = "/almanac.html"
        elif self.path in {"/", "/pvp", "/bot-maker", "/rogue", "/rogue/designer"}:
            self.path = "/"
        super().do_GET()

    def do_POST(self) -> None:
        if self.path.startswith("/api/rogue/"):
            try:
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length) or b"{}")
                if self.path == "/api/rogue/reset":
                    result = ROGUE_SESSION.reset()
                elif self.path == "/api/rogue/character":
                    result = ROGUE_SESSION.choose_character(payload["character"])
                elif self.path == "/api/rogue/action":
                    result = ROGUE_SESSION.player_action(payload)
                elif self.path == "/api/rogue/buy-drop":
                    result = ROGUE_SESSION.buy_and_drop(payload)
                elif self.path == "/api/rogue/bank-drop":
                    result = ROGUE_SESSION.bank_drop(payload)
                elif self.path == "/api/rogue/reward":
                    result = ROGUE_SESSION.choose_reward(payload["piece"])
                else:
                    self.send_error(HTTPStatus.NOT_FOUND, "unknown rogue endpoint")
                    return
                self._send_json(result)
            except (KeyError, TypeError, ValueError) as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/reset":
            self._send_json(SESSION.reset())
            return
        if self.path == "/api/mode":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length) or b"{}")
                self._send_json(SESSION.set_mode(payload["mode"], payload.get("variant")))
            except (KeyError, TypeError, ValueError) as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/step":
            try:
                self._send_json(SESSION.step())
            except RuntimeError as exc:
                self._send_json({"error": str(exc), "state": SESSION.state()}, HTTPStatus.CONFLICT)
            return
        self.send_error(HTTPStatus.NOT_FOUND, "unknown endpoint")

    def log_message(self, format: str, *args) -> None:
        return

    def _send_json(self, payload: Dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Serve the 9x9 arena web view.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    server = ThreadingHTTPServer((args.host, args.port), ArenaRequestHandler)
    print(f"Serving arena web view at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
