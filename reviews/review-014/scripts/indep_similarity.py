# Reviewer check: how different are corrected scores from start-fixed on test rows (rank correlation, score-scale ratio)
import pandas as pd, numpy as np, sys
from scipy.stats import spearmanr
p = pd.read_parquet(sys.argv[1])
q = p[(p.availability_mode=='paired')&(p.support=='centre')&(p.seed==14014)&(p.reference_mode=='global')]
for (m,t),g in q.groupby(['model','task']):
    b=g[g.method=='start_fixed'].set_index('point_id').sort_index()
    for meth in ['concurrent','control_adjusted']:
        o=g[g.method==meth].set_index('point_id').loc[b.index]
        d=o.score-b.score
        # within fold & before_year groups, control_adjusted differs by constant
        within_sd = d.groupby([b.fold,b.before_year]).std().max()
        print(m,t,meth,'spearman=%.4f'%spearmanr(o.score,b.score)[0],'sd(diff)/sd(base)=%.3f'%(d.std()/b.score.std()),'max within-fold-year sd(diff)=%.2e'%within_sd)
