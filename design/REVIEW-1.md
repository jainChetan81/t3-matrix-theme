The theme builds and passes every T3 limit, but it is not ready to ship: it was verified against a mock that differs from the real app in four places that matter. I checked the selectors against the installed T3 client bundle (`0.1.10-nightly.20261114`, read-only) and ran the built CSS in my own headless Chrome; nothing in the repo was changed.

## Findings

| # | Sev | File:line | Issue | Fix |
|---|---|---|---|---|
| 1 | High | `src/theme.css:191-203` | The busy light never shows while an agent works. On `composer-host`, `aria-busy` is set from the queued-message edit "is saving" state (together with `inert`). The rule also takes over the host's `::after`, which T3 already uses for the composer outline ring. | Delete the rule and `sh` keyframes. I found no working-state hook on the composer; sidebar rows carry `aria-busy` if an indicator is wanted. |
| 2 | High | `src/theme.css:19,26,56-62,73-75` | `[data-workspace-area="home"]` is not the new-thread screen. It marks the no-projects page, the "Couldn't start a new thread" page and the Welcome page; none has a composer. On the no-projects page an opaque full-size child covers the rain. The real new-thread screen is a conversation area with the composer centred as an overlay, so it gets the margin rain. | Drop the home rules, or keep them knowingly for those three pages. Re-check the draft screen in the live app. `design/verify/new-thread*.png` show a screen that does not exist. |
| 3 | High | `src/theme.css:13` | `--m` hard-codes the 736 px column. T3 has a chat-width setting (`:root[data-chat-width=wide]` is 72rem, `full` is 100%). At 72rem the rain runs under the text (reproduced at 1900 px). | `--m: calc(50% - var(--chat-content-max-width, 46rem)/2 - 32px)`. Tested: 214 px margins at 72rem and 1900 px; algebraically 0 at full. The lane can also be shifted by `--chat-lane-inset-start/end`; not checked. |
| 4 | High | `src/theme.css:66-67,185-188` | The rain dims on focus, not on typing. If the composer keeps focus while you read (the usual state, not confirmed live), the rain sits at .16 (brightest glyph 1.5:1) and the caret blink loops forever. That makes three infinite animations, not the README's two. | Dim only when there is text: `:root:has(.composer-tiptap:focus):not(:has(.composer-tiptap > p:only-child > br:only-child))`. Give the blink a finite count, e.g. `bl 1.1s steps(1) 10`. |
| 5 | Med | `src/theme.css:259-261` | Reduced motion is fully static (0 running animations, confirmed), but `*, ::before, ::after` with `!important` also switches off every T3 animation and transition, so T3's own indicators freeze. | List only the theme's own selectors: the rain pseudos, the glitch target, the caret `::after`, and the transitions on lines 35, 153 and 207. |
| 6 | Med | `src/theme.css:79-81` | Each breadcrumb text span sits alone in its own `<li>`, so `:last-of-type` matches all three and all of them glitch. Line 79 also paints the muted parent parts in `--hi`. | Target `[data-chat-header] li[aria-current="page"] [data-slot="workspace-breadcrumb-text"]` for both rules. |
| 7 | Med | `src/theme.css:146-158` | The forced border adds a second hairline next to T3's `::after` ring. `overflow: hidden` and `position` are only there for the busy light. The 12 px radius does not match the inner 16 px surface. | Recolour the existing ring: set `--chat-composer-outline` on the host (`#2a4034`, `#0affa073` on `:focus-within`). Drop the border, `overflow` and radius. |
| 8 | Med | `src/theme.css:42,48,70-75` | Narrow windows do drop the rain (≤1240 px thread, ≤820 px home, confirmed). The breakpoints use viewport width, so at 1241 px the strips are 92 px slivers, and an open right panel is not accounted for. On home between 821 and about 1066 px the mask stops cross and leave a hard edge. | `width: clamp(0px, (var(--m) - 96px) * 999, var(--m))` hides strips under 96 px without a media query. Raise the home breakpoint to about 1100 px or remove home. |
| 9 | Med | `src/theme.css:33,56-62` | The 1000×650 tile repeats. Horizontally it repeats on the full-width home layer; vertically it repeats every 650 px in every layer, including the real margin strips. | Horizontal: split home into `::before` and `::after` at `width: 50%` with mirrored masks; the right one gets `background-position: right -565px top 0`, a different duration and `animation-delay: -4s`. Tested at 1512 px: no visible repeat, two animations. Vertical: needs a taller tile; 1000×900 costs about 2.8k of the 5.6k chars left. |
| 10 | Low | `src/colors.json:24`, `src/theme.css:253,255` | Placeholder contrast is 4.21:1 on the composer. The scrollbar thumb is 1.6:1. All other text roles are 5.3:1 or better (table below). | Placeholder `#6f8f7d` gives 5.14:1. Thumb `#4a6b5a` gives 3.3:1. |
| 11 | Low | `src/theme.css:161-185` | `:has(> * > .composer-tiptap)` has no anchor, so every element is a candidate. The structure itself matches the real DOM, including the placeholder. | Prefix with `[data-chat-composer-form]` or `[data-slot="composer-host"]`. |
| 12 | Low | `src/theme.css:100-103` | The app's CSS defines `.chat-markdown.user-message-markdown`. If user bubbles render with it, the `.chat-markdown` colour and line-height override the bubble's, and the `# ` prefix appears in user messages. I did not confirm where the class is applied. | Scope the assistant rules with `[data-message-role="assistant"] .chat-markdown`. |
| 13 | Low | `src/theme.css:19-23` | `contain: paint` makes the area the containing block for any fixed-position descendant. `isolation` is redundant beside it, and the conversation area is already `relative`. I found no breakage. | `overflow: clip; isolation: isolate`. |
| 14 | Low | `src/theme.css:251-252` | The global `::-webkit-scrollbar` sizing applies to every scroller. Where scrollbars normally overlay, this would reserve 10 px and shift the lane against the composer (untested). | Check on the Mac; otherwise style only the thumb colour. |
| 15 | Low | `build.py:24,58` | Minifying runs after the SVGs are inlined, so it rewrites inside data URIs: `a , b ; c: d > e` becomes `a,b;c:d>e`. Today's SVGs come through intact. The descendant-combinator fix holds (`a :is(b)` survives). | Minify first, then substitute the placeholders. |
| 16 | Low | `build.py:48` | The `url()` check is case-sensitive: `URL(http://…)` passes the build. T3's own check is case-insensitive. | Add `re.I`. |
| 17 | Low | `build.py:63` | `"id"` is not in T3's theme file schema; the id comes from the filename. | Remove it. |
| 18 | Low | `README.md:11,14` | `~/.t3/bin/t3` does not exist on this VPS; `t3` is on PATH at `~/.local/bin/t3`. | Use `t3 theme set ./matrix.json` (publishes and sets in one step). Undo with `t3 theme clear` or a built-in: `t3-chat`, `grove`, `ocean`, `ember`, `iris`. |
| 19 | Low | `README.md:36,41,49,85,91,96` | Six statements are wrong given findings 1, 2, 4, 6 and 7: the new-thread paragraph, the "agent works" light, "at most two animations", "same hooks and nesting as the live app", the `:last-of-type` note, and owning `::after` on the composer card. | Correct after the fixes. |

## What checked out

- **Limits:** CSS is 14,377 of 20,000 chars (15,475 bytes) and the file is 17,702 of 32,768 bytes. There is no `@import`, `image-set()`, `src()`, backslash or `</`; only `data:` URLs.
- **Build:** a rebuild in a temp copy is byte-identical to `matrix.json`. All 61 colour roles match the app's role list, and the file fits T3's schema.
- **Sanitizer:** I replayed T3's CSS sanitizer on the built CSS: 67 rules, 672 declarations, none dropped.
- **Performance rules:** the rain is transform-only with `steps(26)`. There are no filters, no `text-shadow` and no backdrop blur. Layers are small (two strips of about 228×1500 px at 1512 px wide).
- **Animation counts on the mock:** two when idle, three when focused and empty, three when typing with `aria-busy` forced.
- **README numbers:** build line, 61 roles, 40 columns, 83 and 62 px/s, 13% centre and "0 running animations" are all correct. I did not re-run the benchmark table.

## Contrast

| Role | Ratio |
|---|---|
| Body text | 13.6 |
| Headings and strong | 16.6 |
| Muted text | 7.2 |
| Icon muted | 5.3 |
| User bubble | 13.3 |
| Inline code | 13.0 |
| Link | 12.3 |
| Blockquote | 9.3 |
| `# ` heading prefix | 7.5 |
| List marker | 5.7 |
| Code | 12.8 |
| Code comment | 7.3 |
| Sidebar | 12.5 |
| Sidebar muted | 6.5 |
| Tooltip | 12.1 |
| Send button | 14.3 |
| Error / warning / update | 7.8 / 11.2 / 10.1 |
| Placeholder | 4.2 |
| Rain head at .46 / at .16 | 4.3 / 1.5 |

## Verdict

The colours, limits, build and performance approach are sound, and the thread view looks calm and clearly Matrix. Fix findings 1–4 first; they are small edits, and removing the busy light and home rules frees roughly 700 chars.

The DOM facts here come from the shipped bundle, not the live app, so the draft screen and the sidebar row still need a look in the real app after the fixes.
