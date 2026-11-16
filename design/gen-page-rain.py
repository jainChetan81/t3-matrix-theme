#!/usr/bin/env python3
"""Generate the page-style rain: a fixed glyph field and the alpha mask that reveals it.

The field (src/rain-field.svg) holds one 25 px glyph per cell. The mask (src/rain-loop.svg) is
opaque except one window per column: a trail whose alpha falls from 1 to 0 down to a clear head
cell. theme.css moves the mask down one cell per step, so heads pass over fixed glyphs.
Usage: python3 -I design/gen-page-rain.py [seed]
"""
import random
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "src"
CELL = 25
COLS = 58  # 1450 px
ROWS = 40  # field height 1000 px
PERIOD = 3200  # mask tile height; 7.62 s at 420 px/s
HALF = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ"
GLYPHS = HALF + "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 23
rng = random.Random(SEED)
W = COLS * CELL


def field():
    xs = " ".join(str(c * CELL + 12) for c in range(COLS))
    rows = "".join(
        f'<text x="{xs}" y="{r * CELL + 21}">{"".join(rng.choice(GLYPHS) for _ in range(COLS))}</text>'
        for r in range(ROWS))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{ROWS * CELL}">'
            '<style>text{font:25px ui-monospace,monospace;text-anchor:middle;fill:#0affa0}</style>'
            f'{rows}</svg>\n')


def mask():
    # Two streams per column, heads spread over the whole period, so the density stays even.
    firsts = [(c * 31 % 128) * CELL for c in range(COLS)]
    rng.shuffle(firsts)
    solid, trails = [], []
    for c, first in enumerate(firsts):
        x = c * CELL
        clear = []
        for head in (first, (first + rng.randint(52, 76) * CELL) % PERIOD):
            trail = rng.randint(14, 28) * CELL
            top = head - trail
            for shift in (0, PERIOD, -PERIOD):
                # The gradient spans the whole trail even where the tile edge cuts it.
                if top + shift < PERIOD and head + shift > 0:
                    trails.append(f'<rect x="{x}" y="{top + shift}" width="25" height="{trail}" fill="url(#f)"/>')
                a, b = max(top + shift, 0), min(head + CELL + shift, PERIOD)
                if a < b:
                    clear.append((a, b))
        y = 0
        for a, b in sorted(clear):
            if a > y:
                solid.append(f'M{x} {y}h25v{a - y}h-25z')
            y = max(y, b)
        if y < PERIOD:
            solid.append(f'M{x} {y}h25v{PERIOD - y}h-25z')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{PERIOD}">'
            '<linearGradient id="f" x2="0" y2="1"><stop offset=".1"/><stop offset="1" stop-opacity="0"/></linearGradient>'
            f'<path d="{"".join(solid)}"/>{"".join(trails)}</svg>\n')


(OUT / "rain-field.svg").write_text(field())
(OUT / "rain-loop.svg").write_text(mask())
print(f"page rain: seed {SEED}, {COLS} columns, {PERIOD // CELL} cell period")
