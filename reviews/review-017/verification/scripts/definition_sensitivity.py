"""Reviewer check (read-only): H1 interaction and component gains by coverage definition (any/50/75),
for the original split and pooled over the original + 3 rotation splits (counts summed within region, then equal region weight),
from regional-scores.csv. Condition standardized_0.05, tolerance 0, raw, RF, budget 2000. Point estimates only."""
import csv, sys, statistics as st
from collections import defaultdict
rows = [r for r in csv.DictReader(open(sys.argv[1]))
        if r['decoder'] == 'rf' and r['budget'] == '2000' and r['version'] == 'raw' and r['condition'] == 'standardized_0.05'
        and r['boundary_tolerance_m'] == '0' and r['size_bin'] == 'small' and r['policy'] in ('area', 'object')
        and r['representation'] in ('aef', 'optical')]
def est(scopes, target):
    num = defaultdict(float); den = defaultdict(float)
    for r in rows:
        if r['scope'] in scopes and r['coverage_target'] == target:
            k = (r['representation'], r['policy'], r['seed'], r['region_id'])
            num[k] += float(r['recovered_patches']); den[k] += float(r['scored_patch_count'])
    arm = {}
    for rep in ('aef', 'optical'):
        for pol in ('area', 'object'):
            seeds = sorted({k[2] for k in num if k[0] == rep and k[1] == pol})
            vals = []
            for s in seeds:
                regs = sorted({k[3] for k in num if k[:3] == (rep, pol, s)})
                vals.append(st.mean(num[(rep, pol, s, g)] / den[(rep, pol, s, g)] for g in regs if den[(rep, pol, s, g)] > 0))
            arm[rep, pol] = st.mean(vals) * 100
    ga = arm['aef', 'object'] - arm['aef', 'area']; go = arm['optical', 'object'] - arm['optical', 'area']
    return arm, ga, go, ga - go
targets = sorted({r['coverage_target'] for r in rows})
for label, scopes in [('original split', {'within'}), ('rotation1', {'rotation1'}), ('rotation2', {'rotation2'}), ('rotation3', {'rotation3'}),
                      ('pooled 4 splits', {'within', 'rotation1', 'rotation2', 'rotation3'}), ('pooled 3 new rotations', {'rotation1', 'rotation2', 'rotation3'})]:
    for t in targets:
        arm, ga, go, it = est(scopes, t)
        print(f"{label:24s} target={t:5s} aef {arm['aef','area']:.1f}->{arm['aef','object']:.1f} (gain {ga:.1f}) | optical {arm['optical','area']:.1f}->{arm['optical','object']:.1f} (gain {go:.1f}) | interaction {it:.1f}")
