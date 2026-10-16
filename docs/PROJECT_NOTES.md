# Project Notes

## Current direction

All the Pieces Go is a 9x9 hybrid board-game engine. The rules engine is
shared by every mode; mode-specific product state should live outside
`core/engine.py`.

## Game modes

| Mode | Audience | Status | Next boundary |
| --- | --- | --- | --- |
| Player vs Player | Two local players | Active foundation | Add input/turn UI; keep sandbox as a PvP variant |
| Player vs Player: Sandbox | Two players experimenting with positions | Active foundation | Add unrestricted setup and reset/inspect tools |
| Bot Maker | Python bot authors | On hold | Add bot project/session state and a safe evaluation loop |
| Rogue Run | One player | Wave editor | Add run state, encounters, rewards, and bot execution |

The API and browser view should keep exposing a board for every mode, even
when a mode is not playable yet. This makes the bot-maker and rogue surfaces
easy to develop incrementally and keeps rendering independent from game mode.

The browser routes mirror this structure: `/` is the mode picker, while
`/pvp`, `/bot-maker`, `/rogue`, and `/rogue/designer` are separate mode pages.

The `/almanac` page is a focused reference surface for Chess, Xiangqi, and
Shogi pieces. The supported piece list is documented in
[`docs/PIECE_ALMANAC.md`](PIECE_ALMANAC.md). It previews representative
destinations from an empty center square; those previews are educational
geometry, not a replacement for each game's full legality rules.

## Architecture decisions

- `core/board.py` owns board storage and coordinate operations.
- `core/engine.py` owns shared movement, turns, setup, and win conditions.
- `core/modes.py` owns the mode registry and mode-aware engine creation.
- `bots/` owns Python bot implementations and discovery.
- `web/` owns transport and browser presentation, not game rules.

## Planned work

1. Make PvP board interaction work in the browser, including selecting and
   submitting legal moves for the active player.
2. Connect the Rogue wave editor's saved formations and behavior notes to a
   `RogueRunState` around the shared engine: encounter seed, player resources,
   rewards, and bot execution.
3. Define a bot-maker session that can load a bot module, run one side, and
   capture reproducible match results.
4. Add persistence only after the above session boundaries are stable.
