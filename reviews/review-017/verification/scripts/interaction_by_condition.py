"""Reviewer check: point estimates of H1 interaction by evaluation condition from a scores.csv (read-only)."""
import csv, sys, statistics as st
from collections import defaultdict
path = sys.argv[1]
rows = list(csv.DictReader(open(path)))
acc = defaultdict(list)
for r in rows:
    acc[(r['scope'], r['decoder'], r['budget'], r['version'], r['condition'] + '@tol' + r['boundary_tolerance_m'], r['representation'], r['policy'])].append(r)
def m(key, field='small_macro_recovery_50'):
    v = [float(x[field]) for x in acc.get(key, []) if x[field] != '']
    return (st.mean(v), len(v)) if v else (None, 0)
print('scope decoder budget version condition | aef_area aef_obj opt_area opt_obj | interaction | FPRs(aef_area,aef_obj,opt_area,opt_obj) | n_seeds')
seen = sorted({k[:5] for k in acc})
for s in seen:
    vals = [m(s + (rep, pol)) for rep, pol in [('aef','area'),('aef','object'),('optical','area'),('optical','object')]]
    if any(v[0] is None for v in vals):
        continue
    fprs = [m(s + (rep, pol), 'upland_fpr')[0] for rep, pol in [('aef','area'),('aef','object'),('optical','area'),('optical','object')]]
    inter = (vals[1][0]-vals[0][0]) - (vals[3][0]-vals[2][0])
    print(' '.join(s), '|', ' '.join(f'{v[0]*100:.1f}' for v in vals), '|', f'{inter*100:.1f}', '|', ' '.join(f'{f*100:.1f}' for f in fprs), '|', [v[1] for v in vals])
