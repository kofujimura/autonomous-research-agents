#!/usr/bin/env python3
"""Read-only check of run-017/review/submission-1/OUTPUT_SHA256.jsonl against the research directory.

Usage: python3 -I check_target_hashes.py <research_dir> <output_json>
Only reads files in <research_dir>; writes only <output_json>.
"""
import hashlib, json, os, sys, datetime

root, out = sys.argv[1], sys.argv[2]
lst = os.path.join(root, "review", "submission-1", "OUTPUT_SHA256.jsonl")
start = datetime.datetime.now(datetime.timezone.utc).isoformat()
match, mismatch, missing = 0, [], []
scope = None
n = 0
with open(lst) as f:
    for line in f:
        rec = json.loads(line)
        if rec.get("type") == "scope":
            scope = rec
            continue
        n += 1
        p = os.path.join(root, rec["path"])
        if not os.path.isfile(p):
            missing.append(rec["path"])
            continue
        h = hashlib.sha256()
        size = 0
        with open(p, "rb") as g:
            while True:
                b = g.read(1 << 20)
                if not b:
                    break
                h.update(b)
                size += len(b)
        if h.hexdigest() == rec["sha256"] and size == rec["bytes"]:
            match += 1
        else:
            mismatch.append({"path": rec["path"], "expected_bytes": rec["bytes"], "actual_bytes": size})
end = datetime.datetime.now(datetime.timezone.utc).isoformat()
res = {"list": lst, "started_at_utc": start, "completed_at_utc": end, "scope_record": scope,
       "entries": n, "match": match, "mismatch": len(mismatch), "missing": len(missing),
       "mismatch_paths": mismatch, "missing_paths": missing}
with open(out, "w") as f:
    json.dump(res, f, indent=1)
print(json.dumps({k: res[k] for k in ["entries", "match", "mismatch", "missing", "started_at_utc", "completed_at_utc"]}))
print("mismatch paths:", [m["path"] for m in mismatch])
print("missing paths:", missing)
