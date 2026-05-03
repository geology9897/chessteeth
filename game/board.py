import pygame
import chess
from .themes import Theme
from .state import GameState, ANIM_DURATION
from . import pieces as p

FILES = "abcdefgh"


def draw(surface: pygame.Surface, state: GameState, theme: Theme,
         ox: int, oy: int, fonts: dict, sq: int = 80):
    _squares(surface, state, theme, ox, oy, sq)
    _labels(surface, theme, ox, oy, fonts["sm"], sq)
    _pieces(surface, state, theme, ox, oy, sq)
    _anim_piece(surface, state, theme, ox, oy, sq)
    _chomp_text(surface, state, theme, ox, oy, fonts["chomp"], sq)
    _status_bar(surface, state, theme, ox, oy, fonts, sq)
    _controls_bar(surface, state, theme, ox, oy, fonts["sm"], sq)
    if state.game_over:
        _game_over_banner(surface, state, theme, ox, oy, fonts, sq)


def _squares(surface, state, theme, ox, oy, sq):
    for rank in range(8):
        for file in range(8):
            square = chess.square(file, rank)
            x, y = ox + file * sq, oy + (7 - rank) * sq

            is_light = (file + rank) % 2 == 1
            color = theme.light_sq if is_light else theme.dark_sq

            if square == state.selected:
                color = theme.highlight
            elif state.in_check() and square == state.king_sq():
                color = theme.check_sq

            pygame.draw.rect(surface, color, (x, y, sq, sq))

            if square in state.legal_targets:
                dot_r = max(3, sq // 9)
                pygame.draw.circle(surface, theme.move_dot,
                                   (x + sq // 2, y + sq // 2), dot_r)

    pygame.draw.rect(surface, theme.dark_sq, (ox, oy, sq * 8, sq * 8), 3)


def _labels(surface, theme, ox, oy, font, sq):
    for i in range(8):
        rank_lbl = font.render(str(8 - i), True, theme.label_color)
        surface.blit(rank_lbl, (ox + sq * 8 + 5,
                                oy + i * sq + sq // 2 - rank_lbl.get_height() // 2))
        file_lbl = font.render(FILES[i], True, theme.label_color)
        surface.blit(file_lbl, (ox + i * sq + sq // 2 - file_lbl.get_width() // 2,
                                oy + sq * 8 + 4))


def _pieces(surface, state, theme, ox, oy, sq):
    for square in chess.SQUARES:
        if state.animating() and square == state.anim_to_sq:
            continue
        piece = state.board.piece_at(square)
        if piece is None:
            continue
        file, rank = chess.square_file(square), chess.square_rank(square)
        cx = ox + file * sq + sq // 2
        cy = oy + (7 - rank) * sq + sq // 2
        fill    = theme.white_piece   if piece.color == chess.WHITE else theme.black_piece
        outline = theme.white_outline if piece.color == chess.WHITE else theme.black_outline
        timer = state.chomp_timer if square == state.chomping_square else 0
        p.draw_piece(surface, piece, cx, cy, sq, fill, outline, timer)


def _sq_center(square, ox, oy, sq):
    return (ox + chess.square_file(square) * sq + sq // 2,
            oy + (7 - chess.square_rank(square)) * sq + sq // 2)


def _anim_piece(surface, state, theme, ox, oy, sq):
    if not state.animating() or state.anim_piece is None:
        return
    raw = 1.0 - state.anim_timer / ANIM_DURATION
    t = raw * raw * (3 - 2 * raw)
    fx, fy = _sq_center(state.anim_from_sq, ox, oy, sq)
    tx, ty = _sq_center(state.anim_to_sq,   ox, oy, sq)
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


def _controls_bar(surface, state, theme, ox, oy, font, sq):
    txt = font.render("R — restart    ESC — menu", True, theme.label_color)
    # sit below file labels (which are at sq*8+4, one line tall)
    surface.blit(txt, (ox, oy + sq * 8 + font.get_height() + 8))


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
