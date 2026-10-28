# Reviewer exploratory check: cosine change magnitude and initial-vector readouts by test year pair, AEF vs TESSERA.
import pandas as pd, numpy as np, sys
from sklearn.metrics import roc_auc_score
p = pd.read_parquet(sys.argv[1])
q = p[(p.availability_mode=='paired')&(p.support=='centre')&(p.seed==14014)&(p.reference_mode=='global')&(p.method=='cosine_change')]
for (m,t,y),g in q.groupby(['model','task','before_year']):
    pos=g[g.truth==1].score; neg=g[g.truth==0].score
    print(m,t,f'{y}-{y+1}','P=%d N=%d'%(len(pos),len(neg)),'median mag pos=%.4f neg=%.4f'%(pos.median(),neg.median()),'AUROC=%.3f'%roc_auc_score(g.truth,g.score),'TP=%d FP=%d'%(g[g.truth==1].flag.sum(),g[g.truth==0].flag.sum()))
