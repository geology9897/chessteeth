"""Stockfish wrapper with background-thread move generation."""
import os
import shutil
import threading
import chess
import chess.engine

# (num, label, skill_level 0-20, think_time seconds)
DIFFICULTIES = [
    (1, "Easy",   0,  0.10),
    (2, "Medium", 5,  0.50),
    (3, "Hard",  12,  1.20),
    (4, "Expert",20,  3.00),
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
        path = find_stockfish()
        if not path:
            return False
        try:
            self._engine = chess.engine.SimpleEngine.popen_uci(path)
            _, _, skill, _ = DIFFICULTIES[self.difficulty - 1]
            self._engine.configure({"Skill Level": skill})
            return True
        except Exception:
            return False

    def request_move(self, board: chess.Board) -> None:
        if self._thread and self._thread.is_alive():
            return
        board_copy = board.copy()
        _, _, _, think = DIFFICULTIES[self.difficulty - 1]

        def _run():
            try:
                assert self._engine is not None
                result = self._engine.play(board_copy, chess.engine.Limit(time=think))
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
