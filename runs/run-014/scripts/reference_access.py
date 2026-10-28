"""Fixed v20 reference availability boundary; original target labels remain held out."""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from record import ROOT
from analyse import make_predictions,summarize,SEED
from features import load_features
from initial_readouts import equality

SUPERVISED=['state_random_forest','subsequent_state_random_forest','subsequent_state_logistic','direct_gradient_boosting']

def reference_access(output,dataset,main,extension=None,original=None):
    output.mkdir(parents=True,exist_ok=False)
    extended=dataset=='nlcd'
    vec,_,hashes,_=load_features(include_nlcd=extended)
    old=pd.read_csv(ROOT/'data/prepared/targets.csv');refs=pd.read_csv(ROOT/'data/prepared/references.csv')
    if extended:
        assert extension is not None and original is not None
        early=old[old.before_year<=2018].copy();early['feature_point_id']=early.point_id
        new=pd.read_csv(ROOT/'data/nlcd/prepared/targets.csv');t=pd.concat([early,new],ignore_index=True)
        before=pd.read_parquet(extension/'raw-predictions.parquet')
    else:
        t=old;before=pd.read_parquet(main/'predictions.parquet')
    pred,th,counts,ident,near=make_predictions(vec,t,refs,seeds=[SEED],include_test_region_references=True)
    # This boundary cannot change learners, partitions, scores or flags that do not use references.
    key=['model','support','fold','seed','reference_mode','task','method','point_id']
    a=pred[pred.method.isin(SUPERVISED)].sort_values(key).reset_index(drop=True)
    b=before[(before.availability_mode=='paired')&(before.seed==SEED)&(before.reference_mode=='global')&
             before.method.isin(SUPERVISED)].sort_values(key).reset_index(drop=True)
    assert len(a)==len(b)
    pd.testing.assert_frame_equal(a[key+['truth','flag']],b[key+['truth','flag']])
    for col in ['score','threshold']:np.testing.assert_allclose(a[col],b[col],rtol=0,atol=1e-12)
    if extended:
        equality(th,pd.read_csv(original/'thresholds.csv')).to_csv(output/'threshold-equality.csv',index=False)
    pred.to_parquet(output/'raw-predictions.parquet',index=False)
    if extended:
        meta=new.set_index('point_id');reports=[]
        for horizon in ['overlapping_2019_2021','beyond_2021']:
            for agreement in ['primary','unambiguous']:
                ids=meta.index[(meta.horizon==horizon)&(meta.unambiguous if agreement=='unambiguous' else True)]
                q=pred[pred.point_id.isin(ids)].copy();q['availability_mode']=f'nlcd_{horizon}_{agreement}';reports.append(q)
        report=pd.concat(reports,ignore_index=True)
    else:report=pred
    metrics,pairs,strata=summarize(report)
    report.to_parquet(output/'predictions.parquet',index=False)
    for name,df in [('metrics',metrics),('paired-comparisons',pairs),('strata',strata),('thresholds',th),
                    ('reference-availability',counts),('identities',ident),('nearest-reference-distances',near)]:
        df.to_csv(output/f'{name}.csv',index=False)
    (output/'input-sha256.json').write_text(json.dumps(hashes,sort_keys=True,indent=2)+'\n')
    summary=dict(dataset=dataset,exploratory=True,baseline_references_include_test_region=True,
        target_fitting_excludes_test_region=True,supervised_invariance_rows=len(a),supervised_scores_and_flags_unchanged=True,
        interpretation='Different reference-information access; not equal resources or proof of ecological matching.')
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary));print(pairs[(pairs.support=='centre')&pairs.method.isin(['concurrent','control_adjusted'])].to_string(index=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--dataset',choices=['lcmap','nlcd'],required=True);p.add_argument('--main',type=Path,required=True)
    p.add_argument('--extension',type=Path);p.add_argument('--original',type=Path)
    a=p.parse_args();reference_access(a.output,a.dataset,a.main,a.extension,a.original)
