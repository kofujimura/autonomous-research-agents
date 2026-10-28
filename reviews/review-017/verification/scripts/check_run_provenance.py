"""Reviewer check (read-only): for each experiments/*/run.json, check plan/code commit IDs exist and their commit time precedes started_at_utc."""
import json, glob, subprocess, sys, datetime, os
root = sys.argv[1]
def ctime(c):
    try:
        out = subprocess.check_output(['git', '--no-optional-locks', '-C', root, 'show', '-s', '--format=%cI', c + '^{commit}'], stderr=subprocess.DEVNULL).decode().strip()
        return datetime.datetime.fromisoformat(out)
    except Exception:
        return None
rows = []
for f in sorted(glob.glob(os.path.join(root, 'experiments/*/run.json'))):
    d = json.load(open(f))
    st = d.get('started_at_utc')
    st = datetime.datetime.fromisoformat(st.replace('Z', '+00:00')) if st else None
    res = {'exp': d.get('experiment_id'), 'plan': d.get('plan_path'), 'exit': d.get('exit_code'), 'timed_out': d.get('timed_out')}
    for k in ['plan_commit_id', 'code_commit_id']:
        c = d.get(k)
        t = ctime(c) if c else None
        res[k] = (c[:8] if c else None, 'missing' if c and t is None else ('none' if not c else ('precedes' if st and t <= st else 'AFTER_START')))
    res['elapsed_s'] = round(d.get('elapsed_seconds') or 0, 1)
    rows.append(res)
bad = [r for r in rows if any(v[1] not in ('precedes',) for k, v in r.items() if k in ('plan_commit_id', 'code_commit_id'))]
for r in rows: print(r)
print('TOTAL', len(rows), 'NOT_PRECEDING_OR_MISSING', len(bad))
for r in bad: print('FLAG', r)
print('max elapsed', max(r['elapsed_s'] for r in rows))
