# All the Pieces Go

A local Python CLI arena for a custom 10x10 auto-chess variant that mixes FIDE Chess,
Xiangqi, and Shogi-inspired pieces. The engine supports a setup phase, palace
restrictions, five sequential actions per turn, dynamic bot discovery, and a
baseline random bot.

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

The CLI prints the 10x10 board after every action.

## Test

```bash
.venv/bin/python -m pytest -q
```

Current suite coverage includes board setup validation, piece movement rules,
Xiangqi cannon and knight behavior, palace restrictions, five-action turn
switching, and bot discovery.

## Project Layout

```text
chess_arena_10x10/
├── bots/       # Bot interface and plugin modules
├── core/       # Board and engine
└── pieces/     # FIDE, Xiangqi, and Shogi-style pieces
tests/          # Pytest suite
cli.py          # Local command-line runner
```

## Adding Bots

Create a new `.py` file in `chess_arena_10x10/bots/` with a class that subclasses
`BaseBot`. The engine discovers bot modules automatically by filename.
