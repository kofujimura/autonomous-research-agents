# For claims.jsonl expected records not found in CSVs, search regenerated JSON files for a dict containing all key/values.
import json, sys, os, glob, math
src, out, prev, report = sys.argv[1:5]
claims = {json.loads(l)['claim_id']: json.loads(l) for l in open(os.path.join(src, 'claims.jsonl'))}
def dicts(o):
    if isinstance(o, dict):
        yield o
        for v in o.values(): yield from dicts(v)
    elif isinstance(o, list):
        for v in o: yield from dicts(v)
def eq(a, b):
    if isinstance(b, float) or isinstance(a, float):
        try: return abs(float(a) - float(b)) <= 1e-12 + 1e-9 * abs(float(b))
        except Exception: return False
    return a == b
res = []
for r in json.load(open(prev)):
    c = claims[r['claim_id']]
    folders = {os.path.join(out, p.split('/')[1]) for p in c['evidence_paths'] if p.startswith('analysis/')}
    files = [f for d in folders for f in glob.glob(os.path.join(d, '**/*.json'), recursive=True)]
    for d in r['nonmatching']:
        rec = d['record']; found = None
        for f in files:
            try: o = json.load(open(f))
            except Exception: continue
            for x in dicts(o):
                if all(k in x and eq(x[k], v) for k, v in rec.items()): found = os.path.relpath(f, out); break
            if found: break
        res.append(dict(claim_id=r['claim_id'], path=d['path'], status='match' if found else 'not_found', file=found))
        print(r['claim_id'], d['path'], 'match' if found else 'NOT FOUND', found)
json.dump(res, open(report, 'w'), indent=1)
