# Reviewer exploratory check (not in the paper): drift of the reference-forest centroid across years,
# and year-to-year change of baseline-stable tree cohort plots, per product, from raw arrays.
import numpy as np, pandas as pd, os, sys, itertools
src = sys.argv[1]
ref = pd.read_csv(os.path.join(src, 'data/prepared/references.csv'))
def vec(model, pid, year):
    f = os.path.join(src, f'data/embeddings/{model}/{pid}-{year}.npz')
    if not os.path.exists(f): return None
    z = np.load(f, allow_pickle=False)['raw'][1, 1]
    if model == 'aef':
        if (z == -128).any(): return None
        c = np.sign(z.astype(float)) * (z.astype(float) / 127.5) ** 2
    else:
        c = z.astype(float)
    if not np.isfinite(c).all() or np.linalg.norm(c) == 0: return None
    return c / np.linalg.norm(c)
years = range(2017, 2024)
for model in ['aef', 'tessera']:
    V = {(r.point_id, y): vec(model, r.point_id, y) for r in ref.itertuples() for y in years}
    R = ref[ref.role == 'R'].point_id.tolist()
    # common plots valid in all years 2017-2021 (and separately to 2023)
    for last in (2021, 2023):
        ys = list(range(2017, last + 1))
        common = [p for p in R if all(V[(p, y)] is not None for y in ys)]
        if len(common) < 8: print(model, 'to', last, 'common R plots', len(common), '(too few)'); continue
        cent = {y: np.mean([V[(p, y)] for p in common], axis=0) for y in ys}
        cent = {y: v / np.linalg.norm(v) for y, v in cent.items()}
        adj = [1 - cent[y] @ cent[y + 1] for y in ys[:-1]]
        frm = [1 - cent[ys[0]] @ cent[y] for y in ys[1:]]
        print(f'{model} R centroid (n={len(common)} plots valid {ys[0]}-{last}): 1-cos adjacent years', ' '.join(f'{y}-{y+1}:{d:.4f}' for y, d in zip(ys, adj)))
        print(f'{model}   1-cos from {ys[0]}:', ' '.join(f'{y}:{d:.4f}' for y, d in zip(ys[1:], frm)))
    # per-plot adjacent-year change of all R and C cohort plots
    allp = ref.point_id.tolist()
    for y in range(2017, 2023):
        d = [1 - V[(p, y)] @ V[(p, y + 1)] for p in allp if V[(p, y)] is not None and V[(p, y + 1)] is not None]
        if d: print(f'{model}   cohort plots {y}-{y+1}: n={len(d)} median 1-cos={np.median(d):.4f} p90={np.quantile(d,.9):.4f}')
