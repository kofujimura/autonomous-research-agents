"""Local research records, timestamped by the operating system."""
import argparse
import datetime as dt
import hashlib
import json
import os
import fcntl
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

def append(path, obj):
    with (ROOT / path).open("a") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def event(kind, summary, paths=(), related=(), **extra):
    # Two bounded retrieval processes may report simultaneously.
    with (ROOT / 'events.jsonl').open('a+') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        stream.seek(0)
        eid = f"E{len(stream.read().splitlines())+1:04d}"
        obj = dict(event_id=eid, observed_at_utc=now(), type=kind,
                   summary=summary, artifact_paths=list(paths), related_ids=list(related), **extra)
        stream.write(json.dumps(obj, ensure_ascii=False)+'\n');stream.flush()
        fcntl.flock(stream, fcntl.LOCK_UN)
    print(json.dumps(obj))
    return eid

def check_secrets():
    secret = os.environ.get("FREE_RESEARCH_OPENAI_API_KEY", "").encode()
    if not secret:
        print("SECRET_SCAN: key not available; scan cannot compare its value")
        return
    matches = []
    for p in ROOT.rglob("*"):
        if p.is_file() and not p.is_symlink():
            try:
                with p.open("rb") as f:
                    tail = b""
                    while chunk := f.read(1024*1024):
                        data = tail + chunk
                        if secret in data:
                            matches.append(str(p.relative_to(ROOT)))
                            break
                        tail = data[-max(0, len(secret)-1):]
            except OSError:
                raise
    if matches:
        print("SECRET_SCAN: FAIL; matching file count:", len(matches))
        raise SystemExit(20)
    print("SECRET_SCAN: PASS (no key value printed)")

def commit(kind, summary, paths=()):
    check_secrets()
    eid = event(kind, summary, paths)
    subprocess.run(["git", "add", "--all"], cwd=ROOT, check=True)
    subprocess.run(["git", "-c", "user.name=Free Research 014", "-c", "user.email=research-014@localhost",
                    "commit", "-q", "-m", f"{eid}: {summary}"], cwd=ROOT, check=True)
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    event("git_commit", f"Committed {eid}", ["events.jsonl"], [eid], commit_id=sha)
    return sha

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["event", "commit", "secret-scan"])
    p.add_argument("kind", nargs="?", default="checkpoint")
    p.add_argument("summary", nargs="?", default="")
    p.add_argument("paths", nargs="*")
    a = p.parse_args()
    if a.action == "secret-scan": check_secrets()
    elif a.action == "event": event(a.kind, a.summary, a.paths)
    else: commit(a.kind, a.summary, a.paths)
