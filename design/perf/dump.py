import json,sys,time
sys.argv=[sys.argv[0]]
import bench
from collections import Counter
orig=json.loads
def run(url):
    import urllib.request
    b=bench.CDP(json.load(urllib.request.urlopen('http://127.0.0.1:9344/json/version'))['webSocketDebuggerUrl'])
    p=bench.CDP(bench.page_target())
    p.call('Page.enable'); p.call('Page.navigate',url=url); p.wait_event('Page.loadEventFired'); time.sleep(2)
    b.call('Tracing.start',traceConfig={'includedCategories':bench.CATS.split(',')+['disabled-by-default-devtools.timeline.invalidationTracking','blink.animations','disabled-by-default-blink.debug']},transferMode='ReturnAsStream')
    time.sleep(2); b.call('Tracing.end')
    s=b.wait_event('Tracing.tracingComplete')['params']['stream']; buf=[]
    while True:
        r=b.call('IO.read',handle=s,size=1<<22); buf.append(r.get('data',''))
        if r.get('eof'): break
    d=json.loads(''.join(buf)); evs=d['traceEvents'] if isinstance(d,dict) else d
    c=Counter(); ex={}
    for e in evs:
        if True:
            k=(e.get('cat'),e.get('name'),e.get('ph')); c[k]+=1; ex.setdefault(k,e.get('args'))
    for k,v in c.most_common(30): print(v,k,json.dumps(ex[k])[:300])
run('http://127.0.0.1:8765/'+sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8765/a.html')
