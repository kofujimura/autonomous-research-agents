"""Synthetic integration checks: identities, operating points and label separation.

These fixtures are software checks, not environmental measurements or study evidence.
"""
import os
os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1'
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from analyse import make_predictions,summarize
from features import unit
from record import ROOT,now

def main(output):
    targets=[];refs=[];vectors={(m,s):{} for m in ['aef','tessera'] for s in ['centre','patch']}
    routes=[('Grass/forb/herb','Grass/forb/herb'),('Shrubs','Shrubs'),('Trees','Trees'),('Grass/forb/herb','Trees'),('Trees','Grass/forb/herb')]
    for region in range(5):
        for year in range(2017,2021):
            for k,(before,after) in enumerate(routes):
                for rep in range(4):
                    pid=f't{region}{year}{k}{rep}'
                    targets.append(dict(point_id=pid,x=-120+region*10+rep*.1,y=35+k*.5,region=region,
                        before_year=year,after_year=year+1,label_name_before=before,label_name_after=after,
                        block=f'{region}_{rep}',calibration_cell=rep<2,gain_task=before!='Trees',loss_task=before=='Trees',
                        gain_positive=after=='Trees',loss_positive=after!='Trees'))
                    for model,d in [('aef',64),('tessera',128)]:
                        for yr,cl in [(year,before),(year+1,after)]:
                            v=np.zeros(d);v[0 if cl=='Trees' else 1]=1
                            for support in ['centre','patch']:vectors[model,support][f'{pid}-{yr}']=v.copy()
        for k in range(16):
            pid=f'r{region}{k}';refs.append(dict(point_id=pid,x=-120+region*10,y=40+k*.1,region=region))
            for model,d in [('aef',64),('tessera',128)]:
                for yr in range(2017,2022):
                    v=np.zeros(d);v[0]=1
                    for support in ['centre','patch']:vectors[model,support][f'{pid}-{yr}']=v.copy()
    t=pd.DataFrame(targets);r=pd.DataFrame(refs)
    pred,threshold,fold,ident,near=make_predictions(vectors,t,r)
    metrics,pairs,strata=summarize(pred)
    primary=metrics[(metrics.seed==14014)&(metrics.reference_mode=='global')]
    assert (primary.sensitivity==1).all() and (primary.false_positive_rate==0).all()
    assert not (pred.method=='standardized_concurrent').any(), 'Zero control variance must be unavailable'
    assert (pred.before_year>=2019).all()
    assert (ident.start_end_equal==ident.n).all() and (ident.start_concurrent_equal==ident.n).all()
    assert (pairs.delta_J==0).all() and (pairs.changed_flags==0).all()
    assert (pairs.delta_J_lo==0).all() and (pairs.delta_J_hi==0).all()
    # Later outcome labels may change truth, never fitted scores or thresholds.
    changed=t.copy();late=changed.before_year>=2019
    changed.loc[late,'gain_positive']=~changed.loc[late,'gain_positive']
    changed.loc[late,'loss_positive']=~changed.loc[late,'loss_positive']
    changed.loc[late,'label_name_after']='Shrubs'
    pred2,threshold2,*_=make_predictions(vectors,changed,r)
    key=['model','support','fold','seed','reference_mode','task','method','point_id']
    a=pred.sort_values(key).reset_index(drop=True);b=pred2.sort_values(key).reset_index(drop=True)
    pd.testing.assert_frame_equal(a.drop(columns='truth'),b.drop(columns='truth'))
    pd.testing.assert_frame_equal(threshold,threshold2)
    result=dict(checked_at_utc=now(),status='PASS',fixture='Perfect, time-invariant synthetic class vectors',
                target_pairs=len(t),reference_pool=len(r),primary_rows=len(primary),
                checks=['perfect transitions and zero false positives','zero control variance excluded',
                        'reference-anchor equality','paired bootstrap difference exactly zero',
                        'later target labels do not affect scores or thresholds'],
                note='Software verification only; not an empirical environmental result')
    if output.exists():raise FileExistsError(output)
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);main(p.parse_args().output)
