"""Reviewer's descriptive synthesis of archived half-coverage contrasts: real embedding augmentation vs
null perturbations (constant, independent scalar, within-stratum permuted embeddings), by learner setting.
Inputs: perturbation_table.json (from perturbation_table.py). No refitting."""
import json, statistics as S
t = json.load(open('perturbation_table.json'))
def diff(c, m, k):  # k=0 window-mean, 1 pooled
    d = t[c]; return d[m][k] - d['hydro_pair'][k]
groups = {
 'forest 0.7 real AEF': [('primary-corrected-summary','pair_aef'),('controls/seed-1000-summary','pair_aef'),('controls/seed-2000-summary','pair_aef')],
 'forest 0.7 real TESSERA': [('primary-corrected-summary','pair_tessera'),('controls/seed-1000-summary','pair_tessera'),('controls/seed-2000-summary','pair_tessera')],
 'forest 0.7 null (constant x3 seeds, scalar x3, permuted AEF x3, permuted TESSERA x3)': [(f'controls/constant-seed-{s}-summary','pair_constant') for s in (0,1000,2000)] + [(f'controls/noise-{i}-summary','pair_noise') for i in range(3)] + [(f'controls/permute-{i}-summary','pair_aef') for i in range(3)] + [(f'controls/permute-{i}-summary','pair_tessera') for i in range(3)],
 'all-feature forest real AEF': [(f'controls/all-corrected-seed-{s}-summary','pair_aef') for s in (0,1000,2000)],
 'all-feature forest real TESSERA': [(f'controls/all-corrected-seed-{s}-summary','pair_tessera') for s in (0,1000,2000)],
 'all-feature forest null (scalar x3, constant x1)': [(f'controls/noise-all-{i}-summary','pair_noise') for i in range(3)] + [('controls/constant-all-summary','pair_constant')],
 'boosted trees real AEF / TESSERA': [('controls/hgb-corrected-summary','pair_aef'),('controls/hgb-corrected-summary','pair_tessera')],
}
for g, lst in groups.items():
    wm = [diff(c, m, 0) for c, m in lst]; po = [diff(c, m, 1) for c, m in lst]
    print(f'{g}\n  window-mean pp: ' + ', '.join(f'{x:+.2f}' for x in wm) + f'  (mean {S.mean(wm):+.2f}, range {min(wm):+.2f}..{max(wm):+.2f})')
    print('  pooled pp:      ' + ', '.join(f'{x:+.2f}' for x in po) + f'  (mean {S.mean(po):+.2f}, range {min(po):+.2f}..{max(po):+.2f})')
print('Seed variation of hydro_pair baseline (forest 0.7): window-mean', [t[c]['hydro_pair'][0] for c in ('primary-corrected-summary','controls/seed-1000-summary','controls/seed-2000-summary')], 'pooled', [t[c]['hydro_pair'][1] for c in ('primary-corrected-summary','controls/seed-1000-summary','controls/seed-2000-summary')])
print('Seed variation of hydro_pair baseline (all-feature forest): window-mean', [t[f'controls/all-corrected-seed-{s}-summary']['hydro_pair'][0] for s in (0,1000,2000)], 'pooled', [t[f'controls/all-corrected-seed-{s}-summary']['hydro_pair'][1] for s in (0,1000,2000)])
