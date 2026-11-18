# Matrix theme for T3 Code

A green "digital rain" theme for T3 Code in the **Possessed** direction from the Claude Design rounds: page-style digital rain behind the whole conversation (heads writing down fixed glyph columns, as on the canvas reference page), a phosphor-terminal chrome, short one-shot effects when a thread opens or a reply arrives, and the **Watcher**, a 30 px White Rabbit on the composer that follows what you and the agent are doing. Prose stays in the app's sans on a dark pocket, so it reads comfortably all day, and the idle cost is at most about 15 ms of main thread per 5 s.

Screenshots from the real app (T3 0.1.10) are in `design/verify/`; see "Verify".

## Install

```sh
t3 theme set ./matrix.json            # VPS: t3 is on PATH
~/.t3/bin/t3 theme set ./matrix.json  # Mac
```

Needs T3 Nightly 0.1.10-nightly.20261115 or later: the theme is about 48,000 CSS chars, and older builds reject themes over 20,000.

`theme set` with a file publishes the theme and selects it in one step. Undo by selecting another theme: `t3 theme set pixel-quest-plus`, or a built-in: `t3-chat`, `grove`, `ocean`, `ember`, `iris`.

## Build

```sh
python3 -I build.py
# css 48068/50000 chars, file 53437/316384 bytes, svgs: prompt, rabbit, rabbit-work, rain, rain-field, rain-loop, spinner, spinner-b, spinner-c, spinner-d
```

`build.py` minifies `src/theme.css` (quoted strings are left untouched), inlines `src/*.svg` as `data:` URLs, adds the colour roles from `src/colors.json` and writes `matrix.json`. It fails the build if the theme breaks a T3 limit (T3 Nightly 2026-11-15 and later): CSS over 50,000 chars, file over 316,384 bytes, a `url()` that is not `data:` or `#id`, `@import`, `image-set()`, `src()` or a backslash.

| file | what |
|---|---|
| `src/theme.css` | all rules, commented by section. Uses CSS nesting to stay inside the character limit (roughly a thousand characters saved) |
| `src/colors.json` | 61 colour roles (dark only). The `errorForeground`, `warningForeground` and `updateForeground` roles are light: T3 uses them only as text colours on dark surfaces (the error banner, the sidebar "Failed", "Approval" and "Limited" labels, destructive text, warning alerts) |
| `src/rain-field.svg` | the fixed glyph field: 1450x1000, one 25 px glyph per cell (58 x 40), half-width katakana, 0-9 and A-Z in `#0affa0`. Generated with the mask by `python3 -I design/gen-page-rain.py [seed]` |
| `src/rain-loop.svg` | the rain's alpha mask, 1450x3200 (58 x 128 cells): opaque except two windows per column, each a 14 to 28 cell trail fading to a clear head cell |
| `src/rain.svg` | the older sparse tile, still used by the reply decode effect |
| `src/rabbit.svg` | the Watcher sprite strip, six 30 px frames of the White Rabbit on the pixel grid: folded, ears up, one ear tilted, red, a blink (ears up, eyes shut) and a twitch (one ear raised) |
| `src/rabbit-work.svg` | the Watcher's working pose: ears up with ア, 7, ヌ cycling under the rabbit (`steps(1)`, .75 s loop) |
| `src/prompt.svg` | the composer prompt chevron |
| `src/spinner.svg`, `spinner-b.svg`, `spinner-c.svg`, `spinner-d.svg` | 14 px sidebar spinners from the Possessed kit: one glyph at a time with a soft cross-fade. The four differ in glyph set, cycle (1.8, 1.35, 2.25 and 1.6 s) and phase; each sidebar row takes one by its id (see The look) |

## The look

- **Typography.** Monospace for the chrome: sidebar, header, user bubbles, composer, work-log rows, tooltips, menus and popovers. Assistant prose stays sans; inline code is mono.
- **Rain.** Modelled on the canvas reference page (https://chetan-examples.vercel.app/matrix): glyphs never move; a head writes down each column and leaves a trail that fades out in place. The conversation background is the fixed glyph field at full `#0affa0`. Over it sits one black overlay (`::after`) whose mask (`rain-loop.svg`) is opaque except two windows per column. The overlay moves down 25 px per step (`steps(128)` over 12 s, about 267 px/s), so only the windows move: each passes over fixed glyphs, bright at the head and fading up the trail. The sidebar keeps the field still under an 88% wash.
- **Intro.** A curtain (`::before`, a gradient) covers the streams on load and slides off downwards over 7.5 s, so the rain starts from the top edge everywhere at once.
- **Repeats.** The field and the mask are both 1450 px wide, so a conversation wider than that repeats the same columns; the mask repeats every 3200 px (12 s), the field every 1000 px.
- **Reading column.** A horizontal gradient over the field lays an 88% dim (`#030a07e0`) under the reading column plus a 20 px gutter, fading over 110 px, so the windows show dim glyphs under prose and full ones at the sides. The column is computed from T3's `--chat-content-max-width` and lane insets, so the "wide" and "full" chat widths and an overlapping panel are followed. Assistant messages also sit on a dark pocket (`#030a07` at 85%, extended 14 px sideways with flat shadows, no blur).
- **New thread.** The draft screen puts a 75% dim (`#030a07bf`) over the rain under the column; the composer card is opaque and stays clear.
- **Dim while typing.** While the composer is focused and has text the dim under the column rises to 92% (`#030a07eb`).
- **Panels.** User bubble, composer card and code panes have a `#347856` hairline and no glow. Menus and popovers have a `#0affa061` hairline and a faint green halo (`0 0 24px #0affa024`); dialogs have a `#0affa061` hairline and a `0 0 40px #0affa029` glow. Those overlay glows are the only ones, and they show only while the overlay is open. Code panes are CRT tubes: 12 px radius, radial dark-green background, static scanlines and vignette. Code text has no glow.
- **Confirm dialogs** (`alert-dialog`) get the same hairline, and their buttons are the pills: blue for Cancel, red for Confirm.
- **Composer.** Drawn `❯` chevron, mono input, block caret while empty (four soft fades after focus, 1.6 s each, opacity 1 to .35; then it stays lit). The outline is T3's own ring recoloured through `--chat-composer-outline`, brighter on focus.
- **Sidebar.** The active row has a `#0affa059` outline and a stepped flicker when it becomes current; hover is instant and fades out over .9 s; project monograms are green-bordered tiles. A running thread gets a slow sheen and its status icon becomes the glyph spinner. Each row takes one of four spinner variants from the last hex character of its `data-sidebar-row` (0 to 3 the first, 4 to 7 `spinner-b`, 8 to b `spinner-c`, c to f `spinner-d`), so two running rows never cycle in step. The Working and Connecting status labels are the theme green (`#0affa0`: 15:1 on a normal row, at least 10:1 on selected and sheen rows) instead of Tailwind sky, which is off-palette and low contrast on the dark rows.
- **Tooltips** are dark with a solid `#347856` edge and a `#0affa052` halo; they type on in 12 steps over .4 s, a dark cover wiping off the text. **Selection** is the accent inverted. **Scrollbars** only change colour (a dim green thumb).
- **Contrast and focus.** Three text tiers: `#e3f6ea` for headings and the active row, `#c9e2d4` for body text, `#86ae98` for muted labels. Borders are `#347856`. Focus is a 2 px `#0affa0` outline: 1 px inside the edge on inputs and select triggers (over the border), at the edge on buttons, to limit clipping in `overflow: hidden` containers.

## The Watcher

A White Rabbit in a 30 px dark disc, on the composer's top edge at the left, on thread and new-thread screens. The disc has no ring. The rabbit is drawn on `[data-chat-composer-surface]::before`; `::after` carries the red error copy and the bullet-time rings, which keep their green hairline. Its six 30 px frames are in `src/rabbit.svg` (folded, ears up, one ear tilted, red, blink, twitch), and its working pose is `src/rabbit-work.svg`. The Sentinel eye it replaced is no longer built; its sources are kept as `design/round4/possessed-eye-sprite.svg` and `design/round4/possessed-eye-work.svg`. The board for the rabbit is `design/round4/boards/watcher-concepts.dc.html`, row d. All hooks below were read from the running app (T3 0.1.10), not guessed.

| state | hook | what you see |
|---|---|---|
| idle | none | ears folded, eyes shut; one ear twitches every 8 s (the twitch frame holds for .32 s) |
| composer focused | `[data-chat-composer-surface]:has(.composer-tiptap:focus)` | ears up, green eyes; opens once (.3 s, 3 steps), then blinks every 7 s (.28 s) |
| text in the composer | `:not(:has(.composer-tiptap > p:only-child > br:only-child))` | one ear tilted, the rabbit nudged 1 px toward the text; no twitch or blink |
| agent working | `:has([aria-label="Stop generation"], [aria-label="Stopping"], [aria-label="Queue message"], [aria-label="Steer message"])`: the composer's send button during a turn. It is "Stop generation" while the composer is empty, "Queue message" or "Steer message" once you type, and "Stopping" after you press stop | ears up with ア, 7, ヌ cycling under the head (one .75 s `steps(1)` loop) at 1.15x |
| done | none: a `transition` on `transform` | steps back to rest in .45 s |
| error | `html:has(.chat-banner-lane [data-variant="error"])`: T3's error banner over the thread | a dark red disc with red eyes and nose jitters once, holds, and fades by 1.2 s. It plays when the banner appears and when you open a thread whose banner is still up |
| a `/`, `@` or `$` picker is open | `html:has(> body > [data-composer-drawer-layer])`: T3 portals the picker into `body` in this layer, and it exists only while a picker is open | the rabbit fades out in .2 s and comes back when the picker closes |
| reduced motion | the scoped reduced-motion block | no twitch, blink or glyph cycle: idle, focused and typing hold their frame; working is the still focused frame; the red copy stays while the banner is up, except over the working pose |

The `/`, `@` and `$` pickers open upward from the card's top edge and sit above the Watcher (they are `position: fixed`, z-index 40), which used to cut off its top half. The Watcher (rabbit, rings and red copy) is now hidden while a picker is open.

Why these hooks: the send button is local to the composer and carries one of the four running labels from send to the end of the turn, whatever is in the composer (the sidebar "Working" label and the `working` timeline row cover the same span, but one can be scrolled away and the other is virtualised). `[data-thread-now-line]` never appeared in a real run. The error banner is the only error element that is tied to the open thread; `[role="alert"]` alone is also used by settings forms and file viewers, and the sidebar's "Failed" label disappears once the thread is opened.

## Matrix touches (round 4)

- **Bullet time.** While a reply streams (`html:has([data-streaming])`) three rings leave the Watcher (.26 s each, .78 s in all, upper half only so they never cross the composer text). The rings are started by a variable, `--r`, that is set the moment streaming starts and released .8 s after it ends (a delayed transition), so a reply that streams for less than .78 s still gets all three.
- **"Wake up, Neo…"** On the new-thread screen only (keyed on the centred composer overlay, so a thread that is still loading does not start it) the line types itself over the placeholder (13 steps), holds, and then fades as T3's real hint ("Ask anything. @ files, $ skills, / commands") fades in. 3.6 s in total, once per new-thread screen. T3 mounts a new placeholder every time the editor is emptied, which used to replay the line; the two animation names now come from the composer overlay, which mounts once per screen, starts with them (`@starting-style`) and drops them after 4.1 s. Typing and clearing after that shows the plain hint. Emptying the editor inside those first 4.1 s restarts the line, and it is cut off at 4.1 s.
- **Red pill / blue pill.** On confirm dialogs: `[data-slot="alert-dialog-footer"] > *` are capsules with a gloss on the left cap, blue by default and red for the `[data-slot="button"]` child (Confirm).

## Motion

| effect | trigger | length |
|---|---|---|
| rain | always (a still frame under 62rem window width) | loop, 12 s, 128 steps; intro curtain 7.5 s once |
| roll bar: a faint 140 px band crossing the window | always | loop, 28 s, 126 steps |
| sheen on a sidebar row | only while that thread is working | loop, 4 s |
| Watcher opens / steps back / red jitter / ear twitch / blink | composer focus / turn ends / error banner / every 8 s while idle / every 7 s while focused | .3 s / .45 s / 1.2 s once; twitch .32 s; blink .28 s |
| bullet time: three rings | a reply is streaming | rings 3 x .26 s, completed even if the stream is shorter |
| "Wake up, Neo…" | new-thread screen mounts | 3.6 s once |
| the line: a scan band sweeps down the conversation | thread opens | .9 s once |
| title glitch | thread opens | two .08 s jumps, once |
| active sidebar row flicker | a row becomes the current one | .25 s stepped flicker, once |
| the timeline flickers | thread opens | three .17 s blinks, once |
| a row flickers in | a row mounts (new message; also a row scrolled back in, usually still off screen) | .18 s fade once; .5 s for the row whose reply is streaming |
| the Watcher fades | a picker opens or closes | .2 s |
| decode: bright glyphs on a dark plate step away over the new reply | a reply starts streaming | .2 s fade once |
| scan-line wipe down the whole reply | the reply finishes streaming | .65 s once |
| menus and popovers flicker in (.25 s, stepped), dialogs power on (.32 s), tooltips type on (.4 s, 12 steps) | on open | once |
| caret fades | composer focused and empty | four soft fades, 1.6 s each |

How the two triggers that are not plain mount animations work:

- **Thread open.** In T3 0.1.10 nothing above the message rows remounts when you switch threads, so a mount animation cannot fire. Sixteen rules set a custom property `--n` on the root from the last hex character of the active sidebar row's id, and twelve more set `--m` from the first character of the thread id (the character after a colon in `<env>:<thread>` or `<env>:mcp:<thread>`; 0 to 3 share the default). The scan line, the title and the timeline flicker use `animation-name: var(--n), var(--m)`: two animations with the same keyframes, so a switch that changes either name replays the effect. The sixteen `@keyframes` are identical and read their start values from the element (`--a`, `--b`), so one set serves all three effects and both keys. A switch is missed only when both characters match, or when the two names swap places: 1 switch in 100 for random ids (simulated), against 1 in 16 with the single key.
- **Rows.** The timeline is a virtualised list that remounts rows as they scroll back in, so a mount animation on rows replays while you scroll: in a 6,000 px thread a slow scripted scroll (4 s, bottom to top) had a flickering row in view in 62 animation frames. The thread-open flicker is therefore on the timeline scroller (keyed as above), and the per-row mount flicker is .18 s, which is over before a row mounted 250 px outside the window reaches it. The same scroll now has one in view in 8 frames (2 on the way down, against 41).
- **New reply.** The markdown root carries `data-streaming` while a message streams. The decode is an animation keyed on that attribute, so it starts once when streaming starts and is not replayed by text updates. The wipe is a *transition* that runs when the attribute goes away, so it never plays on mount or on thread open.

Reduced motion: every animation and transition the theme adds is switched off by a scoped selector list (not `*`), the rain stays as a still image, both spinner selectors (`lucide-loader*` and the sidebar's `lucide-circle-dashed`) go back to T3's icon, and the Watcher's working pose is swapped for the still focused frame of the sprite. Its twitch and blink, and the popup and dialog motion, are off as well. A `prefers-reduced-motion` query inside an SVG image did not stop the glyph cycle in the test Chrome, so the swap is done in the page CSS. Checked in the real app in idle, focused, typing, working, streaming, error and draft states: 0 running animations, and the glyph does not change.

## What changed from the Possessed kit, and why

- **Rain under prose is masked down** instead of running at full strength behind 87% pockets, and the pockets have no 34 px blurred shadow (a paint cost on every row while scrolling).
- **The sidebar rain is still.** The kit animated two more layers there; a still field gives the same texture with no loop.
- **Slower rain** (one moving layer at about 267 px/s; the kit ran two, at 176 and 48 px/s) and softer text (`#c9e2d4` on `#030a07`, about 14:1) for all-day use.
- **The glitch runs once per thread open** instead of every 11 s, and without the animated red/cyan `text-shadow`.
- **No `filter: drop-shadow` on icons, no text glow on code or headings, no glowing scrollbar.** The only text glow is on the one-line header title.
- **The roll bar is stepped** (see Performance).
- **The per-row scan line became one line for the whole conversation** on thread open, plus the wipe on a finished reply. Row containers in T3 have paint containment, so a row cannot draw outside itself anyway.
- **Stagger.** The kit staggered the last three rows with `:nth-last-child`. T3's timeline is a virtualised list where every row is the only child of its own lane, so that selector is meaningless, and rows remount on scroll; the whole timeline flickers on thread open instead, with no stagger.

## Performance

Rules the CSS follows: every loop is a `transform` on its own layer; rain images are static and use `steps()`; nothing animates inside an SVG; `background-position` only changes in `steps(1)` jumps (the Watcher's poses, twitch and blink); no filters, no blur, no animated `text-shadow`; the only glows are the overlay outlines listed under The look; `box-shadow` otherwise draws hairline rings and flat panel shadows. Exceptions, all small: "Wake up, Neo…" animates `clip-path` and `color` on one line of text, once; the Watcher's pose changes, twitch and blink are discrete `background-position` jumps, not eased animations.

Running animations per state (`document.getAnimations()` in the real app):

| state | running |
|---|---|
| thread, idle | 3: rain, roll bar, the Watcher's twitch loop (plus the intro curtain for 7.5 s after load) |
| draft, just opened | 3 + caret fades (6.4 s) + "Wake up" x2 and its two gate transitions (4 s), then 3 |
| composer focused and empty | 4 for 6.4 s (caret fades), then 3; the Watcher's open is a .3 s one-shot |
| typing | 3 |
| thread working | 3 + sheen, T3's own two live-activity animations and the 14 px spinner |
| reply streaming | 2 looping (rain, roll bar) + sheen; one-shots at the start: row flicker, decode (.2 s), rings (.78 s) |
| turn ends | the wipe (2 transitions, .65 s), the Watcher's step back (.45 s) and the `--r` release (.8 s); back to 3 |
| error banner appears | 3 + the red rabbit for 1.2 s |
| window under 992 px | 1 (roll bar) |
| reduced motion, every state above | 0 |

Measured in the real app (T3 0.1.10, throwaway instance) in headless Chrome 157 at 1512x900 on a Linux VPS, 5 s traces, round 6. This Chrome has no GPU (SwiftShader), and the machine was loaded (load average 2.5 to 3.1 on 4 cores), so treat frame rates as relative and expect run-to-run swings of 20% or more in the busy rows. "idle" is the page left alone; "busy" adds a `requestAnimationFrame` loop so Chrome produces main frames continuously, as it does while a reply streams. Main thread = style + layout + prepaint + paint + commit. The no-theme rows were measured in the same session; the reference page row is from round 4.

| page | mode | style | prepaint | paint | commit | main thread ms / 5 s | frames/s | running |
|---|---|---|---|---|---|---|---|---|
| thread, no theme | idle | 0.0 | 0.0 | 0.0 | 0.1 | 0.1 | 0.0 | 0 |
| thread, Matrix | idle | 0.3 | 0.0 | 0.0 | 0.1 | 0.4 (0.4 and 2.4) | 13.8 | 3 |
| thread, Matrix, typing | idle | 4.3 | 1.6 | 0.0 | 6.5 | 12.4 | 15.4 | 3 |
| thread, Matrix, Watcher working (hand-set) | idle | 46.4 | 12.8 | 16.2 | 44.5 | 119.9 | 15.4 | 3 + glyph |
| thread, Matrix, streaming (hand-set) | idle | 29.0 | 9.0 | 11.9 | 10.7 | 60.6 | 14.0 | 2 + glyph |
| draft, no theme | idle | 8.9 | 0.2 | 0.4 | 1.0 | 10.6 | 0.2 | 0 |
| draft, Matrix, 1.4 to 6.4 s after it mounts (caret + "Wake up") | idle | 179.8 | 25.6 | 28.4 | 36.2 | 270.0 (270 and 315) | 19.6 | 4 to 8 |
| the same with the round-5 "Wake up" trigger | idle | 164.1 | 28.1 | 29.8 | 36.3 | 258.3 (258 and 261) | 19.2 | 4 to 6 |
| the same with no "Wake up" | idle | 15.9 | 3.0 | 0.0 | 6.2 | 25.1 (25 and 58) | 15.4 | 4 |
| draft, Matrix, after 5 s | idle | 1.6 | 0.4 | 0.0 | 0.8 | 2.8 | 9.4 | 3 |
| reference canvas page | idle | 0.0 | 13.6 | 0.0 | 355.9 | 369.5 | 24.6 | canvas |
| thread, no theme | busy | 29.4 | 29.6 | 41.6 | 120.3 | 220.9 | 59.8 | 0 |
| thread, Matrix | busy | 54.5 | 28.7 | 62.2 | 109.1 | 254.5 (250 and 255) | 51.0 (45 and 51) | 3 |
| thread, Matrix, typing | busy | 54.2 | 22.4 | 59.1 | 123.5 | 259.1 | 41.6 | 3 |
| thread, Matrix, Watcher working (hand-set) | busy | 67.0 | 28.6 | 58.0 | 91.0 | 244.7 | 46.6 | 3 + glyph |
| thread, Matrix, streaming (hand-set) | busy | 61.8 | 27.7 | 58.6 | 96.1 | 244.2 | 53.2 | 2 + glyph |
| draft, no theme | busy | 56.0 | 50.5 | 57.7 | 188.0 | 352.2 | 59.8 | 0 |
| draft, Matrix, 1.4 to 6.4 s after it mounts | busy | 283.3 | 50.0 | 105.6 | 102.1 | 554.1 | 49.8 | 4 to 8 |
| draft, Matrix, after 5 s | busy | 55.6 | 25.9 | 29.1 | 74.2 | 184.9 | 57.6 | 3 |

The caret-blink row of round 5 (34 ms idle) was not re-measured: the blink did not start under the harness's focus emulation in this session. The draft "first seconds" rows are not comparable with round 5's 138 ms: this window starts earlier (1.4 s after the screen mounts instead of about 3.5 s) and so holds most of the type-on; measured the same way, the old trigger costs the same as the new one.

The Watcher's twitch and blink, the rabbit poses and the popup motion came after these measurements and were not re-measured.

What this means:

- **Idle** the theme costs at most about 15 ms of main thread per 5 s, about 25 times less than the reference canvas page.
- **The Watcher is free at rest** (idle and focused have one sprite jump every 7 to 8 s, not measured; typing is still). While the agent works, its former glyph cycle made about 4 main frames a second and cost 55 to 120 ms per 5 s (57 in round 5, 120 in this one; measured before the cycle was removed), a third of the reference page at worst, and only for the length of the turn. Under a busy main thread it adds nothing measurable (245 ms against 250 to 255 without it).
- **"Wake up, Neo…" is the most expensive one-shot**: `clip-path` and `color` are animated on the main thread, so the first seconds of a new-thread screen cost about 270 ms per 5 s, against 25 to 60 ms without the line and 3 ms once it has settled. It runs once per new-thread screen; if that matters, drop the type-on and keep a plain fade.
- **Page-style rain (round 7)**, headless Chrome 157 on the MacBook, no GPU, 1440x900 at DPR 2, a test page with the theme CSS, 5 s traces: main thread 22 ms busy / 0.7 ms idle (old two-layer rain 35 / 0.3), 60 frames/s busy (old 57), no paints per step. Raster work is about 455 ms per 5 s on raster threads (old 215 to 234): the overlay layer is 3200 px taller than the window. A three-layer mask composite (the first intro design) repainted on every step and cost 17 to 20 s of raster per 5 s; the overlay keeps one mask layer for that reason.
- **Busy**, the per-frame main-thread cost is about the same with and without the theme (about 1.2 ms per main frame). The totals are lower with the theme only because fewer frames were produced.
- **Frame rate under load (round 6, the two-layer rain)** was 45 to 51 frames/s in this GPU-less Chrome, against 60 with no theme. Round 5 measured 24 to 41. The cause is compositing the two full-area rain layers on the CPU. Round 6 tried six cheap changes against the same build, in pairs: no mask on either layer, no mask on the far layer, `contain: strict` on the layers, no roll bar, no rain at all, and no `will-change: transform` on the layers. Only the last one helped beyond noise: 50.2 frames/s on average against 44.4 with the hint, ahead in 7 of 8 pairs (38 to 56 against 41 to 49), with no change at idle. The hint is gone; the running transform animation still gives each layer its own compositor layer. The other five were within noise (no rain at all measured 36 to 59) and were not kept. A real GPU composites these layers in well under a millisecond, but it has not been measured on one; if the Mac shows dropped frames while streaming, the first thing to try is removing the far layer.
- **Roll bar.** A smooth (linear) roll bar made the compositor draw 46 frames/s at idle, against 8 without it. Stepped (`steps(72)`, about 4.5 moves a second while it crosses) it draws 15 frames/s and adds no measurable main-thread time (16.7 and 14.9 ms with it, 16.7 and 14.2 without), so it stays as a loop.
- The reference page was measured over the network from `https://chetan-examples.vercel.app/matrix`.

## Verify

The harness drives a throwaway T3 server and its own headless Chrome (see the docstring of `design/verify/real/shoot.py`; it needs the `websocket-client` Python package). It never touches the live T3.

```sh
python3 -I build.py
python3 design/verify/real/shoot.py reload-theme
python3 design/verify/real/shoot.py shot thread --action 'thread:Matrix rendering one' --action nopanel
python3 design/verify/real/shoot.py burst open --action 'thread:Matrix python notes' --thread 'Matrix rendering one' --rate 0.12 --shots
python3 design/verify/real/shoot.py arrive --rate 0.15      # sends one real message
python3 design/verify/real/shoot.py bench thread --action 'thread:Matrix rendering one'
```

`burst` and `arrive` print the animations alive at each frame, and `--rate` slows CSS animations so screenshots can catch sub-second effects. `--action 'eval:<js>'` runs JS in the page, for hand-setting a state (for example relabelling the send button to "Stop generation" to hold the Watcher's working pose for a benchmark).

Nothing in the round-4 screenshots was hand-set: working, bullet time and déjà vu are from real sends (animations slowed to a quarter speed), the error is a real failed turn, the dialog is the real delete confirmation (cancelled). Only the benchmark rows marked "hand-set", the reduced-motion checks of the working and streaming poses, and the checks of the "Stopping" and "Steer message" labels and of the "Goal" and "Setting up" sheen used a hand-set attribute. "Queue message" was seen in a real turn (typing while the agent worked): the eye kept the working pose.

Screenshots in `design/verify/` (`thread.png`, `draft.png`, `reduced-motion.png`, `wake-up.png`, the two wide shots and `watcher-picker.png` are from round 6; the rest are from round 5 or earlier):

| file | what |
|---|---|
| `thread.png`, `thread-end.png` | thread at the top and at the latest message, 1512 px |
| `thread-wide-1900.png` | "wide" chat width at 1900 px (round 6: no repeat at the far edge) |
| `thread-wide-2560.png` | 2560x1300 window: the second copy of the near tile starts 1370 px into the conversation, shifted down 17 cells |
| `watcher-picker.png` | the `/` picker open: the Watcher is hidden |
| `thread-narrow-1100.png` | 1100 px window |
| `draft.png` | new thread |
| `watcher-idle.png` | Watcher shut, composer blurred |
| `watcher-focused.png`, `watcher-typing.png` | open eye with the block caret; narrowed eye, typing, rain dimmed |
| `watcher-working.png` | real run: the stop button is up, the glyph is in the iris, sidebar sheen |
| `watcher-error.png` | red eye and the error banner (light text on the dark banner), opening the test instance's thread with a real failed turn (slow motion) |
| `review-2-error-banner-before.png`, `review-2-error-banner-after.png` | the banner with the old dark `errorForeground` and with the light one, from review 2 |
| `bullet-time.png` | real run, reply streaming: a ring leaving the Watcher, near rain paused (slow motion) |
| `dejavu.png` | real run: the streaming row displaced for its one beat, under the decode (slow motion) |
| `wake-up.png` | new thread, "Wake u" mid-type |
| `pills-dialog.png` | the real "Delete thread" confirm dialog |
| `thread-open-line.png` | the scan line and title glitch mid-sweep (slow motion). From the previous round, before the Watcher and the new tile |
| `arrive-1-working.png` | real run: user row, "Working" rows, sidebar sheen and glyph spinner |
| `arrive-2-decode.png` | decode over the new reply (slow motion; `data-streaming` set by hand on the real message) |
| `arrive-3-flicker.png` | real run: the reply flickering in |
| `arrive-4-wipe.png`, `arrive-5-done.png` | the wipe line crossing the reply, then settled. All five `arrive-*` shots are from the previous round, before the Watcher and the new tile |
| `menu.png`, `tooltip.png`, `dialog.png`, `terminal.png` | overlays and the terminal drawer |
| `tool-run.png` | work-log rows |
| `reduced-motion.png` | `prefers-reduced-motion: reduce` |

## Fragile selectors

These depend on T3 internals that have no stable hook. If a T3 update breaks the look, check them first. `design/verify/real/dom-notes.md` records what was seen in 0.1.10.

- `html:has([aria-current][data-sidebar-row$="…"])` and `html:has([aria-current][data-sidebar-row*=":…"])`: the two thread-open keys. They need the active sidebar row to carry `<env>:<thread id>` in `data-sidebar-row`, the id to end in a hex character, and a hex character to follow a colon. If the first stops matching, only the second key is left; if both do, the scan line, the title glitch and the timeline flicker never play.
- `.messages-timeline-scroll`: the timeline scroller, which carries the thread-open flicker. It is a plain class name.
- `html:has(> body > [data-composer-drawer-layer])`: "a picker is open". T3 portals the `/`, `@` and `$` pickers into `body` inside this layer. If it changes, the Watcher is again half covered while a picker is open.
- `transition … allow-discrete` on a custom property (`--r` on the composer surface, `--h` and `--u` on the composer overlay) and `@starting-style`: need Chrome 117. The first item of the surface's `transition` repeats T3's own `background-color .2s cubic-bezier(.4, 0, .2, 1)`; if T3 changes that transition, the theme overrides it.
- `[data-assistant-citation-viewport]`: the non-scrolling parent of the timeline scroller; its `::after` is the scan line.
- `.chat-markdown[data-streaming]`: the streaming hook for the decode and the wipe.
- `[data-sidebar-row]:is([aria-label*=", Working,"], [aria-label*=", Goal,"], [aria-label*=", Setting up,"])` and `.lucide-circle-dashed`: how a running thread is detected ("Setting up" while preparing, "Goal" while a goal is active). The label text is English.
- `[data-sidebar-row$="…"]` (last hex character of the row id): picks the spinner variant. An id that does not end in a hex character keeps the first spinner.
- `[data-sidebar-row] [role="img"][class*="text-sky-"]`: the Working and Connecting status labels (Tailwind sky classes). If T3 renames the colour class, the labels go back to sky.
- `[data-workspace-area="conversation"]:has(~ [data-chat-composer-overlay].items-center)`: how the new-thread screen is detected for the fuller rain. `.items-center` is a Tailwind class on the composer overlay; in a thread the overlay is `inset-x-0 bottom-0` without it. `[data-timeline-loading]` (also up for 200 to 330 ms while a thread opens) is made transparent so the rain shows through.
- `[data-timeline-row-kind] > .border-b`: the work-log hairline, a Tailwind class.
- `[data-chat-header] li[aria-current="page"] [data-slot="workspace-breadcrumb-text"]`: the thread title.
- `[data-chat-composer-form] :has(> * > .composer-tiptap)`: the editor's grandparent, which carries the prompt and the block caret. Its child `.text-placeholder` (a Tailwind class) is the placeholder; T3 removes it while there is text and mounts a new one when the editor is emptied.
- `.composer-tiptap:has(> p:only-child > br:only-child)`: "the editor is empty". The typing dim uses the same test, negated.
- `[data-chat-composer-surface]`: the Watcher's anchor. It must stay `position: static` inside a positioned card (`[data-chat-composer-main-surface]`) with free pseudos; if T3 starts using them, the rabbit disappears or lands elsewhere.
- `[aria-label="Stop generation"]`, `"Stopping"`, `"Queue message"`, `"Steer message"` inside the composer: "the agent is working". English labels; if one changes, the Watcher drops the working pose in that state.
- `.chat-banner-lane [data-variant="error"]`: the thread error banner (a Tailwind-style class plus the alert's variant). If it changes, the error state never plays.
- `html:has([data-streaming])`: bullet time. `[data-timeline-row-kind]:has([data-streaming])`: the row flicker for the streaming row.
- `[data-chat-composer-overlay].items-center .text-placeholder`: "Wake up, Neo…". It relies on the Tailwind class `.items-center`, which the overlay has only on the new-thread screen, and on the overlay mounting once per new-thread screen (it survived typing and clearing; only the placeholder was replaced). If the class goes, the line never plays and the plain hint shows.
- `[data-slot="alert-dialog-footer"] > *` and `> [data-slot="button"]`: the pills. Cancel is `[data-slot="alert-dialog-close"]`, Confirm is a plain button; a footer with a third control would turn it into a pill too.
- `[data-slot$="dialog-popup"]`: matches both `dialog-popup` and `alert-dialog-popup`.
- CSS nesting: needs Chrome 120 or later. T3's theme loader passed nested rules through in the test instance (headless Chrome 157). The desktop app ships Electron 44.10.1 (`third-party-licenses.json` in the client bundle), far past Electron 28, the first with Chrome 120.
- `--chat-content-max-width`, `--chat-lane-inset-start`, `--chat-lane-inset-end`: T3's lane geometry. If renamed, the mask falls back to a 46rem column.
- `--chat-composer-outline` on `[data-slot="composer-host"]`. `[data-chat-composer-surface]` has no background of its own, so the host's gradient shows; the theme leaves its background alone so T3's drag-over tint still works.
- `.chat-content-lane { overflow-clip-margin }`: lets the reading pocket extend past the lane's horizontal clip.
- The theme owns `::before` and `::after` on the conversation area, on assistant `.chat-markdown`, on the composer surface and on the composer grandparent, `::before` on the new-thread placeholder, the `animation` of the timeline scroller, and `::after` on the citation viewport, the chat header, code blocks, tooltips and running sidebar rows.

## Not verified

- **Long threads beyond 6,000 px, and a fast wheel or trackpad.** Row remounting was measured with scripted scrolls of a 6,000 px thread at 1512x900. After the change a row still flickers in view now and then (in 8 animation frames of a 4 s scroll up, user bubbles mostly). A real trackpad fling was not tried.
- **A real GPU / the Mac app.** All numbers are from software compositing on a VPS.
- **A long streamed reply.** The longest real stream in the test instance was about 3 s (eight paragraphs from Haiku), enough for the decode, the déjà vu beat and all three rings. A very short reply was not caught: a real one-word reply showed no `data-streaming` at all at a 250 ms sampling interval, so its rings were not seen; the "rings complete after a short stream" check used a hand-set attribute removed after 300 ms (all three iterations ran, the last ending about .8 s after the start). A multi-minute turn with several streamed segments (rings and the beat on each) was not seen.
- **Errors other than a failed turn.** Only the provider-error banner was seen. Any other use of the banner lane with `data-variant="error"` will also turn the rabbit red once.
- **"Wake up, Neo…" inside its first 4.1 s.** Emptying the editor in that window restarts the line and it is cut off at 4.1 s, where the plain hint appears at once. Seen in the harness; judged harmless.
- **Thread ids that do not look like `<env>:<uuid>`.** The second thread-open key reads the character after a colon. Only ids of the form `<env>:mcp:<uuid>` (threads started from the CLI) exist in the test instance; the form without `mcp:` is assumed from the draft URL.
- **Reduced motion inside SVG images** with the real OS setting (only Chrome's emulation was tested; the theme does not rely on it for the Watcher, but the 14 px spinner swap is the only guard for the sidebar spinner).
- **`lucide-loader` icons.** `lucide-loader-circle` is in the send button while a message is being submitted (per the bundle and review 2); it was not caught on screen here. The spinner rule and its reduced-motion fallback were checked on a probe element with that class.
- **"Goal" and "Setting up" sidebar labels, "Stopping" and "Steer message" button labels.** Read from the bundle and checked with a hand-set label; not seen in a real run.
- **The drag-over tint on the composer.** The theme no longer overrides the surface background, but a drag was not exercised.

## Design history

- `design/prompt1.txt`–`prompt3.txt`: the three Claude Design rounds.
- `design/rounds/reference-page.png`: the look the user asked for.
- `design/rounds/r2-*.png`: round 2 explorations (Downpour, Depth Chamber, Possessed).
- `design/claude-design-kit/`: the Possessed kit (CSS, tile, spinner, palette) this build follows.
- `design/rounds/build1-too-dense.png`: the first build, rejected as too dense and too slow.
- `design/BRIEF-implement.md`, `design/REVIEW-1.md`: the quiet margin-only build and its review; those fixes are kept.
- `design/BRIEF-possessed.md`: the brief for the Possessed round.
- `design/round4/`: Claude Design round 4, the Watcher and the Matrix touches (boards A to E, its kit, the two prompts and replies, `round4.real.css`). Canvas: https://claude.ai/artifact/UUftboWWM9ECibT6gKWEuf (page "Round 4 · Watcher + Matrix").
- `design/BRIEF-review-2.md`, `design/REVIEW-2.md`: the second review and its eight findings, all applied (status-text colours, the "Wake up" trigger, the Watcher's running labels, the reduced-motion spinner, the sheen labels).
- `design/BRIEF-watcher.md`: the brief for the Watcher round. What changed from round 4: the eye was redrawn at 30 px on the pixel grid (the kit's 28 px strip was scaled to 30 and blurred), with lashes on the shut pose and a larger, simpler glyph; working is keyed on the stop button instead of `[data-streaming="true"]` / `[data-thread-now-line]` (the first never matches, the attribute is bare; the second never appeared); the error is keyed on the thread's error banner instead of `[role="alert"]`; the pills use the real `alert-dialog` slots; "Wake up, Neo…" gives way to the real hint instead of replacing it; the reduced-motion working pose is a sprite frame, not a media query inside the SVG.
- `design/BRIEF-fixes.md`: round 6, seven open issues: the Watcher under the pickers, the "Wake up" replay, rings on short replies, the near rain repeating in wide windows, the thread-open key, rows flickering on scroll, and the frame rate under load.
- `design/perf/`: the benchmark that picked the transform technique.
- `design/verify/`: real-app harness, DOM notes and screenshots for this build.
