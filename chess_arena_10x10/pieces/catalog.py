"""Reference catalog for the Chess, Xiangqi, and Shogi piece almanac.

The live rules engine only implements the pieces used by the current arena
position. The catalog is deliberately limited to the three supported source
games; experimental and fairy variants belong in a separate future catalog.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class CatalogPiece:
    slug: str
    name: str
    game: str
    archetype: str
    movement: str
    promotion: str
    special: str
    preview: str
    asset_family: str = "letter"
    asset_name: str = "piece"
    glyph: str = "?"

    def as_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["assetFamily"] = data.pop("asset_family")
        data["assetName"] = data.pop("asset_name")
        return data


def _slug(name: str, game: str) -> str:
    return f"{name}-{game}".lower().replace(" ", "-").replace("/", "-")


def p(
    name: str,
    game: str,
    archetype: str,
    movement: str,
    promotion: str,
    special: str,
    preview: str,
    asset_family: str = "letter",
    asset_name: str = "piece",
    glyph: str = "?",
) -> CatalogPiece:
    return CatalogPiece(
        _slug(name, game), name, game, archetype, movement, promotion,
        special, preview, asset_family, asset_name, glyph,
    )


CATALOG: List[CatalogPiece] = [
    p("King", "Chess", "Royal / commander", "One step in any direction", "None", "Royal; castling with a rook", "king", "lichess", "K", "♔"),
    p("Shah", "Shatranj", "Royal / commander", "One step in any direction", "None", "Royal; no modern castling", "king", "lichess", "K", "♔"),
    p("Raja", "Chaturanga", "Royal / commander", "One step in any direction", "None", "Early Indian royal piece", "king", "lichess", "K", "♔"),
    p("General / Jiang", "Xiangqi", "Royal / commander", "One orthogonal point inside the palace", "None", "Palace-bound; opposing generals cannot face", "xiangqi_king", "xiangqi", "general", "♔"),
    p("General / Janggun", "Janggi", "Royal / commander", "One palace-line step", "None", "Palace diagonals and bikjang rules", "king", "xiangqi", "general", "♔"),
    p("King / Ōshō", "Shogi", "Royal / commander", "One step in any direction", "None", "Royal; no castling", "king", "lishogi", "OU", "♔"),
    p("Khun", "Makruk", "Royal / commander", "One step in any direction", "None", "Royal; no Western castling", "king", "lichess", "K", "♔"),
    p("Mann / Commoner", "Courier / fairy", "Royal / commander", "One step in any direction", "None", "King movement without royal status", "king", "lichess", "K", "♙"),
    p("Prince", "Chu shogi", "Royal / commander", "One step in any direction", "None", "Additional royal piece", "king", "letter", "piece", "♔"),
    p("Royal Knight", "Knightmate", "Royal / commander", "Knight leap", "None", "The knight is the royal piece", "knight", "lichess", "N", "♞"),
    p("Queen", "Chess", "Queen / major rider", "Orthogonal or diagonal sliding", "None", "Combines rook and bishop", "queen", "lichess", "Q", "♕"),
    p("Ferz / Fers", "Shatranj / Courier", "Restricted stepper", "One diagonal step", "None", "Historical queen predecessor", "ferz", "lichess", "B", "◇"),
    p("Mantri / Minister", "Chaturanga", "Restricted stepper", "Usually one diagonal step", "None", "Historical reconstruction varies", "ferz", "lichess", "B", "◇"),
    p("Met / Seed", "Makruk", "Restricted stepper", "One diagonal step", "None", "Much weaker than a modern queen", "ferz", "lichess", "B", "◇"),
    p("Neang / Queen", "Ouk Chatrang", "Restricted stepper", "One diagonal step", "None", "May have a special initial forward move", "ferz", "lichess", "B", "◇"),
    p("Amazon", "Fairy chess", "Hybrid rider + leaper", "Queen slide or knight leap", "None", "Queen plus knight", "amazon", "lichess", "Q", "♕"),
    p("Free King", "Chu shogi", "Queen / major rider", "Queen-like sliding", "None", "Non-royal despite its name", "queen", "letter", "piece", "♕"),
    p("Centaur", "Fairy chess", "Hybrid rider + leaper", "King step or knight leap", "None", "Usually non-royal", "centaur", "lichess", "K", "♘"),
    p("Bishop", "Chess", "Bishop / elephant", "Unlimited diagonal sliding", "None", "Remains on one square color", "bishop", "lichess", "B", "♗"),
    p("Alfil / Pil", "Shatranj", "Bishop / elephant", "Exactly two diagonal squares; leaps", "None", "Jumps over the midpoint", "alfil", "lichess", "B", "◈"),
    p("Gaja / Elephant", "Chaturanga", "Bishop / elephant", "Usually a two-square diagonal leap", "None", "Ancient descriptions vary", "alfil", "lichess", "B", "◈"),
    p("Xiang / Elephant", "Xiangqi", "Bishop / elephant", "Exactly two diagonal points", "None", "Eye must be empty; cannot cross river", "xiangqi_elephant", "xiangqi", "elephant", "象"),
    p("Sang / Elephant", "Janggi", "Bishop / elephant", "(3,2)-type bent move", "None", "Both intermediate points must be clear", "janggi_elephant", "xiangqi", "elephant", "象"),
    p("Kakugyō / Bishop", "Shogi", "Bishop / elephant", "Unlimited diagonal sliding", "Dragon Horse", "Promoted form gains orthogonal steps", "bishop", "lishogi", "KA", "角"),
    p("Dragon Horse", "Shogi", "Hybrid rider + stepper", "Bishop slide plus one orthogonal step", "Variant-specific", "Promoted bishop", "dragon_horse", "lishogi", "UM", "龍"),
    p("Ferocious Leopard", "Chu shogi", "Bishop / elephant", "Diagonal step plus forward/backward step", "Bishop", "Short-range compound", "ferz", "letter", "piece", "豹"),
    p("Drunk Elephant", "Chu shogi", "Bishop / elephant", "One step except directly backward", "Prince", "Promotion can create a second royal", "king", "letter", "piece", "象"),
    p("Blind Tiger", "Chu shogi", "Restricted stepper", "One step except directly forward", "Flying Stag", "Directional king compound", "king", "letter", "piece", "虎"),
    p("Khon / Nobleman", "Makruk / Ouk Chatrang", "Bishop / elephant", "One diagonal or one forward step", "None", "Never slides", "khon", "lichess", "B", "♗"),
    p("Sin / Elephant", "Sittuyin", "Bishop / elephant", "One diagonal or one forward step", "None", "Short-range regional bishop", "khon", "lichess", "B", "♗"),
    p("Courier", "Courier chess", "Bishop / elephant", "Unlimited diagonal sliding", "None", "Coexists with a two-square elephant", "bishop", "lichess", "B", "♗"),
    p("Archbishop / Cardinal", "Capablanca / fairy", "Hybrid rider + leaper", "Bishop slide or knight leap", "None", "Bishop plus knight", "archbishop", "lichess", "B", "♗"),
    p("Rook / Castle", "Chess", "Rook / chariot", "Unlimited orthogonal sliding", "None", "Participates in castling", "rook", "lichess", "R", "♖"),
    p("Rukh", "Shatranj", "Rook / chariot", "Unlimited orthogonal sliding", "None", "No Western castling", "rook", "lichess", "R", "♖"),
    p("Ratha / Chariot", "Chaturanga", "Rook / chariot", "Orthogonal sliding", "None", "Historical predecessor", "rook", "lichess", "R", "♖"),
    p("Ju / Chariot", "Xiangqi", "Rook / chariot", "Unlimited orthogonal sliding", "None", "Also called the chariot", "rook", "lichess", "R", "車"),
    p("Cha / Chariot", "Janggi", "Rook / chariot", "Orthogonal and palace-diagonal sliding", "None", "Palace lines add diagonals", "rook", "lichess", "R", "車"),
    p("Hisha / Flying Chariot", "Shogi", "Rook / chariot", "Unlimited orthogonal sliding", "Dragon King", "Promotes to rook plus diagonal steps", "rook", "lishogi", "HI", "飛"),
    p("Dragon King", "Shogi", "Hybrid rider + stepper", "Rook slide plus one diagonal step", "Variant-specific", "Promoted rook", "dragon_king", "lishogi", "RY", "龍"),
    p("Ruea / Boat", "Makruk / Ouk Chatrang", "Rook / chariot", "Unlimited orthogonal sliding", "None", "Regional rook", "rook", "lichess", "R", "♖"),
    p("Lance / Kyōsha", "Shogi", "Rook / chariot", "Unlimited forward-only sliding", "Gold General", "Cannot retreat or move sideways", "lance", "lishogi", "KY", "香"),
    p("Reverse Chariot", "Chu shogi", "Rook / chariot", "Forward/backward sliding only", "Whale", "Never moves sideways", "lance", "lishogi", "KY", "反"),
    p("Vertical Mover", "Chu shogi", "Rook / chariot", "Forward/backward slide plus side steps", "Flying Ox", "Directional compound", "rook", "letter", "piece", "縦"),
    p("Side Mover", "Chu shogi", "Rook / chariot", "Sideways slide plus forward/back steps", "Free Boar", "Directional compound", "rook", "letter", "piece", "横"),
    p("Flying Ox", "Chu shogi", "Rook / chariot", "Vertical and diagonal sliding", "None", "Cannot slide horizontally", "queen", "letter", "piece", "牛"),
    p("Free Boar", "Chu shogi", "Rook / chariot", "Horizontal and diagonal sliding", "None", "Cannot slide vertically", "queen", "letter", "piece", "猪"),
    p("Whale", "Chu shogi", "Rook / chariot", "Vertical plus backward diagonal sliding", "None", "Directional rider", "queen", "letter", "piece", "鯨"),
    p("White Horse", "Chu shogi", "Rook / chariot", "Forward diagonals plus vertical sliding", "None", "Cannot move backward diagonally", "queen", "letter", "piece", "馬"),
    p("Knight", "Chess / Shatranj / Chaturanga", "Knight / cavalry", "(2,1) leap", "Variant-specific", "Jumps over intervening pieces", "knight", "lichess", "N", "♘"),
    p("Horse / Ma", "Xiangqi / Janggi", "Knight / cavalry", "One orthogonal then one diagonal step", "None", "First leg can be blocked", "xiangqi_knight", "xiangqi", "horse", "馬"),
    p("Keima / Knight", "Shogi", "Knight / cavalry", "Two forward and one sideways leap", "Gold General", "Only two forward destinations", "shogi_knight", "lishogi", "KE", "桂"),
    p("Camel", "Fairy chess", "Knight / cavalry", "(3,1) leap", "None", "Usually color-bound", "camel", "lichess", "N", "♞"),
    p("Zebra", "Fairy chess", "Knight / cavalry", "(3,2) leap", "None", "Changes square color", "zebra", "lichess", "N", "♞"),
    p("Giraffe", "Fairy chess", "Knight / cavalry", "Commonly a (4,1) leap", "None", "Naming varies by variant", "giraffe", "lichess", "N", "♞"),
    p("Nightrider", "Fairy chess", "Knight / cavalry", "Repeated knight vectors in one direction", "None", "Knight rider; stops when blocked", "nightrider", "lichess", "N", "♞"),
    p("Wildebeest / Gnu", "Wildebeest chess", "Hybrid rider + leaper", "Knight plus camel leaps", "None", "Compound leaper", "wildebeest", "lichess", "N", "♞"),
    p("Okapi", "Fairy chess", "Hybrid rider + leaper", "Knight plus zebra leaps", "None", "Compound leaper", "okapi", "lichess", "N", "♞"),
    p("Pawn", "Chess", "Pawn / infantry", "Forward step; diagonal capture", "Queen, rook, bishop, or knight", "Initial double-step, en passant", "pawn", "lichess", "P", "♙"),
    p("Baidaq / Pawn", "Shatranj", "Pawn / infantry", "Forward step; diagonal capture", "Ferz", "No double-step or en passant", "pawn", "lichess", "P", "♙"),
    p("Bing / Zu / Soldier", "Xiangqi", "Pawn / infantry", "Forward; sideways after river", "None", "No promotion; river changes movement", "xiangqi_soldier", "xiangqi", "soldier", "卒"),
    p("Byeong / Jol / Soldier", "Janggi", "Pawn / infantry", "Forward or sideways step", "None", "Can use enemy palace diagonals", "xiangqi_soldier", "xiangqi", "soldier", "卒"),
    p("Fuhyō / Pawn", "Shogi", "Pawn / infantry", "One forward step", "Tokin / Gold General", "Move and capture are the same", "pawn", "lishogi", "FU", "歩"),
    p("Bia / Cowrie Pawn", "Makruk", "Pawn / infantry", "Forward step; diagonal capture", "Met-like piece", "Promotes on its sixth rank", "pawn", "lichess", "P", "♙"),
    p("Nè / Feudal Lord", "Sittuyin", "Pawn / infantry", "Forward step; diagonal capture", "General", "Promotion has marked-zone restrictions", "pawn", "lichess", "P", "♙"),
    p("Berolina Pawn", "Fairy chess", "Pawn / infantry", "Diagonal move; straight capture", "Variant-specific", "Reverse pawn geometry", "pawn", "lichess", "P", "♙"),
    p("Torpedo Pawn", "Torpedo chess", "Pawn / infantry", "One or two forward squares", "Variant-specific", "Two-square advance is not first-move-only", "pawn", "lichess", "P", "♙"),
    p("Pincer Pawn", "Baroque chess", "Indirect capturer", "Rook-like movement", "None", "Captures by custodial sandwiching", "rook", "lichess", "R", "♙"),
    p("Advisor / Shi", "Xiangqi", "Advisor / guard", "One diagonal point in palace", "None", "Palace-bound", "ferz", "xiangqi", "advisor", "士"),
    p("Guard / Sa", "Janggi", "Advisor / guard", "One marked palace-line step", "None", "Palace-bound", "ferz", "xiangqi", "advisor", "士"),
    p("Gold General", "Shogi", "Advisor / guard", "Forward, orthogonal, and forward-diagonal steps", "None", "Cannot move diagonally backward", "gold", "lishogi", "GI", "金"),
    p("Silver General", "Shogi", "Advisor / guard", "Forward or diagonal steps", "Gold General", "Promotes to Gold movement", "silver", "lishogi", "GI", "銀"),
    p("Copper General", "Chu shogi", "Advisor / guard", "Forward, forward-diagonal, or backward step", "Side Mover", "Short directional stepper", "gold", "lishogi", "GI", "銅"),
    p("Iron General", "Dai / Tenjiku shogi", "Advisor / guard", "Forward or forward-diagonal step", "Vertical Soldier", "Cannot move sideways or backward", "gold", "lishogi", "GI", "鉄"),
    p("Go-between", "Chu shogi", "Advisor / guard", "One forward or backward step", "Drunk Elephant", "Cannot move sideways", "gold", "lishogi", "GI", "仲"),
    p("Dog", "Tenjiku shogi", "Advisor / guard", "Forward or backward-diagonal step", "Multi General", "Directional stepper", "gold", "lishogi", "GI", "犬"),
    p("Wazir", "Fairy chess", "Restricted stepper", "One orthogonal step", "None", "Core movement primitive", "wazir", "lichess", "R", "＋"),
    p("Dabbaba", "Fairy chess", "Restricted stepper", "Two-square orthogonal leap", "None", "Core movement primitive", "dabbaba", "lichess", "R", "◇"),
    p("Cannon / Pao", "Xiangqi", "Cannon / screen-capturer", "Orthogonal sliding; captures over one screen", "None", "Moves through empty squares; captures exactly one piece beyond a screen", "cannon", "xiangqi", "cannon", "炮"),
    p("Cannon / Po", "Janggi", "Cannon / screen-capturer", "Orthogonal sliding with screen captures", "None", "Requires one screen for every move and capture", "cannon", "xiangqi", "cannon", "包"),
    p("Grasshopper", "Fairy chess", "Hopper", "Queen-line hop over one hurdle", "None", "Lands immediately beyond hurdle", "grasshopper", "letter", "piece", "♘"),
    p("Rook-hopper", "Fairy chess", "Hopper", "Orthogonal hop over one hurdle", "None", "Directional grasshopper", "grasshopper", "letter", "piece", "♖"),
    p("Bishop-hopper", "Fairy chess", "Hopper", "Diagonal hop over one hurdle", "None", "Directional grasshopper", "grasshopper", "letter", "piece", "♗"),
    p("Locust", "Fairy chess", "Hopper", "Jumps and captures the hurdle", "None", "Lands beyond on an empty square", "grasshopper", "letter", "piece", "♘"),
    p("Lion / Shishi", "Chu shogi", "Lion / multi-step", "Up to two king steps in one turn", "None", "Can double-capture or perform igui", "lion", "letter", "piece", "獅"),
    p("Lion Hawk", "Tenjiku shogi", "Lion / multi-step", "Lion powers plus bishop sliding", "None", "Compound multi-step attacker", "lion", "letter", "piece", "鷹"),
    p("Horned Falcon", "Chu shogi", "Lion / multi-step", "Diagonal and selected orthogonal slides", "None", "Promoted Dragon Horse with special forward powers", "lion", "letter", "piece", "鷹"),
    p("Soaring Eagle", "Chu shogi", "Lion / multi-step", "Orthogonal and backward-diagonal slides", "None", "Promoted Dragon King with multi-step powers", "lion", "letter", "piece", "鷲"),
    p("Phoenix", "Chu / Tenjiku shogi", "Mythical compound leaper", "Orthogonal step or diagonal Alfil leap", "Queen / Free King", "Promotes dramatically", "phoenix", "letter", "piece", "鳳"),
    p("Kirin / Kylin", "Chu / Tenjiku shogi", "Mythical compound leaper", "Diagonal step or orthogonal Dabbaba leap", "Lion", "Lion promotion creates tactical value", "kirin", "letter", "piece", "麒"),
    p("Champion", "Omega Chess", "Mythical compound leaper", "Wazir, Dabbaba, or Alfil movement", "None", "Three movement primitives combined", "champion", "letter", "piece", "♘"),
    p("Wizard", "Omega Chess", "Mythical compound leaper", "Ferz or camel leap", "None", "Color-bound camel compound", "wizard", "letter", "piece", "♗"),
    p("Fire Demon", "Tenjiku shogi", "Area-effect / special capture", "Sliding and limited multi-step movement", "None", "Burns adjacent enemy pieces", "fire_demon", "letter", "piece", "炎"),
    p("Water Buffalo", "Tenjiku shogi", "Area-effect / special capture", "Diagonal and sideways sliding; limited vertical", "Fire Demon", "Promotes into an area-effect piece", "water_buffalo", "letter", "piece", "牛"),
    p("Withdrawer", "Baroque chess", "Displacement / indirect capturer", "Queen-like movement", "None", "Captures by moving away from an adjacent enemy", "queen", "lichess", "Q", "↖"),
    p("Long Leaper", "Baroque chess", "Displacement / indirect capturer", "Queen-line movement", "None", "Captures by jumping enemy pieces to empty squares", "queen", "lichess", "Q", "↗"),
    p("Coordinator", "Baroque chess", "Displacement / indirect capturer", "Queen-like movement", "None", "Captures at king-aligned intersections", "queen", "lichess", "Q", "⊕"),
    p("Immobilizer", "Baroque chess", "Area-effect / special capture", "Queen-like movement", "None", "Freezes adjacent enemy pieces", "queen", "lichess", "Q", "⊗"),
    p("Orphan", "Baroque chess", "Imitative / conditional", "Movement acquired from attacking enemies", "None", "Conditional movement", "queen", "lichess", "Q", "?"),
    p("Friend", "Baroque chess", "Imitative / conditional", "Movement acquired from protecting friends", "None", "Conditional movement", "queen", "lichess", "Q", "?"),
    p("Chancellor / Marshal", "Capablanca / fairy", "Hybrid rider + leaper", "Rook slide or knight leap", "None", "Orthogonal rider plus knight", "chancellor", "lichess", "R", "♖"),
    p("Nightriderhopper", "Fairy chess", "Hopper", "Knight-rider line with a hurdle", "None", "Screened knight-rider movement", "nightrider", "lichess", "N", "♞"),
    p("Rook General", "Tenjiku shogi", "Hierarchical jumper", "Orthogonal rider with rank-sensitive jumps", "Great General", "Jumping captures depend on piece hierarchy", "rook", "letter", "piece", "車"),
    p("Bishop General", "Tenjiku shogi", "Hierarchical jumper", "Diagonal rider with rank-sensitive jumps", "Vice General", "Jumping captures depend on piece hierarchy", "bishop", "letter", "piece", "角"),
    p("Great General", "Tenjiku shogi", "Hierarchical jumper", "Queen-direction movement", "None", "Powerful rank-sensitive jumping capture", "queen", "letter", "piece", "将"),
    p("Vice General", "Tenjiku shogi", "Hierarchical jumper", "Diagonal riding and multi-step abilities", "None", "Specialized hierarchical captures", "bishop", "letter", "piece", "副"),
    p("Kyoto Rook", "Kyoto shogi", "Identity-switching", "Rook sliding", "Flips to Pawn after moving", "Piece identity changes every move", "rook", "lichess", "R", "飛"),
    p("Kyoto Pawn", "Kyoto shogi", "Identity-switching", "Pawn movement", "Flips to Rook after moving", "Piece identity changes every move", "pawn", "lichess", "P", "歩"),
    p("Kyoto Silver / Bishop", "Kyoto shogi", "Identity-switching", "Silver or bishop movement", "Flips after moving", "Paired identity cycle", "silver", "lishogi", "GI", "銀"),
    p("Kyoto Gold / Knight", "Kyoto shogi", "Identity-switching", "Gold or knight movement", "Flips after moving", "Paired identity cycle", "gold", "lishogi", "GI", "金"),
]

# Keep the live Almanac focused on the three games this project supports.
CATALOG = [piece for piece in CATALOG if piece.game in {"Chess", "Xiangqi", "Shogi"}]


def catalog_as_dicts() -> List[Dict[str, Any]]:
    return [piece.as_dict() for piece in CATALOG]
