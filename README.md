# ChessTeeth

A desktop chess game built for a 9-year-old who just got into chess and had one specific request: the pieces should **bare their teeth** when they capture.

Two goals, one project — she gets a game made just for her, and a codebase to start learning Python with.

---

## What it does

- Full two-player chess with legal-move highlighting, check detection, and all draw conditions
- **CHOMP!** — capturing pieces flash a toothed mouth, scale up, and the board shouts CHOMP!
- Play against a Stockfish bot at four difficulty levels (Easy → Expert)
- Pixel-art humanized chess pieces — queen, king, bishop, knight, rook, pawn as characters
- Resizable window — drag it as big as you like, the board scales with it
- Parchment color theme

---

## Requirements

| Tool | Install |
|------|---------|
| Python 3.12+ | https://www.python.org/downloads/ |
| uv | `curl -LsSf https://astral.sh/uv/install.sh \| sh` (Mac/Linux) · `winget install astral-sh.uv` (Windows) |
| Stockfish *(optional, for bot)* | `sudo apt install stockfish` (Linux) · `brew install stockfish` (Mac) · https://stockfishchess.org/download/ (Windows) |

---

## Run

```bash
git clone https://github.com/nli276/chessteeth.git
cd chessteeth
uv run chessteeth
```

`uv` handles the virtual environment and installs `pygame`, `python-chess`, and `Pillow` automatically on first run.

---

## Controls

| Action | Effect |
|--------|--------|
| Click a piece | Select (legal moves shown as dots) |
| Click a dot | Move there |
| `R` | Back to menu |
| `ESC` | Back to menu |

---

## Project layout

```
chessteeth/
├── source/          # original pixel-art source images
├── game/            # Python package
│   ├── main.py      # window, menu, game loop
│   ├── state.py     # game state (wraps python-chess)
│   ├── board.py     # board rendering, scales with window size
│   ├── pieces.py    # piece drawing + chomp animation
│   ├── sprites.py   # sprite loading and caching
│   ├── themes.py    # color theme
│   ├── bot.py       # Stockfish wrapper (background thread)
│   └── assets/      # generated 80×80 PNGs (auto-created)
├── pyproject.toml
└── uv.lock
```

---

## License

MIT — see [LICENSE](LICENSE).
