#!/usr/bin/env python3
"""Reviewer's own recomputation (not using the research-side estimator code) of the
primary direct-sampling results from raw labels and saved sample-index draws.
Usage: independent_direct.py <source_copy_root> <output_dir> [taxonomy]"""
import json, sys, os
import numpy as np
root, out = sys.argv[1], sys.argv[2]
tax = sys.argv[3] if len(sys.argv) > 3 else 'broad'
os.makedirs(out, exist_ok=True)
pop = json.load(open(os.path.join(root, 'data/population-main-v1.json')))
draws = json.load(open(os.path.join(root, 'data/audit-draws-main/manifest.json')))['draws']
ids = pop[tax + '_ids']; K = len(ids)
lookup = np.full(256, -1, int); lookup[ids] = np.arange(K)
recs = {r['landscape_id']: r for r in pop['landscapes']}

def H(p):
    p = np.asarray(p, float)
    with np.errstate(divide='ignore', invalid='ignore'):
        t = np.where(p > 0, -p * np.log(np.where(p > 0, p, 1)), 0.0)
    return t.sum(-1)

def direct(ya, yb, ia, ib, paired, eps=1e-6):
    N = len(ya); n = ia.shape[1]; R = ia.shape[0]
    sa = ya[ia]; sb = yb[ib]
    pa = np.zeros((R, K)); pb = np.zeros((R, K))
    for r in range(R):
        pa[r] = np.bincount(sa[r], minlength=K) / n
        pb[r] = np.bincount(sb[r], minlength=K) / n
    est = H(pb) - H(pa)
    ga = -(np.log(np.maximum(pa, eps)) + 1); gb = -(np.log(np.maximum(pb, eps)) + 1)
    va = np.take_along_axis(ga, sa, 1); vb = np.take_along_axis(gb, sb, 1)
    if paired:
        var = np.var(vb - va, axis=1, ddof=1)
    else:
        var = np.var(va, axis=1, ddof=1) + np.var(vb, axis=1, ddof=1)
    se = np.sqrt(np.maximum(var * (1 - n / N) / n, 0))
    zero_change = (sa == sb).all(1) if paired else np.zeros(R, bool)
    return est, se, zero_change

rows = []
for u in draws:
    if not u['primary']:
        continue
    r = recs[u['landscape_id']]
    z = np.load(os.path.join(root, r['path']))
    ix = np.asarray(r['valid_indices'], int)
    lab = lookup[z[tax][:, ix]]
    assert (lab >= 0).all()
    ya = lab[u['year_a'] - 2021]; yb = lab[u['year_b'] - 2021]
    assert len(ya) == u['N']
    truth = H(np.bincount(yb, minlength=K) / len(yb)) - H(np.bincount(ya, minlength=K) / len(ya))
    d = np.load(os.path.join(root, u['path']))
    A = d['a'].astype(int); B = d['b'].astype(int)
    base = dict(unit=f"{u['landscape_id']}-{u['year_a']}-{u['year_b']}", truth=float(truth),
                labels_changed_frac=float((ya != yb).mean()), N=len(ya),
                arable=r.get('baseline_arable_fraction'), grass=r.get('baseline_grassland_fraction'))
    for n in u['budgets']:
        for design in ['paired', 'independent']:
            ia = A[:, :n]; ib = A[:, :n] if design == 'paired' else B[:, :n]
            est, se, zc = direct(ya, yb, ia, ib, design == 'paired')
            lo, hi = est - 1.96 * se, est + 1.96 * se
            cov = (lo <= truth + 1e-10) & (hi >= truth - 1e-10)
            dirn = np.where(lo > 1e-10, 1, np.where(hi < -1e-10, -1, 0))
            st = int(np.sign(truth)) if abs(truth) > 1e-10 else 0
            rep = dirn != 0; wrong = rep & (dirn != st)
            rows.append(dict(base, n=n, design=design, mse=float(np.mean((est - truth) ** 2)),
                             coverage=float(cov.mean()), reports=int(rep.sum()), wrong=int(wrong.sum()),
                             zero_change_draws=int(zc.sum()), R=len(est)))
json.dump(rows, open(os.path.join(out, f'rows-{tax}.json'), 'w'))
import collections
units = sorted({r['unit'] for r in rows})
truth = {r['unit']: r['truth'] for r in rows}
t = np.array([truth[u] for u in units])
summary = dict(taxonomy=tax, units=len(units), no_change_rmse=float(np.sqrt(np.mean(t ** 2))),
               tiny=int((np.abs(t) < 0.01).sum()), exact_zero=int((np.abs(t) <= 1e-10).sum()),
               rms_truth=float(np.sqrt(np.mean(t ** 2))), median_abs_truth=float(np.median(np.abs(t))))
by = collections.defaultdict(list)
for r in rows:
    by[(r['n'], r['design'])].append(r)
tab = []
for (n, d), rs in sorted(by.items()):
    tab.append(dict(n=n, design=d, rmse=float(np.sqrt(np.mean([r['mse'] for r in rs]))),
                    coverage=float(np.mean([r['coverage'] for r in rs])),
                    report_rate=sum(r['reports'] for r in rs) / sum(r['R'] for r in rs),
                    wrong_rate=sum(r['wrong'] for r in rs) / sum(r['R'] for r in rs),
                    reports=sum(r['reports'] for r in rs), wrong=sum(r['wrong'] for r in rs),
                    zero_change_frac=sum(r['zero_change_draws'] for r in rs) / sum(r['R'] for r in rs)))
for n in sorted({x['n'] for x in tab}):
    p = [x for x in tab if x['n'] == n and x['design'] == 'paired'][0]
    i = [x for x in tab if x['n'] == n and x['design'] == 'independent'][0]
    p['mse_ratio_paired_over_independent'] = (p['rmse'] / i['rmse']) ** 2
summary['table'] = tab
json.dump(summary, open(os.path.join(out, f'summary-{tax}.json'), 'w'), indent=1)
print(json.dumps(summary, indent=1))
