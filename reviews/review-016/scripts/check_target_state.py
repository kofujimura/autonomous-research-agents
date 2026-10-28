#!/usr/bin/env python3
"""Check run-016 state against review/submission-1/SHA256SUMS.json (read-only)."""
import hashlib, json, os, subprocess, sys, datetime
R = "/Users/fujimura/Research/ai-free-research-en/run-016"
out = sys.argv[1]
def sh(*a):
    return subprocess.run(a, capture_output=True, text=True).stdout
res = {"observed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}
res["head"] = sh("git", "-C", R, "rev-parse", "HEAD").strip()
res["tag_submission_1"] = sh("git", "-C", R, "rev-parse", "submission-1^{commit}").strip()
res["git_status"] = sh("git", "-C", R, "--no-optional-locks", "status")
res["git_status_porcelain"] = sh("git", "-C", R, "--no-optional-locks", "status", "--porcelain")
inv = json.load(open(os.path.join(R, "review/submission-1/SHA256SUMS.json")))
match = mismatch = missing = 0
mism, miss = [], []
for f in inv["files"]:
    p = os.path.join(R, f["path"])
    if not os.path.isfile(p):
        missing += 1; miss.append(f["path"]); continue
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        if f["mode"] == "prefix":
            h.update(fh.read(f["bytes"]))
        else:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
    if h.hexdigest() == f["sha256"]:
        match += 1
    else:
        mismatch += 1; mism.append(f["path"])
res.update({"inventory_entries": len(inv["files"]), "match": match, "mismatch": mismatch,
            "missing": missing, "mismatch_paths": mism, "missing_paths": miss})
json.dump(res, open(out, "w"), indent=2)
print(json.dumps({k: v for k, v in res.items() if k != "git_status"}, indent=2))
