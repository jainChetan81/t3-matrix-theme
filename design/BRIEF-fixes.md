# Brief: fix the open issues of the Matrix theme (round 6)

You implement and verify, yourself (no subagents). Work in `~/Codebase/t3-matrix-theme`. Do not commit/push. Do not touch the user's live T3 (`~/.t3/userdata`, `t3code.service`), the Chrome on :9222, the MacBook, or anything on :20128. Kill only PIDs you start; no blanket kills. No outbound messages, no logins.

## Context
Read `README.md`, `design/BRIEF-watcher.md`, `design/BRIEF-possessed.md` (perf rules, real DOM facts), `design/REVIEW-2.md`, `design/verify/real/dom-notes.md`, `design/verify/real/shoot.py`. Theme source: `src/theme.css`, `src/colors.json`, `src/*.svg`; build with `python3 -I build.py` (CSS ≤ 20,000 chars, now 18,653; file ≤ 32 KB).

## Harness (currently STOPPED — restart it)
- Server: `/home/chetan/.t3/runtime/versions/0.1.10-nightly.20261114.4695/t3 serve --base-dir /tmp/t3-matrix-test --port 3999 --no-browser --host 127.0.0.1` (background, write its PID to `/tmp/t3-matrix-test/serve.pid`). Never use the `t3` on PATH (v0.1.2).
- Headless Chrome on CDP :9388 with profile `/tmp/t3-matrix-test/chrome` (see `chrome.log` there for the previous launch flags; it was paired before — if pairing is lost, mint a token with the runtime binary's `t3 pair`/auth commands against base-dir `/tmp/t3-matrix-test`, never the live one). PID to `chrome.pid`.
- At the end, stop both (only those PIDs) and confirm with `ss -ltnp` that :3999/:9388 are free and :20128 is still listening.

## Fix these (each: fix, verify in the real app, screenshot to `design/verify/`)
1. **`/` and `@` pickers cover the top half of the Watcher.** Find the real picker hook in the DOM and, while a picker is open, hide or move the Watcher cleanly (e.g. fade it out). Shot: `watcher-picker.png`.
2. **"Wake up, Neo…" replays after typing and then clearing a draft.** It's keyed on `[data-chat-composer-overlay].items-center`. Find a trigger that only mounts once per new-thread screen (or make the replay impossible, e.g. key on an element that does not remount on typing). If no reliable CSS-only fix exists, make the replay harmless (e.g. only the short final reveal) and say so.
3. **Very short replies end before the third bullet-time ring.** Rings stop when `[data-streaming]` goes away. Make all three rings complete within a short window (≈0.6–0.8 s total), or anchor them so they finish regardless. Verify with a hand-set streaming attribute removed after 300 ms.
4. **Above ~1850 px wide the near rain repeats at the far edge.** Fix via tile scale/offset (keep 2 layers, transform-only, steps()). Shots: `thread-wide-1900.png`, plus a 2560 px shot `thread-wide-2560.png`.
5. **Thread-open key misses ~1/16 switches** (last hex char of the active sidebar row id). Improve cheaply if possible (e.g. a second independent key on a second element/property so both must collide), within the char budget; otherwise leave it and document.
6. **Rows may flicker in again when scrolled back in long virtualised threads (unverified).** Make a long thread in the throwaway instance (a few `thread send` calls to Haiku asking for long answers is fine, keep it to ≤4), scroll up/down, and observe. If re-flicker is distracting, gate it (e.g. limit to user bubbles + streaming assistant rows, or shorten). Report what you saw.
7. **Frame rate under load in GPU-less Chrome (~30–40 fps).** Look for a cheap win that keeps the look (e.g. `contain`/`will-change` placement, smaller masked area, simpler mask on the far layer). Measure before/after with `shoot.py bench`; keep only changes that help.

## Then
- Re-measure perf (thread idle/busy, draft idle/busy, typing, working, reduced motion; running-animation counts) and update the README perf table, fragile selectors, open issues and screenshots list. Refresh `thread.png`, `draft.png`, `reduced-motion.png`.
- Look critically at every new shot; the look must stay the Possessed/Watcher design the user approved.
- `python3 -I build.py` must pass.

## Report
Changed files, build line, per-issue: fixed / mitigated / left (and why), screenshot list, perf table, anything still open.
