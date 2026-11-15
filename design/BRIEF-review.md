# Brief: independent review of the Matrix theme (read-only)

Review `~/Codebase/t3-matrix-theme` (a T3 Code theme). Read-only: do not edit any file, do not commit, do not publish or select themes in T3, do not touch Chrome on port 9222, never stop anything on port 20128. You may run `python3 -I build.py` into a temp copy and your own headless Chrome (kill only your own PID).

Read: `README.md`, `build.py`, `src/theme.css`, `src/colors.json`, `src/rain.svg`, `src/prompt.svg`, `matrix.json`, `design/BRIEF-implement.md` (requirements and verified DOM facts), screenshots in `design/verify/`.

Check and report findings ranked by severity, each with file:line, what breaks, and a concrete fix:
1. Correctness against the real T3 DOM facts in the brief (selectors that won't match, :has() structure, placeholder/prompt overlap, aria-busy sheen, glitch target, active row, monogram, terminal drawer, overlays). Flag any rule that could break T3 layout or interaction (overflow clipping, pointer-events, z-index, contain/isolation side effects, position changes on app elements).
2. Performance: count infinite animations, anything that repaints per frame, filters/blur/text-shadow on many or large elements, large layers. Rain must be transform-only.
3. Theme limits and build.py: CSS ≤ 20,000, file ≤ 32 KB, url() only data:/#id, no @import/image-set()/backslashes, "</" escaped inside data URIs, minifier correctness (it once broke descendant combinators).
4. Visual quality vs goal ("clearly Matrix, soothing, readable all day"): contrast of every text role (compute ratios), visible tile repetition (the 1000px rain tile visibly repeats on the new-thread screen at ~1500px width — propose a fix within budget, e.g. different background-size/offset per layer or a second layer offset), and anything that looks cluttered.
5. Reduced motion is fully static; narrow windows drop the rain.
6. README accuracy (install/undo commands, numbers, fragile selectors).

Final message: findings table (severity, file:line, issue, fix), then a short verdict.
