"""Compare claims.jsonl expected values (C01-C08 main claims, plus C17, C19) with the reviewer's replayed outputs.
Usage: python -I claim_check.py CLAIMS_JSONL REPLAY_DIR"""
import sys, json, pandas as pd
claims = {json.loads(l)['claim_id']: json.loads(l) for l in open(sys.argv[1])}
R = sys.argv[2]; TOL = 1e-7; out = {}
def close(a, b): return abs(float(a) - float(b)) <= TOL if isinstance(a, (int, float)) and not isinstance(a, bool) else a == b
def check(cid, pairs):
    bad = [(k, e, g) for k, e, g in pairs if not close(e, g)]
    out[cid] = {'compared': len(pairs), 'mismatches': bad}
w = pd.read_csv(f'{R}/primary/width-summary.csv')
base = w[(w.n_sites == 12) & (w.model == 'all') & (w.lead.astype(str) == 'all') & (w.geometry == 'all')]
inf = base[base.stratum == 'informative'].iloc[0]; al = base[base.stratum == 'all'].iloc[0]
e = claims['C01']['expected']
check('C01', [('informative_cases', e['informative_cases'], int(inf.cases)), ('matched_dates', e['matched_dates'], int(inf.dates))] +
      [(f'{k}_width', v, inf[f'{k}_width']) for k, v in e['mean_widths'].items()])
e = claims['C02']['expected']
check('C02', [('all_cases', e['all_cases'], int(al.cases)), ('q_zero', e['q_zero'], int(al.q_zero)), ('q_one', e['q_one'], int(al.q_one)),
              ('at_most_two_uncertain', e['at_most_two_uncertain'], int(al.at_most_two_uncertain)),
              ('pair_identified_all', e['pair_identified_all'], int(al.pair_exact_count)), ('pair_identified_informative', e['pair_identified_informative'], int(inf.pair_exact_count))])
check('C03', [('share', claims['C03']['expected']['aggregate_reduction_share_ratio_of_sums'], inf.aggregate_reduction_share)])
d = pd.read_csv(f'{R}/primary/decision-summary.csv'); d = d[(d.model == 'all') & (d.stratum == 'informative_near_boundary')]
p = []
for r in claims['C04']['expected']:
    g = d[abs(d.cost_ratio - r['cost_ratio']) < 1e-9].iloc[0]
    for k in ('cases', 'ties', 'oracle_act_strict', 'oracle_skip_strict', 'marginal_certified', 'aggregate_certified', 'pair_certified'):
        p.append((f"{r['cost_ratio']}:{k}", r[k], g[k]))
check('C04', p)
rc = pd.read_csv(f'{R}/primary/reconstruction-summary.csv'); rc = rc[(rc.availability == 'historical_matched') & (rc.stratum == 'informative')]
p = []
for r in claims['C05']['expected']:
    g = rc[rc.method == r['method']].iloc[0]
    for k in ('cases', 'dates', 'mean_absolute_error'): p.append((f"{r['method']}:{k}", r[k], g[k]))
check('C05', p)
for cid, f, key in [('C06', 'sensitivity/integer-summary.csv', 'mode'), ('C07', 'sensitivity/epsilon-summary.csv', 'epsilon')]:
    t = pd.read_csv(f'{R}/{f}'); p = []
    for r in claims[cid]['expected']:
        g = t[t[key] == r[key]].iloc[0] if key == 'mode' else t[abs(t[key] - r[key]) < 1e-12].iloc[0]
        for k, v in r.items():
            if k != key: p.append((f'{r[key]}:{k}', v, g[k]))
    check(cid, p)
t = pd.read_csv(f'{R}/sensitivity/member-summary.csv'); p = []
for r in claims['C08']['expected']:
    g = t[(t.members == r['members']) & (t.stratum == r['stratum'])].iloc[0]
    for k, v in r.items():
        if k not in ('members', 'stratum'): p.append((f"{r['members']}/{r['stratum']}:{k}", v, g[k]))
check('C08', p)
t = pd.read_csv(f'{R}/controlled-moments/width-summary.csv'); p = []
for r in claims['C17']['expected']:
    g = t[(t.condition == r['condition']) & (abs(t.epsilon - r['epsilon']) < 1e-12)].iloc[0]
    for k, v in r.items():
        if k not in ('condition', 'epsilon') and k in g: p.append((f"{r['condition']}/{r['epsilon']}:{k}", v, g[k]))
check('C17', p)
print(json.dumps(out, indent=1, default=str))
