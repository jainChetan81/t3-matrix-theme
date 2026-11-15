# possessed — t3 code theme

digital rain plus a live phosphor terminal. css and embedded svg only.

## files

| file | what it is |
|---|---|
| `src/possessed.css` | theme source. `@{hook}` marks a hook placeholder. |
| `src/round4.css` | the watcher and the matrix touches, appended after possessed. `/*== name ==*/` sections are counted separately. |
| `src/rain.svg` | the rain tile, 1000×650. one tile feeds all three depths. |
| `src/spinner.svg` | 14×14 glyph cycler that replaces any lucide loader icon. |
| `src/watcher.svg` | the watcher's still poses as one 4-frame strip: idle, focused, typing, error. |
| `src/watcher-work.svg` | the watcher's working pose: one bold glyph cycling in the iris. the only looping svg. |
| `hooks.json` | hook name → selector. **fill in t3 code's real selectors.** |
| `palette.json` | colour roles, syntax, terminal ansi. rename the keys to the theme file's role names. |
| `build.mjs` | swaps hooks, inlines the svgs, minifies, counts chars. |
| `dist/possessed.css` | built output with the placeholder hooks. |

## build

```sh
node build.mjs            # uses ./hooks.json
node build.mjs my-hooks.json
```

the script prints chars per piece and fails if the result is over 20,000. current output, with the placeholder selectors in `hooks.json`:

```
piece         rules   svg   total
possessed      7434  7221   14655
watcher        1085  1482    2567
bullet time     389     0     389
wake up         474     0     474
deja vu         171     0     171
pills           377     0     377
round 4 adds 3,978 chars
total 18,633 chars / 20,000 (93.2%) · headroom 1,367
```

real selectors are shorter or longer than the placeholders, so the total moves once `hooks.json` is filled in. rebuild and read the number.

## hooks used

`sidebar`, `thread-row`, `thread-row-active`, `thread-row-running`, `project-monogram`, `chat-header`, `chat-title`, `conversation`, `message-row`, `message-row-assistant`, `user-bubble`, `assistant-markdown`, `code-block`, `composer-form`, `composer-card`, `composer-input`, `composer-empty`, `composer-empty-line`, `terminal-drawer`, `tooltip`, `menu`, `popover`, `dialog`, `button-destructive`, `button-cancel`, `error-alert`, `input`, `select`, `switch-checked`, `button`, `streaming` (`[data-streaming="true"]`), `working` (`[data-thread-now-line]`). lucide icons are targeted by class (`.lucide`, `[class*="lucide-loader"]`).

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
2. **the timeline is virtualised,** so the boot flicker and scan line play whenever a row mounts, including when it scrolls into view. the old `:nth-last-child` stagger was removed: in a virtualised list every row is an only child, so it never matched.
3. **the prompt and block caret live on the editor** (`@{composer-input}::before` / `::after`, editor `position: relative`, prompt at `0 0`, caret at `left: 14px; top: 3px`, text at `padding-left: 26px`). if the editor is its own scroll container, both scroll with long drafts.
4. **the roll bar is a `position: fixed` pseudo on the chat header.** a transformed ancestor would turn it into an absolute one.
5. **the dialog power-on uses the `scale` property,** so it composes with the app's own centring transform.
6. **the theme takes over `::before` and `::after`** on conversation, sidebar, message rows, chat header, composer card, composer editor, code block, tooltip and running thread rows, plus the empty editor line's `::after`. if t3 code already uses any of these, they'll conflict.
7. **the data: uris keep raw utf-8 katakana,** escaping only `%`, `#` and `</style`. base64 is no longer an option: all four svgs in base64 take 12,996 chars instead of 8,703, which puts the theme at 22,926, over the limit.

## round 4: the watcher and matrix touches

### the watcher

a 30 px sentinel eye sealed onto the composer card's top edge, left side. it is the **composer card's `::before`** (card `position: relative`, pseudo at `top: -15px; left: 14px`), so it follows the card wherever the card sits. the card's **`::after`** holds the red error copy and the bullet-time ring. the `❯` prompt and block caret moved to the editor to free both. strokes are 1.15 (15% heavier), and the disc is opaque `#010803`, so the card border never shows through.

| state | selector | what plays |
|---|---|---|
| idle | `@{composer-card}::before` | eye shut. no animation, no breath. |
| focused | `@{composer-card}:has(@{composer-input}:focus)::before` | eye open, iris centred: looking at you. opens once (.3 s, scaleY, 3 steps). |
| typing | `@{composer-card}:not(:has(@{composer-empty}))::before` | lids narrow, iris low-right: glancing at the text. steps 1 px down-right (.45 s, 3 steps). |
| working | `:root:has(@{streaming}, @{working}) @{composer-card}::before` | swaps to `watcher-work.svg`: one bold glyph cycles ア 7 ヌ in the iris, and the eye steps up to 1.1×. the only loop. |
| done | none of its own | a transition, not an animation: when working or typing stops matching, the eye steps back to 1× (.45 s, 3 steps). it never plays on page load. |
| error | `:root:has(@{error-alert}) @{composer-card}::after` | a red copy jitters twice, holds, fades by .8 s and stays gone. |
| reduced motion | possessed's global rule + the svg's own media query | every state shows its pose still. working holds ア. error stays red. |

- `@{composer-empty}` is the `<br>` of `<p><br></p>`. the typing rule is `:not(:has(…))` because `:has()` can't nest inside `:has()`.

### matrix touches

| touch | selector | what plays | chars |
|---|---|---|---|
| bullet time | `:root:has(@{streaming})` | the near rain (`::before`) pauses and the far rain (`::after`) keeps falling, in the conversation and the sidebar. three rings leave the watcher when streaming starts (.8 s each, scale .8 → 2.2, clipped to the half above the card), then stop. | 389 |
| wake up | `:root:not(:has(@{message-row})) @{composer-empty-line}` | on a new thread the placeholder is "Wake up, Neo…" and types itself on once. | 474 |
| déjà vu | `@{message-row}:has(@{streaming})` | when streaming starts in a row, that row jumps 6 px and dims for one 120 ms beat, once. | 171 |
| red pill / blue pill | `@{dialog} @{button-destructive}` / `@{button-cancel}` | capsules with a gloss on the left cap. labels measured at 6.6:1 (red) and 7.6:1 (blue). | 377 |

### checked in chrome

- idle: no animation, no transform.
- streaming starts: near rain `paused`, far rain `running` (conversation and sidebar). the ring runs `rip` × 3. the watcher swaps to the working svg.
- déjà vu runs only on the streaming row. it doesn't restart on a text update, ends on its own, and never restarts the row's boot. no other row is affected.
- streaming ends: the watcher transitions from 1.1× back to 1×.
- reduced motion: 0 running animations, and every state holds its pose (crops on the round-4 build board).

### rejected

- **sunglasses reflection on code panes:** a moving sheen would sit over code.
- **sentinel scan:** the working watcher already scans. a sweep across the thread would cross prose.
- **the construct (white room) for dialogs:** a white flash on a black app is harsh, worst at night.
- **phone-booth exit:** css can't animate an element being removed, and there's no closing hook.
- **the oracle's cookie:** no state to attach it to.
- **there is no spoon:** cut for budget.
- **music:** a theme can't play audio.

### assumptions

- **streaming attribute:** `[data-streaming="true"]` sits inside the message row, not on the row element. `:has()` only looks at descendants.
- **placeholder:** the new-thread line assumes the editor draws its placeholder as the empty `<p>`'s `::before`, as tiptap and prosemirror placeholder plugins do. if t3 code renders it as a separate element, both would show.
- **déjà vu replays on remount:** if a streaming row is scrolled out and back in, it remounts and plays its boot and déjà vu again.
