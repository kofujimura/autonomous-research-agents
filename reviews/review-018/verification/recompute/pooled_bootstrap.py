"""Reviewer's descriptive check: window-bootstrap (10,000, seed 18018) interval for pooled-risk differences,
resampling windows and pooling errors/retained counts. Input: primary_recompute.json."""
import json, numpy as np
r = json.load(open('primary_recompute.json')); pw = r['per_window']; regs = sorted(pw['hydro_pair'])
def arr(m):
    n = np.array([pw[m][g][0] for g in regs], float); e = np.array([round(pw[m][g][0] * pw[m][g][1]) for g in regs], float); return n, e
rng = np.random.default_rng(18018); idx = rng.integers(0, len(regs), (10000, len(regs)))
for m in ['pair_aef', 'pair_tessera', 'pair_both']:
    for b in ['hydro_pair', 'hydro_decoder']:
        nm, em = arr(m); nb, eb = arr(b)
        point = em.sum() / nm.sum() - eb.sum() / nb.sum()
        bs = em[idx].sum(1) / nm[idx].sum(1) - eb[idx].sum(1) / nb[idx].sum(1)
        lo, hi = np.quantile(bs, [.025, .975])
        print(f'{m}|{b}: pooled diff {100*point:+.2f} pp [{100*lo:+.2f}, {100*hi:+.2f}]')
# leave-R07-out and leave-R07+R08-out window means
for m in ['pair_aef', 'pair_tessera']:
    for drop in (['R07'], ['R07', 'R08']):
        d = [pw[m][g][1] - pw['hydro_pair'][g][1] for g in regs if g not in drop]
        print(f'{m}|hydro_pair window-mean without {drop}: {100*np.mean(d):+.2f} pp')
