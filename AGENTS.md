# AGENTS.md

## Purpose

Matrix theme for T3 Code: a green digital-rain theme with a phosphor-terminal chrome and the Watcher (a White Rabbit on the composer). The shipped artifact is `matrix.json`, a T3 theme file. Keep the theme inside T3's limits.

## Layout

- `src/theme.css`: the theme CSS, with `{{svg:NAME}}` placeholders.
- `src/*.svg`: artwork inlined as data URIs (prompt, rabbit, rabbit-work, rain, rain-field, rain-loop, spinners).
- `src/colors.json`: `dark` palette and optional `light` palette.
- `build.py`: builds `matrix.json` from `src/`. It minifies the CSS, inlines the SVGs, and checks the limits. No network access.
- `matrix.json`: generated. Commit it with the source change that made it.
- `README.md`: the look, motion, performance numbers, verify steps, and the fragile-selector list. Read the "Fragile selectors" and "Not verified" sections before a T3 update.
- `design/`: briefs, reviews, rounds and verify harness. History and reference only. Do not edit it for a code change.

## Build and check

```sh
python3 -I build.py                              # writes matrix.json; fails on a limit breach
python3 design/verify/real/shoot.py reload-theme # needs websocket-client; drives a throwaway T3 server
```

Limits enforced by `build.py`: CSS at most 50,000 characters, no `@import`, `image-set()`, `src()`, backslashes, or non-local `url()`. Only `data:` and `#` URLs pass.

The verify harness uses its own headless Chrome and never touches the live T3. Run it for visual changes. Screenshots go to `design/verify/` only when the change needs them.

## Install

- VPS: `t3 theme set ./matrix.json` (`t3` is on PATH). Undo by selecting another theme, such as `t3 theme set pixel-quest-plus`.
- Needs T3 Nightly `0.1.10-nightly.20261115` or later. Older builds reject a theme over 20,000 CSS characters.

## Rules

- Edit `src/`, then run `build.py`. Never hand-edit `matrix.json`.
- Keep the CSS under 50,000 characters. Check the count after each change.
- Keep every T3 selector in "Fragile selectors" in step with the code. If a change adds a selector, document it there.
- Keep reduced motion working. Check `reduced-motion.png` after motion changes.
- Do not add remote assets, fonts, or `@import`. The theme must stay self-contained.
- Commit only when the owner asks.
