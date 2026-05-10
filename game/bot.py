"""Stockfish wrapper with background-thread move generation."""
import os
import random
import shutil
import threading
import chess
import chess.engine

# (num, label, uci_options, limit_kwargs)
# Skill Level 0 = maximum blunder rate; depth cap forces very shallow search.
# UCI_LimitStrength bottoms out at ~1350 ELO (still hard), so we use depth
# limits instead for Easy/Medium to get a more gradual beginner curve.
DIFFICULTIES = [
    (1, "Easy",   {"Skill Level": 0},  {"depth": 1,  "time": 0.05}),
    (2, "Medium", {"Skill Level": 5},  {"depth": 4,  "time": 0.3}),
    (3, "Hard",   {"Skill Level": 14}, {"time": 0.8}),
    (4, "Expert", {"Skill Level": 20}, {"time": 3.0}),
]


def find_stockfish() -> str | None:
    path = shutil.which("stockfish")
    if path:
        return path
    for p in ["/usr/games/stockfish", "/usr/local/bin/stockfish",
              "/opt/homebrew/bin/stockfish", r"C:\Program Files\stockfish\stockfish.exe"]:
        if os.path.isfile(p):
            return p
    return None


class BotEngine:
    def __init__(self, difficulty: int = 2):
        self.difficulty = difficulty
        self._engine: chess.engine.SimpleEngine | None = None
        self._pending: chess.Move | None = None
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()

    def start(self) -> bool:
        if self.difficulty == 1:
            return True  # Easy uses random moves — no engine needed
        path = find_stockfish()
        if not path:
            return False
        try:
            self._engine = chess.engine.SimpleEngine.popen_uci(path)
            _, _, opts, _ = DIFFICULTIES[self.difficulty - 1]
            if opts:
                self._engine.configure(opts)
            return True
        except Exception:
            return False

    def request_move(self, board: chess.Board) -> None:
        if self._thread and self._thread.is_alive():
            return
        board_copy = board.copy()

        if self.difficulty == 1:
            def _run():
                moves = list(board_copy.legal_moves)
                if moves:
                    with self._lock:
                        self._pending = random.choice(moves)
            self._thread = threading.Thread(target=_run, daemon=True)
            self._thread.start()
            return

        _, _, _, limit_kwargs = DIFFICULTIES[self.difficulty - 1]

        def _run():
            try:
                assert self._engine is not None
                result = self._engine.play(board_copy, chess.engine.Limit(**limit_kwargs))
                with self._lock:
                    self._pending = result.move
            except Exception:
                pass

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()

    def poll_move(self) -> chess.Move | None:
        with self._lock:
            m = self._pending
            self._pending = None
            return m

    def thinking(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    def close(self) -> None:
        if self._engine:
            try:
                self._engine.quit()
            except Exception:
                pass
            self._engine = None
