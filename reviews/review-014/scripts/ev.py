# usage: ev.py TYPE SUMMARY [comma-separated artifact paths] [observed_at_utc override]
import json, sys, datetime, os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'events.jsonl')
n = sum(1 for _ in open(p)) if os.path.exists(p) else 0
t = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
paths = sys.argv[3] if len(sys.argv) > 3 else ''
if len(sys.argv) > 4 and sys.argv[4]: t = sys.argv[4]
ev = dict(event_id=f"E{n+1:03d}", observed_at_utc=t, type=sys.argv[1], summary=sys.argv[2], artifact_paths=[a for a in paths.split(',') if a])
open(p, 'a').write(json.dumps(ev, ensure_ascii=False) + "\n")
print(json.dumps(ev, ensure_ascii=False))
