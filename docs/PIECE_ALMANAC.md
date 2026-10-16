# Supported Piece Almanac

This project currently keeps the playable/reference piece set limited to
Chess, Xiangqi, and Shogi. The entries below are the candidate pieces exposed
by the web Almanac. Other variants are intentionally out of scope for now.

## Chess

| Piece | Movement | Promotion | Special rule |
| --- | --- | --- | --- |
| King | One step in any direction | None | Royal; castling with a rook |
| Queen | Orthogonal or diagonal sliding | None | Combines rook and bishop |
| Bishop | Unlimited diagonal sliding | None | Remains on one square color |
| Rook / Castle | Unlimited orthogonal sliding | None | Participates in castling |
| Pawn | Forward step; diagonal capture | Queen, rook, bishop, or knight | Initial double-step, en passant |

## Xiangqi

| Piece | Movement | Promotion | Special rule |
| --- | --- | --- | --- |
| General / Jiang | One orthogonal point inside the palace | None | Palace-bound; opposing generals cannot face |
| Xiang / Elephant | Exactly two diagonal points | None | Eye must be empty; cannot cross the river |
| Ju / Chariot | Unlimited orthogonal sliding | None | Also called the chariot |
| Bing / Zu / Soldier | Forward; sideways after the river | None | No promotion; river changes movement |
| Advisor / Shi | One diagonal point in the palace | None | Palace-bound |
| Cannon / Pao | Orthogonal sliding; captures over one screen | None | Moves through empty squares; captures exactly one piece beyond a screen |

## Shogi

| Piece | Movement | Promotion | Special rule |
| --- | --- | --- | --- |
| King / Ōshō | One step in any direction | None | Royal; no castling |
| Kakugyō / Bishop | Unlimited diagonal sliding | Dragon Horse | Promoted form gains orthogonal steps |
| Dragon Horse | Bishop slide plus one orthogonal step | Variant-specific | Promoted bishop |
| Hisha / Flying Chariot | Unlimited orthogonal sliding | Dragon King | Promotes to rook plus diagonal steps |
| Dragon King | Rook slide plus one diagonal step | Variant-specific | Promoted rook |
| Lance / Kyōsha | Unlimited forward-only sliding | Gold General | Cannot retreat or move sideways |
| Keima / Knight | Two forward and one sideways leap | Gold General | Only two forward destinations |
| Fuhyō / Pawn | One forward step | Tokin / Gold General | Move and capture are the same |
| Gold General | Forward, orthogonal, and forward-diagonal steps | None | Cannot move diagonally backward |
| Silver General | Forward or diagonal steps | Gold General | Promotes to Gold movement |

The movement previews are illustrative. Board occupancy, direction, palace
limits, river limits, promotion zones, and special capture rules are applied by
the rules engine separately.
