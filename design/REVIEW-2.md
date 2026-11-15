# Review 2: Matrix theme at HEAD (3246b43)

The theme is close, but not ready to ship: three colour roles are inverted, which makes every error, warning and update text in the app unreadable, and two effects trigger in the wrong state. Everything else the brief asked about checked out, including nesting, the sanitizer and the hooks.

Checked against the 0.1.10 client bundle (read-only) and the throwaway instance on :3999. Nothing in the repo was changed except this file and two screenshots.

## Findings

| # | Sev | File:line | Issue | Fix | How verified |
|---|---|---|---|---|---|
| 1 | High | `src/colors.json:29,32,35` | `errorForeground`, `warningForeground` and `updateForeground` are dark (`#1a0805`, `#171305`, `#04140f`). T3 uses these roles only as text colours on dark surfaces. The error banner text is 1.03:1 on its background; the same roles colour the sidebar "Failed", "Approval" and "Limited" labels, destructive text and warning alerts. This is the flagged banner. | Make them light: `#ffb3a3` (10.4:1 on `errorSurface`), `#f0df8a` (12.7:1 on `warningSurface`), `#8fe9e0` (12.1:1 on `updateSurface`). | Live: banner computed colour is `--error-foreground`, background is the canvas at 80%. Bundle: built-in dark values are `#ff6467`, `#ffb900`, `#51a2ff`; about 60 `text-*-foreground` class uses, none as a background. Before and after: `design/verify/review-2-error-banner-*.png`. |
| 2 | Med | `src/theme.css:361` | "Wake up, Neo…" also starts on every thread load. `[data-timeline-loading]` is up for 200 to 330 ms when a thread opens; for that time the placeholder is transparent (the `backwards` fill) and the rain mask jumps to 53% (line 72). A load over .4 s would start typing the line in an existing thread. | Key on the draft layout: `… ~ [data-chat-composer-overlay].items-center .text-placeholder`. It matches the draft (1 element); the thread overlay is `inset-x-0 bottom-0` with no `items-center`. It is a Tailwind class, so list it under fragile selectors. | Live: logged animations per frame on a reload and three thread switches; `wh` and `wu::before` ran each time while loading. |
| 3 | Med | `src/theme.css:337,494` | The Watcher leaves its working pose when you type during a turn. With text in the composer the stop button becomes "Queue message" or "Steer message", and "Stopping" after you press stop. | `:has([aria-label="Stop generation"], [aria-label="Stopping"], [aria-label="Queue message"], [aria-label="Steer message"])` in both rules (about 170 chars; 1,607 are free). | Live, one real turn: button label was "Queue message" from 2.0 to 2.8 s and the eye showed the narrowed pose under "Working for 1s". Labels read from the bundle. |
| 4 | Low | `src/theme.css:491` | The reduced-motion spinner fallback never applies to `lucide-loader*` icons: line 405's `:is()` gives (0,2,0), line 491's bare `[class*="lucide-loader"]` is (0,1,0). They keep the animated SVG. | Use the same selector: `:is([class*="lucide-loader"], [data-sidebar-row] .lucide-circle-dashed) { … }`. | Live, emulated reduced motion, probe element: background still the data URL, stroke transparent. `.lucide-circle-dashed` was fine. The icon is real: `lucide-loader-circle` is in the send button while "Submitting message". |
| 5 | Low | `src/theme.css:384` | The sheen needs the label ", Working,". A running thread is labelled "Setting up" while preparing and "Goal" while a goal is active, so those get no sheen. | `:is([aria-label*=", Working,"], [aria-label*=", Goal,"], [aria-label*=", Setting up,"])`, or document it. | Bundle only (the sidebar status expression); neither state was seen live. |
| 6 | Low | `src/theme.css:319` | `background: none !important` on the composer surface does nothing (the surface has no background) and blocks T3's drag-over tint (`in-data-[thread-context-over]:bg-accent/45`). | Delete the declaration. | Live: computed background is identical with the declaration removed. The class is on the live element; the drag itself was not exercised. |
| 7 | Low | `src/theme.css:320-328` | The `/` and `@` pickers end at the card's top edge and sit above the Watcher, so its top half is cut off while a picker is open. No text or control is covered. | Accept and document, or drop it. | Live: typed `/` and `@`; the picker is `fixed`, z-index 40; screenshot taken. |
| 8 | Low | `README.md:58,68,83,104,221,224,227,241` | Six statements are off: the stop button is not there "for the whole turn" (#3); "Wake up" is not limited to the new-thread screen (#2); line 104 says 33 px/s, the far layer is 31 (560 px / 18 s, as line 38 says); line 241 says no `lucide-loader` icon was seen (#4); line 227 says the desktop Chromium was not checked. | Correct after the fixes. The desktop app ships Electron 44.10.1. | `third-party-licenses.json` in the client bundle, entry `electron`, bundle `desktop`. |

## What checked out

- **Build.** A rebuild in a temp copy is byte-identical to `matrix.json`: 18,393 of 20,000 chars, 21,100 of 32,768 bytes, 61 roles, five `data:` URLs. T3 counts UTF-16 units and `build.py` counts code points; they agree because the CSS has no astral characters.
- **Sanitizer and nesting.** The sheet T3 applied is rule-for-rule identical to a fresh parse of the built CSS: 106 style rules, 32 keyframes, 2 media rules, nothing dropped. All 372 declarations pass `CSS.supports`. The sanitizer recurses into nested rules and only strips values with a backslash, `image-set(`, `src(` or a non-`data:` `url()`.
- **Nesting on desktop.** Safe. The nested type selectors need Chrome 120; Electron 28 was the first with it, and T3 ships 44.10.1.
- **Hooks**, each found in the bundle and seen live:
  - `data-streaming` is a bare attribute on `.chat-markdown`.
  - "Stop generation" is the send button's label while running with an empty composer.
  - `.chat-banner-lane [data-variant="error"]` is the thread error banner.
  - All eight `alert-dialog-*` slots exist.
  - `[data-chat-composer-surface]` is static inside a relative card, with both pseudos unused by T3.
  - `data-sidebar-row` holds `<env>:<thread id>`; the label is title, status, project joined by ", ".
  - `--chat-composer-outline` colours T3's `::after` ring (computed `#0affa0b3` on focus).
  - `--chat-content-max-width` is 46rem, 72rem for `wide`, 100% for `full`, set by `:root[data-chat-width]`.
  - No theme variable collides with a T3 one.
- **Performance rules.** Idle is 3 running animations (rain x2, roll bar). During the real turn the only extra loops were the sheen and T3's own two; the near rain paused while streaming; every one-shot ended. No filter, blur or animated `text-shadow`; the one static `text-shadow` is on the header title.
- **Reduced motion.** 0 running animations in an idle thread and in the error thread.
- **Overlap.** Nothing sits under the Watcher in a thread, a draft, with an image attached, or during a run. Tooltips are readable (dark ink on the accent).

## Not verified

- **Row remount on scroll.** The timeline list is LegendList 3.7.2 with recycling off and the default 250 px draw distance, so rows can remount and flicker in a long thread. I could not force it: at a 278 px viewport over a 1,535 px timeline all six rows stayed mounted.
- **A queued-message banner above the composer.** My queued line was consumed before a banner showed, so its overlap with the Watcher is unknown.
- **Streaming segments.** `data-streaming` toggled twice in my one turn, so the decode, déjà vu and rings each played twice. The README already describes this.

## Side effects of this review

The `probe2` thread in the throwaway instance has one more real turn (two user lines, one Haiku reply). The test page was reloaded and left on "Matrix rendering one" with no emulation set.

## Verdict

Fix #1 before shipping; it is three hex values. #2 and #3 are one-selector edits and worth doing in the same pass. The rest is polish. Hooks, limits, the sanitizer, nesting and the motion budget are sound.
