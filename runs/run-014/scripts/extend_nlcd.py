"""Secondary sample/ontology/horizon transfer with unchanged earlier thresholds."""
import os
os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from features import load_features,target_coverage
from analyse import make_predictions,summarize,SEED
from secondary import make_secondary_predictions
from record import ROOT

def extend(output,baseline,secondary):
    output.mkdir(parents=True,exist_ok=False)
    vec,availability,hashes,metadata=load_features(include_nlcd=True,include_controls=True)
    old=pd.read_csv(ROOT/'data/prepared/targets.csv')
    early=old[old.before_year<=2018].copy();early['feature_point_id']=early.point_id
    new=pd.read_csv(ROOT/'data/nlcd/prepared/targets.csv')
    detail,coverage=target_coverage(vec,new)
    detail.to_csv(output/'availability-targets.csv',index=False);coverage.to_csv(output/'coverage.csv',index=False)
    alltargets=pd.concat([early,new],ignore_index=True)
    refs=pd.read_csv(ROOT/'data/prepared/references.csv');controls=pd.read_csv(ROOT/'data/controls/controls.csv')
    pred,threshold,refcounts,ident,near=make_predictions(vec,alltargets,refs,seeds=[SEED],reference_modes=['global'])
    more,th2,controlcounts=make_secondary_predictions(vec,alltargets,refs,controls)
    pred=pd.concat([pred,more],ignore_index=True)
    # Thresholds must match exactly the previously fixed earlier calibration.
    keys=['availability_mode','model','support','fold','seed','reference_mode','task','method']
    prior=pd.read_csv(baseline/'thresholds.csv')
    prior=prior[(prior.availability_mode=='paired')&(prior.seed==SEED)&(prior.reference_mode=='global')]
    previous_secondary=pd.read_csv(secondary/'thresholds.csv')
    previous=pd.concat([prior,previous_secondary],ignore_index=True)
    current=pd.concat([threshold,th2],ignore_index=True)
    join=current.merge(previous,on=keys,suffixes=('_new','_old'),validate='one_to_one')
    assert len(join)==len(current)
    np.testing.assert_allclose(join.threshold_new,join.threshold_old,rtol=0,atol=1e-12,equal_nan=True)
    assert np.array_equal(join.calibration_negatives_new,join.calibration_negatives_old)
    assert np.array_equal(join.available_new,join.available_old)
    join.to_csv(output/'threshold-equality.csv',index=False)
    pred.to_parquet(output/'raw-predictions.parquet',index=False)
    meta=new.set_index('point_id')
    reports=[]
    for horizon in ['overlapping_2019_2021','beyond_2021']:
        for uncertainty in ['primary','unambiguous']:
            valid=meta.index[meta.horizon==horizon]
            if uncertainty=='unambiguous':valid=meta.index[(meta.horizon==horizon)&meta.unambiguous]
            q=pred[pred.point_id.isin(valid)].copy()
            q['availability_mode']=f'nlcd_{horizon}_{uncertainty}'
            reports.append(q)
    report=pd.concat(reports,ignore_index=True)
    metrics,paired,strata=summarize(report)
    report.to_parquet(output/'predictions.parquet',index=False)
    metrics.to_csv(output/'metrics.csv',index=False);paired.to_csv(output/'paired-comparisons.csv',index=False)
    strata.to_csv(output/'strata.csv',index=False);current.to_csv(output/'thresholds.csv',index=False)
    refcounts.to_csv(output/'reference-availability.csv',index=False);controlcounts.to_csv(output/'control-availability.csv',index=False)
    (output/'input-sha256.json').write_text(json.dumps(hashes,sort_keys=True,indent=2)+'\n')
    summary=dict(thresholds_compared=len(join),thresholds_match=True,new_pairs=len(new),new_plots=new.plotid.nunique(),
                 primary_test_pairs_by_task={task:int(pred[(pred.task==task)&(pred.method=='start_fixed')&(pred.model=='aef')&(pred.support=='centre')].shape[0]) for task in ['gain','loss']},
                 endpoint='NLCD Forest-class transitions; distinct from LCMAP dominant Trees')
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2));print(metrics[(metrics.support=='centre')&metrics.availability_mode.str.endswith('_primary')].to_string(index=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--secondary',type=Path,required=True);a=p.parse_args();extend(a.output,a.baseline,a.secondary)
