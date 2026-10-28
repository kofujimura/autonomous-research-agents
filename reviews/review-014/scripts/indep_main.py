# Independent recomputation (reviewer-written) of operating points from saved predictions.
import pandas as pd, numpy as np, sys, json
from sklearn.metrics import roc_auc_score
p = pd.read_parquet(sys.argv[1])
q = p[(p.availability_mode=='paired')&(p.support=='centre')&(p.seed==14014)&(p.reference_mode=='global')].copy()
# check flag rule
q['flag_re'] = (q.score > q.threshold).astype(int)
print('flag rule mismatches:', int((q.flag_re != q.flag).sum()), 'of', len(q))
rows=[]
for (m,t,meth),g in q.groupby(['model','task','method']):
    pos=g[g.truth==1]; neg=g[g.truth==0]
    tp=int(pos.flag.sum()); fp=int(neg.flag.sum())
    J=tp/len(pos)-fp/len(neg)
    try: auc=roc_auc_score(g.truth,g.score)
    except Exception: auc=np.nan
    rows.append(dict(model=m,task=t,method=meth,tp=tp,P=len(pos),fp=fp,N=len(neg),J=round(J,3),auroc=round(auc,3)))
r=pd.DataFrame(rows)
print(r.to_string())
# paired contrasts vs start_fixed
out=[]
for (m,t),g in q.groupby(['model','task']):
    base=g[g.method=='start_fixed'].set_index('point_id')
    bJ=r[(r.model==m)&(r.task==t)&(r.method=='start_fixed')].J.iloc[0]
    for meth in ['concurrent','control_adjusted','direct_gradient_boosting']:
        o=g[g.method==meth].set_index('point_id').loc[base.index]
        changed=int((o.flag!=base.flag).sum())
        pos=base.truth==1
        dJ=(o.flag[pos].mean()-o.flag[~pos].mean())-(base.flag[pos].mean()-base.flag[~pos].mean())
        out.append(dict(model=m,task=t,method=meth,dJ=round(dJ,6),changed=changed,n=len(base)))
print(pd.DataFrame(out).to_string())
r.to_csv(sys.argv[2],index=False); pd.DataFrame(out).to_csv(sys.argv[3],index=False)
