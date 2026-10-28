import json, sys, numpy as np, collections
rows = json.load(open(sys.argv[1]))
u = {}
for r in rows: u[r['unit']] = r
ch = np.array([r['labels_changed_frac'] for r in u.values()])
print('units', len(u), 'labels changed fraction: median %.4f, q25 %.4f, q75 %.4f, min %.4f, max %.4f' % (np.median(ch), *np.percentile(ch, [25, 75]), ch.min(), ch.max()))
gr = {k: (v['grass'] or 0) > 0.5 for k, v in u.items()}
ar = {k: (v['arable'] or 0) > 0.5 for k, v in u.items()}
print('grass>0.5 units', sum(gr.values()), 'arable>0.5 units', sum(ar.values()))
for n in [128]:
    for d in ['paired', 'independent']:
        rs = [r for r in rows if r['n'] == n and r['design'] == d]
        for name, sel in [('tiny |dH|<0.01', lambda r: abs(r['truth']) < 0.01), ('|dH|>=0.01', lambda r: abs(r['truth']) >= 0.01),
                          ('grass-dominated', lambda r: gr[r['unit']]), ('arable-dominated', lambda r: ar[r['unit']])]:
            s = [r for r in rs if sel(r)]
            rep = sum(r['reports'] for r in s); wr = sum(r['wrong'] for r in s); R = sum(r['R'] for r in s)
            print(n, d, name, 'units', len(s), 'cov %.3f' % np.mean([r['coverage'] for r in s]), 'reports %d (%.3f)' % (rep, rep / R), 'wrong %d' % wr, 'wrong/report %.3f' % (wr / rep if rep else float('nan')),
                  'rmse %.4f' % np.sqrt(np.mean([r['mse'] for r in s])), 'noch rmse %.4f' % np.sqrt(np.mean([r['truth'] ** 2 for r in s])))
        # units where no-change beats estimator
        beat = sum(r['truth'] ** 2 < r['mse'] for r in rs)
        print(n, d, 'units where no-change squared error < estimator MSE:', beat, '/', len(rs))
        cv = np.array([r['coverage'] for r in rs]); print(n, d, 'per-unit coverage min %.3f q10 %.3f median %.3f; units cov<0.9: %d' % (cv.min(), np.quantile(cv, .1), np.median(cv), (cv < 0.9).sum()))
for n in [32, 64, 128, 256, 512]:
    rs = [r for r in rows if r['n'] == n and r['design'] == 'paired']
    print('n', n, 'paired units where no-change better', sum(r['truth'] ** 2 < r['mse'] for r in rs))
