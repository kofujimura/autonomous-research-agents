"""Exploratory matched direct-learner inputs; fixed target labels and calibration."""
import os
os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from features import load_features,matrix,MODELS
from analyse import summarize,SEED
from initial_readouts import equality
from record import ROOT

METHODS=['direct_before','direct_after','direct_difference','direct_gradient_boosting']
KEY=['model','support','fold','seed','reference_mode','task','method','point_id']

def contrasts(pred):
    results=[]
    comparisons=[(m,'direct_gradient_boosting') for m in METHODS[:-1]]+[('direct_after','direct_before')]
    for method,baseline in comparisons:
        q=pred[pred.method.isin([method,baseline])].copy()
        q.loc[q.method==baseline,'method']='start_fixed'
        _,p,_=summarize(q)
        if len(p):p['baseline_method']=baseline;results.append(p)
    return pd.concat(results,ignore_index=True)

def direct_inputs(output,dataset,baseline,original=None):
    output.mkdir(parents=True,exist_ok=False);extended=dataset=='nlcd'
    vec,_,hashes,_=load_features(include_nlcd=extended)
    old=pd.read_csv(ROOT/'data/prepared/targets.csv')
    if extended:
        assert original is not None
        early=old[old.before_year<=2018].copy();early['feature_point_id']=early.point_id
        new=pd.read_csv(ROOT/'data/nlcd/prepared/targets.csv');t=pd.concat([early,new],ignore_index=True)
        previous=pd.read_parquet(baseline/'raw-predictions.parquet')
    else:t=old;previous=pd.read_parquet(baseline/'predictions.parquet')
    feature=t.feature_point_id if 'feature_point_id' in t else t.point_id
    before=feature+'-'+t.before_year.astype(str);after=feature+'-'+t.after_year.astype(str)
    arrays={m:(matrix(vec,m,'centre',before),matrix(vec,m,'centre',after)) for m in MODELS}
    good=np.logical_and.reduce([np.isfinite(a).all(1)&np.isfinite(b).all(1) for a,b in arrays.values()])
    records=[];thresholds=[];fitting=[]
    for model,(a,b) in arrays.items():
        features=dict(direct_before=a,direct_after=b,direct_difference=b-a,
            direct_gradient_boosting=np.concatenate([a,b,b-a],axis=1))
        for fold in range(5):
            early=(t.before_year.to_numpy()<=2018)&(t.region.to_numpy()!=fold)&good
            fit=early&~t.calibration_cell.to_numpy(bool);cal=early&t.calibration_cell.to_numpy(bool)
            test=(t.before_year.to_numpy()>=2019)&(t.region.to_numpy()==fold)&good
            for task in ['gain','loss']:
                relevant=t[f'{task}_task'].to_numpy(bool);truth=t[f'{task}_positive'].to_numpy(int)
                train=fit&relevant
                for method,x in features.items():
                    score=np.full(len(t),np.nan);trained=len(np.unique(truth[train]))==2
                    if trained:
                        learner=HistGradientBoostingClassifier(max_iter=150,learning_rate=.05,max_leaf_nodes=7,
                            min_samples_leaf=10,l2_regularization=1,early_stopping=False,class_weight='balanced',random_state=SEED)
                        learner.fit(x[train],truth[train]);score[good]=learner.predict_proba(x[good])[:,1]
                    ci=cal&relevant&(truth==0)&np.isfinite(score);ti=test&relevant&np.isfinite(score)
                    valid=ci.sum()>=10;threshold=float(np.quantile(score[ci],.9,method='higher')) if valid else None
                    base=dict(availability_mode='paired',model=model,support='centre',fold=fold,seed=SEED,reference_mode='global',task=task,method=method)
                    thresholds.append(dict(**base,calibration_negatives=int(ci.sum()),threshold=threshold,available=bool(valid),
                        calibration_false_flags=int((score[ci]>threshold).sum()) if valid else None,
                        calibration_ties=int((score[ci]==threshold).sum()) if valid else None,test_rows=int(ti.sum())))
                    fitting.append(dict(model=model,fold=fold,task=task,method=method,fit_pairs=int(train.sum()),
                        positive_fit_pairs=int(truth[train].sum()),negative_fit_pairs=int((truth[train]==0).sum()),
                        input_features=x.shape[1],trained=bool(trained)))
                    if not valid:continue
                    for j in np.flatnonzero(ti):
                        records.append(dict(**base,point_id=t.point_id[j],block=t.block[j],before_year=int(t.before_year[j]),
                            truth=int(truth[j]),score=float(score[j]),threshold=threshold,flag=int(score[j]>threshold)))
    pred=pd.DataFrame(records);th=pd.DataFrame(thresholds)
    both=pred[pred.method=='direct_gradient_boosting'].sort_values(KEY).reset_index(drop=True)
    previous=previous[(previous.availability_mode=='paired')&(previous.support=='centre')&(previous.seed==SEED)&
        (previous.reference_mode=='global')&(previous.method=='direct_gradient_boosting')].sort_values(KEY).reset_index(drop=True)
    pd.testing.assert_frame_equal(both[KEY+['truth','flag']],previous[KEY+['truth','flag']])
    for col in ['score','threshold']:np.testing.assert_allclose(both[col],previous[col],rtol=0,atol=1e-12)
    oldth=pd.read_csv(baseline/'thresholds.csv');oldth=oldth[(oldth.availability_mode=='paired')&(oldth.support=='centre')&
        (oldth.seed==SEED)&(oldth.reference_mode=='global')&(oldth.method=='direct_gradient_boosting')]
    equality(th[th.method=='direct_gradient_boosting'],oldth).to_csv(output/'both-threshold-equality.csv',index=False)
    if extended:equality(th,pd.read_csv(original/'thresholds.csv')).to_csv(output/'threshold-equality.csv',index=False)
    pred.to_parquet(output/'raw-predictions.parquet',index=False)
    if extended:
        meta=new.set_index('point_id');reports=[]
        for horizon in ['overlapping_2019_2021','beyond_2021']:
            for agreement in ['primary','unambiguous']:
                ids=meta.index[(meta.horizon==horizon)&(meta.unambiguous if agreement=='unambiguous' else True)]
                q=pred[pred.point_id.isin(ids)].copy();q['availability_mode']=f'nlcd_{horizon}_{agreement}';reports.append(q)
        report=pd.concat(reports,ignore_index=True)
    else:report=pred
    metrics,_,strata=summarize(report);paired=contrasts(report)
    for name,df in [('metrics',metrics),('strata',strata),('contrasts',paired),('thresholds',th),('fitting-counts',pd.DataFrame(fitting))]:
        df.to_csv(output/f'{name}.csv',index=False)
    report.to_parquet(output/'predictions.parquet',index=False)
    (output/'input-sha256.json').write_text(json.dumps(hashes,sort_keys=True,indent=2)+'\n')
    summary=dict(exploratory=True,dataset=dataset,input_methods=METHODS,both_reconstruction_rows=len(both),
        original_both_scores_flags_thresholds_match=True,forest_outcomes_already_inspected_before_plan=True,
        interpretation='Same direct learner/transition target, different inputs/dimensions; retrospective and not equal model capacity or physical observation causality.')
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary));print(metrics[metrics.availability_mode.str.endswith('_primary') if extended else metrics.index.notna()].to_string(index=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dataset',choices=['lcmap','nlcd'],required=True)
    for name in ['output','baseline']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--original',type=Path);a=p.parse_args();direct_inputs(a.output,a.dataset,a.baseline,a.original)
