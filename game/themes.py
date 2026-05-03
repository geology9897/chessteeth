from dataclasses import dataclass
from typing import Tuple

Color = Tuple[int, int, int]


@dataclass
class Theme:
    name: str
    light_sq: Color
    dark_sq: Color
    white_piece: Color
    white_outline: Color
    black_piece: Color
    black_outline: Color
    highlight: Color
    move_dot: Color
    background: Color
    label_color: Color
    text_color: Color
    banner_bg: Color
    banner_text: Color
    check_sq: Color


THEMES: list[Theme] = [
    Theme(
        name="Parchment",
        light_sq=(238, 224, 194),
        dark_sq=(155, 95, 55),
        white_piece=(248, 240, 222),
        white_outline=(115, 65, 25),
        black_piece=(95, 35, 25),
        black_outline=(55, 18, 8),
        highlight=(215, 175, 55),
        move_dot=(75, 135, 75),
        background=(208, 188, 158),
        label_color=(90, 50, 20),
        text_color=(58, 28, 8),
        banner_bg=(135, 75, 35),
        banner_text=(248, 238, 208),
        check_sq=(175, 38, 18),
    ),
]
