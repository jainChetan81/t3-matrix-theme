# possessed — t3 code theme

digital rain plus a live phosphor terminal. css and embedded svg only.

## files

| file | what it is |
|---|---|
| `src/possessed.css` | theme source. `@{hook}` marks a hook placeholder. |
| `src/rain.svg` | the rain tile, 1000×650. one tile feeds all three depths. |
| `src/spinner.svg` | 14×14 glyph cycler that replaces any lucide loader icon. |
| `hooks.json` | hook name → selector. **fill in t3 code's real selectors.** |
| `palette.json` | colour roles, syntax, terminal ansi. rename the keys to the theme file's role names. |
| `build.mjs` | swaps hooks, inlines the svgs, minifies, counts chars. |
| `dist/possessed.css` | built output with the placeholder hooks. |

## build

```sh
node build.mjs            # uses ./hooks.json
node build.mjs my-hooks.json
```

the script fails if the result is over 20,000 chars. current output:

```
total 14,735 chars / 20,000 (73.7%)
  art 7,221 · rules 7,514 · headroom 5,265
```

## hooks used

`sidebar`, `thread-row`, `thread-row-active`, `thread-row-running`, `project-monogram`, `chat-header`, `chat-title`, `conversation`, `message-row`, `message-row-assistant`, `user-bubble`, `assistant-markdown`, `code-block`, `composer-card`, `composer-input`, `terminal-drawer`, `tooltip`, `menu`, `popover`, `dialog`, `input`, `select`, `switch-checked`, `button`. lucide icons are targeted by class (`.lucide`, `[class*="lucide-loader"]`).

if a hook maps to a selector list, the build wraps it in `:is()`. a missing hook is reported and gets a selector that matches nothing.

## the rain

| depth | where | size | motion | opacity |
|---|---|---|---|---|
| still field | element background | tile at 40% (400×260) under an 83% wash | none | ~17% |
| far | `::after` | tile at 60% (600×390), 15px cells | 26 steps per 8.1 s = 48 px/s | .42 (sidebar .30) |
| near | `::before` | tile at 100% (1000×650), 25px cells | 26 steps per 3.7 s = 176 px/s | .60 (sidebar .42) |

- streams are continuous columns of 10–20 glyphs (plus some 4–8). the old end is dark green and the head is near-white with a halo. every column has a stream, and streams wrap the tile edge.
- motion is `steps()`, one cell per step, like the reference redrawing heads cell by cell. each screen cell changes glyph about 7 times a second, so the rain reads as mutating without animating anything inside the svg.
- the three depths use different sizes and x offsets, and the sidebar uses different offsets again. in a 1176×848 conversation area, the near tile repeats in a 176 px strip across and about 200 px down. bigger windows show more repeats.
- while the composer is focused, the rain drops to .26 / .20 opacity.

## effects

- **boot:** message rows flicker in (stepped opacity, staggered from the bottom up) and a scan line wipes down each row once when it mounts.
- **glitch:** the chat title jumps and splits colour for about 140 ms every 11 s.
- **roll bar:** a faint band crosses the window every 16 s.
- **decoding:** running thread rows get a moving sheen, and every lucide loader becomes a cycling glyph.
- **composer:** `❯` prompt. a blinking block caret shows while the field is empty, and the real caret takes the accent colour once you type.
- **crt code panes:** rounded, inner glow, scanlines, vignette, faint text glow.
- **small things:** glowing icons and scrollbar; text selection inverts to the accent; tooltips type on; menus and popovers flicker in; dialogs power on; thread rows fade out slowly after hover.

## receipts

- **chars:** measured by `build.mjs`. figures are above.
- **paint cost:** traced in headless chrome at 1440×900 over 4 s, software raster, so treat it as relative. paint took 5.4 ms over 42 events and raster 6.0 ms, with 0 layouts. an earlier version that swapped glyphs inside the svg cost 1,554 ms paint and 1,188 ms raster over the same 4 s, because every surface that draws the tile re-rasterises on each swap. that's why the tile is a still image.
- **gpu memory:** about 63 MB at 2× density, as an upper bound. this is calculated, not measured: four moving layers totalling about 3.97 M px (conversation 1176×(848+650) and 1176×(848+390), sidebar 264×(900+650) and 264×(900+390)), × 4 bytes × 4 for 2× density. chromium rasterises visible tiles first.
- **reduced motion:** checked with chrome's reduced-motion emulation. 0 running animations, and no doubled glyphs.
- **contrast:** text #cff8df on canvas #010803 is 17.5:1. muted #88bd9e is 9.5:1. replies sit on an 87% pocket, so rain behind them stays faint.

## assumptions to check in t3 code

1. **`conversation` is a layer behind the messages, not the scroller.** if it scrolls, its pseudo-elements scroll away; put the rain on a non-scrolling ancestor instead. `contain: paint` clips the overscan without changing scrolling.
2. **message rows remount when you switch threads,** so the boot plays per thread. if rows are virtualised, it also replays when rows scroll into view.
3. **the composer prompt and caret offsets** (`left: 14px` / `30px`, `top: 12px` / `15px`, input `padding-left: 26px`) assume a card padding of 12px 12px 10px 16px. nudge them to match the real card.
4. **the roll bar is a `position: fixed` pseudo on the chat header.** a transformed ancestor would turn it into an absolute one.
5. **the dialog power-on uses the `scale` property,** so it composes with the app's own centring transform.
6. **the theme takes over `::before` and `::after`** on conversation, sidebar, message rows, chat header, composer card, code block, tooltip and running thread rows. if t3 code already uses any of these, they'll conflict.
7. **the data: uris keep raw utf-8 katakana,** escaping only `%`, `#` and `</style`. if the theme loader needs ascii, base64 the svgs: the art grows 53%, from 7,221 to 11,070 chars, about 18.6k in total.
