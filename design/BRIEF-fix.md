# Brief: apply review fixes to the Matrix theme

Work in `~/Codebase/t3-matrix-theme`. Do not commit/push, do not publish or select themes in T3, do not touch Chrome on port 9222, never stop anything on port 20128, do not spawn subagents. You may run your own headless Chrome (kill only your PID).

Context: `design/BRIEF-implement.md` (original requirements), `design/REVIEW-1.md` (independent review with 19 findings, verified against the installed T3 bundle). Apply ALL findings 1–19 as the review proposes, with these decisions:
- #1: remove the composer busy sheen entirely (no reliable working hook on the composer).
- #2: drop the `[data-workspace-area="home"]` rain rules. The real new-thread (draft) screen is a conversation area with no timeline rows and the composer centred as an overlay. Give that state fuller rain: when `[data-workspace-area="conversation"]:not(:has([data-timeline-row-kind]))`, widen the two rain layers to 50% each (left/right halves) with masks that fade toward the centre so the centred composer and heading stay clear, mirrored offsets/durations (review #9 recipe) so the tile does not visibly repeat. Keep it at two animations. Update/rebuild the mock so a draft screen exists (conversation area without rows + centred composer) and screenshot it.
- #3: margins from `--chat-content-max-width` (fallback 46rem); hide strips narrower than 96px without media queries (#8 recipe); also respect `--chat-lane-inset-start/end` if cheap.
- #4: dim only while the composer has text; caret blink finite (e.g. 10 iterations).
- #5: reduced-motion only for the theme's own animated selectors/transitions.
- #6, #7, #10–#17: as proposed. #9 vertical repeat: leave unless budget clearly allows.
- #18/#19: README corrections. For this Mac the CLI is `~/.t3/bin/t3`; on the VPS it is `t3` on PATH. Document both: `t3 theme set ./matrix.json` publishes and selects; undo by selecting another theme (`t3 theme set pixel-quest-plus` or a built-in: t3-chat, grove, ocean, ember, iris).

Then: `python3 -I build.py` must pass; regenerate `design/verify/*.png` (thread at default width, thread at wide chat width 1900px, draft/new-thread screen, composer focused empty, composer typing, narrow); re-run idle+busy perf for thread and draft vs no theme vs reference (https://chetan-examples.vercel.app/matrix); count running animations in each state. Look at the screenshots critically: calm, readable, clearly Matrix.

Final message: findings table with status (fixed/changed/skipped + why), build line, perf table, animation counts, screenshot paths, remaining risks.
