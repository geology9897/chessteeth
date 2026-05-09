"""
Pixel-art chess piece sprites drawn in 32×32 logical space, stored as 128×128 PNGs.

Normal state: proper chess piece silhouettes, no face.
Chomp state:  same silhouette but with a gaping toothed mouth (the "chessteeth" moment).

PNGs are written to game/assets/ on first run (filename includes canvas size).
Edit them in any image editor — the game loads from disk.
"""
from __future__ import annotations
import io, os
import chess
import pygame
from PIL import Image, ImageDraw

_SCALE   = 2          # internal drawing space is 32×32; multiply all coords by this
_SZ      = 32 * _SCALE  # = 64 — canvas for PIL drawing
_DISPLAY = 80         # PNG stored at this size; disk PNGs are already 80×80
_ASSETS  = os.path.join(os.path.dirname(__file__), "assets")
_cache: dict[str, pygame.Surface] = {}

_PIECE_NAMES  = {chess.PAWN:"pawn", chess.ROOK:"rook", chess.KNIGHT:"knight",
                 chess.BISHOP:"bishop", chess.QUEEN:"queen", chess.KING:"king"}
_COLOR_NAMES  = {chess.WHITE:"white", chess.BLACK:"black"}


# ── colour helpers ────────────────────────────────────────────────────────────

def _c(rgb, a=255):     return rgb + (a,)
def _dk(rgb, n=40):     return tuple(max(0,   v-n) for v in rgb) + (255,)
def _lk(rgb, n=40):     return tuple(min(255, v+n) for v in rgb) + (255,)


# ── drawing primitives (32×32 logical space — all coords scaled by _SCALE) ───

def _r(d, x, y, w, h, col):
    s = _SCALE
    if w > 0 and h > 0:
        d.rectangle([(x*s, y*s), (x*s + w*s - 1, y*s + h*s - 1)], fill=col)

def _e(d, x0, y0, x1, y1, fill, outline=None):
    s = _SCALE
    d.ellipse([(x0*s, y0*s), (x1*s, y1*s)], fill=fill, outline=outline)

def _p(d, x, y, col):
    s = _SCALE
    base = _SZ // s
    if 0 <= x < base and 0 <= y < base:
        d.rectangle([(x*s, y*s), (x*s+s-1, y*s+s-1)], fill=col)

def _tri(d, pts, fill, outline=None):
    s = _SCALE
    d.polygon([(px*s, py*s) for px, py in pts], fill=fill, outline=outline)

def _hline(d, x, y, w, col):
    _r(d, x, y, w, 1, col)

def _vline(d, x, y, h, col):
    _r(d, x, y, 1, h, col)


# ── shared "bite" mouth ───────────────────────────────────────────────────────

def _chomp_mouth(d, mx, my, mw, mh, TW, MI, GR):
    """Horizontal toothed gash. mx,my = top-left, mw×mh = size."""
    _r(d, mx, my, mw, mh, MI)
    # upper teeth: evenly spaced, 2px wide × ½ height tall
    n     = max(2, mw // 4)
    tw    = max(2, mw // n)
    tooth_h = max(2, mh // 2)
    for i in range(n):
        tx = mx + i * (mw // n) + 1
        if tx + tw - 1 < mx + mw:
            _r(d, tx, my, tw, tooth_h, TW)
    # lower teeth (offset)
    for i in range(n - 1):
        tx = mx + i * (mw // n) + mw // (n * 2)
        if tx + tw - 1 < mx + mw:
            _r(d, tx, my + mh - tooth_h, tw, tooth_h, TW)
    # tongue
    _r(d, mx + mw//4, my + mh - 2, mw // 2, 2, GR)


# ── piece silhouettes ─────────────────────────────────────────────────────────

def _pawn(d, F, D, H, TW, MI, GR, chomping):
    _e(d,  3, 26, 28, 31, F, D)            # base
    _e(d,  8, 21, 23, 26, F, D)            # lower body
    _r(d, 13, 17,  6,  6, F)               # waist
    _vline(d, 13, 17, 6, D);  _vline(d, 18, 17, 6, D)
    _e(d,  9, 15, 22, 20, F, D)            # collar
    _e(d,  8,  2, 23, 17, F, D)            # head
    _e(d, 11,  4, 18,  9, H)               # highlight
    if chomping:
        _chomp_mouth(d, 10, 9, 12, 6, TW, MI, GR)


def _rook(d, F, D, H, TW, MI, GR, chomping):
    _e(d,  2, 26, 29, 31, F, D)            # base
    _r(d,  6, 18, 20,  9, F)               # lower body
    _vline(d,  6, 18, 9, D);  _vline(d, 25, 18, 9, D)
    _hline(d,  6, 26, 20, D)
    _r(d,  7,  8, 18, 11, F)               # upper body
    _vline(d,  7,  8, 11, D);  _vline(d, 24,  8, 11, D)
    _hline(d,  7, 18, 18, D)
    _hline(d,  7,  8, 18, D)
    # 3 merlons
    for bx in (7, 14, 21):
        _r(d, bx, 1, 5, 8, F)
        _vline(d, bx,   1, 8, D);  _vline(d, bx+4, 1, 8, D)
        _hline(d, bx,   1, 5, D)
    # merlon gaps (inner shadow)
    _r(d, 12,  3, 2, 6, D)
    _r(d, 19,  3, 2, 6, D)
    _r(d,  8,  9, 3, 9, H)                 # highlight
    if chomping:
        _chomp_mouth(d, 8, 11, 16, 6, TW, MI, GR)


def _knight(d, F, D, H, TW, MI, GR, chomping):
    _e(d,  2, 26, 29, 31, F, D)            # base
    # neck block
    _r(d,  5, 18, 10, 10, F)
    _vline(d,  5, 18, 10, D);  _vline(d, 14, 18, 10, D)
    _hline(d,  5, 27, 10, D)
    # head body
    _r(d,  9,  6, 15, 14, F)
    _vline(d,  9,  6, 14, D);  _vline(d, 23,  6, 14, D)
    _hline(d,  9,  6, 15, D);  _hline(d,  9, 19, 15, D)
    # muzzle (right extension)
    _r(d, 21,  9,  9, 10, F)
    _vline(d, 29,  9, 10, D)
    _hline(d, 21,  9,  9, D);  _hline(d, 21, 18,  9, D)
    # ear
    _r(d, 11,  1,  6,  6, F)
    _vline(d, 11,  1, 6, D);  _vline(d, 16,  1, 6, D)
    _hline(d, 11,  1, 6, D)
    # nostril
    _r(d, 27, 15,  2,  2, D)
    # eye (white sclera + dark pupil)
    _r(d, 20,  8,  4,  4, (255, 255, 255, 255))
    _r(d, 20,  8,  2,  4, D)
    # mane shading
    _r(d,  9,  8,  3, 10, _lk(F[:-1], 15))
    # highlight
    _r(d, 10,  7,  4,  5, H)
    if chomping:
        # horse mouth opens naturally in the muzzle
        _chomp_mouth(d, 21, 12, 8, 5, TW, MI, GR)
    else:
        # closed lips line
        _hline(d, 22, 15, 6, D)


def _bishop(d, F, D, H, TW, MI, GR, chomping):
    _e(d,  3, 26, 28, 31, F, D)            # base
    _e(d,  7, 19, 24, 27, F, D)            # lower body
    _r(d, 10, 13, 12,  8, F)               # body stem
    _vline(d, 10, 13, 8, D);  _vline(d, 21, 13, 8, D)
    _hline(d, 10, 20, 12, D)
    # mitre hat (triangle)
    _tri(d, [(16, 1), (7, 13), (25, 13)], F, D)
    # hat band
    _r(d,  9, 11, 14,  3, D)
    _r(d,  9, 11, 14,  2, _lk(F[:-1], 10))
    # orb on tip
    _e(d, 13,  1,  19,  6, F, D)
    _e(d, 14,  2,  17,  4, H)
    # highlight on body
    _r(d, 11, 14,  4,  6, H)
    if chomping:
        _chomp_mouth(d, 10, 14, 12, 5, TW, MI, GR)


def _queen(d, F, D, H, TW, MI, GR, chomping):
    _e(d,  1, 26, 30, 31, F, D)            # base
    _e(d,  5, 20, 26, 27, F, D)            # lower body
    _r(d,  7, 11, 18, 11, F)               # body
    _vline(d,  7, 11, 11, D);  _vline(d, 24, 11, 11, D)
    _hline(d,  7, 21, 18, D)
    # crown: 5 spikes pointing up from row 11
    for sx, ty in [(7,4),(10,7),(15,2),(20,7),(23,4)]:
        _tri(d, [(sx,11),(sx+4,11),(sx+2,ty)], F, D)
    # crown band (row 8-11)
    _r(d,  6,  8, 20,  4, F)
    _hline(d,  6,  8, 20, D);  _hline(d,  6, 11, 20, D)
    _vline(d,  6,  8,  4, D);  _vline(d, 25,  8,  4, D)
    # jewels on tall spikes
    for sx, ty in [(7,4),(15,2),(23,4)]:
        _r(d, sx+1, ty+1, 2, 2, _c((200, 70, 110)))
    # highlight
    _r(d,  8, 12,  4,  8, H)
    if chomping:
        _chomp_mouth(d, 8, 13, 16, 6, TW, MI, GR)


def _king(d, F, D, H, TW, MI, GR, chomping):
    _e(d,  1, 26, 30, 31, F, D)            # base
    _e(d,  5, 20, 26, 27, F, D)            # lower body
    _r(d,  7, 11, 18, 11, F)               # body
    _vline(d,  7, 11, 11, D);  _vline(d, 24, 11, 11, D)
    _hline(d,  7, 21, 18, D)
    # crown: 3 spikes
    for sx, ty in [(7,6),(13,3),(21,6)]:
        _tri(d, [(sx,11),(sx+5,11),(sx+2,ty)], F, D)
    _r(d,  6,  8, 20,  4, F)
    _hline(d,  6,  8, 20, D);  _hline(d,  6, 11, 20, D)
    _vline(d,  6,  8,  4, D);  _vline(d, 25,  8,  4, D)
    # cross on centre spike
    _r(d, 14,  1,  4, 10, F)               # vertical bar
    _r(d, 10,  5,  12, 3, F)               # horizontal bar
    _vline(d, 14,  1,  10, D);  _vline(d, 17,  1, 10, D)
    _hline(d, 14,  1,  4,  D);  _hline(d, 14, 10,  4, D)
    _hline(d, 10,  5,  12, D);  _hline(d, 10,  7, 12, D)
    _vline(d, 10,  5,   3, D);  _vline(d, 21,  5,  3, D)
    # highlight
    _r(d,  8, 12,  4,  8, H)
    if chomping:
        _chomp_mouth(d, 8, 13, 16, 6, TW, MI, GR)


_DRAWERS = {
    chess.PAWN: _pawn, chess.ROOK: _rook, chess.KNIGHT: _knight,
    chess.BISHOP: _bishop, chess.QUEEN: _queen, chess.KING: _king,
}


# ── generation & I/O ──────────────────────────────────────────────────────────

def _generate(piece_type, fill_rgb, outline_rgb, chomping) -> Image.Image:
    img = Image.new("RGBA", (_SZ, _SZ), (0, 0, 0, 0))
    d   = ImageDraw.Draw(img)
    F   = _c(fill_rgb)
    D   = _c(outline_rgb)
    H   = _lk(fill_rgb, 35)
    TW  = (252, 252, 248, 255)
    MI  = (30,   10,  10, 255)
    GR  = (200,  50,  70, 255)
    _DRAWERS[piece_type](d, F, D, H, TW, MI, GR, chomping)
    return img


def _asset_path(piece_type, color, chomping) -> str:
    state = "chomp" if chomping else "normal"
    return os.path.join(_ASSETS, f"{_PIECE_NAMES[piece_type]}_{_COLOR_NAMES[color]}_{state}.png")


def export_all(fill_white, outline_white, fill_black, outline_black):
    """Write all 24 PNGs to assets/. Safe to call any time to regenerate."""
    os.makedirs(_ASSETS, exist_ok=True)
    for pt in chess.PIECE_TYPES:
        for color, fill, outline in [(chess.WHITE, fill_white, outline_white),
                                     (chess.BLACK, fill_black, outline_black)]:
            for chomping in (False, True):
                _generate(pt, fill, outline, chomping).save(_asset_path(pt, color, chomping))
    print(f"Exported 24 sprites → {_ASSETS}/")


def get_surface(piece: chess.Piece, fill_rgb: tuple, outline_rgb: tuple,
                chomping: bool = False) -> pygame.Surface:
    path = _asset_path(piece.piece_type, piece.color, chomping)
    if path in _cache:
        return _cache[path]
    if os.path.exists(path):
        img = Image.open(path).convert("RGBA")
    else:
        img = _generate(piece.piece_type, fill_rgb, outline_rgb, chomping)
    big  = img.resize((_DISPLAY, _DISPLAY), Image.NEAREST)
    buf  = io.BytesIO();  big.save(buf, "PNG");  buf.seek(0)
    surf = pygame.image.load(buf, "png")
    _cache[path] = surf
    return surf
