// Build the Possessed theme CSS (possessed.css + round4.css).
// node build.mjs [hooks.json] [--mockup]
//   - swaps every @{hook} for its selector from hooks.json
//   - inlines the svgs in src/ as minimally escaped data: URIs
//   - minifies, reports chars per piece, fails above 20,000
//   --mockup drops the data: URIs (the canvas boards draw rain and watcher inline)
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const mockup = args.includes("--mockup");
const hooksPath = args.find((a) => !a.startsWith("--")) ?? join(here, "hooks.json");
const LIMIT = 20000;
const SOURCES = ["possessed.css", "round4.css"];
const SVGS = ["rain.svg", "spinner.svg", "watcher.svg", "watcher-work.svg"];

const hooks = JSON.parse(readFileSync(hooksPath, "utf8"));
const missing = new Set();
const swapHooks = (css) =>
  css.replace(/@\{([a-z-]+)\}/g, (_, name) => {
    const sel = hooks[name];
    if (!sel) {
      missing.add(name);
      return `[data-missing-hook="${name}"]`;
    }
    return sel.includes(",") ? `:is(${sel})` : sel;
  });

// Spaces before ":" are kept: they are descendant combinators ("a :is(b)").
// Quoted strings ("Wake up, Neo…", attribute values) are left exactly as written.
const minify = (css) =>
  css
    .split(/("[^"]*"|'[^']*')/)
    .map((part, i) =>
      i % 2
        ? part
        : part
            .replace(/\s+/g, " ")
            .replace(/\s*([{};,>])\s*/g, "$1")
            .replace(/:\s+/g, ":")
            .replace(/;}/g, "}"),
    )
    .join("")
    .trim();

// Keep raw UTF-8; escape only what breaks a quoted data: URI inside CSS, or an HTML <style> around it.
const dataUri = (file) => {
  const svg = readFileSync(join(here, "src", file), "utf8").trim().replace(/"/g, "'");
  const esc = svg.replace(/%/g, "%25").replace(/#/g, "%23").replace(/<\/style/g, "%3C/style");
  return `url("data:image/svg+xml,${esc}")`;
};

// Split each source into pieces: possessed.css is one piece, round4.css has "/*== name ==*/" sections.
const pieces = [];
for (const src of SOURCES) {
  const text = readFileSync(join(here, "src", src), "utf8");
  const parts = text.split(/\/\*==\s*([\w -]+?)\s*==\*\//);
  if (parts.length === 1) pieces.push({ name: src.replace(".css", ""), css: text });
  else for (let i = 1; i < parts.length; i += 2) pieces.push({ name: parts[i], css: parts[i + 1] });
}

let total = "";
const rows = [];
for (const p of pieces) {
  let css = minify(swapHooks(p.css.replace(/\/\*[\s\S]*?\*\//g, "")));
  let art = 0;
  for (const file of SVGS) {
    if (!css.includes(`url(${file})`)) continue;
    const uri = mockup ? "none" : dataUri(file);
    art += mockup ? 0 : uri.length;
    css = css.replace(`url(${file})`, uri);
  }
  rows.push({ piece: p.name, rules: css.length - art, svg: art, total: css.length });
  total += css;
}
if (missing.size) console.warn("hooks without a selector:", [...missing].join(", "));

mkdirSync(join(here, "dist"), { recursive: true });
const file = join(here, "dist", mockup ? "possessed.mockup.css" : "possessed.css");
writeFileSync(file, total);

console.log(file);
if (!mockup) {
  console.table(rows);
  const r4 = rows.filter((r) => r.piece !== "possessed").reduce((n, r) => n + r.total, 0);
  console.log(`round 4 adds ${r4.toLocaleString()} chars`);
}
console.log(`total ${total.length.toLocaleString()} chars / ${LIMIT.toLocaleString()} (${((total.length / LIMIT) * 100).toFixed(1)}%) · headroom ${(LIMIT - total.length).toLocaleString()}`);
if (total.length > LIMIT) {
  console.error("over the limit");
  process.exit(1);
}
