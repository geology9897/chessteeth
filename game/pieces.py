import pygame
import chess
from typing import Tuple
from . import sprites

Color = Tuple[int, int, int]

CHOMP_DURATION = 38


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
    scale = 1.0
    if chomp_timer > CHOMP_DURATION // 2:
        t = (chomp_timer - CHOMP_DURATION // 2) / (CHOMP_DURATION // 2)
        scale = 1.0 + 0.14 * t

    surf = sprites.get_surface(piece, fill, outline, chomping)

    if scale != 1.0 or surf.get_width() != sq:
        new_sz = int(sq * scale)
        surf = pygame.transform.scale(surf, (new_sz, new_sz))
    else:
        new_sz = sq

    surface.blit(surf, (cx - new_sz // 2, cy - new_sz // 2))
