#!/usr/bin/env python3
"""Generate mock T3 Code pages (same hooks/structure as the live app) for screenshots and traces.

  python3 -I design/verify/mock.py     -> design/verify/pages/{thread,draft,thread-none,draft-none}.html

Structure follows the T3 client bundle 0.1.10-nightly.20261114: the conversation area is also
[data-chat-canvas] and carries the lane insets inline, the lane width comes from
--chat-content-max-width, breadcrumb parts are <li>s, the composer outline is a ring on
composer-host::after. The draft page is a conversation area with no timeline rows and the
composer centred as an overlay; its heading and chips are stand-ins.
"""
import json
import random
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = HERE / "pages"
random.seed(7)

NEUTRAL = {  # stand-in for the stock dark theme ("no theme" baseline)
    "canvas": "#0d0d0f", "sidebar": "#0b0b0d", "text": "#e6e6e9", "textMuted": "#9a9aa3", "border": "#232329",
    "surface": "#141418", "surfaceRaised": "#1a1a1f", "messageSurface": "#1c1c22", "messageForeground": "#e6e6e9",
    "codeBackground": "#111114", "codeForeground": "#d6d6dc", "placeholder": "#6f6f7a", "accent": "#7aa2ff",
    "accentForeground": "#0b0b0d", "sidebarForeground": "#d9d9de", "sidebarMutedForeground": "#8b8b95",
    "sidebarRowHover": "#ffffff0d", "sidebarRowActive": "#ffffff14", "sidebarBorder": "#1d1d22",
    "toolbarBorder": "#232329", "iconMuted": "#7c7c87", "input": "#2c2c34", "toolbarControl": "#17171b",
    "secondary": "#1a1a1f", "messageAction": "#1a1a1f", "messageActionForeground": "#c9c9cf",
}

# Roughly how T3 consumes colour roles: one CSS variable per role, used by utility classes.
APP_CSS = """
:root{--chat-content-max-width:46rem}:root[data-chat-width=wide]{--chat-content-max-width:72rem}:root[data-chat-width=full]{--chat-content-max-width:100%}
*{box-sizing:border-box}html,body{margin:0;height:100%}
body{background:var(--canvas);color:var(--text);font:14px/1.5 Inter,system-ui,sans-serif;-webkit-font-smoothing:antialiased}
button{font:inherit;color:inherit;background:none;border:0;padding:0}
.app{display:flex;height:100%}
.sb{width:256px;flex:none;background:var(--sidebar);color:var(--sidebarForeground)}
[data-slot=sidebar-inner]{height:100%;display:flex;flex-direction:column;padding:10px 8px;gap:2px;overflow:hidden}
.sbh{display:flex;align-items:center;gap:8px;padding:4px 8px 12px;font-weight:600}.sbh small{font-weight:400;color:var(--sidebarMutedForeground);border:1px solid var(--sidebarBorder);border-radius:999px;padding:0 7px;font-size:11px}
.grp{display:flex;align-items:center;gap:8px;padding:10px 8px 4px;font-size:12px;color:var(--sidebarMutedForeground)}
[data-slot=project-monogram]{width:18px;height:18px;display:grid;place-items:center}[data-slot=project-monogram] svg{width:14px;height:14px;color:var(--iconMuted)}
ul{list-style:none;margin:0;padding:0}
[data-thread-item]>[role=button]{display:flex;align-items:center;gap:8px;padding:6px 8px;cursor:pointer;font-size:13px}
[data-thread-item]>[role=button]:hover{background:var(--sidebarRowHover)}
[data-thread-item]>[aria-current=page]{background:var(--sidebarRowActive)}
[data-thread-item] .t{margin-left:auto;font-size:11px;color:var(--sidebarMutedForeground)}
[data-thread-item] .n{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.main{flex:1;min-width:0;display:flex;flex-direction:column}
[data-chat-header]{height:48px;flex:none;display:flex;align-items:center;gap:8px;padding:0 18px;border-bottom:1px solid var(--toolbarBorder);font-size:14px}
[data-chat-header] ol{display:flex;align-items:center;gap:8px;min-width:0}[data-chat-header] li{display:flex;color:var(--textMuted)}[data-chat-header] li[aria-current]{color:var(--text)}
[data-slot=workspace-breadcrumb-text]{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
[data-chat-header] .ctl{margin-left:auto;display:flex;gap:6px}
[data-slot=button]{width:30px;height:30px;border-radius:7px;display:grid;place-items:center;background:var(--toolbarControl);color:var(--iconMuted)}
svg.lucide{width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
[data-workspace-area]{position:relative;flex:1;min-height:0;min-width:0;display:flex;flex-direction:column}
.messages-timeline-scroll{flex:1;min-height:0;overflow-y:auto}
[data-chat-canvas] .messages-timeline-scroll{padding-inline-start:calc(3rem + var(--chat-lane-inset-start,0px) - var(--chat-timeline-gutter,0px));padding-inline-end:calc(3rem + var(--chat-lane-inset-end,0px) - var(--chat-timeline-gutter,0px))}
.chat-composer-lane{padding-inline-start:calc(3rem + var(--chat-lane-inset-start,0px));padding-inline-end:calc(3rem + var(--chat-lane-inset-end,0px))}
.chat-content-lane{width:100%;min-width:0;max-width:var(--chat-content-max-width);margin-inline:auto;padding-block:20px}
[data-timeline-row-kind]{margin:18px 0}
[data-message-role=user]{display:flex;justify-content:flex-end}
[data-user-message-bubble]{max-width:80%;background:var(--messageSurface);color:var(--messageForeground);border:1px solid transparent;border-radius:16px;padding:9px 14px}
[data-user-message-bubble] p{margin:0!important}
[data-timeline-row-kind=event]{font-size:12px;color:var(--textMuted);display:flex;gap:8px;align-items:center}
.chat-markdown p{margin:.75em 0}.chat-markdown h2{font-size:1.15em;margin:1.4em 0 .5em}.chat-markdown h3{font-size:1em;margin:1.3em 0 .4em}
.chat-markdown ul{list-style:disc;padding-left:1.4em}.chat-markdown li{margin:.3em 0}
.chat-markdown code{font:.9em ui-monospace,Menlo,monospace}
.chat-markdown :not(pre)>code{background:var(--secondary);border-radius:4px;padding:.1em .3em}
.chat-markdown-codeblock{background:var(--codeBackground);color:var(--codeForeground);border-radius:8px;margin:1em 0}
.chat-markdown-codeblock .bar{display:flex;justify-content:space-between;padding:6px 12px;font-size:11px;color:var(--textMuted);border-bottom:1px solid var(--border)}
.chat-markdown-codeblock pre{margin:0;padding:12px 14px;overflow:auto;font:12.5px/1.55 ui-monospace,Menlo,monospace}
.tk-k{color:#7fd6b0}.tk-s{color:#d9c87a}.tk-c{color:var(--textMuted)}
.chat-markdown table{border-collapse:collapse;margin:1em 0;font-size:13px}.chat-markdown :is(th,td){border:1px solid var(--border);padding:5px 10px;text-align:left}
.acts{display:flex;gap:6px;margin-top:6px}.acts button{font-size:11px;padding:2px 8px;border-radius:6px;background:var(--messageAction);color:var(--messageActionForeground)}
.dock{flex:none;padding-bottom:16px}
[data-chat-composer-form]{display:block;margin-inline:auto;width:100%;min-width:0;max-width:var(--chat-content-max-width)}
[data-slot=composer-host]{position:relative;z-index:10;width:100%;background:var(--surface);border-radius:16px;padding:12px 12px 10px 16px}
[data-slot=composer-host]::after{content:"";pointer-events:none;position:absolute;inset:0;border-radius:inherit;border:1px solid var(--chat-composer-outline,#ffffff0d)}
.relative{position:relative}.flow-root{display:flow-root}.absolute{position:absolute}.inset-0{inset:0}.pointer-events-none{pointer-events:none}
.ph{color:var(--placeholder)}
.composer-tiptap{outline:none;min-height:66px}.composer-tiptap p{margin:0}
.cbar{display:flex;align-items:center;gap:10px;color:var(--textMuted);font-size:13px}.cbar .sp{margin-left:auto}
.send{width:30px;height:30px;border-radius:999px;background:var(--accent);color:var(--accentForeground);display:grid;place-items:center}
.empty{flex:1}
.draft{position:absolute;inset-inline:0;top:50%;transform:translateY(-55%);display:flex;flex-direction:column;gap:22px;text-align:center}
.draft h1{font-size:26px;font-weight:600;margin:0}.draft .sub{color:var(--textMuted);margin-top:-14px}.draft form{text-align:left}
.chips{display:flex;gap:8px;justify-content:center}.chips span{border:1px solid var(--border);border-radius:999px;padding:4px 12px;font-size:12px;color:var(--textMuted);background:var(--surface)}
"""

ICON = '<svg class="lucide" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 3v18"/></svg>'
WORDS = ("the build passes once the cache is warm and each worker owns its files so retries stay stable while the "
         "parent keeps a short plan checks results and reports what changed with paths tests and open questions").split()


def para(n):
    s = " ".join(random.choice(WORDS) for _ in range(n))
    return s[0].upper() + s[1:] + "."


def code_block():
    lines = [
        '<span class="tk-c"># assemble the theme and enforce limits</span>',
        '<span class="tk-k">def</span> build(src, out):',
        '    css = minify(read(src / <span class="tk-s">"theme.css"</span>))',
        '    <span class="tk-k">if</span> len(css) &gt; MAX_CSS:',
        '        fail(<span class="tk-s">"css too long"</span>)',
        '    out.write_text(json.dumps(theme(css)))',
        '    <span class="tk-k">return</span> len(css)',
    ]
    return ('<div class="chat-markdown-codeblock"><div class="bar"><span>python</span><span>copy</span></div><pre><code>'
            + "\n".join(f"<span>{l}</span>" for l in lines) + "</code></pre></div>")


def assistant(i):
    parts = [f"<p>{para(26)} Run <code>python3 -I build.py</code> and check <strong>{para(3)[:-1]}</strong>; see <a href='#'>the notes</a>.</p>"]
    if i % 3 == 0:
        parts.append(f"<h2>What I did</h2><ul>" + "".join(f"<li><strong>{para(2)[:-1]}:</strong> {para(9)} <code>{random.choice(WORDS)}</code></li>" for _ in range(4)) + "</ul>")
    parts.append(code_block())
    if i % 3 == 1:
        parts.append("<h3>Numbers</h3><table><tr><th>page</th><th>main ms</th><th>frames/s</th></tr>"
                     "<tr><td>idle</td><td>0.3</td><td>3.3</td></tr><tr><td>busy</td><td>41</td><td>60</td></tr></table>")
        parts.append(f"<blockquote>{para(14)}</blockquote>")
    parts.append(f"<p>{para(22)}</p>")
    return (f'<div data-timeline-row-kind="message" data-message-role="assistant"><div><div class="chat-markdown">{"".join(parts)}</div>'
            f'<div class="acts"><button>Copy</button><button>Retry</button></div></div></div>')


def timeline(n=80):
    rows = []
    for i in range(n):
        rows.append(f'<div data-timeline-row-kind="message" data-message-role="user"><div data-user-message-bubble><div class="chat-markdown user-message-markdown"><p>{para(8 + i % 9)}</p></div></div></div>')
        rows.append(f'<div data-timeline-row-kind="event">{ICON}<span>Ran 3 commands, edited 2 files</span></div>')
        rows.append(assistant(i))
    return "".join(rows)


def sidebar():
    out = [f'<div class="sbh">{ICON}<span>T3 Code</span><small>Nightly</small></div>']
    k = 0
    for proj in ("t3-matrix-theme", "homelab", "notes"):
        out.append(f'<div class="grp"><span data-slot="project-monogram">{ICON}</span><span>{proj}</span></div><ul>')
        for _ in range(9):
            cur = ' aria-current="page"' if k == 1 else ""
            title = para(4)[:-1]
            out.append(f'<li data-thread-item><div role="button" tabindex="0"{cur}><span class="n">{title}</span><span class="t">{k + 1}h</span></div></li>')
            k += 1
        out.append("</ul>")
    return f'<aside class="sb"><div data-slot="sidebar-inner">{"".join(out)}</div></aside>'


def composer():
    return ('<div class="chat-composer-lane"><form data-chat-composer-form="true"><div data-slot="composer-host" aria-busy="false"><div class="relative flow-root">'
            '<div><div class="composer-tiptap ProseMirror" contenteditable="true"><p><br class="ProseMirror-trailingBreak"></p></div></div>'
            '<div class="pointer-events-none absolute inset-0 ph">Ask anything. @ files, $ skills, / commands</div></div>'
            f'<div class="cbar">{ICON}<span class="sp">Opus 5.5 Medium</span><span class="send">{ICON}</span></div></div></form></div>')


def header(title):
    sep = '<li aria-hidden="true">/</li>'
    part = '<li{}><span data-slot="workspace-breadcrumb-text">{}</span></li>'
    return ('<div data-chat-header><ol>' + part.format("", "t3-matrix-theme") + sep + part.format("", "main") + sep
            + part.format(' aria-current="page"', title) + '</ol>'
            f'<span class="ctl"><button data-slot="button">{ICON}</button><button data-slot="button">{ICON}</button></span></div>')


def page(name, colors, css, body):
    root = ":root{" + "".join(f"--{k}:{v};" for k, v in colors.items()) + "}"
    html = (f'<!doctype html><html lang="en"><meta charset="utf-8"><title>{name}</title><style>{root}{APP_CSS}</style>'
            f'<style id="theme">{css}</style><body><div class="app">{sidebar()}<div class="main">{body}</div></div></body></html>')
    (OUT / f"{name}.html").write_text(html)
    return len(re.findall(r"<[a-z]", html))


def main():
    OUT.mkdir(exist_ok=True)
    theme = json.loads((ROOT / "matrix.json").read_text())
    area = ('<div data-workspace-area="conversation" data-chat-canvas="true" '
            'style="--chat-timeline-gutter:0px;--chat-lane-inset-start:0px;--chat-lane-inset-end:0px">')
    thread = (header("Matrix theme rebuild") + area
              + f'<div class="messages-timeline-scroll"><div class="chat-content-lane">{timeline()}</div></div>'
              f'<div class="dock">{composer()}</div></div>')
    draft = (header("New thread") + area + '<div class="empty"></div>'
             '<div class="draft"><h1>What are we building?</h1><div class="sub">t3-matrix-theme · main</div>'
             f'{composer()}<div class="chips"><span>Fix a bug</span><span>Review my diff</span><span>Explain this repo</span></div></div></div>')
    for suffix, colors, css in (("", theme["colors"], theme["css"]), ("-none", {**theme["colors"], **NEUTRAL}, "")):
        print("thread" + suffix, page("thread" + suffix, colors, css, thread), "elements")
        print("draft" + suffix, page("draft" + suffix, colors, css, draft), "elements")


if __name__ == "__main__":
    main()
