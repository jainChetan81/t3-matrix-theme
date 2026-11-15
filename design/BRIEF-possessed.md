# Brief: bring back Claude Design's "Possessed" look (round 3 of the build)

You implement. Work only in `~/Codebase/t3-matrix-theme` (`src/theme.css`, `src/colors.json`, `src/*.svg`, `build.py` if needed, `README.md` later). Do not commit/push. Do not touch the user's live T3 (`~/.t3/userdata`, `t3code.service`), the Chrome on :9222, or anything on :20128. Kill only PIDs you started. No subagents.

## Why
The user: "Claude Design came up with a better UI than what was built; more could have been done." The current `src/theme.css` is a safe, quiet build (margin-only rain, plain dark panels). The user wants the **Possessed** direction back much more faithfully, while staying calm enough to read all day and cheap to render.

What they liked, explicitly:
- **the line**: a scan line sweeping down when a thread opens, and the faint roll bar passing down the window;
- **the flashing UI**: rows flickering in, the title glitch, menus flickering in, tooltips typing on, dialogs powering on;
- the `❯` prompt + block caret, CRT code panes;
- **new messages should interact with the rain**: the newest row "decodes"/materialises out of the rain, a scan line wipes the newest row, glyphs flicker on arrival.

## Sources (read these first)
- `design/claude-design-kit/README.md` (every effect explained) and `design/claude-design-kit/src/possessed.css` (the exact CSS of the boards; the boards in `design/claude-design-kit/boards/*.dc.html` are that CSS applied to a mock, nothing extra), `palette.json`, `src/rain.svg`, `src/spinner.svg`.
- Board screenshots: `design/rounds/r2-possessed-thread.png`, `r2-possessed-new-thread.png`. Compare against the current real-app screenshots in `design/verify/`.
- `design/BRIEF-implement.md` (perf rules + real DOM facts), `design/REVIEW-1.md` (review findings already applied — keep those fixes: chat-width-aware margins, no `[data-workspace-area=home]`, composer outline via `--chat-composer-outline`, scoped reduced motion, breadcrumb `li[aria-current=page]`, etc.).
- Real-app DOM notes: `design/verify/real/dom-notes.md`. Harness: `design/verify/real/` (see "Harness" below).

## Look to reach (Possessed, toned for all-day use)
1. **Typography**: monospace for the chrome — sidebar (project names, thread titles, times), header title, user bubbles, composer, tooltips, menus/popovers, terminal. Assistant prose stays the app's sans for readability; inline code mono.
2. **Rain**: visible, sparse-feeling glyph field like the boards, not the dense stream wall of the rejected build 1.
   - Conversation: rain across the whole area, not only the margins, but **under the reading column it is masked down hard** (≈ .08–.12 effective) so prose is never fighting it; margins at about .35–.5 near-layer. Exactly two running rain animations total (near + far depths, different tile scale/offset/speed, `steps()`, transform-only). Keep chat-width awareness (wide/full widths) and the narrow-window fallback.
   - Sidebar: a **static** still-field of the tile (background image under a dark wash, no animation) so it reads as Possessed's sidebar rain without a third loop. Same idea as Possessed's "still field" on the conversation (tile at 40% under an ~83% wash) — use it on the conversation too, it's free.
   - Draft/new-thread screen (conversation with no rows): rain fuller, composer stays clear (keep the existing approach, adapt).
   - Dims while the composer has text (keep).
3. **Reading pockets** instead of masks only: assistant rows sit on a dark pocket (`#010803`-ish ~.85 alpha) with soft rounded edges so glyphs fade out around text. A big blurred `box-shadow` on every assistant row is a paint cost on scroll — prefer the mask on the rain layer + a cheap solid/gradient background with small radius; measure if you use box-shadow.
4. **Panels with green hairline + soft glow** (static box-shadow is fine on a few elements, not on every row): user bubble (mono, `#0affa061` border, small outer glow), composer card (green ring when focused, faint inner glow, `❯` prompt, block caret), code panes as CRT tubes (rounded 12px, radial dark-green bg, green hairline + soft glow, faint static scanlines + vignette `::after`; **no text-shadow on the code text**), tool/work-log cards with a green hairline, menus/popovers/dialogs with green hairline + glow.
5. **Sidebar**: active thread row = green outline box (`inset 0 0 0 1px #0affa059`, faint green fill) with brighter text; hover instant, fade-out slow (.9s); project monogram = green-bordered tile with green letter/icon and a small glow; running thread rows get a slow "decoding" sheen **only while running** (find the real hook: rows carry `aria-busy` per REVIEW-1 #1 — verify in DOM notes).
6. **Tooltips**: Possessed style — green background, dark ink, mono, types on (scaleX cover with `steps(12)`, one shot).
7. **Header**: mono bold title with a tiny glow; glitch once when a thread opens (keep finite), branch chip with green hairline.
8. **Scrollbar**: thin green-tinted thumb (not full neon; keep it calm), selection = accent inverse like Possessed (`::selection { background: #0affa0; color: #00140a }`) or the softer current one — pick what reads better in screenshots.
9. **Spinner**: lucide loader icons → mutating glyph (kit `spinner.svg`) only if cheap (it's 14 px; SVG-internal animation is OK at that size; verify the hook `[class*=lucide-loader]` exists in the real DOM).

## Motion (the important part)
All of these are **one-shot** (`animation-iteration-count: 1` or a small finite count) unless noted:
- **Thread open — the line**: a scan line sweeps down the whole conversation once when a thread opens (≈ .9 s, linear, faint green band with a brighter leading edge). Find an element that mounts per thread (e.g. the timeline scroller or its first child, or the header breadcrumb `li[aria-current=page]`) and use its pseudo; it must not scroll away mid-sweep and must not cover the composer with anything opaque.
- **Roll bar**: the faint band passing down the window (Possessed: 140 px band, `#0affa00b` peak, every 16 s). It is allowed as the one extra loop **only if** busy-frame cost stays small; otherwise make it finite (e.g. runs N times after thread open). Measure both and choose; report.
- **Rows flicker in on mount**: Possessed `boot` (stepped opacity .55 s), staggered for the last 3 rows only (`:nth-last-child(-n+3)` or similar), older rows no animation.
- **New message arrives — decode out of the rain**: the newest row (`[data-timeline-row-kind]:last-child`, check the DOM notes for the real structure/virtualisation) materialises: a glyph overlay (the rain tile, bright, on the row's pseudo) that steps from strong to gone while the row's text steps in (≈ .6–.8 s), plus the scan line wiping down the row once (Possessed `sweep`). Must run only on mount of that row, not on every streaming text update, and not replay on all rows when a thread opens (only the stagger above).
- **Menus/popovers flicker in** (`flick` .25 s steps), **dialogs power on** (`pwr` .32 s with the `scale` property), **tooltips type on**.
- **Caret**: block caret blink, finite (keep current 10 iterations).
- Infinite loops allowed: the 2 rain layers, (+ roll bar if it passes the perf check), + sheen only on running thread rows. Nothing else loops.
- Reduced motion: every theme animation/transition off (scoped list, not `*`), rain static.

## Perf rules (hard)
- Transform/opacity-only animations, `steps()` for rain; no SVG-internal animation in the rain tile, no background-position animation, no filters/blur/backdrop-filter, no text-shadow on body text, code text, or any large element; no animated text-shadow. Glow = static `box-shadow` on a handful of elements.
- Chrome re-styles every element with a running animation on each main frame, so one-shot effects must actually finish (`both`/`forwards` fill fine) and loops stay few.
- Targets: idle main thread ≪ the reference page (~350–400 ms / 5 s); report idle + busy for thread and draft, with no-theme and reference baselines, and running-animation counts in each state (idle thread, draft, typing, newest-row-just-arrived, running thread).
- Theme limits: CSS ≤ 20,000 chars after build, file ≤ 32 KB, only `data:`/`#id` urls (build.py enforces). If space is tight, trim the rain tile or comments; do not drop the requested effects.

## Harness (real T3 app, already running — reuse it)
- Throwaway T3 server **v0.1.10** (same build as the user's app) on `127.0.0.1:3999`, base dir `/tmp/t3-matrix-test` (PID in `/tmp/t3-matrix-test/serve.pid`); its own headless Chrome on CDP `:9388` (PID in `chrome.pid`), already paired and showing the app. Do not kill or restart them unless they die; if you must restart, use `/home/chetan/.t3/runtime/versions/0.1.10-nightly.20261114.4695/t3 serve --base-dir /tmp/t3-matrix-test --port 3999 --no-browser --host 127.0.0.1` (the `t3` on PATH is an OLD v0.1.2 with a different DOM — never use it).
- `design/verify/real/shoot.py` (read its docstring; fix/extend it freely, it was written quickly): `reload-theme` (rebuild first with `python3 -I build.py`; this publishes `matrix.json` into the throwaway instance only and reloads), `shot NAME --action thread:"Matrix rendering one" | draft | focus | type:TEXT | menu | tooltip | dialog | terminal [--width W --height H --chat-width wide|full --reduced-motion]`, `arrive` (sends a message with the real CLI and takes a screenshot burst), `bench`, `dom`. Threads with content: "Matrix rendering one" (headings, lists, table, blockquote, ts code), "Matrix python notes", "Matrix quote block", "Matrix tool run" (work-log/tool rows). Provider in the instance is Claude Haiku via the user's local claude CLI; keep extra `thread send` calls few and short.
- Close the right-hand project panel in screenshots unless the shot is about it.

## Real DOM facts for the new effects (v0.1.10, verified)
- Timeline is a **LegendList virtualised list**: `.messages-timeline-scroll > .legend-list-content-container > div(relative, height) > div(absolute container, style "contain: layout style paint; top…") > .messages-timeline-row-frame > .chat-content-lane[data-timeline-root] > [data-timeline-row-kind]`. Every row is the only child of its own lane, so `:last-child` / `:nth-last-child` on rows is **meaningless** (always true), and container DOM order is the recycle pool, not message order. Rows remount on thread switch and may remount when scrolled into view.
- `[data-timeline-row-kind]` carries `data-message-role` (user|assistant) and `data-message-id` directly.
- **New assistant output hook:** the markdown root gets `data-streaming="true"` while that message streams (ChatMarkdown component: `<… className data-streaming={…}>`). An animation keyed on `[data-streaming="true"]` starts once when the attribute appears and does not replay on text updates — use it for "decode out of the rain" + the row scan line. Verify in the app with `arrive` and confirm it doesn't loop or replay per token.
- `[data-thread-now-line]` exists (a live status line in the timeline while a thread works) — candidate for the running "decoding" effect.
- `[data-timeline-loading="true"]` is the loading placeholder.
- Pseudos `::before/::after` on rows, the lane, the row frame and the containers are all unused by T3 (computed content none).
- So: "rows flicker in" will run whenever a row mounts (thread open AND virtualised scroll-in). Test scrolling a long thread; if it's busy/distracting, gate it (e.g. only `[data-message-role=user]` bubbles + streaming assistant, or make the flicker very short) — your call, explain it.

## Verify in the real app and iterate
Screenshots into `design/verify/` (overwrite the old mock ones; delete mock-only files that no longer apply, e.g. `mock.py`, `pages/`, `draft-*.png` from the mock, if they are superseded — keep `cdp.py` only if still used): thread default, thread wide chat width (1900 px), draft/new-thread, composer focused empty, composer typing, new message arriving (a 3–5 frame burst showing decode + scan), menu open, tooltip, dialog, terminal drawer, narrow window (≈1100 px), reduced motion. Look at each critically next to the Possessed boards: is it clearly Possessed? Is prose comfortable to read? Iterate. Then perf.

## Report
Changed files; build line; what you took from Possessed and what you changed/toned down and why; screenshot list; perf table (idle/busy main-thread ms per 5 s, frames/s, running animations per state); open issues / fragile selectors.
