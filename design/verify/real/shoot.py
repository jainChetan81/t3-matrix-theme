#!/usr/bin/env python3
"""shoot.py — screenshot / arrival / perf / DOM harness for a CSS theme in the REAL T3 web app.

Throwaway instance only: server http://127.0.0.1:3999 (base-dir /tmp/t3-matrix-test),
headless Chrome on remote-debugging port 9388. Never touches the live T3 instance.

Subcommands (all against port 9388):
  reload-theme   re-run `t3 theme set` on matrix.json, reload the page, wait for settle
  shot NAME      screenshot to design/verify/NAME.png (see --action/--url/--width/...)
  arrive         open a thread, `t3 thread send` a short line, screenshot burst ~80ms x 1.5s
  bench [NAME]   5 s Tracing idle + busy (rAF 1px toggle), report main-thread ms + fps
  dom            dump compact DOM outline to design/verify/real/dom-notes.md

Examples:
  python3 shoot.py shot thread --action thread:"Matrix rendering one"
  python3 shoot.py shot draft --action draft --action focus --action type:"hello rain"
  python3 shoot.py shot menu --action thread:"Matrix rendering one" --action menu
  python3 shoot.py arrive --thread "Matrix rendering one"
  python3 shoot.py bench thread --action thread:"Matrix rendering one"
  python3 shoot.py bench --url https://chetan-examples.vercel.app/matrix
  python3 shoot.py bench baseline --baseline
  python3 shoot.py dom --stream "Write three short paragraphs about rain."
"""
import argparse
import base64
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import websocket

CDP_PORT = 9388
T3 = "/home/chetan/.t3/runtime/versions/0.1.10-nightly.20261114.4695/t3"  # same build as the user's app
BASE = "http://127.0.0.1:3999"
BASE_DIR = "/tmp/t3-matrix-test"
MATRIX_JSON = str(Path(__file__).resolve().parents[3] / "matrix.json")
HERE = Path(__file__).resolve().parent
SHOTS = HERE.parent  # design/verify/NAME.png etc.

CATS = "devtools.timeline,disabled-by-default-devtools.timeline,cc,disabled-by-default-devtools.timeline.frame"
NAMES = ["UpdateLayoutTree", "Layout", "PrePaint", "Paint", "Commit", "RasterTask"]


class CDP:
    def __init__(self, url):
        self.ws = websocket.create_connection(url, suppress_origin=True)
        self.i = 0
        self.events = []

    def call(self, method, **params):
        self.i += 1
        self.ws.send(json.dumps({"id": self.i, "method": method, "params": params}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == self.i:
                if "error" in m:
                    raise RuntimeError(m["error"])
                return m.get("result", {})

    def wait(self, name, timeout=30):
        end = time.time() + timeout
        while time.time() < end:
            for e in self.events:
                if e.get("method") == name:
                    self.events.remove(e)
                    return e
            self.ws.settimeout(1)
            try:
                self.events.append(json.loads(self.ws.recv()))
            except websocket.WebSocketTimeoutException:
                pass
            finally:
                self.ws.settimeout(None)
        raise TimeoutError(name)

    def js(self, expr):
        r = self.call("Runtime.evaluate", expression=expr, returnByValue=True)
        res = r.get("result", {})
        if "value" in res:
            return res["value"]
        return "NO-VALUE:" + json.dumps(res)[:200]

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass


def targets():
    return json.load(urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json"))


def page():
    tabs = targets()
    cands = [t for t in tabs if t["type"] == "page" and "127.0.0.1:3999" in t.get("url", "")]
    if not cands:
        cands = [t for t in tabs if t["type"] == "page"]
    p = CDP(cands[0]["webSocketDebuggerUrl"])
    p.call("Page.enable")
    p.call("Emulation.setFocusEmulationEnabled", enabled=True)
    return p


def browser_cdp():
    return CDP(json.load(urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json/version"))["webSocketDebuggerUrl"])


def nav(p, url, settle=2.5):
    p.events.clear()
    p.call("Page.navigate", url=url)
    try:
        p.wait("Page.loadEventFired", timeout=30)
    except TimeoutError:
        pass
    time.sleep(settle)


def size(p, w, h=900):
    p.call("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=False)


def clear_size(p):
    p.call("Emulation.clearDeviceMetricsOverride")


def shot(p, name):
    data = p.call("Page.captureScreenshot", format="png")["data"]
    out = SHOTS / f"{name}.png"
    out.write_bytes(base64.b64decode(data))
    print("saved", out, flush=True)
    return out


def click_center(p, x, y):
    p.call("Input.dispatchMouseEvent", type="mouseMoved", x=x, y=y)
    time.sleep(0.05)
    p.call("Input.dispatchMouseEvent", type="mousePressed", x=x, y=y, button="left", clickCount=1)
    time.sleep(0.05)
    p.call("Input.dispatchMouseEvent", type="mouseReleased", x=x, y=y, button="left", clickCount=1)


def click_js(p, find_expr, settle=0.8):
    """find_expr: JS returning an Element. Scrolls it into view, clicks its center via CDP."""
    r = p.js(
        "(function(){const el=(" + find_expr + ");if(!el)return null;"
        "el.scrollIntoView({block:'center'});const b=el.getBoundingClientRect();"
        "return JSON.stringify({x:b.x+b.width/2,y:b.y+b.height/2})})()"
    )
    if r in (None, "null", "NO-VALUE:null") or (isinstance(r, str) and r.startswith("NO-VALUE")):
        raise RuntimeError("click target not found: " + find_expr[:120])
    pt = json.loads(r)
    click_center(p, pt["x"], pt["y"])
    time.sleep(settle)
    return pt


ROW_BY_TITLE = ("[...document.querySelectorAll('[data-testid=\"sidebar-row-card\"]')]"
                ".find(x=>(x.getAttribute('aria-label')||'').startsWith(%s))")


def open_thread(p, title, timeout=20):
    # done when the clicked row is the active one (the click can miss right after a resize)
    active = "(function(){const r=(" + (ROW_BY_TITLE % json.dumps(title)) + ");return !!r&&r.getAttribute('aria-current')==='page'})()"
    end = time.time() + timeout
    while time.time() < end and not p.js(active):
        click_js(p, ROW_BY_TITLE % json.dumps(title), settle=0.6)
    time.sleep(1.5)
    href = p.js("location.href")
    print("open thread:", title, "->", href, flush=True)
    return href


def open_draft(p):
    click_js(p, "[...document.querySelectorAll('button')].find(b=>(b.getAttribute('aria-label')||'')==='New thread')")
    time.sleep(1.5)
    print("open draft ->", p.js("location.href"), flush=True)


def focus_composer(p):
    click_js(p, "document.querySelector('.composer-tiptap')", settle=0.5)
    p.js("(function(){const t=document.querySelector('.composer-tiptap');if(t)t.focus()})()")
    time.sleep(0.4)


def do_action(p, action):
    if action.startswith("thread:"):
        open_thread(p, action[len("thread:"):])
    elif action == "draft":
        open_draft(p)
    elif action == "nopanel":
        # close the right-hand thread details panel if it is showing
        vis = p.js("(function(){const a=document.querySelector('[data-workspace-area=details]');"
                   "return !!a&&getComputedStyle(a).display!=='none'&&a.getBoundingClientRect().width>0})()")
        if vis:
            click_js(p, "[...document.querySelectorAll('button')].find(b=>(b.getAttribute('aria-label')||'')==='Toggle thread details panel')")
    elif action.startswith("scroll:"):
        p.js("document.querySelector('.messages-timeline-scroll').scrollTop=" + str(int(action[7:])))
        time.sleep(0.8)
    elif action.startswith("wait:"):
        time.sleep(int(action[5:]) / 1000.0)
    elif action == "esc":
        for t in ("keyDown", "keyUp"):
            p.call("Input.dispatchKeyEvent", type=t, key="Escape", code="Escape", windowsVirtualKeyCode=27)
        time.sleep(0.4)
    elif action == "clear":
        # empty the composer (drafts persist per thread)
        focus_composer(p)
        p.js("document.execCommand('selectAll')")
        for t in ("keyDown", "keyUp"):
            p.call("Input.dispatchKeyEvent", type=t, key="Backspace", code="Backspace", windowsVirtualKeyCode=8)
        time.sleep(0.4)
    elif action == "blur":
        p.js("document.activeElement&&document.activeElement.blur()")
    elif action == "focus":
        focus_composer(p)
    elif action.startswith("type:"):
        focus_composer(p)
        text = action[len("type:"):]
        p.call("Input.insertText", text=text)
        time.sleep(0.6)
    elif action == "menu":
        click_js(p, "[...document.querySelectorAll('button')].find(b=>/More composer controls/i.test(b.getAttribute('aria-label')||''))")
    elif action == "tooltip":
        r = p.js("(function(){const el=[...document.querySelectorAll('button')].find(b=>(b.getAttribute('aria-label')||'')==='Attach files');if(!el)return null;"
                 "const b=el.getBoundingClientRect();"
                 "return JSON.stringify({x:b.x+b.width/2,y:b.y+b.height/2})})()")
        pt = json.loads(r)
        p.call("Input.dispatchMouseEvent", type="mouseMoved", x=pt["x"] - 3, y=pt["y"] - 3)
        time.sleep(0.1)
        p.call("Input.dispatchMouseEvent", type="mouseMoved", x=pt["x"], y=pt["y"])
        time.sleep(1.4)
    elif action == "dialog":
        click_js(p, "[...document.querySelectorAll('button')].find(b=>(b.getAttribute('aria-label')||'')==='Settings')")
    elif action == "terminal":
        click_js(p, "[...document.querySelectorAll('button')].find(b=>(b.getAttribute('aria-label')||'')==='Toggle terminal drawer')")
    else:
        raise SystemExit("unknown action: " + action)


def cmd_shot(a):
    p = page()
    try:
        if a.width:
            size(p, a.width, a.height)
        if a.reduced_motion:
            p.call("Emulation.setEmulatedMedia", features=[{"name": "prefers-reduced-motion", "value": "reduce"}])
        if a.url:
            nav(p, BASE + a.url if a.url.startswith("/") else a.url)
        for act in a.action or []:
            do_action(p, act)
        if a.chat_width:
            p.js(f"document.documentElement.dataset.chatWidth={json.dumps(a.chat_width)}")
            time.sleep(0.5)
        if a.eval:
            print("eval ->", p.js(a.eval), flush=True)
        if a.wait:
            time.sleep(a.wait / 1000.0)
        else:
            time.sleep(0.5)
        shot(p, a.name)
        if a.reduced_motion:
            p.call("Emulation.setEmulatedMedia", features=[])
        clear_size(p)
    finally:
        p.close()


def cmd_js(a):
    """Evaluate JS in the app page (after optional actions) and print the result."""
    p = page()
    try:
        if a.width:
            size(p, a.width, a.height)
        for act in a.action or []:
            do_action(p, act)
        src = Path(a.file).read_text() if a.file else a.expr
        print(p.js(src), flush=True)
    finally:
        p.close()


ANIMS = ("JSON.stringify(document.getAnimations().map(a=>{const t=a.effect&&a.effect.target;"
         "return (a.animationName||a.transitionProperty||'?')+':'+a.playState+'@'+(t?(t.getAttribute('data-slot')||"
         "t.getAttribute('data-timeline-row-kind')||t.getAttribute('data-workspace-area')||t.className.toString().slice(0,24)||t.tagName):'?')"
         "+(a.effect.pseudoElement||'')}))")


def cmd_burst(a):
    """Run the actions, then click a sidebar thread (or run --eval) and grab frames as fast as possible.
    Prints the animations alive at each frame, so one-shots can be checked for start and finish."""
    p = page()
    try:
        if a.width:
            size(p, a.width, a.height)
        for act in a.action or []:
            do_action(p, act)
        if a.rate != 1:
            # slow every animation down so a screenshot burst can catch sub-second one-shots
            p.call("Animation.enable")
            p.call("Animation.setPlaybackRate", playbackRate=a.rate)
        if a.thread:
            click_js(p, ROW_BY_TITLE % json.dumps(a.thread), settle=0)
        if a.eval:
            p.js(a.eval)
        t0 = time.time()
        for n in range(a.frames):
            if a.shots:
                shot(p, f"{a.name}-{n:02d}")
            print(f"  +{time.time() - t0:4.2f}s", p.js(ANIMS), flush=True)
            dt = t0 + (n + 1) * a.interval / 1000.0 - time.time()
            if dt > 0:
                time.sleep(dt)
        clear_size(p)
    finally:
        if a.rate != 1:
            p.call("Animation.setPlaybackRate", playbackRate=1)
        p.close()


def cmd_reload_theme(a):
    r = subprocess.run([T3, "theme", "set", MATRIX_JSON, "--base-dir", BASE_DIR],
                       capture_output=True, text=True)
    print((r.stdout or "").strip(), (r.stderr or "").strip(), flush=True)
    p = page()
    try:
        p.events.clear()
        p.call("Page.reload")
        try:
            p.wait("Page.loadEventFired", timeout=30)
        except TimeoutError:
            pass
        time.sleep(3)
        print("reloaded:", p.js("location.href"), flush=True)
    finally:
        p.close()


def thread_id_for_title(title):
    out = subprocess.run([T3, "thread", "list", "--base-dir", BASE_DIR,
                          "--project", BASE_DIR + "/proj", "--json"],
                         capture_output=True, text=True, check=True)
    for t in json.loads(out.stdout):
        th = t.get("thread", t)
        if (th.get("title") or "") == title:
            return th["threadId"]
    raise SystemExit("no thread titled: " + title)


def cmd_arrive(a):
    """Send one message with the real CLI and record what the theme does while the reply arrives.
    Frames go to design/verify/arrive-NN.png; each line shows the timeline rows, whether a message
    is streaming, and the animations alive at that moment. --rate slows CSS animations only."""
    title = a.thread or "Matrix rendering one"
    tid = thread_id_for_title(title)
    p = page()
    try:
        if a.width:
            size(p, a.width, a.height)
        open_thread(p, title)
        do_action(p, "nopanel")
        do_action(p, "blur")
        if a.rate != 1:
            p.call("Animation.enable")
            p.call("Animation.setPlaybackRate", playbackRate=a.rate)
        state = ("(function(){const r=[...document.querySelectorAll('[data-timeline-row-kind]')];"
                 "const s=document.querySelector('[data-streaming]');if(s&&!s.__m)s.__m=Math.random().toString(36).slice(2,6);"
                 "const m=[...document.querySelectorAll('.chat-markdown')].find(x=>x.__m);"
                 "return r.length+' rows, streaming='+(s?s.__m:'no')+', marked node alive='+(m?m.isConnected:'-')+"
                 "', working='+!!document.querySelector('[data-sidebar-row][aria-label*=\", Working,\"]')})()")
        proc = subprocess.Popen([T3, "thread", "send", "--base-dir", BASE_DIR, tid, a.message],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        start = time.time()
        n = 0
        while time.time() - start < a.seconds:
            st = p.js(state)
            an = p.js(ANIMS)
            shot(p, f"arrive-{n:02d}")
            print(f"  +{time.time() - start:5.2f}s {st} | {an}", flush=True)
            n += 1
        proc.communicate(timeout=120)
        clear_size(p)
    finally:
        if a.rate != 1:
            p.call("Animation.setPlaybackRate", playbackRate=1)
        p.close()


def trace(p, b, url, busy, secs=5, inject="", after=()):
    nav(p, url)
    for act in after:
        do_action(p, act)
    if inject:
        p.js("document.head.insertAdjacentHTML('beforeend'," + json.dumps("<style>" + inject + "</style>") + ")")
    p.js("window.__f=0;window.__b=null;"
         + ("window.__b=document.createElement('div');__b.style.cssText='position:fixed;left:0;top:0;width:1px;height:1px;background:#000;z-index:99999;';"
            "document.body.appendChild(__b);(function l(){window.__f++;__b.style.opacity=__f%2?'1':'0';requestAnimationFrame(l)})()" if busy else ""))
    time.sleep(1)
    b.call("Tracing.start", traceConfig={"includedCategories": CATS.split(","),
                                          "recordMode": "recordAsMuchAsPossible"},
           transferMode="ReturnAsStream")
    time.sleep(secs)
    anims = p.js("(function(){const a=document.getAnimations().filter(a=>a.playState==='running');"
                 "return a.length+' ['+a.map(x=>x.animationName||x.transitionProperty||'?').join(',')+']'})()")
    b.call("Tracing.end")
    stream = b.wait("Tracing.tracingComplete", 60)["params"]["stream"]
    buf = []
    while True:
        r = b.call("IO.read", handle=stream, size=1 << 22)
        buf.append(r.get("data", ""))
        if r.get("eof"):
            break
    b.call("IO.close", handle=stream)
    data = json.loads("".join(buf))
    evs = data["traceEvents"] if isinstance(data, dict) else data
    ms = {n: 0.0 for n in NAMES}
    draws = nodmg = mainfr = 0
    for e in evs:
        n = e.get("name")
        if n in ms and e.get("ph") == "X":
            ms[n] += e.get("dur", 0) / 1000
        elif e.get("ph") not in ("X", "B", "I", "i"):
            continue
        elif n == "ProxyImpl::ScheduledActionDraw":
            draws += 1
        elif n == "EarlyOut_NoDamage":
            nodmg += 1
        elif n == "ProxyMain::BeginMainFrame":
            mainfr += 1
    main = sum(ms[n] for n in NAMES[:5])
    return ms, main, (draws - nodmg) / secs, mainfr / secs, anims


def cmd_bench(a):
    label = a.name or "page"
    if a.baseline:
        subprocess.run([T3, "theme", "set", "t3-chat", "--base-dir", BASE_DIR],
                       capture_output=True, text=True)
        print("baseline: theme -> t3-chat", flush=True)
    try:
        b = browser_cdp()
        p = page()
        try:
            if a.url:
                url = a.url if not a.url.startswith("/") else BASE + a.url
            else:
                for act in a.action or []:
                    do_action(p, act)
                url = p.js("location.href")
            print(f"{'page':14s} {'mode':4s} {'style':>7s} {'layout':>7s} {'prepaint':>8s} {'paint':>7s} "
                  f"{'commit':>7s} | {'main':>7s} {'raster':>7s} {'frames/s':>8s} {'mainfr/s':>8s} anims",
                  flush=True)
            for mode in ("idle", "busy"):
                ms, main, fps, mfps, anims = trace(p, b, url, mode == "busy", inject=a.inject or "", after=a.after)
                print(f"{label:14s} {mode:4s} {ms['UpdateLayoutTree']:7.1f} {ms['Layout']:7.1f} {ms['PrePaint']:8.1f} {ms['Paint']:7.1f} "
                      f"{ms['Commit']:7.1f} | {main:7.1f} {ms['RasterTask']:7.1f} {fps:8.1f} {mfps:8.1f} {anims}", flush=True)
        finally:
            p.close()
            b.close()
    finally:
        if a.baseline:
            subprocess.run([T3, "theme", "set", MATRIX_JSON, "--base-dir", BASE_DIR],
                           capture_output=True, text=True)
            print("restored: theme -> matrix", flush=True)


def cmd_dom(a):
    p = page()
    lines = ["# Real-app DOM notes (throwaway instance :3999, headless Chrome :9388)", ""]
    try:
        if a.thread:
            open_thread(p, a.thread)
        else:
            # ensure we are on a thread page
            href = p.js("location.href")
            if "/mcp" not in href and "/thread" not in href:
                open_thread(p, "Matrix rendering one")
        q = p.js
        lines += ["## Timeline", ""]
        lines.append("rows: " + str(q("document.querySelectorAll('[data-timeline-row-kind]').length")))
        lines.append("row kinds: " + str(q("JSON.stringify([...document.querySelectorAll('[data-timeline-row-kind]')].map(e=>e.getAttribute('data-timeline-row-kind')))")))
        lines.append("scroll kids: " + str(q("document.querySelector('.messages-timeline-scroll').children.length")))
        lines.append("scroll ancestry: " + str(q("(function(){let p=document.querySelector('.messages-timeline-scroll'),c=[];for(let k=0;k<4&&p;k++){c.push(p.tagName+'.'+(''+(p.className||'')).slice(0,70));p=p.parentElement}return JSON.stringify(c)})()")))
        lines.append("row frame kids: " + str(q("document.querySelector('.messages-timeline-row-frame')?document.querySelector('.messages-timeline-row-frame').children.length:'none'")))
        lines.append("row structure: " + str(q("(function(){const r=[...document.querySelectorAll('[data-timeline-row-kind]')].map(e=>({kind:e.getAttribute('data-timeline-row-kind'),tag:e.tagName,cls:(''+(e.className||'')).slice(0,90),ptag:e.parentElement.tagName,pcls:(''+(e.parentElement.className||'')).slice(0,90),isLast:e===e.parentElement.lastElementChild,idx:[...e.parentElement.children].indexOf(e),sibs:e.parentElement.children.length}));return JSON.stringify(r).slice(0,2000)})()")))
        lines.append("workspace-area count: " + str(q("document.querySelectorAll('[data-workspace-area]').length")))
        lines.append("legend-list nodes: " + str(q("document.querySelectorAll('[class*=legend-list]').length")))
        lines.append("content-visibility on sidebar rows: " + str(q("(()=>{const li=document.querySelector('[data-thread-item]');return li?getComputedStyle(li).contentVisibility:'none'})()")))
        # remount test: mark rows, switch away and back
        lines += ["", "## Remount on thread switch", ""]
        lines.append("mark: " + str(q("(function(){document.querySelectorAll('[data-timeline-row-kind]').forEach((r,i)=>r.setAttribute('data-shootmark','m'+i));return document.querySelectorAll('[data-shootmark]').length})()")))
        open_thread(p, "Matrix python notes")
        open_thread(p, "Matrix rendering one")
        lines.append("marks surviving round-trip: " + str(q("document.querySelectorAll('[data-shootmark]').length")))
        lines += ["", "## Header / composer / popups / terminal", ""]
        lines.append("chat-header: " + str(q("document.querySelector('[data-chat-header]').tagName+'.'+(''+document.querySelector('[data-chat-header]').className).slice(0,80)")))
        lines.append("header buttons: " + str(q("JSON.stringify([...document.querySelector('[data-chat-header]').querySelectorAll('button')].map(b=>(b.innerText||b.getAttribute('aria-label')||'').slice(0,30)))"))[:800])
        lines.append("composer: " + str(q("(function(){const t=document.querySelector('.composer-tiptap');const f=t?t.closest('form'):null;return JSON.stringify({tiptap:t?t.className.slice(0,100):null,formKids:f?f.children.length:-1})})()")))
        lines.append("chat-width default: " + str(q("document.documentElement.getAttribute('data-chat-width')")))
        lines.append("popups now: " + str(q("JSON.stringify([...document.querySelectorAll('[role=menu],[role=dialog],[role=tooltip],[data-slot=tooltip-content],[data-slot=dialog-content]')].map(e=>e.getAttribute('role')||e.getAttribute('data-slot')))")))
        # terminal drawer toggle
        do_action(p, "terminal")
        time.sleep(1)
        lines.append("terminal drawer after toggle: " + str(q("(function(){const els=[...document.querySelectorAll('*')].filter(e=>{for(const at of (e.attributes||[])){if(/terminal/i.test(at.name+'='+at.value))return true}return false});return JSON.stringify(els.slice(0,8).map(e=>e.tagName+'.'+(''+(e.className||'')).slice(0,80)))})()"))[:900])
        do_action(p, "terminal")
        # menu popup
        do_action(p, "menu")
        lines.append("popups after menu action: " + str(q("JSON.stringify([...document.querySelectorAll('[role=menu],[role=dialog],[role=tooltip],[data-slot=tooltip-content]')].map(e=>(e.getAttribute('role')||e.getAttribute('data-slot'))+':'+(e.textContent||'').slice(0,60)))"))[:700])
        p.js("(function(){const e=document.elementFromPoint(10,10);if(e&&e.click)e.click()})()")
        if a.stream:
            lines += ["", "## Streaming", ""]
            tid = thread_id_for_title("Matrix rendering one")
            open_thread(p, "Matrix rendering one")
            proc = subprocess.Popen([T3, "thread", "send", "--base-dir", BASE_DIR, tid, a.stream],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            seen_streaming = []
            end = time.time() + 90
            prev_n = -1
            while time.time() < end:
                time.sleep(0.5)
                st = p.js("(function(){const rows=[...document.querySelectorAll('[data-timeline-row-kind]')];const last=rows[rows.length-1];"
                          "const stop=[...document.querySelectorAll('button')].filter(b=>/stop/i.test(b.getAttribute('aria-label')||''));"
                          "return JSON.stringify({n:rows.length,lastKind:last?last.getAttribute('data-timeline-row-kind'):null,"
                          "lastCls:last?(''+last.className).slice(0,120):null,"
                          "lastAttrs:last?[...last.attributes].map(a=>a.name).join(','):null,"
                          "stopBtns:stop.map(b=>b.getAttribute('aria-label')),"
                          "busy:document.querySelectorAll('[data-timeline-row-kind]').length})})()")
                if st != prev_n:
                    seen_streaming.append(st)
                    prev_n = st
                if proc.poll() is not None:
                    time.sleep(1.5)
                    st2 = p.js("(function(){const rows=[...document.querySelectorAll('[data-timeline-row-kind]')];const last=rows[rows.length-1];"
                               "return JSON.stringify({n:rows.length,lastKind:last?last.getAttribute('data-timeline-row-kind'):null,"
                               "lastCls:last?(''+last.className).slice(0,120):null,"
                               "lastHtml:last?last.outerHTML.slice(0,600):null})})()")
                    seen_streaming.append("SETTLED:" + st2)
                    break
            out, err = proc.communicate(timeout=30)
            lines.append("stream rc: " + str(proc.returncode))
            for s in seen_streaming:
                lines.append("- " + s[:900])
        out_path = HERE / "dom-notes.md"
        out_path.write_text("\n".join(lines) + "\n")
        print("wrote", out_path, flush=True)
    finally:
        p.close()


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("reload-theme")

    sh = sub.add_parser("shot")
    sh.add_argument("name")
    sh.add_argument("--action", action="append", default=[],
                    help="thread:<title>|draft|focus|type:<text>|menu|tooltip|dialog|terminal (repeatable)")
    sh.add_argument("--url", default=None)
    sh.add_argument("--width", type=int, default=None)
    sh.add_argument("--height", type=int, default=900)
    sh.add_argument("--reduced-motion", action="store_true")
    sh.add_argument("--chat-width", choices=["wide", "full"], default=None)
    sh.add_argument("--eval", default=None)
    sh.add_argument("--wait", type=int, default=None)

    ar = sub.add_parser("arrive")
    ar.add_argument("--thread", default="Matrix rendering one")
    ar.add_argument("--message", default="reply with one short line")
    ar.add_argument("--rate", type=float, default=1.0)
    ar.add_argument("--seconds", type=float, default=14)
    ar.add_argument("--width", type=int, default=None)
    ar.add_argument("--height", type=int, default=900)

    be = sub.add_parser("bench")
    be.add_argument("name", nargs="?", default="page")
    be.add_argument("--action", action="append", default=[])
    be.add_argument("--url", default=None)
    be.add_argument("--baseline", action="store_true")
    be.add_argument("--after", action="append", default=[], help="actions to run after each navigation, before tracing")
    be.add_argument("--inject", default=None, help="extra CSS added before tracing (to compare variants)")

    dm = sub.add_parser("dom")
    dm.add_argument("--thread", default=None)
    dm.add_argument("--stream", default=None)

    js = sub.add_parser("js")
    js.add_argument("expr", nargs="?", default="")
    js.add_argument("--file", default=None)
    js.add_argument("--action", action="append", default=[])
    js.add_argument("--width", type=int, default=None)
    js.add_argument("--height", type=int, default=900)

    bu = sub.add_parser("burst")
    bu.add_argument("name")
    bu.add_argument("--action", action="append", default=[])
    bu.add_argument("--thread", default=None)
    bu.add_argument("--eval", default=None)
    bu.add_argument("--frames", type=int, default=8)
    bu.add_argument("--interval", type=int, default=150)
    bu.add_argument("--shots", action="store_true")
    bu.add_argument("--rate", type=float, default=1.0, help="animation playback rate, e.g. 0.15 for slow motion")
    bu.add_argument("--width", type=int, default=None)
    bu.add_argument("--height", type=int, default=900)

    a = ap.parse_args()
    {"reload-theme": cmd_reload_theme, "shot": cmd_shot, "arrive": cmd_arrive,
     "bench": cmd_bench, "dom": cmd_dom, "js": cmd_js, "burst": cmd_burst}[a.cmd](a)


if __name__ == "__main__":
    main()
