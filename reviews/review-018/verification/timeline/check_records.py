import json, os, subprocess, sys, hashlib, datetime as D, glob
src = sys.argv[1]
def git(*a):
    r = subprocess.run(['git', '-C', src, *a], capture_output=True, text=True)
    return r.returncode, r.stdout.strip()
rows = []
for rec in sorted(glob.glob(os.path.join(src, 'experiments', '*', 'record.json'))):
    name = rec.split('/')[-2]
    try:
        r = json.load(open(rec))
    except Exception as ex:
        rows.append({'exp': name, 'error': str(ex)}); continue
    out = {'exp': name, 'start': r.get('start_time_utc'), 'exit': r.get('exit_code')}
    st = r.get('start_time_utc')
    st = D.datetime.fromisoformat(st) if st else None
    for k in ('plan_commit', 'code_commit'):
        c = r.get(k)
        if not c:
            out[k] = 'absent'; continue
        rc, t = git('show', '-s', '--format=%cI', c)
        if rc != 0:
            out[k] = 'MISSING'; continue
        ct = D.datetime.fromisoformat(t)
        out[k] = 'ok' if (st is None or ct <= st) else 'AFTER_START'
        out[k + '_time'] = t
    pc, pp, ps = r.get('plan_commit'), r.get('plan_path'), r.get('plan_sha256')
    if pc and pp and ps:
        rc, _ = git('cat-file', '-e', f'{pc}:{pp}')
        if rc == 0:
            b = subprocess.run(['git', '-C', src, 'show', f'{pc}:{pp}'], capture_output=True).stdout
            out['plan_sha_match'] = hashlib.sha256(b).hexdigest() == ps
        else:
            out['plan_sha_match'] = 'plan_not_in_commit'
    if pc and r.get('code_commit'):
        rc, _ = git('merge-base', '--is-ancestor', pc, r['code_commit'])
        out['plan_ancestor_of_code'] = rc == 0
    rows.append(out)
json.dump(rows, open(sys.argv[2], 'w'), indent=1)
n = len(rows)
def cnt(f): return sum(1 for x in rows if f(x))
print('records', n)
print('plan_commit ok', cnt(lambda x: x.get('plan_commit') == 'ok'), 'missing', cnt(lambda x: x.get('plan_commit') == 'MISSING'), 'after_start', cnt(lambda x: x.get('plan_commit') == 'AFTER_START'), 'absent', cnt(lambda x: x.get('plan_commit') == 'absent'))
print('code_commit ok', cnt(lambda x: x.get('code_commit') == 'ok'), 'missing', cnt(lambda x: x.get('code_commit') == 'MISSING'), 'after_start', cnt(lambda x: x.get('code_commit') == 'AFTER_START'), 'absent', cnt(lambda x: x.get('code_commit') == 'absent'))
print('plan sha match', cnt(lambda x: x.get('plan_sha_match') is True), 'mismatch', cnt(lambda x: x.get('plan_sha_match') is False), 'other', cnt(lambda x: x.get('plan_sha_match') not in (True, False)))
print('plan ancestor of code', cnt(lambda x: x.get('plan_ancestor_of_code') is True), 'not', cnt(lambda x: x.get('plan_ancestor_of_code') is False))
print('nonzero exit', [(x['exp'], x.get('exit')) for x in rows if x.get('exit') not in (0, None)])
for x in rows:
    if x.get('plan_commit') not in ('ok',) or x.get('code_commit') not in ('ok',) or x.get('plan_sha_match') is not True:
        print('FLAG', json.dumps(x))
