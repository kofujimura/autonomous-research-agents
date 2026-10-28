# Compare paper.md Tables 1 and 3 (operating points) with reviewer recomputation from saved predictions.
import re, sys, pandas as pd
paper = open(sys.argv[1]).read(); r = pd.read_csv(sys.argv[2])
name = {'Start-year reference':'start_fixed','Concurrent reference':'concurrent','Tree controls':'control_adjusted','Cosine change magnitude':'cosine_change',
        'Direct gradient boosting':'direct_gradient_boosting','State random forest':'state_random_forest','Subsequent-reference similarity':'subsequent_reference_similarity',
        'Subsequent-state logistic':'subsequent_state_logistic','Subsequent-state forest':'subsequent_state_random_forest'}
model = {'AlphaEarth V1 mosaic':'aef','TESSERA v1':'tessera'}
sec = paper[paper.index('### 4.2'):paper.index('### 4.4')]
n = ok = 0; bad = []
for line in sec.splitlines():
    c = [x.strip() for x in line.strip('|').split('|')]
    if len(c) >= 8 and c[0] in model and c[2] in name:
        tp, P = map(int, c[3].split('/')); fp, N = map(int, c[4].split('/')); J = float(c[7])
        row = r[(r.model == model[c[0]]) & (r.task == c[1]) & (r.method == name[c[2]])].iloc[0]
        good = (tp, P, fp, N) == (row.tp, row.P, row.fp, row.N) and abs(J - row.J) < 6e-4
        if len(c) >= 9 and c[8]: good = good and abs(float(c[8]) - row.auroc) < 6e-4
        n += 1; ok += good
        if not good: bad.append(line)
print('rows compared', n, 'matched', ok, 'mismatched', bad)
