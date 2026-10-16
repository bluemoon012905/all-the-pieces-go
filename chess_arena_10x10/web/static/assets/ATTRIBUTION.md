# Piece Asset Attribution

This project keeps third-party piece SVGs in `web/static/assets/pieces/`.

## Lichess

- Source: `lichess-org/lila`, `public/piece/chessnut`
- URL: https://github.com/lichess-org/lila/tree/master/public/piece/chessnut
- License: Apache License 2.0, as distributed by the Lichess repository.

## Lishogi

- Source: `WandererXII/lishogi`, `ui/@build/pieces/assets/standard/intl_colored_2d`
- URL: https://github.com/WandererXII/lishogi/tree/master/ui/%40build/pieces/assets/standard/intl_colored_2d
- License details are documented by Lishogi in `COPYING.md`.

## Xiangqi

- Source: Wikimedia Commons traditional Xiangqi SVGs
- Example URL: https://commons.wikimedia.org/wiki/File:Xiangqi_General_(Trad).svg
- License: public domain where marked on Wikimedia Commons.

If a configured SVG is missing, the web UI intentionally falls back to a styled
letter token so local play remains usable.
