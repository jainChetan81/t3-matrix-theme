# Brief: independent review of the Matrix theme (review 2)

You review; you do NOT edit repo files, commit, publish themes, or touch the user's live T3 (`~/.t3/userdata`, `t3code.service`), the Chrome on :9222, or :20128. Do not spawn subagents. Write your report to `design/REVIEW-2.md` (the only file you create, plus optional `design/verify/review-*.png`).

Review HEAD of `~/Codebase/t3-matrix-theme`: `src/theme.css`, `src/colors.json`, `src/*.svg`, `build.py`, `README.md`; build output via `python3 -I build.py` in a temp copy (don't rewrite the tree's matrix.json).

The theme: one JSON (colour roles + ≤ 20,000 chars CSS, data: SVGs only) for T3 Code v0.1.10. Client bundle: `~/.t3/runtime/versions/0.1.10-nightly.20261114.4695/client/assets/*.js`. Verify every hook the CSS relies on exists and means what the CSS assumes (`[data-streaming]`, `[aria-label="Stop generation"]`, `.chat-banner-lane [data-variant="error"]`, `alert-dialog-*` slots, `[data-chat-composer-surface]` and whether T3 uses its pseudos, `data-sidebar-row`, `", Working,"`, `--chat-composer-outline`, `--chat-content-max-width`, `[data-chat-width]`, LegendList virtualisation). Check T3's theme CSS sanitizer/loader in the bundle: does it accept CSS nesting (`&`); would any declaration be dropped? Is relying on nesting safe for T3 desktop (find the Electron/Chromium version it ships if discoverable)?

A throwaway T3 0.1.10 instance with the theme applied runs at 127.0.0.1:3999 with headless Chrome on CDP :9388; `design/verify/real/shoot.py` drives it (docstring). Existing screenshots of every state: `design/verify/*.png`.

Look for: correctness bugs (selectors never/over-matching, effects that replay/loop wrongly, z-index/pointer-events covering controls, the Watcher overlapping text/buttons, reduced-motion gaps), perf-rule violations (rain transform-only with steps; infinite animations limited to rain ×2 + roll bar + Watcher glyph only while working + sidebar sheen only while running; one-shots finish; no filters/blur/text-shadow on large/many elements; no animated text-shadow), readability/contrast (the error banner's dark-red text was flagged as nearly unreadable), build/limit issues, README inaccuracies.

Report: findings table (severity, file:line, issue, concrete fix, how verified). Only real, verified findings. Concise. End with a verdict.
