"""Reviewer check (read-only on inputs): compare each claim's `expected` in claims.jsonl with regenerated outputs.
usage: compare_claims.py <claims.jsonl> <verify_out_dir> <report.json>"""
import json, sys, csv, statistics as st, math
claims_path, out, report_path = sys.argv[1:4]
summary = json.load(open(f'{out}/analysis/summary.json'))
robust = json.load(open(f'{out}/analysis/robustness/summary.json'))['families']
align = json.load(open(f'{out}/alignment-stress/summary.json'))
scores = list(csv.DictReader(open(f'{out}/analysis/scores.csv')))
def secondary(scope, decoder, budget=2000):
    for e in summary['secondary_condition_contrasts']:
        if e['scope'] == scope and e['decoder'] == decoder and int(e['budget']) == budget:
            return e['contrasts']
def arm_means(condition, fields):
    res = {}
    for rep in ('aef', 'optical'):
        for pol, name in (('area', 'area'), ('object', 'object')):
            xs = [r for r in scores if r['scope'] == 'within' and r['decoder'] == 'rf' and r['budget'] == '2000' and r['version'] == 'raw'
                  and r['condition'] == condition and r['boundary_tolerance_m'] == '0' and r['representation'] == rep and r['policy'] == pol]
            res[f'{rep}_{name}'] = {f: st.mean(float(x[f]) for x in xs) for f in fields}
    return res
def compare(a, e, p=''):
    fails, n = [], 0
    if isinstance(e, dict):
        for k, v in e.items():
            if not isinstance(a, dict) or k not in a:
                fails.append(p + '/' + k + ': missing'); continue
            f, m = compare(a[k], v, p + '/' + k); fails += f; n += m
    elif isinstance(e, list):
        if not isinstance(a, list) or len(a) != len(e): return [p + ': length'], 1
        for i, (x, y) in enumerate(zip(a, e)):
            f, m = compare(x, y, p + f'/{i}'); fails += f; n += m
    elif isinstance(e, (int, float)) and not isinstance(e, bool):
        n += 1
        if a is None or not math.isclose(a, e, rel_tol=0, abs_tol=1e-12): fails.append(f'{p}: {a} != {e}')
    else:
        n += 1
        if a != e: fails.append(f'{p}: {a!r} != {e!r}')
    return fails, n
report = {}
for line in open(claims_path):
    c = json.loads(line); cid = c['claim_id']; e = c['expected']
    if cid in ('C01', 'C02'): actual = summary
    elif cid in ('C08', 'C09'): actual = summary['primary_contrasts']
    elif cid == 'C03': actual = arm_means('validation_0.05', ['small_macro_recovery_50', 'upland_fpr'])
    elif cid == 'C10': actual = arm_means('standardized_0.05', ['producer_accuracy', 'user_accuracy', 'iou', 'small_macro_recovery_50'])
    elif cid == 'C04': actual = {k: secondary(k, 'rf')['H1_interaction'] for k in e}
    elif cid == 'C05': actual = align
    elif cid == 'C06': actual = robust
    elif cid == 'C07': actual = secondary('within', 'rf_noboot')
    else: actual = None
    fails, n = compare(actual, e) if actual is not None else (['no rule'], 0)
    report[cid] = {'compared_leaf_values': n, 'mismatches': len(fails), 'result': 'match' if not fails and n else 'mismatch', 'details': fails[:20]}
    print(cid, report[cid]['result'], 'leaves', n, 'mismatches', len(fails), fails[:3])
json.dump(report, open(report_path, 'w'), indent=1)
