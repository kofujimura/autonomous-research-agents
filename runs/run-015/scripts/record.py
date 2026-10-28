"""Local append-only research records; all timestamps come from the OS clock."""
import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

def append(name, item):
    with (ROOT / name).open("a") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        stream.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")
        stream.flush()
        fcntl.flock(stream, fcntl.LOCK_UN)

def event(kind, summary, paths=(), related=(), **extra):
    # Allocate IDs and append while holding one lock: acquisition workers may
    # finish concurrently, and independent count/read operations would race.
    with (ROOT / "events.jsonl").open("a+") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        stream.seek(0)
        count=sum(1 for _ in stream)
        item = dict(event_id=f"E{count+1:04d}", observed_at_utc=now(), type=kind,
                    summary=summary, artifact_paths=list(paths), related_ids=list(related), **extra)
        stream.write(json.dumps(item, ensure_ascii=False, sort_keys=True)+"\n")
        stream.flush()
        fcntl.flock(stream, fcntl.LOCK_UN)
    return item["event_id"]

def secret_check():
    # Never prints the value, length, digest or location of the secret.
    value = os.environ.get("FREE_RESEARCH_OPENAI_API_KEY", "").encode()
    if not value:
        return "key_not_set"
    for path in ROOT.rglob("*"):
        if path.is_file() and not path.is_symlink():
            if value in path.read_bytes():
                raise SystemExit("STOP: API key value found in research directory; notify human and revoke key")
    return "key_value_absent"

def commit(summary, paths=()):
    check = secret_check()
    eid = event("git_commit_intent", summary, paths, secret_scan=check)
    subprocess.run(["git", "add", "--all"], cwd=ROOT, check=True)
    subprocess.run(["git", "-c", "user.name=Autonomous Research", "-c", "user.email=research@localhost", "commit", "--quiet", "-m", f"{eid}: {summary}"], cwd=ROOT, check=True)
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    event("git_commit_completed", summary, paths, [eid], commit_id=sha)
    print(json.dumps(dict(event_id=eid, commit_id=sha, observed_at_utc=now(), secret_scan=check)))
    return sha

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["event", "commit", "secret-check", "time", "clock-checkpoint"])
    parser.add_argument("text", nargs="?", default="")
    parser.add_argument("--kind", default="milestone")
    parser.add_argument("--paths", nargs="*", default=[])
    args = parser.parse_args()
    if args.action == "event": print(event(args.kind, args.text, args.paths))
    elif args.action == "commit": commit(args.text, args.paths)
    elif args.action == "secret-check": print(secret_check())
    elif args.action == "clock-checkpoint":
        stamp=now()
        (ROOT/'checkpoint-time.json').write_text(json.dumps({'observed_at_utc':stamp,
            'source':'OS UTC clock read by explicit exec_command tool call; durable clock checkpoint, not estimated'},indent=2)+'\n')
        print(stamp)
    else: print(now())
