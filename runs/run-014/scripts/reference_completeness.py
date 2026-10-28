"""Exploratory v14: use the same valid reference plots before and after."""
import os
os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from features import load_features,matrix,MODELS,SUPPORTS
from analyse import make_predictions,summarize,allocation,SEED
from record import ROOT

INVARIANT=['cosine_change','state_random_forest','subsequent_state_random_forest',
           'subsequent_state_logistic','direct_gradient_boosting']

def reference_completeness(output,baseline):
    output.mkdir(parents=True,exist_ok=False)
    vec,av,hashes,_=load_features();assert av.file_present.all()
    t=pd.read_csv(ROOT/'data/prepared/targets.csv');refs=pd.read_csv(ROOT/'data/prepared/references.csv')
    roles=allocation(refs,SEED);membership=[]
    for model in MODELS:
        for support in SUPPORTS:
            for fold in range(5):
                r=refs[(roles=='R')&(refs.region.to_numpy()!=fold)]
                for year in range(2017,2021):
                    a=matrix(vec,model,support,r.point_id+'-'+str(year));b=matrix(vec,model,support,r.point_id+'-'+str(year+1))
                    va=np.isfinite(a).all(1);vb=np.isfinite(b).all(1)
                    membership.append(dict(model=model,support=support,fold=fold,before_year=year,
                        selected_reference_plots=len(r),before_valid=int(va.sum()),after_valid=int(vb.sum()),
                        common_valid=int((va&vb).sum()),only_before=int((va&~vb).sum()),only_after=int((~va&vb).sum()),
                        membership_disagreements=int((va!=vb).sum())))
    pd.DataFrame(membership).to_csv(output/'reference-membership.csv',index=False)
    pred,th,counts,ident,near=make_predictions(vec,t,refs,seeds=[SEED],reference_modes=['global'],paired_reference_membership=True)
    old=pd.read_parquet(baseline/'predictions.parquet')
    old=old[(old.availability_mode=='paired')&(old.seed==SEED)&(old.reference_mode=='global')]
    keys=['model','support','fold','task','method','point_id']
    joined=pred.merge(old[keys+['score','flag','threshold']],on=keys,suffixes=('_new','_old'),validate='one_to_one')
    assert len(joined)==len(pred)
    invariant=joined.method.isin(INVARIANT)
    np.testing.assert_allclose(joined.loc[invariant,'score_new'],joined.loc[invariant,'score_old'],rtol=0,atol=1e-12)
    np.testing.assert_allclose(joined.loc[invariant,'threshold_new'],joined.loc[invariant,'threshold_old'],rtol=0,atol=1e-12)
    assert (joined.loc[invariant,'flag_new']==joined.loc[invariant,'flag_old']).all()
    comparisons=[]
    for key,g in joined.groupby(['model','support','task','method']):
        y=g.truth.to_numpy();dn=(g.flag_new-g.flag_old).to_numpy()
        dt=float(dn[y==1].mean()) if (y==1).any() else np.nan
        df=float(dn[y==0].mean()) if (y==0).any() else np.nan
        comparisons.append(dict(zip(['model','support','task','method'],key))|dict(
            common_cases=len(g),positive=int((y==1).sum()),negative=int((y==0).sum()),
            changed_scores=int((abs(g.score_new-g.score_old)>1e-12).sum()),
            changed_thresholds=int((abs(g.threshold_new-g.threshold_old)>1e-12).sum()),
            changed_flags=int((g.flag_new!=g.flag_old).sum()),delta_sensitivity=dt,delta_false_positive_rate=df,delta_J=dt-df))
    pd.DataFrame(comparisons).to_csv(output/'changes-versus-original.csv',index=False)
    pred['availability_mode']='paired_reference_intersection';th['availability_mode']='paired_reference_intersection'
    pred.to_parquet(output/'predictions.parquet',index=False);th.to_csv(output/'thresholds.csv',index=False)
    metrics,pairs,strata=summarize(pred)
    for name,df in [('metrics',metrics),('paired-comparisons',pairs),('strata',strata),('reference-availability',counts)]:
        df.to_csv(output/f'{name}.csv',index=False)
    (output/'input-sha256.json').write_text(json.dumps(hashes,sort_keys=True,indent=2)+'\n')
    summary=dict(exploratory=True,unchanged_reference_independent_readouts=True,
        groups=len(membership),groups_with_membership_disagreements=sum(r['membership_disagreements']>0 for r in membership),
        common_prediction_rows=len(joined))
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2));print(pd.DataFrame(comparisons).query("support=='centre'").to_string(index=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True)
    a=p.parse_args();reference_completeness(a.output,a.baseline)
