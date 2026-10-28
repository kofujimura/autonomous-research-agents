"""Reviewer descriptive analyses from submitted results/primary/cases.csv (no new solves).
Usage: python -I reviewer_strata.py SUBMITTED_COPY"""
import sys, pandas as pd
root = sys.argv[1]
c = pd.read_csv(f'{root}/results/primary/cases.csv', dtype={'date': str})
c = c[(c.n == 12) & (c.member_count == 50) & (c.matched_date == True)]
i = c[c.informative == 1].copy(); tol = 1e-7
i['ident'] = i.pair_width <= tol
print('## Table 1 recomputation')
print('all', len(c), int((c.q == 0).sum()), int((c.q == 1).sum()), int((c.uncertain_sites <= 2).sum()), int((c.pair_width <= tol).sum()),
      round(c.marginal_width.mean(), 4), round(c.aggregate_width.mean(), 4), round(c.pair_width.mean(), 4))
print('informative', len(i), round(i.marginal_width.mean(), 4), round(i.aggregate_width.mean(), 4), round(i.pair_width.mean(), 4), int(i.ident.sum()),
      'share', round((i.marginal_width - i.aggregate_width).sum() / (i.marginal_width - i.pair_width).sum(), 4))
print('## Informative: identification vs number of binary states remaining after zero-cell pruning (pair_possible_states)')
print(i.groupby(pd.cut(i.pair_possible_states, [0, 10, 20, 30, 50, 100, 500, 5000])).agg(n=('ident', 'size'), pair_identified_frac=('ident', 'mean'), pair_width=('pair_width', 'mean'), marginal_width=('marginal_width', 'mean')).round(3).to_string())
print('## Informative: geometry x lead')
print(i.groupby(['geometry', 'lead']).agg(n=('ident', 'size'), pair_identified_frac=('ident', 'mean'), marginal=('marginal_width', 'mean'), aggregate=('aggregate_width', 'mean'), pair=('pair_width', 'mean')).round(4).to_string())
print('## Certification (U<=c or L>=c, tol 1e-7)')
for scope, d in [('all_queries', c), ('informative_near(|q-c|<=0.1)', i)]:
    for g in ['all', 'compact', 'dispersed']:
        dd = d if g == 'all' else d[d.geometry == g]
        for cr in (0.1, 0.25, 0.5):
            s = dd if scope == 'all_queries' else dd[(dd.q - cr).abs() <= 0.1 + 1e-12]
            row = [scope, g, cr, len(s)]
            for lab in ('marginal', 'aggregate', 'pair'):
                row.append(round(float(((s[f'{lab}_upper'] <= cr + tol) | (s[f'{lab}_lower'] >= cr - tol)).mean()), 4))
            print(*row)
a = i[i.historical_q.notna()]
print('## Reconstruction MAE (informative, historical available)', len(a), a.date.nunique(),
      round((a.independent_q - a.q).abs().mean(), 4), round((a.historical_q - a.q).abs().mean(), 4), round((a.midpoint_q - a.q).abs().mean(), 4),
      'marginal-midpoint', round((((a.marginal_lower + a.marginal_upper) / 2) - a.q).abs().mean(), 4))
