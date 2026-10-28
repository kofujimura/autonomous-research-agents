"""Collect half-coverage window-mean and pooled risks for seed, null-feature and permutation controls
from archived summaries (no refitting), to compare the primary increment with pipeline perturbations."""
import csv, sys, os, json
src = sys.argv[1]
conds = ['primary-corrected-summary', 'primary-summary', 'controls/seed-1000-summary', 'controls/seed-2000-summary',
         'controls/constant-seed-0-summary', 'controls/constant-seed-1000-summary', 'controls/constant-seed-2000-summary',
         'controls/noise-0-summary', 'controls/noise-1-summary', 'controls/noise-2-summary',
         'controls/permute-0-summary', 'controls/permute-1-summary', 'controls/permute-2-summary',
         'controls/all-corrected-seed-0-summary', 'controls/all-corrected-seed-1000-summary', 'controls/all-corrected-seed-2000-summary',
         'controls/noise-all-0-summary', 'controls/noise-all-1-summary', 'controls/noise-all-2-summary',
         'controls/constant-all-summary', 'controls/hgb-corrected-summary', 'controls/constant-hgb-summary']
out = {}
M = ['hydro_pair', 'hydro_decoder', 'pair_aef', 'pair_tessera', 'pair_both', 'pair_noise', 'pair_constant']
for c in conds:
    p = os.path.join(src, 'analysis', c, 'metrics.csv')
    if not os.path.exists(p):
        out[c] = 'missing'; continue
    d = {}
    for r in csv.DictReader(open(p)):
        if abs(float(r['coverage']) - 0.5) < 1e-9 and r['method'] in M:
            d[r['method']] = (100 * float(r['macro_risk']), 100 * float(r['pooled_risk']))
    out[c] = d
json.dump(out, open(sys.argv[2], 'w'), indent=1)
print(f"{'condition':42s} " + ' '.join(f'{m:>15s}' for m in M))
for c, d in out.items():
    if d == 'missing': print(c, 'missing'); continue
    print(f'{c:42s} ' + ' '.join((f'{d[m][0]:6.2f}/{d[m][1]:6.2f}  ' if m in d else ' ' * 15) for m in M))
print('\nDifferences vs same-condition hydro_pair (window-mean pp / pooled pp):')
for c, d in out.items():
    if d == 'missing' or 'hydro_pair' not in d: continue
    s = []
    for m in ['pair_aef', 'pair_tessera', 'pair_both', 'pair_noise', 'pair_constant']:
        if m in d: s.append(f'{m}: {d[m][0]-d["hydro_pair"][0]:+.2f}/{d[m][1]-d["hydro_pair"][1]:+.2f}')
    print(f'{c:42s} ' + '; '.join(s))
