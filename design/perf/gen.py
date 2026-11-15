# Build bench pages: realistic T3-like chat DOM + theme base + one rain variant each.
import re, random, urllib.parse, json
random.seed(1)
cur = open('theme_current.css').read()
k = cur.index('[data-workspace-area="conversation"],[data-workspace-area="home"]{position')
e = cur.index('.chat-markdown:is(h1')
BASE = cur[:k] + cur[e:]          # theme without rain rules (keeps --rain var)
RAIN_CUR = cur[k:e]
svg_raw = open('/tmp/matrix-tools/repo/src/rain.svg').read()

def enc(svg):
    # same encoding style as the theme build: escape #, <, %
    s = svg.replace('%', '%25').replace('#', '%23').replace('</', '%3C/').replace('"', "'")
    return 'url("data:image/svg+xml;charset=utf-8,' + s + '")'

def chat_dom(n_msgs=48):
    words = 'the quick brown fox jumps over lazy dog compile render layer frame style paint commit raster tile buffer'.split()
    def para(n): return ' '.join(random.choice(words) for _ in range(n))
    out = []
    for i in range(n_msgs):
        if i % 2 == 0:
            out.append(f'<div data-timeline-row-kind="user" class="row"><div data-user-message-bubble class="bubble"><p>{para(18)}</p></div></div>')
        else:
            parts = []
            for j in range(4):
                parts.append(f'<p>{para(30)} <code>{random.choice(words)}()</code> {para(12)} <strong>{para(3)}</strong> <a href="#">{para(2)}</a></p>')
            parts.append('<ul>' + ''.join(f'<li><span>{para(6)}</span> <code>{random.choice(words)}</code></li>' for _ in range(5)) + '</ul>')
            parts.append('<div class="chat-markdown-codeblock"><pre><code>' + ''.join(f'<span class="tk">{random.choice(words)}</span><span>({para(2)})</span>\n' for _ in range(8)) + '</code></pre></div>')
            parts.append('<h3 class="chat-markdown">' + para(4) + '</h3>')
            out.append(f'<div data-timeline-row-kind="assistant" class="row"><div class="chat-markdown md">{"".join(parts)}</div><div class="tools"><button>copy</button><button>retry</button><span>12:0{i%10}</span></div></div>')
    return ''.join(out)

def sidebar():
    items = ''.join(f'<div data-thread-item><div role="button"><span class="dot"></span><span>Thread title number {i}</span><span class="t">{i}m</span></div></div>' for i in range(40))
    return f'<aside class="sb"><div data-slot="sidebar-inner">{items}</div></aside>'

PAGE_CSS = '''html,body{margin:0;height:100%;background:#010803;color:#b8f5d0;font:14px/1.5 system-ui,sans-serif}
.app{display:flex;height:100%}.sb{width:260px;flex:none;border-right:1px solid #123522;overflow:auto}
.main{flex:1;display:flex;flex-direction:column;min-width:0}[data-chat-header]{height:44px;flex:none;display:flex;align-items:center;padding:0 16px}
[data-workspace-area="conversation"]{flex:1;min-height:0}
.scroller{position:absolute;inset:0;overflow-y:auto}.col{max-width:736px;margin:0 auto;padding:16px}
.row{margin:16px 0}.bubble{padding:8px 12px}.tools{display:flex;gap:8px;font-size:12px;opacity:.6}
[data-slot="composer-host"]{max-width:736px;margin:8px auto 16px;width:100%;min-height:80px}
[data-thread-item] [role=button]{display:flex;gap:6px;padding:4px 10px}'''

def page(name, rain_css, extra_dom='', base=True):
    css = (BASE if base else '') + rain_css + PAGE_CSS
    html = (f'<!doctype html><meta charset=utf-8><title>{name}</title><style>{css}</style>'
            f'<div class="app">{sidebar()}<div class="main"><div data-chat-header><span data-slot="workspace-breadcrumb-text">project / thread</span></div>'
            f'<div data-workspace-area="conversation">{extra_dom}<div class="scroller"><div class="col">{chat_dom()}</div></div></div>'
            f'<div data-slot="composer-host"><div class="composer-tiptap" contenteditable><p>draft text</p></div></div></div></div>')
    open(f'/tmp/matrix-tools/bench/v/{name}.html', 'w').write(html)
    return len(css)

if __name__ == '__main__':
    import variants
    for name, css, dom in variants.VARIANTS(RAIN_CUR, svg_raw, enc):
        n = page(name, css, dom)
        print(name, 'css chars', n, 'rain chars', len(css))
