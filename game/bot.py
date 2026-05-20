"""Stockfish wrapper with background-thread move generation."""
import os
import random
import shutil
import threading
import chess
import chess.engine

# (num, label, uci_options, limit_kwargs)
# Beginner plays randomly (no engine). Easy uses depth-capped Stockfish with
# maximum error injection. Medium–Expert use UCI_LimitStrength + ELO so the
# mistakes Stockfish makes match those of a human at that rating — a smooth
# ramp rather than a sudden spike. Stockfish clamps UCI_Elo at ~1320 minimum,
# so the two weakest levels rely on depth limits instead.
DIFFICULTIES = [
    (1, "Beginner", {},                                            {}),
    (2, "Easy",     {"Skill Level": 0},                            {"depth": 1}),
    (3, "Medium",   {"UCI_LimitStrength": True, "UCI_Elo": 1350},  {"time": 0.5}),
    (4, "Hard",     {"UCI_LimitStrength": True, "UCI_Elo": 1800},  {"time": 1.0}),
    (5, "Expert",   {"UCI_LimitStrength": True, "UCI_Elo": 2400},  {"time": 3.0}),
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
            return True  # Beginner always plays randomly, no engine needed
        path = find_stockfish()
        if path:
            try:
                self._engine = chess.engine.SimpleEngine.popen_uci(path)
                _, _, opts, _ = DIFFICULTIES[self.difficulty - 1]
                if opts:
                    self._engine.configure(opts)
            except Exception:
                self._engine = None
        if self._engine is None:
            return False
        return True

    def request_move(self, board: chess.Board) -> None:
        if self._thread and self._thread.is_alive():
            return
        board_copy = board.copy()

        if self._engine is None:
            # Beginner difficulty always reaches here — no engine was started
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
