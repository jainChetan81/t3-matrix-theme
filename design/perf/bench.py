# Trace a page for N s idle on headless Chrome :9344; print style/layout/paint/commit/raster ms, fps, animations.
import json, sys, time, urllib.request, websocket

PORT = 9344
CATS = 'devtools.timeline,disabled-by-default-devtools.timeline,blink.animations,cc,gpu,disabled-by-default-devtools.timeline.frame'
NAMES = ['UpdateLayoutTree', 'Layout', 'PrePaint', 'Paint', 'Commit', 'RasterTask']


class CDP:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, max_size=None, suppress_origin=True)
        self.i = 0
        self.events = []

    def call(self, method, **params):
        self.i += 1
        my = self.i
        self.ws.send(json.dumps({'id': my, 'method': method, 'params': params}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get('id') == my:
                if 'error' in m:
                    raise RuntimeError(m['error'])
                return m.get('result', {})
            self.events.append(m)

    def wait_event(self, name, timeout=30):
        end = time.time() + timeout
        for e in self.events:
            if e.get('method') == name:
                return e
        self.ws.settimeout(1)
        while time.time() < end:
            try:
                m = json.loads(self.ws.recv())
            except websocket.WebSocketTimeoutException:
                continue
            if m.get('method') == name:
                self.ws.settimeout(None)
                return m
        raise TimeoutError(name)


def page_target():
    tabs = json.load(urllib.request.urlopen(f'http://127.0.0.1:{PORT}/json'))
    pages = [t for t in tabs if t['type'] == 'page']
    return pages[0]['webSocketDebuggerUrl']


def run(url, secs=5, settle=2.5, raf=True):
    browser = json.load(urllib.request.urlopen(f'http://127.0.0.1:{PORT}/json/version'))['webSocketDebuggerUrl']
    b = CDP(browser)
    p = CDP(page_target())
    p.call('Page.enable')
    p.call('Page.navigate', url=url)
    p.wait_event('Page.loadEventFired')
    time.sleep(settle)
    p.call('Runtime.evaluate', expression="window.__f=0;(function l(){window.__f++;requestAnimationFrame(l)})()" if raf else "window.__f=0")
    b.call('Tracing.start', traceConfig={'includedCategories': CATS.split(','), 'recordMode': 'recordAsMuchAsPossible'},
           transferMode='ReturnAsStream')
    f0 = p.call('Runtime.evaluate', expression='window.__f', returnByValue=True)['result']['value']
    time.sleep(secs)
    f1 = p.call('Runtime.evaluate', expression='window.__f', returnByValue=True)['result']['value']
    anims = p.call('Runtime.evaluate', expression='document.getAnimations().length', returnByValue=True)['result']['value']
    b.call('Tracing.end')
    stream = b.wait_event('Tracing.tracingComplete')['params']['stream']
    buf = []
    while True:
        r = b.call('IO.read', handle=stream, size=1 << 22)
        buf.append(r.get('data', ''))
        if r.get('eof'):
            break
    b.call('IO.close', handle=stream)
    data = json.loads(''.join(buf))
    evs = data['traceEvents'] if isinstance(data, dict) else data
    tot = {n: 0.0 for n in NAMES}
    cnt = {n: 0 for n in NAMES}
    fails = {}
    reasons = {}
    other = {'ProxyImpl::ScheduledActionDraw': 0, 'EarlyOut_NoDamage': 0, 'ProxyMain::BeginMainFrame': 0}
    for e in evs:
        n = e.get('name')
        if n in other and e.get('ph') in ('X', 'I', 'i', 'B'):
            other[n] += 1
        if n in tot and e.get('ph') == 'X':
            tot[n] += e.get('dur', 0) / 1000
            cnt[n] += 1
        a = e.get('args', {}).get('data', {}) or {}
        if 'compositeFailed' in a:
            fails[(n, a.get('compositeFailed'), str(a.get('unsupportedProperties')))] = 1
        if n == 'ScheduleStyleRecalculation' or n == 'StyleRecalcInvalidationTracking' or n == 'StyleInvalidatorInvalidationTracking':
            r = a.get('reason') or a.get('invalidationSet') or ''
            if r:
                reasons[str(r)[:40]] = reasons.get(str(r)[:40], 0) + 1
    return {
        'ms': {k: round(v, 1) for k, v in tot.items()},
        'n': cnt,
        'fps': round((f1 - f0) / secs, 1),
        'anims': anims,
        'compositeFailed': list(fails.keys())[:6],
        'reasons': reasons,
        'dfps': round((other['ProxyImpl::ScheduledActionDraw'] - other['EarlyOut_NoDamage']) / secs, 1),
        'mainframes': round(other['ProxyMain::BeginMainFrame'] / secs, 1),
    }


if __name__ == '__main__':
    args = sys.argv[1:]
    modes = ['busy', 'idle']
    if args and args[0] in ('busy', 'idle'):
        modes = [args.pop(0)]
    rows = []
    for u in args:
        url = u if u.startswith('http') else f'http://127.0.0.1:8765/{u}'
        for mode in modes:
            r = run(url, raf=(mode == 'busy'))
            ms = r['ms']
            main = ms['UpdateLayoutTree'] + ms['Layout'] + ms['PrePaint'] + ms['Paint'] + ms['Commit']
            rows.append((u, mode, r))
            print(f"{u.split('/')[-1][:24]:24s} {mode:4s} style {ms['UpdateLayoutTree']:6.1f} layout {ms['Layout']:5.1f} prepaint {ms['PrePaint']:6.1f} "
                  f"paint {ms['Paint']:6.1f} commit {ms['Commit']:6.1f} raster {ms['RasterTask']:7.1f} | main {main:6.1f} "
                  f"rAF {r['fps']:5.1f} dmg/s {r['dfps']:5.1f} mainfr/s {r['mainframes']:5.1f} anims {r['anims']} n {r['n']['UpdateLayoutTree']}/{r['n']['Paint']}/{r['n']['RasterTask']} fail {r['compositeFailed'][:2]}", flush=True)
    json.dump([(u, m, r) for u, m, r in rows], open('/tmp/matrix-tools/bench2/last.json', 'w'), default=str)
