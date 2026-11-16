# TRD: page-style rain (round 7)

## Goal

Rain that looks like the canvas reference page (https://chetan-examples.vercel.app/matrix): one stream per 25 px column, glyphs fixed in their cells, a head writing downward with a trail fading out in place, `#0affa0` on near-black. CSS only, within T3's theme rules.

## Limits

T3 Nightly 0.1.10-nightly.20261115 (upstream `e82050b8`) raised theme limits to 50,000 CSS chars and 6 x 50,000 + 16 KB = 316,384 file bytes. `build.py` checks these after inlining the SVGs. Older builds (for example 4695) still enforce 20,000 / 32,768 and reject this theme; use 4761 or later.

## Design as built

- **Field** (`src/rain-field.svg`, 1450x1000): one glyph per cell, half-width katakana, digits and A-Z, full `#0affa0`. It is the conversation background, under a horizontal gradient that dims it to 20% under the reading column.
- **Overlay** (`[data-workspace-area="conversation"]::after`): solid `--bg`, masked by `src/rain-loop.svg` (1450x3200, alpha). The mask is opaque except two windows per column: a trail of 14 to 28 cells whose alpha falls from 1 to 0 down to a clear head cell. The window shapes are drawn as separate pieces: painting a transparent gradient over an opaque rect cannot punch a hole.
- **Motion**: the overlay is 3200 px taller than the conversation and moves down `translateY(3200px)` in `steps(128)` over 7.62 s (420 px/s, one cell per step). Glyphs stay; windows move.
- **Intro**: `::before`, a gradient curtain (clear top edge fading to `--bg` over 500 px) covering the streams, slides down 2000 px in 4.76 s and stays off-screen.
- **Reduced motion and windows under 62rem**: no curtain; the overlay is a still frame (`translateY(1250px)`).
- Generator: `python3 -I design/gen-page-rain.py [seed]` writes both SVGs.

## Rejected

- Three mask layers composited (`intersect`, `add`) for an intro wall of heads: correct look, but Chrome repainted the mask every step (17 to 20 s of raster per 5 s, 25 frames/s). One mask layer stays composited.
- Two stacked opaque overlays (intro + loop): the field shows only where both are clear.
- Animating inside an SVG: re-rasterised every frame, and reduced motion cannot stop it.

## Measured

Headless Chrome 157, no GPU, 1440x900 at DPR 2, 5 s traces, test page with the theme CSS:

| | busy main ms | busy fps | idle main ms | raster ms | paints |
|---|---|---|---|---|---|
| old two-layer rain | 35.0 | 57.4 | 0.3 | 215-234 | 0 |
| page rain | 22.1 | 60.0 | 0.7 | 454-460 | 0 |

Raster runs on raster threads; the cost comes from the 3200 px taller overlay layer. Not yet measured in the real app or on a GPU.

## Remaining

- Check in the real app (4761): scrolling, streaming, panels overlapping the column, the draft screen.
- Phase B: pills, top bar, project picker, branch rail, surface panel, selects and comboboxes, the composer drawer, settings, diff, file tree, kbd, sidebar chrome, toolbar.
- Phase C: watchers and text motion; needs Chromium 156 (T3 4761 ships Electron 44, Chromium 152).
