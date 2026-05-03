import sys
import random
import pygame
import chess
from .state import GameState
from .themes import THEMES
from . import board as board_mod
from .bot import BotEngine, DIFFICULTIES, find_stockfish

FPS = 60


def _layout(w, h):
    """Return (sq, board_x, board_y) for the given window size."""
    sq = max(40, min((w - 60) // 8, (h - 130) // 8))
    board_px = sq * 8
    bx = (w - board_px) // 2
    by = (h - board_px) // 2 + 10
    return sq, bx, by


def _make_fonts(sq):
    f = max(0.5, sq / 80)
    return {
        "title": pygame.font.SysFont("Arial", max(20, int(46 * f)), bold=True),
        "lg":    pygame.font.SysFont("Arial", max(13, int(26 * f)), bold=True),
        "md":    pygame.font.SysFont("Arial", max(11, int(22 * f))),
        "key":   pygame.font.SysFont("Arial", max(11, int(20 * f)), bold=True),
        "sm":    pygame.font.SysFont("Arial", max(9,  int(16 * f))),
        "chomp": pygame.font.SysFont("Arial", max(20, int(52 * f)), bold=True),
    }


def _sq_from_mouse(mx, my, bx, by, sq):
    rx, ry = mx - bx, my - by
    if not (0 <= rx < sq * 8 and 0 <= ry < sq * 8):
        return None
    return chess.square(rx // sq, 7 - (ry // sq))


# ── menu ──────────────────────────────────────────────────────────────────────

_MODE_OPTS  = [("H", "Human vs Human"), ("B", "Play vs Bot")]
_DIFF_OPTS  = [(str(n), lbl) for n, lbl, *_ in DIFFICULTIES]
_COLOR_OPTS = [("W", "White  (you move first)"),
               ("B", "Black  (bot moves first)"),
               ("R", "Random")]


def _draw_menu(screen, theme, fonts, step, cursor, diff, sf_ok):
    screen.fill(theme.background)
    W, H = screen.get_size()

    title = fonts["title"].render("ChessTeeth", True, theme.text_color)
    screen.blit(title, (W // 2 - title.get_width() // 2, H // 8))
    pygame.draw.line(screen, theme.dark_sq, (40, H // 8 + title.get_height() + 8),
                     (W - 40, H // 8 + title.get_height() + 8), 2)

    if step == "mode":
        opts = _MODE_OPTS if sf_ok else _MODE_OPTS[:1]
        heading = "Choose Mode"
    elif step == "difficulty":
        opts = _DIFF_OPTS
        heading = "Bot Difficulty"
    else:
        _, dlbl, *_ = DIFFICULTIES[diff - 1]
        opts = _COLOR_OPTS
        heading = f"Play vs Bot ({dlbl})  —  your colour"

    h2 = fonts["lg"].render(heading, True, theme.label_color)
    start_y = H // 8 + title.get_height() + 30
    screen.blit(h2, (W // 2 - h2.get_width() // 2, start_y))

    row_h = max(44, int(H * 0.07))
    box_w = min(500, int(W * 0.65))
    opt_y = start_y + h2.get_height() + 16

    for i, (key, label) in enumerate(opts):
        y      = opt_y + i * row_h
        active = (i == cursor)
        bg     = theme.highlight if active else theme.dark_sq
        fg     = theme.text_color if active else theme.banner_text
        pygame.draw.rect(screen, bg,
                         (W // 2 - box_w // 2, y, box_w, row_h - 8), border_radius=7)
        pygame.draw.rect(screen, theme.label_color,
                         (W // 2 - box_w // 2, y, box_w, row_h - 8), 2, border_radius=7)
        key_s = fonts["key"].render(f"[{key}]", True, fg)
        lbl_s = fonts["md"].render(label, True, fg)
        screen.blit(key_s, (W // 2 - box_w // 2 + 16, y + (row_h - 8 - key_s.get_height()) // 2))
        screen.blit(lbl_s, (W // 2 - box_w // 2 + 16 + key_s.get_width() + 12,
                            y + (row_h - 8 - lbl_s.get_height()) // 2))

    if not sf_ok and step == "mode":
        warn = fonts["sm"].render("Stockfish not found — bot unavailable", True, theme.check_sq)
        screen.blit(warn, (W // 2 - warn.get_width() // 2,
                           opt_y + len(opts) * row_h + 8))

    hint = fonts["sm"].render("↑↓ navigate    Enter / letter key — select    ESC — back",
                              True, theme.label_color)
    screen.blit(hint, (W // 2 - hint.get_width() // 2, H - hint.get_height() - 16))

    pygame.display.flip()


def _mode_label(bot, bot_color):
    if bot is None:
        return "Human vs Human"
    _, dlbl, *_ = DIFFICULTIES[bot.difficulty - 1]
    side = "White" if bot_color == chess.WHITE else "Black"
    return f"Bot ({dlbl}) plays {side}"


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((700, 800), pygame.RESIZABLE)
    pygame.display.set_caption("ChessTeeth")
    clock = pygame.time.Clock()

    prev_size = screen.get_size()
    sq, bx, by = _layout(*prev_size)
    fonts = _make_fonts(sq)

    theme  = THEMES[0]
    sf_ok  = find_stockfish() is not None
    step   = "mode"
    cursor = 0
    sel_diff = 2

    state:     GameState | None   = None
    bot:       BotEngine | None   = None
    bot_color: chess.Color | None = None
    in_game = False

    def _opts():
        if step == "mode":   return _MODE_OPTS if sf_ok else _MODE_OPTS[:1]
        if step == "difficulty": return _DIFF_OPTS
        return _COLOR_OPTS

    def start_game(b, bc):
        nonlocal state, bot, bot_color, in_game
        state, bot, bot_color, in_game = GameState(), b, bc, True
        if bot and bot_color == chess.WHITE:
            bot.request_move(state.board)

    def back_to_menu():
        nonlocal state, bot, bot_color, in_game, step, cursor
        if bot: bot.close()
        state = bot = bot_color = None
        in_game = False
        step = "mode"; cursor = 0

    def select_option(idx):
        nonlocal step, cursor, sel_diff, sf_ok
        if step == "mode":
            if idx == 0: start_game(None, None)
            elif idx == 1 and sf_ok: step = "difficulty"; cursor = sel_diff - 1
        elif step == "difficulty":
            sel_diff = idx + 1; step = "color"; cursor = 0
        elif step == "color":
            player_color = [chess.WHITE, chess.BLACK,
                            random.choice([chess.WHITE, chess.BLACK])][idx]
            b = BotEngine(sel_diff)
            if b.start():
                start_game(b, chess.BLACK if player_color == chess.WHITE else chess.WHITE)
            else:
                sf_ok = False; step = "mode"; cursor = 0

    while True:
        # ── recompute layout on resize ─────────────────────────────────────────
        cur_size = screen.get_size()
        if cur_size != prev_size:
            sq, bx, by = _layout(*cur_size)
            fonts = _make_fonts(sq)
            prev_size = cur_size

        # ── menu ──────────────────────────────────────────────────────────────
        if not in_game:
            _draw_menu(screen, theme, fonts, step, cursor, sel_diff, sf_ok)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                elif event.type == pygame.KEYDOWN:
                    k    = event.key
                    opts = _opts()
                    n    = len(opts)

                    if k == pygame.K_ESCAPE:
                        if step == "mode": pygame.quit(); sys.exit()
                        elif step == "difficulty": step = "mode"; cursor = 0
                        else: step = "difficulty"; cursor = sel_diff - 1

                    elif k in (pygame.K_UP, pygame.K_w):
                        cursor = (cursor - 1) % n
                    elif k in (pygame.K_DOWN, pygame.K_s):
                        cursor = (cursor + 1) % n
                    elif k in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        select_option(cursor); cursor = 0
                    else:
                        for i, (key, _) in enumerate(opts):
                            if k == getattr(pygame, f"K_{key.lower()}"):
                                cursor = i; select_option(i); cursor = 0; break

            clock.tick(FPS)
            continue

        # ── game ──────────────────────────────────────────────────────────────
        assert state is not None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if bot: bot.close()
                pygame.quit(); sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q, pygame.K_r):
                    back_to_menu(); break

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state.game_over or state.animating(): continue
                if bot and state.board.turn == bot_color: continue
                clicked = _sq_from_mouse(*event.pos, bx, by, sq)
                if clicked is None: continue
                if state.selected is not None:
                    if state.try_move(clicked):
                        if bot and not state.game_over and state.board.turn == bot_color:
                            bot.request_move(state.board)
                    else:
                        state.select(clicked)
                else:
                    state.select(clicked)

        if not in_game:
            continue

        if bot and not state.animating() and not state.game_over:
            if state.board.turn == bot_color:
                move = bot.poll_move()
                if move: state.apply_move(move)

        state.tick()
        screen.fill(theme.background)

        W, H = screen.get_size()
        mode_txt = fonts["sm"].render(_mode_label(bot, bot_color), True, theme.label_color)
        screen.blit(mode_txt, (W - mode_txt.get_width() - 10, 10))

        if bot and (bot.thinking() or (state.board.turn == bot_color and not state.game_over)):
            th = fonts["sm"].render("Bot is thinking…", True, theme.check_sq)
            screen.blit(th, (bx, by - th.get_height() - 6))

        board_mod.draw(screen, state, theme, bx, by, fonts, sq)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
