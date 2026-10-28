import json, sys, datetime, os
# usage: ev.py TYPE SUMMARY [artifact ...]
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'events.jsonl')
n = 0
if os.path.exists(p):
    n = sum(1 for l in open(p) if l.strip())
e = {"event_id": "RE%03d" % (n + 1),
     "observed_at_utc": datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
     "type": sys.argv[1], "summary": sys.argv[2], "artifact_paths": sys.argv[3:]}
open(p, 'a').write(json.dumps(e, ensure_ascii=False) + '\n')
print(json.dumps(e, ensure_ascii=False))
