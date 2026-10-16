# All the Pieces Go

A local Python CLI arena for a custom 9x9 auto-chess variant that mixes FIDE Chess,
Xiangqi, and Shogi-inspired pieces. The shared engine supports a setup phase,
palace restrictions, five sequential actions per turn, dynamic bot discovery,
and a baseline random bot. Three product modes sit around that engine:
Player vs Player (including a sandbox variant), Bot Maker, and Rogue Run.

## Setup

Use Python 3.10 or newer.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

The `.venv/` directory is ignored by git.

## Run Locally

Print a fresh default board:

```bash
.venv/bin/python cli.py new
```

Run a short bot-vs-bot match:

```bash
.venv/bin/python cli.py play --bot1 random_bot --bot2 random_bot --max-actions 10 --seed 7
```

The CLI prints the 9x9 board after every action.

## Web View

Start the local visual arena:

```bash
.venv/bin/python -m chess_arena_10x10.web.server --port 8000
```

Open `http://127.0.0.1:8000` in your browser. The page shows the board,
match state, last action, and move log. The mode selector exposes the three
board-backed surfaces; bot stepping is currently enabled only for Bot Maker.

Web routes:

- `/` — home page and mode picker
- `/pvp` — Player vs Player, including the sandbox variant
- `/bot-maker` — paused Python bot-making board
- `/rogue` — playable Rogue Run: character selection, shop, waves, and rewards
- `/rogue/designer` — saved Rogue Run wave and enemy-formation editor
- `/almanac` — searchable Chess, Xiangqi, and Shogi piece catalog with movement previews

The web board uses local SVG assets from Lichess, Lishogi, and Wikimedia
Commons where available. See
`chess_arena_10x10/web/static/assets/ATTRIBUTION.md` for source notes.

## Test

```bash
.venv/bin/python -m pytest -q
```

Current suite coverage includes board setup validation, piece movement rules,
Xiangqi cannon and knight behavior, palace restrictions, five-action turn
switching, bot discovery, and the game-mode registry.

## Project Layout

```text
chess_arena_10x10/
├── bots/       # Bot interface and plugin modules
├── core/       # Board, engine, and game-mode registry
├── pieces/     # FIDE, Xiangqi, and Shogi-style pieces
└── web/        # Local browser visualization
tests/          # Pytest suite
docs/           # Project notes and future mode boundaries
cli.py          # Local command-line runner
```

See [`docs/PROJECT_NOTES.md`](docs/PROJECT_NOTES.md) for the mode roadmap and
architecture boundaries.

## Adding Bots

Create a new `.py` file in `chess_arena_10x10/bots/` with a class that subclasses
`BaseBot`. The engine discovers bot modules automatically by filename.
