#!/usr/bin/env python3
"""Render assets/banner.txt (braille ASCII art) into assets/banner.png.

No fonts involved: each braille character's codepoint (U+2800 + dot mask)
is decoded bit by bit and every set dot is drawn as a small filled square,
so unicode braille glyph coverage of the rendering font is irrelevant.
"""

from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).parent
TXT_PATH = HERE / "banner.txt"
PNG_PATH = HERE / "banner.png"

BG_COLOR = "#1a2f4a"
DOT_COLOR = "#d8d5a8"

BRAILLE_BASE = 0x2800

# Standard braille dot numbering -> (col, row) in a 2x4 cell.
# bit 0 = dot 1 (0,0)  bit 3 = dot 4 (1,0)
# bit 1 = dot 2 (0,1)  bit 4 = dot 5 (1,1)
# bit 2 = dot 3 (0,2)  bit 5 = dot 6 (1,2)
# bit 6 = dot 7 (0,3)  bit 7 = dot 8 (1,3)
DOT_POSITIONS = [
    (0, 0), (0, 1), (0, 2), (1, 0),
    (1, 1), (1, 2), (0, 3), (1, 3),
]

DOT_SIZE = 3        # side length (px) of each drawn dot
COL_SPACING = 5      # px between the two dot columns within a cell
ROW_SPACING = 5      # px between dot rows within a cell
CHAR_GAP = 3          # extra horizontal px between characters
LINE_GAP = 3          # extra vertical px between lines
PADDING = 20


def dot_mask(ch: str) -> int:
    cp = ord(ch)
    if BRAILLE_BASE <= cp <= BRAILLE_BASE + 0xFF:
        return cp - BRAILLE_BASE
    return 0


def main():
    lines = TXT_PATH.read_text(encoding="utf-8").splitlines()
    max_cols = max((len(line) for line in lines), default=0)

    cell_w = COL_SPACING + CHAR_GAP
    cell_h = ROW_SPACING * 3 + LINE_GAP

    img_w = PADDING * 2 + max_cols * cell_w
    img_h = PADDING * 2 + len(lines) * cell_h

    img = Image.new("RGB", (img_w, img_h), BG_COLOR)
    draw = ImageDraw.Draw(img)

    for row_idx, line in enumerate(lines):
        cell_y = PADDING + row_idx * cell_h
        for col_idx, ch in enumerate(line):
            mask = dot_mask(ch)
            if not mask:
                continue
            cell_x = PADDING + col_idx * cell_w
            for bit in range(8):
                if not (mask & (1 << bit)):
                    continue
                dot_col, dot_row = DOT_POSITIONS[bit]
                cx = cell_x + dot_col * COL_SPACING
                cy = cell_y + dot_row * ROW_SPACING
                draw.rectangle(
                    [cx, cy, cx + DOT_SIZE - 1, cy + DOT_SIZE - 1],
                    fill=DOT_COLOR,
                )

    img.save(PNG_PATH)
    print(f"Saved {PNG_PATH} ({img_w}x{img_h})")


if __name__ == "__main__":
    main()
