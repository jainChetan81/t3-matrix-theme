import json, time, sys, urllib.request, bench
from collections import Counter
url='http://127.0.0.1:8765/'+sys.argv[1]
b=bench.CDP(json.load(urllib.request.urlopen('http://127.0.0.1:9344/json/version'))['webSocketDebuggerUrl'])
p=bench.CDP(bench.page_target())
p.call('Page.enable'); p.call('Page.navigate',url=url); p.wait_event('Page.loadEventFired'); time.sleep(2)
p.call('Runtime.evaluate',expression="(function l(){requestAnimationFrame(l)})()")
b.call('Tracing.start',traceConfig={'includedCategories':['devtools.timeline','disabled-by-default-devtools.timeline','disabled-by-default-devtools.timeline.invalidationTracking','blink.animations']},transferMode='ReturnAsStream')
time.sleep(1); b.call('Tracing.end')
s=b.wait_event('Tracing.tracingComplete')['params']['stream']; buf=[]
while True:
    r=b.call('IO.read',handle=s,size=1<<22); buf.append(r.get('data',''))
    if r.get('eof'): break
d=json.loads(''.join(buf)); evs=d['traceEvents'] if isinstance(d,dict) else d
c=Counter()
for e in evs:
    n=e.get('name')
    if 'Invalidation' in n or n in ('ScheduleStyleRecalculation','UpdateLayoutTree'):
        a=(e.get('args') or {}).get('data',{}) or {}
        c[(n, str(a.get('reason')), str(a.get('nodeName'))[:50], str(a.get('elementCount')))] += 1
for k,v in c.most_common(12): print(v,k)
