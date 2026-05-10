import pygame
import chess
from .themes import Theme
from .state import GameState, ANIM_DURATION
from . import pieces as p

FILES = "abcdefgh"
PROMO_PIECES = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
PROMO_LABELS  = {chess.QUEEN: "Q", chess.ROOK: "R", chess.BISHOP: "B", chess.KNIGHT: "N"}


def promo_rects(ox: int, oy: int, sq: int) -> list[tuple[int, pygame.Rect]]:
    """Pixel rects for the 4 promotion choices — shared by draw and click detection."""
    start_x = ox + sq * 2
    center_y = oy + sq * 3
    return [(pt, pygame.Rect(start_x + i * sq, center_y, sq, sq))
            for i, pt in enumerate(PROMO_PIECES)]


def draw(surface: pygame.Surface, state: GameState, theme: Theme,
         ox: int, oy: int, fonts: dict, sq: int = 80, flip: bool = False):
    _squares(surface, state, theme, ox, oy, sq, flip)
    _labels(surface, theme, ox, oy, fonts["md"], sq, flip)
    _pieces(surface, state, theme, ox, oy, sq, flip)
    _anim_piece(surface, state, theme, ox, oy, sq, flip)
    _chomp_text(surface, state, theme, ox, oy, fonts["chomp"], sq)
    _status_bar(surface, state, theme, ox, oy, fonts, sq)
    _controls_bar(surface, state, theme, ox, oy, fonts, sq)
    _stats_bar(surface, state, theme, fonts)
    if state.game_over:
        _game_over_banner(surface, state, theme, ox, oy, fonts, sq)
    if state.promotion_pending:
        _promotion_overlay(surface, state, theme, ox, oy, fonts, sq)


def _sq_topleft(file, rank, ox, oy, sq, flip):
    """Pixel top-left of the square at (file, rank)."""
    if flip:
        return ox + (7 - file) * sq, oy + rank * sq
    return ox + file * sq, oy + (7 - rank) * sq


def _squares(surface, state, theme, ox, oy, sq, flip=False):
    for rank in range(8):
        for file in range(8):
            square = chess.square(file, rank)
            x, y = _sq_topleft(file, rank, ox, oy, sq, flip)

            is_light = (file + rank) % 2 == 1
            color = theme.light_sq if is_light else theme.dark_sq

            if square == state.selected:
                color = theme.highlight
            elif state.in_check() and square == state.king_sq():
                color = theme.check_sq

            pygame.draw.rect(surface, color, (x, y, sq, sq))

            if square in state.legal_targets:
                cx, cy = x + sq // 2, y + sq // 2
                enemy = state.board.piece_at(square)
                if enemy is not None:
                    # Ring around capturable enemy piece
                    ring_r = max(6, sq * 2 // 5)
                    ring_w = max(2, sq // 16)
                    pygame.draw.circle(surface, theme.check_sq, (cx, cy), ring_r, ring_w)
                else:
                    dot_r = max(3, sq // 9)
                    pygame.draw.circle(surface, theme.move_dot, (cx, cy), dot_r)

    pygame.draw.rect(surface, theme.dark_sq, (ox, oy, sq * 8, sq * 8), 3)


def _labels(surface, theme, ox, oy, font, sq, flip=False):
    for i in range(8):
        rank_num = i + 1 if flip else 8 - i
        rank_lbl = font.render(str(rank_num), True, theme.label_color)
        surface.blit(rank_lbl, (ox + sq * 8 + 5,
                                oy + i * sq + sq // 2 - rank_lbl.get_height() // 2))
        file_idx = 7 - i if flip else i
        file_lbl = font.render(FILES[file_idx], True, theme.label_color)
        surface.blit(file_lbl, (ox + i * sq + sq // 2 - file_lbl.get_width() // 2,
                                oy + sq * 8 + 4))


def _pieces(surface, state, theme, ox, oy, sq, flip=False):
    for square in chess.SQUARES:
        if state.animating() and square == state.anim_to_sq:
            continue
        piece = state.board.piece_at(square)
        if piece is None:
            continue
        file, rank = chess.square_file(square), chess.square_rank(square)
        x, y = _sq_topleft(file, rank, ox, oy, sq, flip)
        cx, cy = x + sq // 2, y + sq // 2
        fill    = theme.white_piece   if piece.color == chess.WHITE else theme.black_piece
        outline = theme.white_outline if piece.color == chess.WHITE else theme.black_outline
        timer = state.chomp_timer if square == state.chomping_square else 0
        p.draw_piece(surface, piece, cx, cy, sq, fill, outline, timer)


def _sq_center(square, ox, oy, sq, flip=False):
    file, rank = chess.square_file(square), chess.square_rank(square)
    x, y = _sq_topleft(file, rank, ox, oy, sq, flip)
    return x + sq // 2, y + sq // 2


def _anim_piece(surface, state, theme, ox, oy, sq, flip=False):
    if not state.animating() or state.anim_piece is None:
        return
    raw = 1.0 - state.anim_timer / ANIM_DURATION
    t = raw * raw * (3 - 2 * raw)
    fx, fy = _sq_center(state.anim_from_sq, ox, oy, sq, flip)
    tx, ty = _sq_center(state.anim_to_sq,   ox, oy, sq, flip)
    cx = int(fx + t * (tx - fx))
    cy = int(fy + t * (ty - fy))
    piece   = state.anim_piece
    fill    = theme.white_piece   if piece.color == chess.WHITE else theme.black_piece
    outline = theme.white_outline if piece.color == chess.WHITE else theme.black_outline
    p.draw_piece(surface, piece, cx, cy, sq, fill, outline)


def _chomp_text(surface, state, theme, ox, oy, font, sq):
    if state.chomp_timer <= 0:
        return
    alpha = min(255, state.chomp_timer * 8)
    txt = font.render("CHOMP!", True, theme.check_sq)
    txt.set_alpha(alpha)
    surface.blit(txt, (ox + sq * 4 - txt.get_width() // 2,
                       oy + sq * 4 - txt.get_height() // 2 - 20))


def _status_bar(surface, state, theme, ox, oy, fonts, sq):
    if state.game_over:
        return
    turn = "White's turn ♙" if state.board.turn == chess.WHITE else "Black's turn ♟"
    if state.in_check():
        turn += "  ⚠ CHECK!"
    txt = fonts["lg"].render(turn, True, theme.text_color)
    surface.blit(txt, (ox, oy - fonts["lg"].get_height() - 6))


def _controls_bar(surface, state, theme, ox, oy, fonts, sq):
    font = fonts["sm"]
    txt = font.render("R — restart    ESC — menu", True, theme.label_color)
    # sit below the file labels (which use fonts["md"])
    y = oy + sq * 8 + fonts["md"].get_height() + 8
    _, H = surface.get_size()
    surface.blit(txt, (ox, min(y, H - txt.get_height() - 4)))


def _stats_bar(surface, state, theme, fonts):
    """Render game stats top-right — always visible regardless of window size."""
    font = fonts["sm"]
    H = font.get_height()
    W, _ = surface.get_size()
    # sit just below the mode label which main.py draws at y=10
    base_y = 10 + H + 8

    white_left = sum(1 for s in chess.SQUARES
                     if (pc := state.board.piece_at(s)) and pc.color == chess.WHITE)
    black_left = sum(1 for s in chess.SQUARES
                     if (pc := state.board.piece_at(s)) and pc.color == chess.BLACK)

    def fmt_caps(caps):
        if not caps:
            return "—"
        cnt: dict[int, int] = {}
        for pc in caps:
            cnt[pc.piece_type] = cnt.get(pc.piece_type, 0) + 1
        syms = {chess.QUEEN: 'Q', chess.ROOK: 'R', chess.BISHOP: 'B',
                chess.KNIGHT: 'N', chess.PAWN: 'P'}
        order = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN]
        parts = [f"{cnt[pt]}{syms[pt]}" if cnt[pt] > 1 else syms[pt]
                 for pt in order if pt in cnt]
        return ' '.join(parts)

    rows = [
        ("White", white_left, state.white_captures, state.white_checks),
        ("Black", black_left, state.black_captures, state.black_checks),
    ]
    y = base_y
    for side, left, caps, checks in rows:
        line1 = f"{side}: {left} pcs  checks: {checks}"
        line2 = f"  took: {fmt_caps(caps)}"
        for line in (line1, line2):
            txt = font.render(line, True, theme.text_color)
            surface.blit(txt, (W - txt.get_width() - 10, y))
            y += H + 2
        y += 3


def _promotion_overlay(surface, state, theme, ox, oy, fonts, sq):
    overlay = pygame.Surface((sq * 8, sq * 8), pygame.SRCALPHA)
    r, g, b = theme.banner_bg
    overlay.fill((r, g, b, 200))
    surface.blit(overlay, (ox, oy))

    heading = fonts["lg"].render("Promote pawn — choose piece:", True, theme.banner_text)
    rects = promo_rects(ox, oy, sq)
    _, first_rect = rects[0]
    surface.blit(heading, (ox + sq * 4 - heading.get_width() // 2,
                           first_rect.top - heading.get_height() - 10))

    color = state.board.turn
    fill    = theme.white_piece   if color == chess.WHITE else theme.black_piece
    outline = theme.white_outline if color == chess.WHITE else theme.black_outline
    hint = fonts["sm"].render("or press  Q / R / B / N", True, theme.banner_text)
    _, last_rect = rects[-1]
    surface.blit(hint, (ox + sq * 4 - hint.get_width() // 2,
                        last_rect.bottom + 8))

    for pt, rect in rects:
        pygame.draw.rect(surface, theme.dark_sq, rect, border_radius=6)
        pygame.draw.rect(surface, theme.label_color, rect, 2, border_radius=6)
        piece = chess.Piece(pt, color)
        p.draw_piece(surface, piece, rect.centerx, rect.centery, sq, fill, outline)
        lbl = fonts["sm"].render(PROMO_LABELS[pt], True, theme.banner_text)
        surface.blit(lbl, (rect.right - lbl.get_width() - 4, rect.top + 2))


def _game_over_banner(surface, state, theme, ox, oy, fonts, sq):
    bw, bh = sq * 8, sq * 3
    bx, by = ox, oy + sq * 2 + sq // 2
    overlay = pygame.Surface((bw, bh), pygame.SRCALPHA)
    r, g, b = theme.banner_bg
    overlay.fill((r, g, b, 210))
    surface.blit(overlay, (bx, by))
    msg = fonts["lg"].render(state.game_over_msg, True, theme.banner_text)
    sub = fonts["sm"].render("Press R to play again", True, theme.banner_text)
    surface.blit(msg, (bx + (bw - msg.get_width()) // 2, by + sq))
    surface.blit(sub, (bx + (bw - sub.get_width()) // 2, by + sq + int(sq * 0.5)))
