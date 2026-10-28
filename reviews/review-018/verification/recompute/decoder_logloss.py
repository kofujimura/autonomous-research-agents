"""Reviewer's exploratory check: window-level paired log-loss difference of saved decoder probabilities
(hybrid or embedding-only minus hydrological decoder), with window bootstrap. Uses saved outputs only."""
import csv, sys, glob, os, math, collections
import numpy as np
src = sys.argv[1]
region = {}
for p in glob.glob(os.path.join(src, 'analysis/main-corrected/r*/pools.csv')):
    for r in csv.DictReader(open(p)):
        region[(r['rotation'], r['query_id'])] = r['region']
ll = collections.defaultdict(dict)
for r in csv.DictReader(open(os.path.join(src, 'analysis/report-data/decoder-query-probabilities.csv'))):
    p = [float(r['pA']), float(r['pC']), float(r['pF'])][int(r['y'])]
    ll[r['method']][(r['rotation'], r['objectid'])] = -math.log(max(p, 1e-15))
keys = list(ll['hydro_decoder'])
miss = [k for k in keys if k not in region]
print('queries', len(keys), 'without region', len(miss))
regs = sorted({region[k] for k in keys if k in region})
rng = np.random.default_rng(18018)
idx = rng.integers(0, len(regs), (10000, len(regs)))
for m in ['aef_decoder', 'tessera_decoder', 'hydro_aef_decoder', 'hydro_tessera_decoder']:
    d = collections.defaultdict(list)
    for k in keys:
        d[region[k]].append(ll[m][k] - ll['hydro_decoder'][k])
    w = np.array([np.mean(d[g]) for g in regs])
    pooled = np.mean([x for g in regs for x in d[g]])
    lo, hi = np.quantile(w[idx].mean(axis=1), [.025, .975])
    print(f'{m:22s} pooled dLL {pooled:+.4f}; window-mean dLL {w.mean():+.4f} [{lo:+.4f}, {hi:+.4f}]; windows better {int((w<0).sum())}/{len(w)}')
