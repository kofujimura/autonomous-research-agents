#!/usr/bin/env python3
"""Reviewer sensitivity check (not part of the submitted study): independent annual
labelling error at audited locations. Each sampled label is replaced, with probability eps
and independently in each year, by a draw from that landscape-year's population class
distribution excluding the true class. Target = error-free population change. Direct estimator
and delta-method SE as in the paper (gradient floor 1e-6, FPC). Saved draws, n=128, broad.
Usage: label_noise_sensitivity.py <source_root> <out_json>"""
import json, sys, os
import numpy as np
root, outp = sys.argv[1], sys.argv[2]
pop = json.load(open(os.path.join(root, 'data/population-main-v1.json')))
draws = json.load(open(os.path.join(root, 'data/audit-draws-main/manifest.json')))['draws']
ids = pop['broad_ids']; K = len(ids)
lookup = np.full(256, -1, int); lookup[ids] = np.arange(K)
recs = {r['landscape_id']: r for r in pop['landscapes']}
def H(p):
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.where(p > 0, -p * np.log(np.where(p > 0, p, 1)), 0).sum(-1)
def noisy(s, eps, q, rng):
    s = s.copy()
    flip = rng.random(s.shape) < eps
    for idx in zip(*np.nonzero(flip)):
        w = q.copy(); w[s[idx]] = 0
        if w.sum() > 0: s[idx] = rng.choice(K, p=w / w.sum())
    return s
def est(sa, sb, N, paired, n):
    R = sa.shape[0]
    pa = np.stack([np.bincount(x, minlength=K) for x in sa]) / n
    pb = np.stack([np.bincount(x, minlength=K) for x in sb]) / n
    d = H(pb) - H(pa)
    ga = -(np.log(np.maximum(pa, 1e-6)) + 1); gb = -(np.log(np.maximum(pb, 1e-6)) + 1)
    va = np.take_along_axis(ga, sa, 1); vb = np.take_along_axis(gb, sb, 1)
    var = np.var(vb - va, 1, ddof=1) if paired else np.var(va, 1, ddof=1) + np.var(vb, 1, ddof=1)
    return d, np.sqrt(np.maximum(var * (1 - n / N) / n, 0))
n = 128; res = {}
for eps in [0.0, 0.01, 0.02, 0.05]:
    rng = np.random.default_rng(20261027)
    acc = {d: dict(mse=[], cov=[], rep=0, wrong=0, R=0) for d in ['paired', 'independent']}
    for u in draws:
        if not u['primary']: continue
        r = recs[u['landscape_id']]; z = np.load(os.path.join(root, r['path']))
        lab = lookup[z['broad'][:, np.asarray(r['valid_indices'], int)]]
        ya = lab[u['year_a'] - 2021]; yb = lab[u['year_b'] - 2021]; N = len(ya)
        qa = np.bincount(ya, minlength=K) / N; qb = np.bincount(yb, minlength=k) / N if False else np.bincount(yb, minlength=K) / N
        truth = H(qb) - H(qa); st = int(np.sign(truth)) if abs(truth) > 1e-10 else 0
        dd = np.load(os.path.join(root, u['path'])); A = dd['a'][:, :n].astype(int); B = dd['b'][:, :n].astype(int)
        for design, IB in [('paired', A), ('independent', B)]:
            sa = noisy(ya[A], eps, qa, rng); sb = noisy(yb[IB], eps, qb, rng)
            d, se = est(sa, sb, N, design == 'paired', n)
            lo, hi = d - 1.96 * se, d + 1.96 * se
            cov = (lo <= truth + 1e-10) & (hi >= truth - 1e-10)
            di = np.where(lo > 1e-10, 1, np.where(hi < -1e-10, -1, 0))
            a = acc[design]; a['mse'].append(np.mean((d - truth) ** 2)); a['cov'].append(cov.mean())
            a['rep'] += int((di != 0).sum()); a['wrong'] += int(((di != 0) & (di != st)).sum()); a['R'] += len(d)
    out = {}
    for design, a in acc.items():
        out[design] = dict(rmse=float(np.sqrt(np.mean(a['mse']))), coverage=float(np.mean(a['cov'])),
                           report_rate=a['rep'] / a['R'], wrong_rate=a['wrong'] / a['R'], reports=a['rep'], wrong=a['wrong'])
    out['mse_ratio'] = (out['paired']['rmse'] / out['independent']['rmse']) ** 2
    res[str(eps)] = out
    print(eps, json.dumps(out), flush=True)
json.dump(res, open(outp, 'w'), indent=1)
