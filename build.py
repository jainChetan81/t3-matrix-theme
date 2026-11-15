#!/usr/bin/env python3
"""Build matrix.json (a T3 Code theme) from src/ without network access."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT = ROOT / "matrix.json"
MAX_CSS = 20_000
MAX_FILE = 32 * 1024


def fail(msg):
    sys.exit("BUILD ERROR: " + msg)


def min_css(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    # Never strip the space before ":" - "a :is(b)" and "a:is(b)" are different selectors.
    css = re.sub(r"\s*([{};,>])\s*", r"\1", css)
    return re.sub(r":\s+", ":", css).replace(";}", "}").strip()


def svg_uri(path):
    svg = path.read_text()
    if not svg.lstrip().startswith("<svg") or not svg.rstrip().endswith("</svg>"):
        fail(f"{path.name} is not a complete SVG")
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    svg = re.sub(r">\s+<", "><", re.sub(r"\s+", " ", svg)).strip()
    svg = svg.replace('"', "'")
    # Escape %, # and "</" (which would close the host <style>); keep UTF-8 glyphs raw.
    svg = svg.replace("%", "%25").replace("#", "%23").replace("</", "%3C/")
    return "data:image/svg+xml;charset=utf-8," + svg


def check(css):
    if len(css) > MAX_CSS:
        fail(f"css is {len(css)} chars, limit {MAX_CSS}")
    if re.search(r"@import|image-set\s*\(", css, re.I):
        fail("@import or image-set() is not allowed")
    if "\\" in css:
        fail("backslash in css is not allowed")
    if re.search(r"\bsrc\s*\(", css, re.I):
        fail("src() is not allowed")
    for m in re.finditer(r"url\(\s*(['\"]?)(.*?)\1\s*\)", css, re.I):
        if not m.group(2).lower().startswith(("data:", "#")):
            fail("non-local url(): " + m.group(2)[:60])


def main():
    css = (SRC / "theme.css").read_text()
    names = sorted(set(re.findall(r"\{\{svg:([a-z0-9-]+)\}\}", css)))
    # Minify before inlining, so the minifier never rewrites the inside of a data: URL.
    css = min_css(css)
    for name in names:
        css = css.replace("{{svg:%s}}" % name, svg_uri(SRC / f"{name}.svg"))
    check(css)
    colors = json.loads((SRC / "colors.json").read_text())
    theme = {
        "version": 1,
        "name": "Matrix",
        "appearance": "dark",
        "colors": colors["dark"],
        "css": css,
    }
    if colors.get("light"):
        theme["variants"] = {"light": colors["light"]}
    text = json.dumps(theme, indent=2, ensure_ascii=False) + "\n"
    size = len(text.encode())
    if size > MAX_FILE:
        fail(f"theme file is {size} bytes, limit {MAX_FILE}")
    OUT.write_text(text)
    print(f"css {len(css)}/{MAX_CSS} chars, file {size}/{MAX_FILE} bytes, svgs: {', '.join(names) or 'none'}")


if __name__ == "__main__":
    main()
