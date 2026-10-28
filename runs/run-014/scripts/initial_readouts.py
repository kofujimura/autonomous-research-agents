"""Exploratory v17 input-necessity diagnostics; no prospective forecast claim."""
import os
os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from features import load_features,matrix,unit,MODELS
from analyse import allocation,fit_supervised,summarize,SEED
from robustness import additional_predictions,ADDED
from record import ROOT

BEFORE=['initial_reference_similarity','initial_state_random_forest',
        'initial_baseline_cohort_random_forest','initial_baseline_cohort_logistic']
PAIRS=dict(initial_reference_similarity='subsequent_start_reference_similarity',
           initial_state_random_forest='subsequent_state_random_forest',
           initial_baseline_cohort_random_forest='baseline_cohort_random_forest',
           initial_baseline_cohort_logistic='baseline_cohort_logistic')
KEY=['availability_mode','model','support','fold','seed','reference_mode','task','method']

def initial_predictions(vec,t,refs,controls):
    pred,th,fitcounts,_=additional_predictions(vec,t,refs,controls,MODELS,'paired',.1,state_input='before')
    keep=['baseline_cohort_random_forest','baseline_cohort_logistic']
    pred=pred[pred.method.isin(keep)].copy();th=th[th.method.isin(keep)].copy()
    pred['method']='initial_'+pred.method;th['method']='initial_'+th.method
    predictions=pred.to_dict('records');thresholds=th.to_dict('records')
    fid=t.feature_point_id if 'feature_point_id' in t else t.point_id
    ids0=fid+'-'+t.before_year.astype(str);ids1=fid+'-'+t.after_year.astype(str)
    arr={(m,y):matrix(vec,m,'centre',ids0 if y==0 else ids1) for m in MODELS for y in [0,1]}
    good=np.logical_and.reduce([np.isfinite(v).all(1) for v in arr.values()]);roles=allocation(refs,SEED)
    for model in MODELS:
        a,b=arr[model,0],arr[model,1]
        for fold in range(5):
            early=(t.before_year.to_numpy()<=2018)&(t.region.to_numpy()!=fold)&good
            cal=early&t.calibration_cell.to_numpy(bool);fit=early&~t.calibration_cell.to_numpy(bool)
            test=(t.before_year.to_numpy()>=2019)&(t.region.to_numpy()==fold)&good
            state=fit_supervised(a,b,t,fit,'gain',include_initial=True)
            rf=state.get('initial_state_random_forest',np.full(len(t),np.nan))
            first=np.full(len(t),np.nan);last=np.full(len(t),np.nan)
            ri=(roles=='R')&(refs.region.to_numpy()!=fold)
            for year in sorted(t.before_year.unique()):
                ix=np.flatnonzero(t.before_year.to_numpy()==year)
                r=matrix(vec,model,'centre',refs.loc[ri,'point_id']+'-'+str(year));r=r[np.isfinite(r).all(1)]
                if len(r)<8:continue
                reference=unit(r.mean(0));first[ix]=a[ix]@reference;last[ix]=b[ix]@reference
            for task in ['gain','loss']:
                direction=1 if task=='gain' else -1
                scores=dict(initial_reference_similarity=direction*first,
                            subsequent_start_reference_similarity=direction*last,
                            initial_state_random_forest=direction*rf)
                relevant=t[f'{task}_task'].to_numpy(bool);truth=t[f'{task}_positive'].to_numpy(bool)
                for method,score in scores.items():
                    cidx=cal&relevant&~truth&np.isfinite(score);tidx=test&relevant&np.isfinite(score)
                    valid=cidx.sum()>=10;threshold=float(np.quantile(score[cidx],.9,method='higher')) if valid else None
                    base=dict(availability_mode='paired',model=model,support='centre',fold=fold,seed=SEED,
                              reference_mode='global',task=task,method=method)
                    thresholds.append(dict(**base,calibration_negatives=int(cidx.sum()),threshold=threshold,
                        calibration_false_flags=int((score[cidx]>threshold).sum()) if valid else None,
                        calibration_ties=int((score[cidx]==threshold).sum()) if valid else None,
                        test_rows=int(tidx.sum()),available=bool(valid)))
                    if not valid:continue
                    for j in np.flatnonzero(tidx):
                        predictions.append(dict(**base,point_id=t.point_id[j],block=t.block[j],before_year=int(t.before_year[j]),
                                                truth=int(truth[j]),score=float(score[j]),threshold=threshold,flag=int(score[j]>threshold)))
    return pd.DataFrame(predictions),pd.DataFrame(thresholds),fitcounts

def equality(current,previous):
    q=current.merge(previous,on=KEY,suffixes=('_new','_old'),validate='one_to_one')
    assert len(q)==len(current)
    np.testing.assert_allclose(q.threshold_new,q.threshold_old,rtol=0,atol=1e-12,equal_nan=True)
    assert (q.calibration_negatives_new==q.calibration_negatives_old).all()
    assert (q.available_new==q.available_old).all()
    return q

def paired_initial(pred):
    rows=[]
    for before,after in PAIRS.items():
        q=pred[pred.method.isin([before,after])].copy()
        q.loc[q.method==after,'method']='start_fixed'
        _,p,_=summarize(q)
        if len(p):p['baseline_method']=after;rows.append(p)
    return pd.concat(rows,ignore_index=True)

def permutation_check(vec,t,refs,controls,original,thresholds,output):
    assert t.point_id.is_unique
    copy={key:dict(values) for key,values in vec.items()};rng=np.random.default_rng(SEED);mapping=[]
    initial_keys=set(t.point_id+'-'+t.before_year.astype(str))
    cohort=set(pd.concat([refs.point_id,controls.point_id]));changed=set()
    for year,g in t[t.before_year>=2019].groupby('before_year',sort=True):
        donors=g.iloc[rng.permutation(len(g))]
        for target,donor in zip(g.itertuples(),donors.itertuples()):
            key=f'{target.point_id}-{target.after_year}';source=f'{donor.point_id}-{donor.after_year}'
            assert key not in initial_keys and target.point_id not in cohort
            for model in MODELS:copy[model,'centre'][key]=vec[model,'centre'][source]
            changed.add(key);mapping.append(dict(point_id=target.point_id,donor_point_id=donor.point_id,before_year=int(year)))
    p,th,_=initial_predictions(copy,t,refs,controls)
    keys=KEY+['point_id']
    a=original[original.method.isin(BEFORE)].sort_values(keys).reset_index(drop=True)
    b=p[p.method.isin(BEFORE)].sort_values(keys).reset_index(drop=True)
    assert a[keys].equals(b[keys]);np.testing.assert_allclose(a.score,b.score,rtol=0,atol=1e-12)
    assert (a.flag==b.flag).all()
    equality(th[th.method.isin(BEFORE)],thresholds[thresholds.method.isin(BEFORE)])
    pd.DataFrame(mapping).to_csv(output/'permutation-map.csv',index=False)
    return dict(status='PASS',seed=SEED,permutations=1,scored_rows=len(a),mapped_target_keys=len(changed),
                maximum_score_difference=float(abs(a.score-b.score).max()),changed_flags=int((a.flag!=b.flag).sum()),
                scope='LCMAP finite later after vectors only; input-dependence software check, not independent replication or forecasting.')

def initial_readouts(output,dataset,baseline,robustness,initial_baseline=None):
    output.mkdir(parents=True,exist_ok=False)
    extended=dataset=='nlcd';vec,av,hashes,_=load_features(include_controls=True,include_nlcd=extended)
    old=pd.read_csv(ROOT/'data/prepared/targets.csv');refs=pd.read_csv(ROOT/'data/prepared/references.csv')
    controls=pd.read_csv(ROOT/'data/controls/controls.csv')
    if extended:
        early=old[old.before_year<=2018].copy();early['feature_point_id']=early.point_id
        new=pd.read_csv(ROOT/'data/nlcd/prepared/targets.csv');t=pd.concat([early,new],ignore_index=True)
        base=pd.read_parquet(baseline/'raw-predictions.parquet');base=base[base.support=='centre']
        post,postth,_,_=additional_predictions(vec,t,refs,controls,MODELS,'paired',.1)
        equality(postth,pd.read_csv(robustness/'thresholds.csv')).to_csv(output/'post-threshold-equality.csv',index=False)
        base=pd.concat([base,post],ignore_index=True)
    else:
        assert av.file_present.all();t=old
        base=pd.read_parquet(baseline/'predictions.parquet')
        base=base[(base.availability_mode=='paired')&(base.support=='centre')&(base.seed==SEED)&(base.reference_mode=='global')]
        post=pd.read_parquet(robustness/'predictions.parquet');post=post[post.method.isin(ADDED)]
        base=pd.concat([base,post],ignore_index=True)
    added,th,fit=initial_predictions(vec,t,refs,controls)
    # Direct initial RF predictions must agree with the identity implicit in saved state scores.
    state=base[base.method.isin(['state_random_forest','subsequent_state_random_forest'])].pivot(
        index=['model','task','point_id'],columns='method',values='score').reset_index()
    state['initial_from_saved']=state.subsequent_state_random_forest-state.state_random_forest
    check=added[added.method=='initial_state_random_forest'].merge(state,on=['model','task','point_id'],validate='one_to_one')
    np.testing.assert_allclose(check.score,check.initial_from_saved,rtol=0,atol=1e-12)
    combined=pd.concat([base,added],ignore_index=True)
    combined.to_parquet(output/'raw-predictions.parquet',index=False)
    if extended:
        assert initial_baseline is not None
        equality(th,pd.read_csv(initial_baseline/'thresholds.csv')).to_csv(output/'initial-threshold-equality.csv',index=False)
        meta=new.set_index('point_id');reports=[]
        for horizon in ['overlapping_2019_2021','beyond_2021']:
            for agreement in ['primary','unambiguous']:
                ids=meta.index[(meta.horizon==horizon)&((meta.unambiguous) if agreement=='unambiguous' else True)]
                q=combined[combined.point_id.isin(ids)].copy();q['availability_mode']=f'nlcd_{horizon}_{agreement}';reports.append(q)
        report=pd.concat(reports,ignore_index=True);permutation=None
    else:
        report=combined;permutation=permutation_check(vec,t,refs,controls,added,th,output)
        (output/'permutation-check.json').write_text(json.dumps(permutation,indent=2)+'\n')
    metrics,pairs,strata=summarize(report);initial_pairs=paired_initial(report)
    report.to_parquet(output/'predictions.parquet',index=False)
    for name,df in [('metrics',metrics),('paired-comparisons',pairs),('strata',strata),
                    ('initial-versus-subsequent',initial_pairs),('thresholds',th),('cohort-fitting-counts',fit)]:
        df.to_csv(output/f'{name}.csv',index=False)
    (output/'input-sha256.json').write_text(json.dumps(hashes,sort_keys=True,indent=2)+'\n')
    summary=dict(exploratory=True,dataset=dataset,initial_target_vector_values_only_methods=BEFORE,
        comparable_after_vector_availability_mask=True,initial_RF_identity_verified=True,permutation_check=permutation,
        interpretation='Retrospective input-necessity diagnostic; no prospective forecasting, static-context cause or equivalence claim.')
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2));print(metrics[metrics.method.isin(BEFORE+list(PAIRS.values()))].to_string(index=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--dataset',choices=['lcmap','nlcd'],required=True)
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--robustness',type=Path,required=True)
    p.add_argument('--initial-baseline',type=Path);a=p.parse_args()
    initial_readouts(a.output,a.dataset,a.baseline,a.robustness,a.initial_baseline)
