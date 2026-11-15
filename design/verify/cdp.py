#!/usr/bin/env python3
"""Screenshots and 5 s traces against a private headless Chrome (needs the websocket-client package).

  google-chrome --headless=new --remote-debugging-port=9377 --user-data-dir=$(mktemp -d) --window-size=1512,900 about:blank &
  python3 design/verify/cdp.py shots
  python3 design/verify/cdp.py bench [url-or-page-name ...]
"""
import base64
import json
import sys
import time
import urllib.request
from pathlib import Path

import websocket

PORT = 9377
HERE = Path(__file__).resolve().parent
CATS = "devtools.timeline,disabled-by-default-devtools.timeline,cc,disabled-by-default-devtools.timeline.frame"
NAMES = ["UpdateLayoutTree", "Layout", "PrePaint", "Paint", "Commit", "RasterTask"]
REF = "https://chetan-examples.vercel.app/matrix"


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
            self.events.append(m)

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
        return self.call("Runtime.evaluate", expression=expr, returnByValue=True)["result"].get("value")


def get(path):
    return json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}{path}"))


def page():
    p = CDP([t for t in get("/json") if t["type"] == "page"][0]["webSocketDebuggerUrl"])
    p.call("Page.enable")
    p.call("Emulation.setFocusEmulationEnabled", enabled=True)  # headless pages are unfocused: :focus would never match
    return p


def url_of(name):
    if name.startswith("http"):
        return name
    name, _, query = name.partition("?")
    return (HERE / "pages" / f"{name}.html").as_uri() + ("?" + query if query else "")


def nav(p, url, settle=2.5):
    p.events.clear()
    p.call("Page.navigate", url=url)
    p.wait("Page.loadEventFired")
    time.sleep(settle)


def shot(p, name):
    data = p.call("Page.captureScreenshot", format="png")["data"]
    (HERE / f"{name}.png").write_bytes(base64.b64decode(data))
    print("saved", HERE / f"{name}.png")


BOTTOM = "document.querySelector('.messages-timeline-scroll').scrollTop=1e9"
FOCUS = "document.querySelector('.composer-tiptap').focus()"
TYPE = ("document.querySelector('.composer-tiptap').innerHTML='<p>make the rain calmer and keep it off the text</p>';"
        "document.querySelector('.ph').remove()")  # the app drops the placeholder once there is text


ANIMS = ("JSON.stringify(document.getAnimations().filter(a=>a.playState==='running')"
         ".map(a=>(a.animationName||'transition')+(a.effect.getComputedTiming().iterations===Infinity?'(loop)':'')))")
STRIPS = ("JSON.stringify(['::before','::after'].map(p=>Math.round(parseFloat("
          "getComputedStyle(document.querySelector('[data-workspace-area=conversation]'),p).width))))")


def state(p, label):
    print(f"{label:34s} running animations {p.js(ANIMS)}  strip widths {p.js(STRIPS)}", flush=True)


def size(p, w, h=900):
    p.call("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=False)


def shots():
    p = page()
    size(p, 1512)
    nav(p, url_of("thread"))
    p.js("document.querySelector('.messages-timeline-scroll').scrollTop=2330")
    time.sleep(.5)
    shot(p, "thread")
    state(p, "thread 1512")
    p.js(BOTTOM)
    p.js(FOCUS)
    time.sleep(1.2)
    shot(p, "composer-focused-empty")
    state(p, "thread, composer focused empty")
    time.sleep(11.5)
    state(p, "  same, 12 s later")
    p.js(TYPE)
    time.sleep(.9)
    shot(p, "composer-typing")
    state(p, "thread, composer typing")
    nav(p, url_of("draft"))
    shot(p, "draft")
    state(p, "draft 1512")
    p.js(FOCUS)
    p.js(TYPE)
    time.sleep(.9)
    shot(p, "draft-typing")
    state(p, "draft, composer typing")
    size(p, 1900)
    nav(p, url_of("thread"))
    p.js("document.documentElement.dataset.chatWidth='wide'")
    p.js("document.querySelector('.messages-timeline-scroll').scrollTop=2330")
    time.sleep(.5)
    shot(p, "thread-wide-1900")
    state(p, "thread 1900, chat width wide")
    p.js("document.documentElement.dataset.chatWidth='full'")
    time.sleep(.3)
    state(p, "thread 1900, chat width full")
    nav(p, url_of("draft"))
    p.js("document.documentElement.dataset.chatWidth='wide'")
    time.sleep(.5)
    shot(p, "draft-wide-1900")
    size(p, 1512)
    nav(p, url_of("thread"))
    p.js("document.querySelector('[data-workspace-area]').style.setProperty('--chat-lane-inset-end','300px')")
    time.sleep(.3)
    state(p, "thread 1512, lane inset end 300")
    size(p, 1100)
    nav(p, url_of("thread"))
    p.js(BOTTOM)
    time.sleep(.5)
    shot(p, "thread-narrow-1100")
    state(p, "thread 1100 (sidebar open)")
    nav(p, url_of("draft"))
    shot(p, "draft-narrow-1100")
    state(p, "draft 1100 (sidebar open)")
    size(p, 980)
    nav(p, url_of("thread"))
    state(p, "thread 980")
    nav(p, url_of("draft"))
    state(p, "draft 980")
    size(p, 1512)
    p.call("Emulation.setEmulatedMedia", features=[{"name": "prefers-reduced-motion", "value": "reduce"}])
    nav(p, url_of("thread"))
    p.js(FOCUS)
    time.sleep(.5)
    state(p, "reduced motion, focused empty")
    p.call("Emulation.setEmulatedMedia", features=[])
    p.call("Emulation.clearDeviceMetricsOverride")


def trace(p, b, url, busy, secs=5, inject=""):
    name, _, query = url.partition("?")
    nav(p, name)
    if query.isdigit():  # "thread?1100" traces the page at that viewport width
        size(p, int(query))
        time.sleep(.5)
    if inject:
        p.js("document.head.insertAdjacentHTML('beforeend'," + json.dumps("<style>" + inject + "</style>") + ")")
    if "pages/thread" in url:
        p.js(BOTTOM)
        time.sleep(1)
    p.js("window.__f=0;" + ("(function l(){window.__f++;requestAnimationFrame(l)})()" if busy else ""))
    b.call("Tracing.start", traceConfig={"includedCategories": CATS.split(","), "recordMode": "recordAsMuchAsPossible"},
           transferMode="ReturnAsStream")
    time.sleep(secs)
    anims = p.js("document.getAnimations().filter(a=>a.playState==='running').length")
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
            continue  # count each begin/instant once, not its end or async halves
        elif n == "ProxyImpl::ScheduledActionDraw":
            draws += 1
        elif n == "EarlyOut_NoDamage":
            nodmg += 1
        elif n == "ProxyMain::BeginMainFrame":
            mainfr += 1
    main = sum(ms[n] for n in NAMES[:5])
    return ms, main, (draws - nodmg) / secs, mainfr / secs, anims


def bench(names):
    b = CDP(get("/json/version")["webSocketDebuggerUrl"])
    p = page()
    print(f"{'page':14s} {'mode':4s} {'style':>7s} {'layout':>7s} {'prepaint':>8s} {'paint':>7s} {'commit':>7s} | {'main':>7s} {'raster':>7s} {'frames/s':>8s} {'mainfr/s':>8s} anims")
    for name in names:
        for mode in ("idle", "busy"):
            ms, main, fps, mfps, anims = trace(p, b, url_of(name), mode == "busy")
            label = "reference" if name.startswith("http") else name
            p.call("Emulation.clearDeviceMetricsOverride")
            print(f"{label:14s} {mode:4s} {ms['UpdateLayoutTree']:7.1f} {ms['Layout']:7.1f} {ms['PrePaint']:8.1f} {ms['Paint']:7.1f} "
                  f"{ms['Commit']:7.1f} | {main:7.1f} {ms['RasterTask']:7.1f} {fps:8.1f} {mfps:8.1f} {anims}", flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "shots":
        shots()
    else:
        bench(sys.argv[2:] or ["thread-none", "thread", "draft-none", "draft", REF])
