// Build the Possessed theme CSS.
// node build.mjs [hooks.json] [--mockup]
//   - swaps every @{hook} for its selector from hooks.json
//   - inlines src/rain.svg and src/spinner.svg as minimally escaped data: URIs
//   - minifies and reports the char count against the 20,000-char limit
//   --mockup drops the two data: URIs (the canvas boards draw the rain inline instead)
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const mockup = args.includes("--mockup");
const hooksPath = args.find((a) => !a.startsWith("--")) ?? join(here, "hooks.json");
const LIMIT = 20000;

const hooks = JSON.parse(readFileSync(hooksPath, "utf8"));
let css = readFileSync(join(here, "src/possessed.css"), "utf8").replace(/\/\*[\s\S]*?\*\//g, "");

const missing = new Set();
css = css.replace(/@\{([a-z-]+)\}/g, (_, name) => {
  const sel = hooks[name];
  if (!sel) {
    missing.add(name);
    return `[data-missing-hook="${name}"]`;
  }
  return sel.includes(",") ? `:is(${sel})` : sel;
});
if (missing.size) console.warn("hooks without a selector:", [...missing].join(", "));

// Keep raw UTF-8; escape only what breaks a quoted data: URI inside CSS, or an HTML <style> around it.
const dataUri = (file) => {
  let svg = readFileSync(join(here, "src", file), "utf8").trim();
  svg = svg.replace(/"/g, "'");
  // "</style" inside the SVG would close an inline <style> element if the theme CSS is ever injected as HTML.
  const esc = svg.replace(/%/g, "%25").replace(/#/g, "%23").replace(/<\/style/g, "%3C/style");
  return `url("data:image/svg+xml,${esc}")`;
};

// Minify first, then inline the SVGs, so the minifier never touches them.
// Spaces before ":" are kept: they are descendant combinators ("a :is(b)").
const out0 = css
  .replace(/\/\*[\s\S]*?\*\//g, "")
  .replace(/\s+/g, " ")
  .replace(/\s*([{};,>])\s*/g, "$1")
  .replace(/:\s+/g, ":")
  .replace(/;}/g, "}")
  .trim();
let out = out0;
for (const file of ["rain.svg", "spinner.svg"]) {
  out = out.replace(`url(${file})`, mockup ? "none" : dataUri(file));
}

mkdirSync(join(here, "dist"), { recursive: true });
const file = join(here, "dist", mockup ? "possessed.mockup.css" : "possessed.css");
writeFileSync(file, out);

const art = mockup ? 0 : dataUri("rain.svg").length + dataUri("spinner.svg").length;
console.log(`${file}`);
console.log(`total ${out.length.toLocaleString()} chars / ${LIMIT.toLocaleString()} (${((out.length / LIMIT) * 100).toFixed(1)}%)`);
if (!mockup) console.log(`  art ${art.toLocaleString()} · rules ${(out.length - art).toLocaleString()} · headroom ${(LIMIT - out.length).toLocaleString()}`);
if (out.length > LIMIT) {
  console.error("over the limit");
  process.exit(1);
}
