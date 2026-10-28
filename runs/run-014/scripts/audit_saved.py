"""Recount saved flags without fitting models; this is not a raw-data reproduction."""
import sys
sys.dont_write_bytecode=True
import argparse,json,time
from pathlib import Path
import numpy as np
import pandas as pd
from record import ROOT

FOLDERS=['aef-closed-v11','main-v1','secondary-v2','robustness-aef-v12','robustness-paired-v12',
    'endpoint-v13','reference-completeness-v14','initial-vector-v17','geography-v18','initial-class-v19',
    'reference-access-v20','direct-inputs-v23','nlcd-v4','nlcd-initial-v17','nlcd-geography-v18','nlcd-class-v19','nlcd-reference-access-v20','nlcd-direct-inputs-v23']
FOLDERS += [f'partition-sensitivity-v24/seed-{seed}' for seed in range(14014,14024)]
KEY=['availability_mode','model','support','seed','reference_mode','task','method']

def audit_saved(directory):
    tick=time.monotonic();checks=[]
    for name in FOLDERS:
        d=directory/name;p=pd.read_parquet(d/'predictions.parquet');m=pd.read_csv(d/'metrics.csv')
        assert not p.duplicated(KEY+['point_id']).any(),name
        assert p.truth.isin([0,1]).all() and p.flag.isin([0,1]).all(),name
        assert np.array_equal(p.flag.to_numpy(int),(p.score>p.threshold).to_numpy(int)),name
        p['n_positive']=p.truth==1;p['n_negative']=p.truth==0
        p['true_positive']=(p.truth==1)&(p.flag==1);p['false_positive']=(p.truth==0)&(p.flag==1)
        q=p.groupby(KEY)[['n_positive','n_negative','true_positive','false_positive']].sum().reset_index()
        join=q.merge(m,on=KEY,suffixes=('_counted','_reported'),validate='one_to_one');assert len(join)==len(q)==len(m),name
        for col in ['n_positive','n_negative','true_positive','false_positive']:
            assert (join[col+'_counted']==join[col+'_reported']).all(),(name,col)
        pos=join.n_positive_counted.to_numpy();neg=join.n_negative_counted.to_numpy()
        tp=join.true_positive_counted.to_numpy();fp=join.false_positive_counted.to_numpy()
        with np.errstate(invalid='ignore',divide='ignore'):
            sens=tp/pos;fpr=fp/neg
        for col,v in [('sensitivity',sens),('false_positive_rate',fpr),('J',sens-fpr)]:
            np.testing.assert_allclose(join[col],v,rtol=0,atol=1e-12,equal_nan=True,err_msg=name+':'+col)
        checks.append(dict(folder=name,metric_rows=len(q),prediction_rows=len(p),status='matched'))
    for name in ['native-pairs-v21','native-single-date-v22']:
        d=directory/name;c=pd.read_csv(d/'comparisons.csv');s=pd.read_csv(d/'summary.csv')
        for r in s.itertuples():
            q=c[(c.support==r.support)&(c.task==r.task)&(c.method==r.method)]
            assert len(q)==r.planned_cases
            q=q[q.score_native.notna()];assert len(q)==r.common_cases
            assert int((q.flag_native!=q.flag_mosaic).sum())==r.changed_flags
            assert int((q.truth==1).sum())==r.positive_cases and int((q.truth==0).sum())==r.negative_cases
            for date in ['native','mosaic']:
                flag=q['flag_'+date]
                assert int(((q.truth==1)&(flag==1)).sum())==getattr(r,date+'_true_positive')
                assert int(((q.truth==0)&(flag==1)).sum())==getattr(r,date+'_false_positive')
        checks.append(dict(folder=name,case_conditions=len(c),summary_rows=len(s),status='matched'))
    return dict(status='PASS',elapsed_seconds=time.monotonic()-tick,scope='Saved predictions/flags and reported counts; no fitting or raw-vector recomputation.',
        checks=checks,network_used=False,ai_api_calls=0)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--analysis',type=Path,default=ROOT/'analysis');p.add_argument('--output',type=Path)
    a=p.parse_args();value=audit_saved(a.analysis)
    if a.output:
        out=a.output.resolve()
        if out==ROOT or out.is_relative_to(ROOT):raise ValueError('Output must be outside source checkout')
        out.write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps(value,indent=2))
