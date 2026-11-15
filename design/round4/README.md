# Round 4 — the Watcher + more Matrix

Canvas: https://claude.ai/artifact/UUftboWWM9ECibT6gKWEuf (page "Round 4 · Watcher + Matrix").
Possessed stays the base. This round adds a 30 px living glyph on the composer and four Matrix touches.
Nothing here is wired into `src/` yet.

## What was asked

Two prompts to Claude Design, saved verbatim: `prompt4.txt` (the round) and `prompt5.txt` (one follow-up).
Its replies are in `claude-design-reply-1.txt` and `claude-design-reply-2.txt`.

The follow-up changed five things after I looked at the first boards:

1. Watcher 26 → 30 px, strokes 15% heavier, opaque disc; working = one bold glyph in the iris (the first version's katakana was mush at 1×); idle fully still.
2. Bullet time: the first version froze all rain for the whole stream, which looks broken on a long reply. Now only the near layer pauses, and the rings fire 3 times instead of looping.
3. Hooks: `:last-child` rules replaced (the timeline is virtualised), déjà vu keyed to `[data-streaming="true"]`, Watcher anchored to the card.
4. Budget cut from 4,615 to 3,978 chars (placeholder selectors).
5. Board B shows the real 1× size beside each state.

## Canvas cleanup

Worked. Page order is now: **Final · Possessed**, **Round 4 · Watcher + Matrix**, **Archive · Round 1**, **Archive · Round 2**. Nothing was deleted. Claude Design also regenerated the three Final · Possessed boards (a canvas-only rain preview bug, and to match the moved prompt/caret); it says the look is unchanged — I did not re-compare those three against round 3.

## What Claude Design produced

| file | board |
|---|---|
| `A-watcher-concepts.png` | four concepts × seven states at 4× and 1× |
| `B-watcher-in-place.png` | the chosen eye on a Possessed composer, 1.5× and real size |
| `C-matrix-thread.png` | thread while streaming: Watcher working, near rain paused |
| `D-matrix-new-thread.png` | new thread: "Wake up, Neo…" |
| `E-matrix-pills-dialog.png` | red pill / blue pill confirm |
| `check-build-output.png` | its built CSS in Chrome, every state, with and without reduced motion |

- `boards/*.dc.html` — the six boards' DOM. `boards/watcher-boards-style.css`, `boards/matrix-boards-style.css` — the boards' CSS (no data URIs in them).
- `kit/` — Claude Design's updated kit: `src/round4.css`, `src/watcher.svg`, `src/watcher-work.svg`, updated `src/possessed.css`, `hooks.json`, `build.mjs`, `README.md`, `dist/possessed.css`. I did not run `build.mjs`; its numbers below are Claude Design's.
- `watcher.svg`, `watcher-work.svg` — the two Watcher SVGs in full (copies of `kit/src/`).
- `round4.real.css` — `kit/src/round4.css` with T3 Code's real selectors substituted, by me. **Not tested in the app.**

Screenshot caveat: in board B/C/D stills the `❯` prompt shows as a hollow box. The VPS Chrome has no font with that glyph; the build-check board (rendered by Claude Design) shows it correctly.

## The Watcher: the Sentinel eye

Concepts: (a) glyph core, (b) Sentinel eye, (c) lens, (d) white rabbit. Picked **b**.

- It reads without motion: shut, open, glancing and red are four different drawings.
- It is the only one that literally watches — focused is an eye looking straight out.
- The glyph core is mush at 30 px, the lens can't show where it looks, the rabbit is the cute mascot the brief ruled out.

### SVGs

`watcher.svg` — one 4-frame strip, 112×28 drawn at 120×30: idle (shut), focused (open, iris centred), typing (narrowed, iris low-right), error (red). 735 chars raw.

`watcher-work.svg` — the working pose: ア → 7 → ヌ cycling in the iris, .6 s, `steps(1)`, with its own reduced-motion rule that holds ア. 659 chars raw. This is the only loop the round adds.

### States (real T3 hooks)

Anchor: `[data-chat-composer-surface]::before` (the eye) and `::after` (red error copy + bullet-time ring). The surface is `position: static` inside the relative `[data-slot="composer-host"]`, so the pseudos position against the host; the surface's pseudos are unused by the app. The host's own `::before`/`::after` are already taken by the app — don't use them. Claude Design's kit puts the Watcher on the composer card's pseudos and moves the prompt and caret to the editor; the real theme already keeps prompt and caret on the editor's grandparent, so nothing has to move.

| state | selector | what plays |
|---|---|---|
| idle | `[data-chat-composer-surface]::before` | eye shut, no animation |
| focused | `[data-chat-composer-surface]:has(.composer-tiptap:focus)::before` | opens once (.3 s, scaleY, 3 steps), looks at you |
| typing | `[data-chat-composer-surface]:not(:has(.composer-tiptap > p:only-child > br:only-child))::before` | lids narrow, iris low-right, nudged 1 px |
| working | `:root:has([data-streaming="true"], [data-thread-now-line]) [data-chat-composer-surface]::before` | swaps to `watcher-work.svg`, 1.1× |
| done | no hook | the `transition: transform .45s steps(3)` plays when working/typing stops matching |
| error | `:root:has([role="alert"]) [data-chat-composer-surface]::after` | red copy jitters twice, holds, fades by .8 s |
| reduced motion | scoped rule + the svg's own media query | static pose per state |

The exact CSS is in `round4.real.css`, section `/*== watcher ==*/`:

```css
:root { --w: url(watcher.svg); --ww: url(watcher-work.svg); }
[data-chat-composer-surface]::before, [data-chat-composer-surface]::after {
  content: ""; position: absolute; z-index: 3; left: 14px; top: -15px;
  width: 30px; height: 30px; pointer-events: none;
}
[data-chat-composer-surface]::before {
  background: var(--w) 0 0 / 120px 30px;
  transition: transform .45s steps(3);
}
[data-chat-composer-surface]:has(.composer-tiptap:focus)::before {
  background-position-x: -30px;
  animation: wk .3s steps(3);
}
[data-chat-composer-surface]:not(:has(.composer-tiptap > p:only-child > br:only-child))::before {
  background-position-x: -60px;
  transform: translate(1px, 1px);
}
:root:has([data-streaming="true"], [data-thread-now-line]) [data-chat-composer-surface]::before {
  background: var(--ww) 0 0 / 30px !important;
  transform: scale(1.1) !important;
}
:root:has([role="alert"]) [data-chat-composer-surface]::after {
  background: var(--w) -90px 0 / 120px 30px;
  border: 0; opacity: 1;
  animation: we .8s steps(1) forwards;
}
@keyframes wk { from { transform: scaleY(.25) } }
@keyframes we { 0% { transform: translate(2px) } 20% { transform: translate(-2px) } 40% { transform: none } 70% { opacity: 1 } to { opacity: 0 } }
```

## Matrix touches: four kept

### Bullet time

While a reply streams, the near rain layer pauses and the far layer keeps falling. Three rings leave the Watcher when streaming starts (.8 s each), clipped to the half above the card, then stop.

```css
:root:has([data-streaming="true"]) [data-workspace-area="conversation"]::before { animation-play-state: paused; }
:root:has([data-streaming="true"]) [data-chat-composer-surface]::after {
  border: 1px solid var(--g); border-radius: 50%;
  clip-path: inset(0 0 50%); opacity: 0;
  animation: rip .8s ease-out 3;
}
@keyframes rip { from { transform: scale(.8); opacity: .6 } to { transform: scale(2.2); opacity: 0 } }
```

The kit also pauses the sidebar's near layer; the real build's sidebar rain is static, so that selector is dropped.

### "Wake up, Neo…"

On a new thread the placeholder types itself on once. Claude Design assumed the placeholder is the empty `<p>`'s `::before`. In T3 it is a separate element (`.pointer-events-none` beside the editor, text "Ask anything. @ files, $ skills, / commands"), so its kit rule would show both. My substitution hides that element's text and types ours in its place:

```css
:root:not(:has([data-timeline-row-kind])) [data-chat-composer-form] :has(> * > .composer-tiptap) > .pointer-events-none { font-size: 0; }
:root:not(:has([data-timeline-row-kind])) [data-chat-composer-form] :has(> * > .composer-tiptap) > .pointer-events-none::before {
  content: "Wake up, Neo…";
  font-size: .875rem;
  display: inline-block;
  clip-path: inset(0 100% 0 0);
  animation: wu 1.3s steps(13) .3s forwards;
}
@keyframes wu { to { clip-path: inset(0) } }
```

This animates `clip-path` on one line of text, once — not transform/opacity. If that breaks the perf rule, drop the animation and keep the static text. It also replaces the real hint about `@`, `$` and `/` on every new thread, which is a usability cost worth a second look.

### Déjà vu

The row whose reply starts streaming jumps 6 px and dims for one 120 ms beat, once.

```css
[data-timeline-row-kind]:has([data-streaming="true"]) { animation: dv .12s .3s steps(1); }
@keyframes dv { from { transform: translate(6px, -3px); opacity: .5 } }
```

Append `dv` to whatever animation that row already has in `src/theme.css`; as written it would replace it. It replays if a streaming row scrolls out and back in (remount).

### Red pill / blue pill

Capsules with a gloss on the left cap, on confirm dialogs. Claude Design measured label contrast at 6.6:1 (red) and 7.6:1 (blue).

```css
[data-slot="dialog-popup"] :is([data-slot="button"][data-variant="destructive"], [data-slot="dialog-close"]) {
  border: 0 !important; border-radius: 99px !important; color: #fff !important;
  background: radial-gradient(12% 32% at 13% 32%, var(--a, #6aa0ff), var(--b, #1a4ac4)) !important;
}
[data-slot="dialog-popup"] [data-slot="button"][data-variant="destructive"] { --a: #ff6a90; --b: #c4124b; }
```

## Hooks: what is verified

Read from the throwaway T3 v0.1.10 instance (one read-only DOM query on a draft screen):

- `[data-slot="composer-host"]` is `position: relative`, overflow visible, and both its pseudos already have content.
- `[data-chat-composer-surface]` is static, overflow visible, pseudos free. No ancestor up to `[data-chat-composer-stack]` clips.
- The placeholder is a separate `div.pointer-events-none`.

Not verified — no such element was on screen:

- **Error:** `[role="alert"]` is a guess. If T3 uses it for non-error toasts, the eye will flash red on those too.
- **Pills:** `[data-variant="destructive"]` and `[data-slot="dialog-close"]` are guesses.
- **Streaming:** `[data-streaming="true"]` must be a descendant of the row (BRIEF-possessed says it is on the markdown root, so it should hold).

## Chars

| piece | Claude Design, placeholder hooks | mine, real hooks |
|---|---|---|
| watcher (rules + 2 svgs) | 2,567 | 2,537 |
| bullet time | 389 | 373 |
| wake up | 474 | 416 |
| déjà vu | 171 | 146 |
| pills | 377 | 371 |
| reduced-motion additions | in Possessed's global rule | 331 |
| **round 4** | **3,978** | **4,174** |

The real-hook column is my own crude minify of `round4.real.css`, not `build.py`'s count. `build.py` reported the current theme at 15,546 / 20,000 when I ran it, so the round lands at about 19,720 — roughly 280 chars of headroom. If it doesn't fit, cut in this order: pills (371), déjà vu (146), the "Wake up" type-on animation.

Base64 is out: Claude Design measured all four SVGs in base64 at 12,996 chars instead of 8,703.

## Perf

- One new loop: the three-glyph cycle inside the 30 px working SVG, only while working/streaming.
- Bullet time removes work (one rain layer paused) and adds a finite 3 × .8 s ring.
- Everything else is one-shot or a transition. No filters, blur, text-shadow or animated shadows.
- Exceptions to transform/opacity-only: the Watcher's state swap changes `background-position` (a discrete change, not animated), and my "Wake up" substitution animates `clip-path` once.
- Claude Design reports 0 running animations under reduced motion in its Chrome check. Nothing was measured in the real app.

## Rejected

By Claude Design, and I agree:

- **Sunglasses reflection on code panes, Sentinel scan** — a sweep over code or prose.
- **The Construct (white room)** — a white flash on a black app.
- **Phone-booth exit** — CSS can't animate an element being removed.
- **The Oracle's cookie** — no state to attach it to.
- **There is no spoon** — built, then cut for budget.
- **Music** — a theme can't play audio.
- **Watcher concepts a, c, d** — see above.

By me:

- **The kit's move of the `❯` prompt and block caret** onto the editor's pseudos — the real theme already solved this differently; keep the real one.
- **The kit's "Wake up" rule** — wrong placeholder assumption, replaced above.
- **Sidebar rain pause** — the real sidebar rain is static.
