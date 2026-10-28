"""Pre-analysis v2 boundary comparisons; reuse the v1 fitted predictions."""
import os
os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from analyse import allocation,spatial_distances,summarize,SEED
from features import load_features,matrix,unit,MODELS,SUPPORTS
from record import ROOT

def make_secondary_predictions(vec,t,refs,controls):
    dcontrol=spatial_distances(t,controls)
    pred=[];thresholds=[];counts=[]
    feature_id=t['feature_point_id'] if 'feature_point_id' in t else t.point_id
    ids0=feature_id+'-'+t.before_year.astype(str);ids1=feature_id+'-'+t.after_year.astype(str)
    max_after=int(t.after_year.max());min_before=int(t.before_year.min())
    roles=allocation(refs,SEED)
    for support in SUPPORTS:
        arr={(m,y):matrix(vec,m,support,ids0 if y==0 else ids1) for m in MODELS for y in [0,1]}
        good=np.logical_and.reduce([np.isfinite(v).all(1) for v in arr.values()])
        for model in MODELS:
            a,b=arr[model,0],arr[model,1]
            rr={y:matrix(vec,model,support,refs.point_id+'-'+str(y)) for y in range(2017,max_after+1)}
            cc={y:matrix(vec,model,support,controls.point_id+'-'+str(y)) for y in range(2017,max_after+1)}
            for fold in range(5):
                early=(t.before_year.to_numpy()<=2018)&(t.region.to_numpy()!=fold)&good
                test=(t.before_year.to_numpy()>=2019)&(t.region.to_numpy()==fold)&good
                cal=early&t.calibration_cell.to_numpy(bool)
                ri=(roles=='R')&(refs.region.to_numpy()!=fold)
                ci=(roles=='C')&(refs.region.to_numpy()!=fold)
                outside=controls.region.to_numpy()!=fold
                scores={k:np.full(len(t),np.nan) for k in ['non_tree_control_adjusted','class_matched_control_adjusted',
                         'nearest8_non_tree_control_adjusted','frozen_2017','frozen_2017_control_adjusted']}
                r17=rr[2017][ri];r17=r17[np.isfinite(r17).all(1)]
                frozen=unit(r17.mean(0)) if len(r17)>=8 else None
                for year in range(min_before,max_after):
                    ix=np.flatnonzero(t.before_year.to_numpy()==year)
                    r0=rr[year][ri];r0=r0[np.isfinite(r0).all(1)]
                    c0,c1=cc[year],cc[year+1]
                    cv=outside&np.isfinite(c0).all(1)&np.isfinite(c1).all(1)
                    tc0,tc1=rr[year][ci],rr[year+1][ci]
                    tv=np.isfinite(tc0).all(1)&np.isfinite(tc1).all(1)
                    counts.append(dict(model=model,support=support,fold=fold,before_year=year,
                                       valid_non_tree_controls=int(cv.sum()),valid_tree_controls=int(tv.sum()),
                                       valid_grass_controls=int((cv&(controls.label_name_before.to_numpy()=='Grass/forb/herb')).sum()),
                                       valid_shrub_controls=int((cv&(controls.label_name_before.to_numpy()=='Shrubs')).sum()),
                                       valid_reference_start=len(r0),valid_reference_2017=len(r17)))
                    if frozen is not None:
                        sf=(b[ix]-a[ix])@frozen;scores['frozen_2017'][ix]=sf
                        if tv.sum()>=8:scores['frozen_2017_control_adjusted'][ix]=sf-((tc1[tv]-tc0[tv])@frozen).mean()
                    if len(r0)<8:continue
                    ref=unit(r0.mean(0));start=(b[ix]-a[ix])@ref
                    if cv.sum()>=8:
                        change=(c1[cv]-c0[cv])@ref
                        scores['non_tree_control_adjusted'][ix]=start-change.mean()
                        nearest=np.argsort(dcontrol[ix][:,cv],axis=1)[:,:8]
                        scores['nearest8_non_tree_control_adjusted'][ix]=start-change[nearest].mean(1)
                    for cover in ['Grass/forb/herb','Shrubs']:
                        match=cv&(controls.label_name_before.to_numpy()==cover)
                        ids=ix[t.label_name_before.to_numpy()[ix]==cover]
                        if match.sum()>=8:
                            scores['class_matched_control_adjusted'][ids]=(b[ids]-a[ids])@ref-((c1[match]-c0[match])@ref).mean()
                for task in ['gain','loss']:
                    relevant=t[f'{task}_task'].to_numpy(bool);truth=t[f'{task}_positive'].to_numpy(bool)
                    for method,value in scores.items():
                        if task=='loss' and 'frozen_2017' not in method:continue
                        score=value if task=='gain' else -value
                        cidx=cal&relevant&~truth&np.isfinite(score);tidx=test&relevant&np.isfinite(score)
                        base=dict(availability_mode='paired',model=model,support=support,fold=fold,seed=SEED,
                                  reference_mode='global',task=task,method=method)
                        valid=cidx.sum()>=10;threshold=float(np.quantile(score[cidx],.9,method='higher')) if valid else None
                        thresholds.append(dict(**base,calibration_negatives=int(cidx.sum()),threshold=threshold,
                                               calibration_false_flags=int((score[cidx]>threshold).sum()) if valid else None,
                                               calibration_ties=int((score[cidx]==threshold).sum()) if valid else None,
                                               test_rows=int(tidx.sum()),available=bool(valid)))
                        if not valid:continue
                        for j in np.flatnonzero(tidx):
                            pred.append(dict(**base,point_id=t.point_id[j],block=t.block[j],before_year=int(t.before_year[j]),
                                             truth=int(truth[j]),score=float(score[j]),threshold=threshold,flag=int(score[j]>threshold)))
    return pd.DataFrame(pred),pd.DataFrame(thresholds),pd.DataFrame(counts)

def secondary(output,baseline):
    output.mkdir(parents=True,exist_ok=False)
    vec,availability,hashes,metadata=load_features(include_controls=True)
    t=pd.read_csv(ROOT/'data/prepared/targets.csv');refs=pd.read_csv(ROOT/'data/prepared/references.csv')
    controls=pd.read_csv(ROOT/'data/controls/controls.csv')
    new,thresholds,counts=make_secondary_predictions(vec,t,refs,controls)
    base=pd.read_parquet(baseline/'predictions.parquet')
    old=base[(base.availability_mode=='paired')&(base.seed==SEED)&(base.reference_mode=='global')]
    combined=pd.concat([old,new],ignore_index=True)
    metrics,comparisons,strata=summarize(combined)
    combined.to_parquet(output/'predictions.parquet',index=False)
    thresholds.to_csv(output/'thresholds.csv',index=False)
    counts.to_csv(output/'control-availability.csv',index=False)
    metrics.to_csv(output/'metrics.csv',index=False);comparisons.to_csv(output/'paired-comparisons.csv',index=False)
    strata.to_csv(output/'strata.csv',index=False)
    (output/'input-sha256.json').write_text(json.dumps(hashes,indent=2,sort_keys=True)+'\n')
    print(metrics[(metrics.support=='centre')&metrics.method.isin(new.method.unique())].to_string(index=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True)
    a=p.parse_args();secondary(a.output,a.baseline)
