"""Reviewer's own recomputation of the primary half-coverage results from saved predictions.
Written independently of code/summarize_matching.py (csv module; numpy only for bootstrap)."""
import csv, sys, json, math, collections, glob, os
import numpy as np
pred_dir, out = sys.argv[1], sys.argv[2]
rows = []
for p in sorted(glob.glob(os.path.join(pred_dir, 'r*', 'predictions.csv'))):
    rows += list(csv.DictReader(open(p)))
groups = collections.defaultdict(list)
for r in rows:
    groups[(r['region'], r['rotation'], r['method'])].append(r)
sel = collections.defaultdict(list)  # (method, region) -> list of mismatch
for (reg, rot, m), g in groups.items():
    g = sorted(g, key=lambda x: (-float(x['confidence']), int(x['query_id'])))
    k = int(math.floor(len(g) * 0.5))
    sel[(m, reg)] += [int(x['mismatch']) for x in g[:k]]
methods = sorted({k[0] for k in sel}); regions = sorted({k[1] for k in sel})
res = {'methods': {}, 'per_window': {}, 'contrasts': {}}
for m in methods:
    risks = {reg: sum(sel[(m, reg)]) / len(sel[(m, reg)]) for reg in regions if len(sel[(m, reg)])}
    allv = [v for reg in regions for v in sel[(m, reg)]]
    res['methods'][m] = {'window_mean': sum(risks.values()) / len(risks), 'pooled': sum(allv) / len(allv), 'retained': len(allv), 'n_windows': len(risks)}
    res['per_window'][m] = {reg: [len(sel[(m, reg)]), risks.get(reg)] for reg in regions}
def boot(d):
    d = np.asarray(d, float); rng = np.random.default_rng(18018)
    means = d[rng.integers(0, len(d), (10000, len(d)))].mean(axis=1)
    return np.quantile(means, [.025, .975]).tolist()
for m in ['pair_aef', 'pair_tessera', 'pair_both']:
    for b in ['hydro_pair', 'hydro_decoder']:
        d = [res['per_window'][m][reg][1] - res['per_window'][b][reg][1] for reg in regions]
        res['contrasts'][f'{m}|{b}'] = {'window_mean_diff': float(np.mean(d)), 'boot95': boot(d),
            'pooled_diff': res['methods'][m]['pooled'] - res['methods'][b]['pooled'],
            'per_window_diff': dict(zip(regions, d)),
            'improved': sum(x < 0 for x in d), 'worsened': sum(x > 0 for x in d), 'equal': sum(x == 0 for x in d)}
json.dump(res, open(out, 'w'), indent=1)
print('method window_mean pooled retained')
for m in methods:
    v = res['methods'][m]; print(f"{m:24s} {100*v['window_mean']:.2f} {100*v['pooled']:.2f} {v['retained']}")
print('retained per window (hydro_pair):', {reg: res['per_window']['hydro_pair'][reg][0] for reg in regions})
for k, v in res['contrasts'].items():
    print(k, 'wm %.2f pp [%.2f, %.2f]' % (100*v['window_mean_diff'], 100*v['boot95'][0], 100*v['boot95'][1]), 'pooled %.2f pp' % (100*v['pooled_diff']), 'impr/wors/eq', v['improved'], v['worsened'], v['equal'])
