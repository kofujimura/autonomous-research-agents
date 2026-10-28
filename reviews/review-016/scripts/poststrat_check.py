#!/usr/bin/env python3
"""Reviewer point-accuracy check (not part of the submitted study): post-stratified estimator by
hard predicted map class (Olofsson-style stratified area estimator applied as post-stratification to
the saved SRS draws). Empty sampled strata are collapsed into the overall sample proportion.
Primary broad units, n=128, frozen logistic predictions. RMSE only; no intervals.
Usage: poststrat_check.py <source_root> <model_dir_rel> <out_json>"""
import json, sys, os
import numpy as np
root, model, outp = sys.argv[1], sys.argv[2], sys.argv[3]
fit = json.load(open(os.path.join(root, model, 'fit.json')))
draws = json.load(open(os.path.join(root, 'data/audit-draws-main/manifest.json')))['draws']
K = len(fit['class_names']); files = {r['landscape_id']: r for r in fit['prediction_files']}
def H(p):
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.where(p > 0, -p * np.log(np.where(p > 0, p, 1)), 0).sum(-1)
def poststrat(y, strata, idx):
    N = len(y); W = np.bincount(strata, minlength=K) / N
    out = np.zeros((idx.shape[0], K))
    for r in range(idx.shape[0]):
        s = strata[idx[r]]; yy = y[idx[r]]; overall = np.bincount(yy, minlength=K) / len(yy)
        est = np.zeros(K)
        for h in np.nonzero(W)[0]:
            m = s == h
            est += W[h] * (np.bincount(yy[m], minlength=K) / m.sum() if m.any() else overall)
        out[r] = est
    return out
n = 128; res = {}
for design in ['paired', 'independent']:
    mse_ps = []; mse_dir = []
    for u in draws:
        if not u['primary']: continue
        e = files[u['landscape_id']]; z = np.load(os.path.join(root, e['path']))
        P, Y = z['probabilities'], z['labels']
        a, b = u['year_a'] - 2021, u['year_b'] - 2021
        ya, yb = Y[a].astype(int), Y[b].astype(int); sa_, sb_ = P[a].argmax(1), P[b].argmax(1)
        truth = H(np.bincount(yb, minlength=K) / len(yb)) - H(np.bincount(ya, minlength=K) / len(ya))
        d = np.load(os.path.join(root, u['path'])); A = d['a'][:, :n].astype(int); B = d['b'][:, :n].astype(int)
        IB = A if design == 'paired' else B
        est = H(poststrat(yb, sb_, IB)) - H(poststrat(ya, sa_, A))
        dr = H(np.stack([np.bincount(yb[i], minlength=K) for i in IB]) / n) - H(np.stack([np.bincount(ya[i], minlength=K) for i in A]) / n)
        mse_ps.append(np.mean((est - truth) ** 2)); mse_dir.append(np.mean((dr - truth) ** 2))
    res[design] = dict(poststrat_rmse=float(np.sqrt(np.mean(mse_ps))), direct_rmse=float(np.sqrt(np.mean(mse_dir))))
    print(model, design, res[design], flush=True)
json.dump(res, open(outp, 'w'), indent=1)
