# Matrix theme for T3 Code

A green "digital rain" theme for T3 Code. Rain falls in the margins beside the reading column, and across both halves of a new, empty thread; the text itself sits on a plain dark surface in soft mint. It is built to be read all day and to cost almost nothing to render.

Screenshots (mock pages, see "Verify"): `design/verify/thread.png`, `thread-wide-1900.png`, `draft.png`, `composer-focused-empty.png`, `composer-typing.png`, `thread-narrow-1100.png`.

## Install

```sh
t3 theme set ./matrix.json            # VPS: t3 is on PATH
~/.t3/bin/t3 theme set ./matrix.json  # Mac
```

`theme set` with a file publishes the theme and selects it in one step. Undo by selecting another theme: `t3 theme set pixel-quest-plus`, or a built-in: `t3-chat`, `grove`, `ocean`, `ember`, `iris`.

## Build

```sh
python3 -I build.py
# css 15025/20000 chars, file 18368/32768 bytes, svgs: prompt, rain
```

`build.py` minifies `src/theme.css`, inlines `src/*.svg` as `data:` URLs, adds the colour roles from `src/colors.json` and writes `matrix.json`. It fails the build if the theme breaks a T3 limit: CSS over 20,000 chars, file over 32 KB, a `url()` that is not `data:` or `#id`, `@import`, `image-set()`, `src()` or a backslash.

| file | what |
|---|---|
| `src/theme.css` | all rules, commented by section |
| `src/colors.json` | 61 colour roles (dark only) |
| `src/rain.svg` | 1000x650 still tile: 40 columns of vertical text, dark tail, light head |
| `src/prompt.svg` | the composer prompt chevron |

## Design decisions

- **Colours.** Text is soft mint `#c6dbcf` on `#060c0a` (about 13.6:1). The bright accent `#0affa0` is only used for small things: prompt, caret, links on hover, the active-row bar, focus rings. No green fills, no glow on text.
- **Rain only where there is nothing to read.** In a thread there is one layer in each margin, masked so it fades out before the reading column plus a 32 px gutter. The margin is computed from T3's own `--chat-content-max-width` (46rem by default, 72rem with the "wide" chat width) and from the lane insets T3 sets when a preview panel overlaps the chat, so the rain follows the column instead of assuming 736 px. The two sides are mirrored: different speeds (83 and 62 px/s), a 4 s phase shift and different tile offsets. Layer opacity is .46 / .40.
- **New thread.** A draft thread is a conversation area with no timeline rows and the composer centred. In that state each layer widens to half the area, full strength at the outer edge, about 20% at the edge of the centre column and about 7% at the centre line, so the heading and composer stay clear. It is still the same two layers and two animations. The opaque composer hides whatever is behind it.
- **Dim while typing.** While the composer is focused and has text the rain fades to .16. Focus alone does not dim it, so the rain stays visible while you read with the cursor parked in the composer.
- **No rain in the sidebar or under messages.** That was the rejected first build (`design/rounds/build1-too-dense.png`).
- **Narrow margins.** A margin under 96 px gets no rain. This is computed from the conversation area's own width (a `clamp()` on the layer width), not from the window, so an open sidebar or panel is accounted for. With the "full" chat width there are no margins and no rain.
- **Composer.** A drawn `❯` chevron (an SVG, because the glyph is missing from some system fonts), monospace input, and a block caret while the editor is empty. The block blinks ten times after the composer takes focus, then stays lit; once there is text the normal caret takes over in the accent colour. The card outline is T3's own ring, recoloured through `--chat-composer-outline` (brighter on focus). There is no "agent is working" light: the composer has no reliable hook for that state.
- **Code panes.** Near-black pane, hairline border, a faint top highlight and very faint static scanlines. No glow, no animation.
- **Glitch.** The current breadcrumb part (the thread title) glitches once for 0.45 s when a thread opens, then never again.
- **Overlays.** Tooltips, menus, popovers and dialogs are dark panels with a hairline border; none of them animate.
- **Scrollbars.** Only the colour changes (`scrollbar-color` on `:root`, plus the overlay thumb). Size and overlay behaviour stay T3's.
- **Reduced motion.** With `prefers-reduced-motion: reduce` the theme's own animations and transitions are off and the rain stays as a still image (checked: 0 running animations). T3's own animations are left alone.
- **Spinners** are left as T3 draws them. The earlier glyph spinner animated inside an SVG, which repaints on every step.

## Performance

Rules the CSS follows:

- The rain is a still SVG moved by a `transform` animation with `steps(26)` (one glyph cell per step) on its own compositor layer. Nothing animates inside the SVG and `background-position` is never animated; both of those repaint and re-raster on every step.
- Exactly two animations loop, the two rain layers, in a thread and on a new thread alike. The caret blink is finite (ten iterations, 11 s) and the glitch runs once.
- No filters, no blurred shadows behind text, no `text-shadow`.

Running animations per state (`document.getAnimations()`, mock pages):

| state | running |
|---|---|
| thread, 1512 px | 2 (rain) |
| thread, composer focused and empty | 3 for 11 s (rain + blink), then 2 |
| thread, typing | 2 |
| new thread, idle or typing | 2 |
| thread, 1900 px, wide chat width | 2 |
| full chat width | 0 |
| window under 992 px (under 1408 px with wide chat width) | 0 |
| 1100 px window with the sidebar open (margins under 96 px) | 2, on zero-width layers |
| reduced motion | 0 |

Measured on the mock pages (about 4,000 elements for the thread) in headless Chrome 157 at 1512x900, Linux VPS, software raster, 5 s traces. "idle" is the page left alone; "busy" adds a `requestAnimationFrame` loop so Chrome produces a main frame 60 times a second, the way the app does while a reply streams. Main thread = style + layout + prepaint + paint + commit. Layout and paint were 0.0 in every run. The columns show the first run; the range in brackets is across three runs.

| page | mode | style ms | prepaint ms | commit ms | main thread ms / 5 s | raster ms | changed frames/s | running animations |
|---|---|---|---|---|---|---|---|---|
| thread, no theme | idle | 0.0 | 0.0 | 0.1 | 0.1 (0.0–0.1) | 0.0 | 0 | 0 |
| thread, Matrix | idle | 0.2 | 0.0 | 0.1 | 0.3 (0.3–0.4) | 0.0 | 5.0 | 2 |
| new thread, no theme | idle | 0.0 | 0.0 | 0.7 | 0.7 (0.1–0.7) | 0.0 | 0 | 0 |
| new thread, Matrix | idle | 0.2 | 0.0 | 0.1 | 0.3 (0.3–0.5) | 3.6 (2.8–3.6) | 4.8 | 2 |
| reference canvas page | idle | 0.0 | 53.6 | 926.2 | 979.8 (378–980, two runs) | 0.0 | 25.2 | 0 (canvas) |
| thread, no theme | busy | 0.0 | 5.4 | 36.3 | 41.6 (29–42) | 0.0 | 0 | 0 |
| thread, Matrix | busy | 46.9 | 71.0 | 92.8 | 210.7 (107–211) | 0.0 | 5.0 | 2 |
| new thread, no theme | busy | 0.0 | 3.9 | 29.8 | 33.7 (28–34) | 0.0 | 0 | 0 |
| new thread, Matrix | busy | 36.0 | 8.8 | 41.0 | 85.8 (73–86) | 3.3 (3.3–6.3) | 4.8 | 2 |
| reference canvas page | busy | 0.0 | 12.3 | 357.1 | 369.4 (369–445, two runs) | 0.0 | 24.4 | 0 (canvas) |

What this means:

- Idle, the theme costs under 1 ms of main thread per 5 s, against several hundred for the reference canvas page.
- When the page is already rendering 60 main frames a second, Chrome re-styles each running animation on every frame. That is the whole busy-mode cost of the theme, and it is why the number of looping animations is kept at two.
- A layer clamped to zero width still animates and still pays that busy-mode cost (measured at 1100 px: 117 ms against 39 ms without the theme). The layers are therefore removed outright (`display: none`) wherever the window alone rules a margin out: under 62rem, under 88rem with the wide chat width, and always with the full chat width. In between (for example a 1100 px window with the sidebar open) the two invisible animations keep running.
- The busy numbers are noisy on this machine (load average 1.6 to 3.3 during the runs). The first run's thread figure (211 ms) was taken as the load peaked; the other two runs were 107 and 110 ms, about 75 ms over the no-theme baseline.
- The reference page was measured over the network from `https://chetan-examples.vercel.app/matrix`.

## Verify

```sh
python3 -I design/verify/mock.py          # writes design/verify/pages/*.html from matrix.json
google-chrome --headless=new --remote-debugging-port=9377 --user-data-dir="$(mktemp -d)" --window-size=1512,900 about:blank &
python3 design/verify/cdp.py shots        # screenshots into design/verify/, animation counts per state
python3 design/verify/cdp.py bench        # the table above
```

`cdp.py` needs the `websocket-client` Python package. The mock follows the structure in the T3 client bundle (0.1.10-nightly.20261114) for the hooks the theme uses: the conversation area with inline lane insets, the lane width variable, `<li>` breadcrumb parts, the composer form, card and outline ring, and the editor with its placeholder. It maps each colour role to a CSS variable. It is not the real app: the draft page's heading and chips are stand-ins, and nothing here has been checked in the live app since the review.

## Fragile selectors

These depend on T3 internals that have no stable hook. If a T3 update breaks the look, check them first.

- `[data-chat-header] li[aria-current="page"] [data-slot="workspace-breadcrumb-text"]`: the current breadcrumb part. Each part is a span in its own `<li>`; only the current one gets the bright colour and the glitch.
- `[data-thread-item] > [role="button"]`: the sidebar row card, with `aria-current="page"` on the active one.
- `[data-chat-composer-form] :has(> * > .composer-tiptap)`: the editor's grandparent. The prompt and block caret are pseudo-elements on it, and it gets left padding so the text clears the prompt. Its child `.pointer-events-none` is the placeholder and gets its own left padding. If T3 changes this nesting, the prompt overlaps the placeholder or disappears.
- `.composer-tiptap:has(> p:only-child > br:only-child)`: how "the editor is empty" is detected. The typing dim uses the same test, negated.
- `[data-workspace-area="conversation"]:not(:has([data-timeline-row-kind], [data-timeline-loading]))`: how "new, empty thread" is detected. A thread that renders no rows for another reason would get the fuller rain too.
- `--chat-content-max-width`, `--chat-lane-inset-start`, `--chat-lane-inset-end` and `[data-chat-width]`: T3's lane geometry. If these are renamed the rain falls back to a 46rem column with no insets.
- `--chat-composer-outline` on `[data-slot="composer-host"]`: the colour of T3's outline ring.
- `[data-message-role="assistant"] .chat-markdown`: the markdown rules are limited to assistant rows so they do not restyle user bubbles.
- The theme owns `::before` and `::after` on the conversation area and on the composer grandparent, and `::after` on code blocks. It no longer touches the composer card's pseudo-elements.

## Design history

- `design/prompt1.txt`–`prompt3.txt`: the three Claude Design rounds.
- `design/rounds/reference-page.png`: the look the user asked for.
- `design/rounds/r2-*.png`: round 2 explorations (Downpour, Depth Chamber, Possessed). The Possessed ideas kept here: `❯` prompt and block caret, CRT code panes, a small glitch, rain dimming while typing.
- `design/claude-design-kit/`: the round 3 kit that the first build came from.
- `design/rounds/build1-too-dense.png`: the first build, rejected as too dense and too slow.
- `design/spec/`: the calmer colour and component spec this build follows.
- `design/perf/`: the benchmark that picked the transform technique.
- `design/verify/`: mock generator, CDP script and screenshots for this build.
