"""Reviewer's independent re-implementation (not derived from the research side's bounds.py).
For selected primary queries: thresholds raw member temperatures, builds the full 2^n binary-state LP
(no pruning), and computes min/max P(S>=k) under (marginal), (marginal + sum_{i<j} b_ij), (marginal + all b_ij).
Also recomputes q, uncertain-site counts and the informative flag from raw arrays.
Usage: python -I indep_bounds.py RUN_ROOT CASES_CSV OUT_CSV MODE [N_SAMPLE SEED]
MODE: composition (all n=12 matched cases, no LP) | sample (stratified random) | informative (all informative)"""
import sys, json, itertools
import numpy as np, pandas as pd
from scipy.optimize import linprog
root, cases_csv, out_csv, mode = sys.argv[1:5]
nsamp = int(sys.argv[5]) if len(sys.argv) > 5 else 0
seed = int(sys.argv[6]) if len(sys.argv) > 6 else 1
c = pd.read_csv(cases_csv, dtype={'date': str})
c = c[(c.n == 12) & (c.member_count == 50) & (c.matched_date == True)].copy()
portfolios = None
cache = {}
def arr(date, model, lead):
    key = (date, model, lead)
    if key not in cache:
        z = np.load(f"{root}/data/weather/{date}/{model}/{lead}/temperatures.npz", allow_pickle=False)
        P = json.loads(str(z['portfolios_json']))
        cache[key] = (z['kelvin'], [(d['center'], d['geometry']) for d in P])
    return cache[key]
n = 12
states = np.array(list(itertools.product([0, 1], repeat=n)), dtype=float)  # 4096 x 12
pc = states.sum(1)
pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
pair_rows = np.array([states[:, i] * states[:, j] for i, j in pairs])
agg_row = pc * (pc - 1) / 2
ones = np.ones((1, len(states)))
def bounds(obj, Aeq, beq):
    out = []
    for sgn in (1, -1):
        r = linprog(sgn * obj, A_eq=Aeq, b_eq=beq, bounds=(0, None), method='highs')
        if r.status != 0: return (np.nan, np.nan, r.status)
        out.append(sgn * r.fun)
    return (out[0], out[1], 0)
rows = []
def case_inputs(r):
    K, P = arr(r.date, r.model, int(r.lead))
    pi = P.index((r.center, r.geometry))
    X = (K[:, pi, :] >= r.threshold_c + 273.15).astype(float)  # 50 x 12
    return X
if mode == 'composition':
    sel = c
elif mode == 'sample':
    rng = np.random.default_rng(seed)
    inf = c[c.informative == 1]; non = c[c.informative == 0]
    sel = pd.concat([inf.sample(nsamp // 2, random_state=seed), non.sample(nsamp - nsamp // 2, random_state=seed + 1)])
elif mode == 'informative':
    sel = c[c.informative == 1]
for r in sel.itertuples():
    X = case_inputs(r)
    p = X.mean(0); S = X.sum(1); k = int(r.k)
    q = float((S >= k).mean())
    unc = int(((p > 0) & (p < 1)).sum())
    inform = int(unc >= 4 and 0.1 <= q <= 0.9)
    rec = dict(case_key=r.case_key, q_rev=q, uncertain_rev=unc, informative_rev=inform)
    if mode != 'composition':
        b = np.array([(X[:, i] * X[:, j]).mean() for i, j in pairs])
        obj = (pc >= k).astype(float)
        A_m = np.vstack([ones, states.T]); b_m = np.concatenate([[1], p])
        mL, mU, s1 = bounds(obj, A_m, b_m)
        aL, aU, s2 = bounds(obj, np.vstack([A_m, agg_row[None, :]]), np.concatenate([b_m, [b.sum()]]))
        pL, pU, s3 = bounds(obj, np.vstack([A_m, pair_rows]), np.concatenate([b_m, b]))
        # independence (Poisson-binomial)
        dist = np.array([1.0])
        for pj in p: dist = np.convolve(dist, [1 - pj, pj])
        rec.update(marg_L=mL, marg_U=mU, agg_L=aL, agg_U=aU, pair_L=pL, pair_U=pU, status=max(s1, s2, s3), indep_q=float(dist[k:].sum()))
    rows.append(rec)
out = pd.DataFrame(rows)
m = sel[['case_key', 'q', 'uncertain_sites', 'informative', 'marginal_lower', 'marginal_upper', 'aggregate_lower', 'aggregate_upper', 'pair_lower', 'pair_upper', 'independent_q']].merge(out, on='case_key')
m.to_csv(out_csv, index=False)
rep = {'mode': mode, 'cases': len(m),
       'q_maxabs': float((m.q - m.q_rev).abs().max()),
       'uncertain_mismatch': int((m.uncertain_sites != m.uncertain_rev).sum()),
       'informative_mismatch': int((m.informative != m.informative_rev).sum()),
       'informative_count_rev': int(m.informative_rev.sum())}
if mode != 'composition':
    for a, bcol in [('marginal_lower', 'marg_L'), ('marginal_upper', 'marg_U'), ('aggregate_lower', 'agg_L'), ('aggregate_upper', 'agg_U'), ('pair_lower', 'pair_L'), ('pair_upper', 'pair_U'), ('independent_q', 'indep_q')]:
        rep[a + '_maxabs'] = float((m[a] - m[bcol]).abs().max())
    rep['lp_nonoptimal'] = int((m.status != 0).sum())
    sub = m
    for lab, L, U in [('marginal', 'marg_L', 'marg_U'), ('aggregate', 'agg_L', 'agg_U'), ('pair', 'pair_L', 'pair_U')]:
        rep['mean_width_rev_' + lab] = float((sub[U] - sub[L]).mean())
    rep['mean_width_sub_reported'] = {lab: float((sub[f'{lab}_upper'] - sub[f'{lab}_lower']).mean()) for lab in ('marginal', 'aggregate', 'pair')}
print(json.dumps(rep, indent=1))
