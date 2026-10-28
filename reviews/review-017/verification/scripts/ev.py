#!/usr/bin/env python3
# usage: ev.py TYPE "summary" [artifact_path ...]  -- appends one event with tool-obtained UTC time
import json, sys, datetime, os
f = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "events.jsonl")
n = 0
if os.path.exists(f):
    with open(f) as g:
        n = sum(1 for _ in g)
rec = {"event_id": "RE%04d" % (n + 1),
       "observed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
       "type": sys.argv[1], "summary": sys.argv[2], "artifact_paths": sys.argv[3:]}
with open(f, "a") as g:
    g.write(json.dumps(rec, ensure_ascii=False) + "\n")
print(json.dumps(rec, ensure_ascii=False))
