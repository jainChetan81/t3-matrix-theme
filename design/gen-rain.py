#!/usr/bin/env python3
"""Generate src/rain.svg: a sparse 1000x650 glyph field (25 px cells, 40 x 26).

Short streams (bright head, fading trail) plus loose single glyphs, like the Possessed boards.
Everything sits on the 25 px grid so steps(26) moves the tile exactly one cell per step, and
nothing crosses the tile edge, so the tile repeats cleanly. Deterministic (fixed seed).
Usage: python3 -I design/gen-rain.py [seed]
"""
import random
import sys
from pathlib import Path

W, H, CELL = 40, 26, 25
GLYPHS = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワン0123456789"
seed = int(sys.argv[1]) if len(sys.argv) > 1 else 7
rnd = random.Random(seed)

used = set()
cls = {"h": [], "b": [], "r": [], "q": [], "t": []}


def put(c, col, row):
    used.add((col, row))
    cls[c].append((col * CELL + 12, row * CELL + 20, rnd.choice(GLYPHS)))


def free(col, row):
    return all((col + dx, row) not in used for dx in (-1, 0, 1))


# streams: head at the bottom, 1-4 trail glyphs above it, never wrapping the tile edge
cols = list(range(W))
rnd.shuffle(cols)
for col in cols[:14]:
    n = rnd.choice([1, 2, 2, 3, 3, 4])
    row = rnd.randrange(n, H)
    if not all(free(col, row - k) for k in range(n + 1)):
        continue
    put("h", col, row)
    for k in range(1, n + 1):
        put("b" if k == 1 and n > 1 else "r" if k <= 2 else "q", col, row - k)

# loose glyphs: mostly dim, a few mid, some small
want = {"b": 7, "r": 18, "q": 24, "t": 18}
for c, n in want.items():
    tries = 0
    while n and tries < 4000:
        tries += 1
        col, row = rnd.randrange(W), rnd.randrange(H)
        if (col, row) in used or (c != "t" and not free(col, row)):
            continue
        put(c, col, row)
        n -= 1

style = (
    "text{font:21px ui-monospace,monospace;text-anchor:middle;fill:#12e08f;fill-opacity:.85}"
    ".r{fill:#0c9c63;fill-opacity:.6}.q{fill:#0a6b45;fill-opacity:.5}"
    ".t{font-size:13px;fill:#0c9c63;fill-opacity:.5}"
    ".h{fill:#d6ffe9;fill-opacity:1;stroke:#0affa0;stroke-opacity:.35;stroke-width:3px;paint-order:stroke}"
)
out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="650"><style>{style}</style>']
for c in "qtrbh":
    pts = sorted(cls[c])
    xs = " ".join(str(x) for x, _, _ in pts)
    ys = " ".join(str(y - (4 if c == "t" else 0)) for _, y, _ in pts)
    attr = "" if c == "b" else f' class="{c}"'
    out.append(f'<text{attr} x="{xs}" y="{ys}">{"".join(g for _, _, g in pts)}</text>')
out.append("</svg>")
svg = "".join(out)
Path(__file__).resolve().parents[1].joinpath("src", "rain.svg").write_text(svg + "\n")
print(f"rain.svg: {len(svg)} chars, {sum(len(v) for v in cls.values())} glyphs", {k: len(v) for k, v in cls.items()})
