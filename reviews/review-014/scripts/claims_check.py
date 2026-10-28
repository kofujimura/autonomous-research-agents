# Reviewer-written generic check: compare claims.jsonl expected records with regenerated CSV/JSON outputs.
# For each expected dict record, find rows in the claim's evidence CSVs (regenerated copies) whose string fields
# all match; prefer rows with availability_mode=paired, support=centre, seed=14014, reference_mode=global when
# those columns exist and the record does not specify them; then compare numeric fields (rtol 1e-9, atol 1e-12).
import json, sys, os, glob, math
import pandas as pd, numpy as np
src, out, report = sys.argv[1], sys.argv[2], sys.argv[3]
DEFAULTS = dict(availability_mode='paired', support='centre', seed=14014, reference_mode='global', calibration_fpr=0.1)
def regenerated(path):
    if path.startswith('analysis/'):
        p = os.path.join(out, path[len('analysis/'):])
        return p if os.path.exists(p) else None
    return None
def load_tables(claim):
    tabs = []
    folders = set()
    for p in claim['evidence_paths']:
        r = regenerated(p)
        if r and r.endswith('.csv'): tabs.append(r)
        if p.startswith('analysis/'): folders.add(os.path.join(out, p.split('/')[1]))
    for f in folders:
        tabs += [t for t in glob.glob(os.path.join(f, '**/*.csv'), recursive=True) if t not in tabs and '/seed-' not in t]
    res = []
    for t in tabs:
        try: res.append((t, pd.read_csv(t)))
        except Exception: pass
    return res
def records(e, prefix=''):
    if isinstance(e, list):
        for i, x in enumerate(e): yield from records(x, f'{prefix}[{i}]')
    elif isinstance(e, dict):
        scal = {k: v for k, v in e.items() if not isinstance(v, (dict, list))}
        nested = {k: v for k, v in e.items() if isinstance(v, (dict, list))}
        if any(isinstance(v, str) for v in scal.values()) and any(isinstance(v, (int, float)) and not isinstance(v, bool) for v in scal.values()):
            yield prefix, scal
        for k, v in nested.items(): yield from records(v, f'{prefix}.{k}')
def match(rec, tables):
    strs = {k: v for k, v in rec.items() if isinstance(v, str)}
    nums = {k: v for k, v in rec.items() if isinstance(v, (int, float)) and not isinstance(v, bool)}
    for t, df in tables:
        if not all(k in df.columns for k in strs): continue
        if not any(k in df.columns for k in nums): continue
        m = df
        for k, v in strs.items(): m = m[m[k].astype(str) == v]
        if len(m) == 0: continue
        for k, v in DEFAULTS.items():
            if k in m.columns and k not in rec and len(m) > 1:
                mm = m[m[k].astype(str) == str(v)]
                if len(mm): m = mm
        cands = []
        for _, row in m.iterrows():
            ok = True; cmp = 0
            for k, v in nums.items():
                if k not in row.index: continue
                a = row[k]
                if v is None or (isinstance(v, float) and math.isnan(v)):
                    ok = ok and pd.isna(a); cmp += 1; continue
                try: a = float(a)
                except Exception: ok = False; continue
                cmp += 1
                if not (abs(a - v) <= 1e-12 + 1e-9 * abs(v)): ok = False
            if cmp: cands.append((ok, cmp))
        if any(ok for ok, _ in cands): return 'match', os.path.relpath(t, out)
        if cands: last = ('mismatch', os.path.relpath(t, out))
    return locals().get('last', ('not_found', None))
results = []
for line in open(os.path.join(src, 'claims.jsonl')):
    c = json.loads(line)
    tabs = load_tables(c)
    counts = dict(match=0, mismatch=0, not_found=0); details = []
    for pre, rec in records(c['expected']):
        st, where = match(rec, tabs); counts[st] += 1
        if st != 'match': details.append(dict(path=pre, record=rec, status=st, table=where))
    results.append(dict(claim_id=c['claim_id'], tables=len(tabs), **counts, nonmatching=details[:10]))
    print(c['claim_id'], 'tables', len(tabs), counts)
json.dump(results, open(report, 'w'), indent=1)
