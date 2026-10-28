import pandas as pd, numpy as np, json, sys
d = pd.read_csv(sys.argv[1])
d = d[(d.taxonomy == 'broad') & (d.n == 128)] if 'taxonomy' in d else d
uid = 'unit_id' if 'unit_id' in d else d.columns[0]
d['landscape'] = d[uid].str.rsplit('-', n=2).str[0]
p = d[d.design == 'paired'].set_index(uid); i = d[d.design == 'independent'].set_index(uid)
units = p.index
L = {}
for u in units: L.setdefault(p.loc[u, 'landscape'], []).append(u)
land = sorted(L); rng = np.random.default_rng(2)
def ratio(ls):
    us = [u for l in ls for u in L[l]]
    return p.loc[us, 'mse'].mean() / i.loc[us, 'mse'].mean()
bs = [ratio(rng.choice(land, len(land), replace=True)) for _ in range(5000)]
per = (p['mse'] / i.loc[p.index, 'mse'])
res = dict(landscapes=len(land), units=len(units), ratio=float(ratio(land)), ci95=np.percentile(bs, [2.5, 97.5]).tolist(),
           per_unit_min=float(per.min()), per_unit_max=float(per.max()), units_ratio_above_1=int((per > 1).sum()))
print(json.dumps(res)); json.dump(res, open(sys.argv[2], 'w'), indent=1)
