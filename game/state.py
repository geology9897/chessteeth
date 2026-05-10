import chess
from dataclasses import dataclass, field
from typing import Optional


CHOMP_DURATION = 55
ANIM_DURATION  = 12   # frames at 60 fps ≈ 200 ms


@dataclass
class GameState:
    board: chess.Board = field(default_factory=chess.Board)
    selected: Optional[chess.Square] = None
    legal_targets: list[chess.Square] = field(default_factory=list)
    chomping_square: Optional[chess.Square] = None
    chomp_timer: int = 0
    game_over: bool = False
    game_over_msg: str = ""
    # slide animation
    anim_piece: Optional[chess.Piece] = None
    anim_from_sq: Optional[chess.Square] = None
    anim_to_sq: Optional[chess.Square] = None
    anim_timer: int = 0
    # pawn promotion awaiting piece choice
    promotion_pending: Optional[tuple] = None   # (from_sq, to_sq) or None
    # metrics
    white_captures: list[chess.Piece] = field(default_factory=list)
    black_captures: list[chess.Piece] = field(default_factory=list)
    white_checks: int = 0
    black_checks: int = 0

    def select(self, square: chess.Square) -> bool:
        piece = self.board.piece_at(square)
        if piece and piece.color == self.board.turn:
            self.selected = square
            self.legal_targets = [
                m.to_square for m in self.board.legal_moves if m.from_square == square
            ]
            return True
        self.selected = None
        self.legal_targets = []
        return False

    def try_move(self, to_sq: chess.Square) -> bool:
        if self.selected is None:
            return False
        move = None
        for m in self.board.legal_moves:
            if m.from_square == self.selected and m.to_square == to_sq:
                if m.promotion:
                    # pause and ask the player which piece they want
                    self.promotion_pending = (m.from_square, m.to_square)
                    self.selected = None
                    self.legal_targets = []
                    return True
                move = m
                break
        if move is None:
            return False
        return self.apply_move(move)

    def complete_promotion(self, piece_type: int) -> bool:
        if self.promotion_pending is None:
            return False
        from_sq, to_sq = self.promotion_pending
        self.promotion_pending = None
        return self.apply_move(chess.Move(from_sq, to_sq, promotion=piece_type))

    def apply_move(self, move: chess.Move) -> bool:
        if move not in self.board.legal_moves:
            return False
        moving_piece = self.board.piece_at(move.from_square)
        is_capture   = self.board.is_capture(move)

        # Record captured piece before the board state changes
        captured = None
        if is_capture:
            if self.board.is_en_passant(move):
                ep_sq = chess.square(chess.square_file(move.to_square),
                                     chess.square_rank(move.from_square))
                captured = self.board.piece_at(ep_sq)
            else:
                captured = self.board.piece_at(move.to_square)

        self.board.push(move)
        self.selected = None
        self.legal_targets = []

        if is_capture:
            self.chomping_square = move.to_square
            self.chomp_timer = CHOMP_DURATION
            if captured and moving_piece:
                if moving_piece.color == chess.WHITE:
                    self.white_captures.append(captured)
                else:
                    self.black_captures.append(captured)

        if self.board.is_check():
            if self.board.turn == chess.BLACK:
                self.white_checks += 1
            else:
                self.black_checks += 1

        if moving_piece:
            self.anim_piece   = moving_piece
            self.anim_from_sq = move.from_square
            self.anim_to_sq   = move.to_square
            self.anim_timer   = ANIM_DURATION
        self._check_game_over()
        return True

    def _check_game_over(self):
        if self.board.is_checkmate():
            winner = "White" if self.board.turn == chess.BLACK else "Black"
            self.game_over = True
            self.game_over_msg = f"{winner} wins by checkmate!"
        elif self.board.is_stalemate():
            self.game_over = True
            self.game_over_msg = "Stalemate — it's a draw!"
        elif self.board.is_insufficient_material():
            self.game_over = True
            self.game_over_msg = "Draw — insufficient material"
        elif self.board.is_seventyfive_moves():
            self.game_over = True
            self.game_over_msg = "Draw — 75-move rule"

    def tick(self):
        if self.chomp_timer > 0:
            self.chomp_timer -= 1
            if self.chomp_timer == 0:
                self.chomping_square = None
        if self.anim_timer > 0:
            self.anim_timer -= 1
            if self.anim_timer == 0:
                self.anim_piece = self.anim_from_sq = self.anim_to_sq = None

    def animating(self) -> bool:
        return self.anim_timer > 0

    def reset(self):
        self.__class__.__init__(self)

    def in_check(self) -> bool:
        return self.board.is_check()

    def king_sq(self) -> Optional[chess.Square]:
        return self.board.king(self.board.turn)
