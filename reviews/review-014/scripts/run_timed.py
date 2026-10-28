# usage: run_timed.py LABEL TIMEOUT_S OUTDIR -- cmd...
import subprocess, sys, json, time, datetime, os
label, timeout, outdir = sys.argv[1], int(sys.argv[2]), sys.argv[3]
cmd = sys.argv[sys.argv.index('--')+1:]
os.makedirs(outdir, exist_ok=True)
now = lambda: datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
rec = dict(label=label, command=cmd, cwd=os.getcwd(), timeout_s=timeout, start_utc=now())
t0 = time.monotonic()
with open(os.path.join(outdir, f'{label}.stdout.txt'), 'w') as so, open(os.path.join(outdir, f'{label}.stderr.txt'), 'w') as se:
    try:
        p = subprocess.run(cmd, stdout=so, stderr=se, timeout=timeout)
        rec['exit_code'] = p.returncode
    except subprocess.TimeoutExpired:
        rec['exit_code'] = 'timeout'
rec['end_utc'] = now(); rec['elapsed_s'] = round(time.monotonic()-t0, 3)
json.dump(rec, open(os.path.join(outdir, f'{label}.run.json'), 'w'), indent=1)
print(json.dumps(rec))
