"""Exploratory v18 static coordinates; no embedding values enter the learners."""
import os
os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier,HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from analyse import summarize,SEED
from record import ROOT

METHODS=['coordinate_state_forest','coordinate_state_logistic','coordinate_direct_boosting']

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def geography(output,dataset,main,extension=None,original=None):
    output.mkdir(parents=True,exist_ok=False)
    old=pd.read_csv(ROOT/'data/prepared/targets.csv')
    mask=pd.read_csv(main/'availability-targets.csv')
    mask=mask[(mask.model=='aef')&(mask.support=='centre')][['point_id','common_pair_available']]
    masks={'main_availability':sha(main/'availability-targets.csv')}
    hashes={'data/prepared/targets.csv':sha(ROOT/'data/prepared/targets.csv')}
    if dataset=='nlcd':
        assert extension is not None and original is not None
        new=pd.read_csv(ROOT/'data/nlcd/prepared/targets.csv')
        t=pd.concat([old[old.before_year<=2018],new],ignore_index=True)
        more=pd.read_csv(extension/'availability-targets.csv');more=more[(more.model=='aef')&(more.support=='centre')]
        mask=pd.concat([mask,more[['point_id','common_pair_available']]],ignore_index=True)
        masks['extension_availability']=sha(extension/'availability-targets.csv')
        hashes['data/nlcd/prepared/targets.csv']=sha(ROOT/'data/nlcd/prepared/targets.csv')
    else:t=old
    assert mask.point_id.is_unique
    good=t.point_id.map(mask.set_index('point_id').common_pair_available)
    assert good.notna().all();good=good.to_numpy(bool)
    lat=np.deg2rad(t.y.to_numpy());lon=np.deg2rad(t.x.to_numpy())
    x=np.column_stack([np.sin(lat),np.cos(lat),np.sin(lon),np.cos(lon)])
    predictions=[];thresholds=[];fitting=[]
    for fold in range(5):
        early=(t.before_year.to_numpy()<=2018)&(t.region.to_numpy()!=fold)&good
        fit=early&~t.calibration_cell.to_numpy(bool);cal=early&t.calibration_cell.to_numpy(bool)
        test=(t.before_year.to_numpy()>=2019)&(t.region.to_numpy()==fold)&good
        states=np.concatenate([x[fit],x[fit]])
        labels=np.r_[(t.label_name_before.to_numpy()[fit]=='Trees'),(t.label_name_after.to_numpy()[fit]=='Trees')].astype(int)
        state_scores={}
        if len(np.unique(labels))==2:
            rf=RandomForestClassifier(n_estimators=300,min_samples_leaf=3,max_features='sqrt',class_weight='balanced_subsample',
                                     random_state=SEED,n_jobs=1)
            rf.fit(states,labels,sample_weight=np.full(len(labels),.5))
            scaler=StandardScaler().fit(states)
            lr=LogisticRegression(C=1,class_weight='balanced',solver='lbfgs',max_iter=2000,random_state=SEED)
            lr.fit(scaler.transform(states),labels,sample_weight=np.full(len(labels),.5))
            state_scores=dict(coordinate_state_forest=rf.predict_proba(x)[:,1],
                              coordinate_state_logistic=lr.predict_proba(scaler.transform(x))[:,1])
        for task in ['gain','loss']:
            relevant=t[f'{task}_task'].to_numpy(bool);truth=t[f'{task}_positive'].to_numpy(bool)
            scores={k:(v if task=='gain' else -v) for k,v in state_scores.items()}
            taskfit=fit&relevant
            if len(np.unique(truth[taskfit]))==2:
                gb=HistGradientBoostingClassifier(max_iter=150,learning_rate=.05,max_leaf_nodes=7,min_samples_leaf=10,
                    l2_regularization=1,early_stopping=False,class_weight='balanced',random_state=SEED)
                gb.fit(x[taskfit],truth[taskfit].astype(int));scores['coordinate_direct_boosting']=gb.predict_proba(x)[:,1]
            for method in METHODS:
                score=scores.get(method,np.full(len(t),np.nan));ci=cal&relevant&~truth&np.isfinite(score)
                ti=test&relevant&np.isfinite(score);valid=ci.sum()>=10
                threshold=float(np.quantile(score[ci],.9,method='higher')) if valid else None
                base=dict(availability_mode='paired',model='coordinates_only',support='centre',fold=fold,seed=SEED,
                          reference_mode='not_applicable',task=task,method=method)
                thresholds.append(dict(**base,calibration_negatives=int(ci.sum()),threshold=threshold,
                    calibration_false_flags=int((score[ci]>threshold).sum()) if valid else None,
                    calibration_ties=int((score[ci]==threshold).sum()) if valid else None,test_rows=int(ti.sum()),available=bool(valid)))
                fitting.append(dict(fold=fold,task=task,method=method,fit_pairs=int(taskfit.sum()) if 'direct' in method else int(fit.sum()),
                                    fit_states=None if 'direct' in method else len(labels),features=4,available=method in scores))
                if not valid:continue
                for j in np.flatnonzero(ti):
                    predictions.append(dict(**base,point_id=t.point_id[j],block=t.block[j],before_year=int(t.before_year[j]),
                        truth=int(truth[j]),score=float(score[j]),threshold=threshold,flag=int(score[j]>threshold)))
    pred=pd.DataFrame(predictions);th=pd.DataFrame(thresholds)
    if dataset=='nlcd':
        previous=pd.read_csv(original/'thresholds.csv');keys=['model','support','fold','seed','reference_mode','task','method']
        eq=th.merge(previous,on=keys,suffixes=('_new','_old'),validate='one_to_one');assert len(eq)==len(th)
        np.testing.assert_allclose(eq.threshold_new,eq.threshold_old,rtol=0,atol=1e-12,equal_nan=True)
        assert (eq.calibration_negatives_new==eq.calibration_negatives_old).all()
        assert (eq.available_new==eq.available_old).all();eq.to_csv(output/'threshold-equality.csv',index=False)
        meta=new.set_index('point_id');reports=[]
        for horizon in ['overlapping_2019_2021','beyond_2021']:
            for agreement in ['primary','unambiguous']:
                ids=meta.index[(meta.horizon==horizon)&(meta.unambiguous if agreement=='unambiguous' else True)]
                q=pred[pred.point_id.isin(ids)].copy();q['availability_mode']=f'nlcd_{horizon}_{agreement}';reports.append(q)
        pred=pd.concat(reports,ignore_index=True)
    metrics,_,strata=summarize(pred)
    pred.to_parquet(output/'predictions.parquet',index=False);metrics.to_csv(output/'metrics.csv',index=False)
    th.to_csv(output/'thresholds.csv',index=False);strata.to_csv(output/'strata.csv',index=False)
    pd.DataFrame(fitting).to_csv(output/'fitting-counts.csv',index=False)
    (output/'input-sha256.json').write_text(json.dumps(hashes,sort_keys=True,indent=2)+'\n')
    (output/'availability-mask-sha256.json').write_text(json.dumps(masks,sort_keys=True,indent=2)+'\n')
    (output/'summary.json').write_text(json.dumps(dict(exploratory=True,dataset=dataset,features='Four sine/cosine latitude/longitude coordinates',
        no_embedding_values_supplied_to_learners=True,availability_mask_uses_both_products_both_years=True,
        no_year_or_initial_subclass_feature=True,independent_baseline_count=1),indent=2)+'\n')
    print(metrics.to_string(index=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--dataset',choices=['lcmap','nlcd'],required=True)
    p.add_argument('--main',type=Path,required=True);p.add_argument('--extension',type=Path);p.add_argument('--original',type=Path)
    a=p.parse_args();geography(a.output,a.dataset,a.main,a.extension,a.original)
