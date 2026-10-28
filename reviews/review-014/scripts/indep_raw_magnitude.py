# Reviewer-written: recompute cosine change magnitude 1 - a.b for test targets directly from raw arrays,
# using the official AEF dequantization, and compare with saved cosine_change scores (paired, centre, 14014, global).
import numpy as np, pandas as pd, sys, os
src = sys.argv[1]
p = pd.read_parquet(os.path.join(src, 'analysis/main-v1/predictions.parquet'))
q = p[(p.availability_mode=='paired')&(p.support=='centre')&(p.seed==14014)&(p.reference_mode=='global')&(p.method=='cosine_change')]
t = pd.read_csv(os.path.join(src, 'data/prepared/targets.csv'))
print('targets columns:', list(t.columns)[:20])
def vec(model, pid, year):
    z = np.load(os.path.join(src, f'data/embeddings/{model}/{pid}-{year}.npz'), allow_pickle=False)['raw']
    c = z[1, 1].astype(np.float64)
    if model == 'aef':
        if (z[1,1] == -128).any(): return None
        c = np.sign(c) * (c / 127.5) ** 2
    if not np.isfinite(c).all() or np.linalg.norm(c) == 0: return None
    return c / np.linalg.norm(c)
rng = np.random.default_rng(0)
out = []
for model in ['aef', 'tessera']:
    g = q[q.model == model].drop_duplicates('point_id')
    samp = g.sample(n=min(60, len(g)), random_state=1)
    for r in samp.itertuples():
        a = vec(model, r.point_id, r.before_year); b = vec(model, r.point_id, r.before_year + 1)
        if a is None or b is None: out.append((model, r.point_id, np.nan, r.score)); continue
        out.append((model, r.point_id, 1 - a @ b, r.score))
o = pd.DataFrame(out, columns=['model', 'point_id', 'reviewer', 'saved'])
o['absdiff'] = (o.reviewer - o.saved).abs()
print(o.groupby('model').absdiff.describe())
o.to_csv(sys.argv[2], index=False)
