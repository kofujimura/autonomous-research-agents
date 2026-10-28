#!/usr/bin/env python3
"""Run a shell command with a timeout and record command, times, exit code, stdout, stderr.
Usage: run_logged.py <outdir> <timeout_seconds> <cwd> <command...>"""
import subprocess, sys, json, datetime, os
outdir, timeout, cwd = sys.argv[1], float(sys.argv[2]), sys.argv[3]
cmd = " ".join(sys.argv[4:])
os.makedirs(outdir, exist_ok=True)
now = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
rec = {"command": cmd, "cwd": cwd, "timeout_s": timeout, "start_utc": now()}
try:
    p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, timeout=timeout,
                       executable="/bin/bash")
    rec["exit_code"] = p.returncode; so, se = p.stdout, p.stderr
except subprocess.TimeoutExpired as e:
    rec["exit_code"] = "timeout"; so, se = e.stdout or b"", e.stderr or b""
rec["end_utc"] = now()
open(os.path.join(outdir, "stdout.txt"), "wb").write(so)
open(os.path.join(outdir, "stderr.txt"), "wb").write(se)
json.dump(rec, open(os.path.join(outdir, "run.json"), "w"), indent=2)
print(json.dumps(rec))
print("--- stdout tail ---"); print(so.decode(errors="replace")[-4000:])
print("--- stderr tail ---"); print(se.decode(errors="replace")[-2000:])
