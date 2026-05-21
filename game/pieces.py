import pygame
import chess
from typing import Tuple
from . import sprites

Color = Tuple[int, int, int]

CHOMP_DURATION = 38
_PIECE_SCALE = 1.0


def draw_piece(
    surface: pygame.Surface,
    piece: chess.Piece,
    cx: int, cy: int,
    sq: int,
    fill: Color,
    outline: Color,
    chomp_timer: int = 0,
):
    chomping = chomp_timer > 0

    # Pop scale-up during first half of chomp
    scale = _PIECE_SCALE
    if chomp_timer > CHOMP_DURATION // 2:
        t = (chomp_timer - CHOMP_DURATION // 2) / (CHOMP_DURATION // 2)
        scale = _PIECE_SCALE + 0.14 * t

    surf = sprites.get_surface(piece, fill, outline, chomping)
    new_sz = int(sq * scale)
    surf = pygame.transform.scale(surf, (new_sz, new_sz))
    surface.blit(surf, (cx - new_sz // 2, cy - new_sz // 2))
