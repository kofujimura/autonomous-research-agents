"""Run a command with a wall-clock limit, recording start/end UTC, exit code, stdout/stderr.
Usage: python3 runlim.py RECORD_DIR LIMIT_SECONDS -- cmd args...
Kills the whole process group on timeout."""
import json, os, signal, subprocess, sys, time
from datetime import datetime, timezone
def now(): return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
rec = sys.argv[1]; limit = float(sys.argv[2]); assert sys.argv[3] == '--'; cmd = sys.argv[4:]
os.makedirs(rec, exist_ok=True)
meta = {'command': cmd, 'cwd': os.getcwd(), 'limit_seconds': limit, 'start_utc': now()}
t0 = time.monotonic()
with open(os.path.join(rec, 'stdout.txt'), 'w') as o, open(os.path.join(rec, 'stderr.txt'), 'w') as e:
    p = subprocess.Popen(cmd, stdout=o, stderr=e, start_new_session=True)
    try:
        rc = p.wait(timeout=limit); meta['timed_out'] = False
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGTERM); time.sleep(5)
        try: os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError: pass
        rc = p.wait(); meta['timed_out'] = True
meta.update(end_utc=now(), elapsed_seconds=round(time.monotonic() - t0, 1), exit_code=rc)
json.dump(meta, open(os.path.join(rec, 'run.json'), 'w'), indent=1)
print(json.dumps(meta))
