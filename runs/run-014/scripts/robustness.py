"""Exploratory v12 checks fixed after first AlphaEarth scores, without test tuning."""
import os
os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
import argparse,io,json,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from pyproj import Transformer,Geod
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from features import load_features,matrix,unit,MODELS
from analyse import allocation,make_predictions,summarize,SEED
from record import ROOT

ADDED=['baseline_cohort_random_forest','baseline_cohort_logistic','embedding_matched_controls']

def additional_predictions(vec,t,refs,controls,models,mode,fpr,state_input='after'):
    assert state_input in ['before','after']
    feature_id=t.feature_point_id if 'feature_point_id' in t else t.point_id
    ids0=feature_id+'-'+t.before_year.astype(str);ids1=feature_id+'-'+t.after_year.astype(str)
    min_before=int(t.before_year.min());max_after=int(t.after_year.max())
    arrays={(m,y):matrix(vec,m,'centre',ids0 if y==0 else ids1) for m in models for y in [0,1]}
    complete={m:np.isfinite(arrays[m,0]).all(1)&np.isfinite(arrays[m,1]).all(1) for m in models}
    common=np.logical_and.reduce(list(complete.values()))
    role=allocation(refs,SEED)
    cohort=pd.concat([refs.assign(binary_class=1),controls.assign(binary_class=0)],ignore_index=True)
    predictions=[];thresholds=[];fitting=[];matching=[]
    for model in models:
        a,b=arrays[model,0],arrays[model,1];good=common if mode=='paired' else complete[model]
        state=np.concatenate([matrix(vec,model,'centre',cohort.point_id+'-'+str(y)) for y in [2017,2018]])
        labels=np.tile(cohort.binary_class.to_numpy(),2);regions=np.tile(cohort.region.to_numpy(),2)
        plotids=np.tile(cohort.point_id.to_numpy(),2)
        rr={y:matrix(vec,model,'centre',refs.point_id+'-'+str(y)) for y in range(2017,max_after+1)}
        cc={y:matrix(vec,model,'centre',controls.point_id+'-'+str(y)) for y in range(2017,max_after+1)}
        for fold in range(5):
            early=(t.before_year.to_numpy()<=2018)&(t.region.to_numpy()!=fold)&good
            cal=early&t.calibration_cell.to_numpy(bool)
            test=(t.before_year.to_numpy()>=2019)&(t.region.to_numpy()==fold)&good
            train=(regions!=fold)&np.isfinite(state).all(1)
            ntrees=len(np.unique(plotids[train&(labels==1)]));nnon=len(np.unique(plotids[train&(labels==0)]))
            fitting.append(dict(model=model,fold=fold,states=int(train.sum()),tree_plots=ntrees,non_tree_plots=nnon,
                                available=min(ntrees,nnon)>=8))
            scores={m:np.full(len(t),np.nan) for m in ADDED}
            if min(ntrees,nnon)>=8:
                rf=RandomForestClassifier(n_estimators=300,min_samples_leaf=3,max_features='sqrt',
                    class_weight='balanced_subsample',random_state=SEED,n_jobs=1)
                rf.fit(state[train],labels[train],sample_weight=np.full(train.sum(),.5))
                scaler=StandardScaler().fit(state[train])
                lr=LogisticRegression(C=1,class_weight='balanced',solver='lbfgs',max_iter=2000,random_state=SEED)
                lr.fit(scaler.transform(state[train]),labels[train],sample_weight=np.full(train.sum(),.5))
                target_state=b if state_input=='after' else a
                scores['baseline_cohort_random_forest'][good]=rf.predict_proba(target_state[good])[:,1]
                scores['baseline_cohort_logistic'][good]=lr.predict_proba(scaler.transform(target_state[good]))[:,1]
            ri=(role=='R')&(refs.region.to_numpy()!=fold);ci=(role=='C')&(refs.region.to_numpy()!=fold)
            for task in ['gain','loss']:
                matchscore=np.full(len(t),np.nan)
                for year in range(min_before,max_after):
                    ix=np.flatnonzero((t.before_year.to_numpy()==year)&t[f'{task}_task'].to_numpy(bool))
                    r0=rr[year][ri];r0=r0[np.isfinite(r0).all(1)]
                    if task=='gain':
                        c0,c1=cc[year],cc[year+1];outside=controls.region.to_numpy()!=fold
                    else:c0,c1=rr[year][ci],rr[year+1][ci];outside=np.ones(ci.sum(),bool)
                    cv=outside&np.isfinite(c0).all(1)&np.isfinite(c1).all(1)
                    matching.append(dict(model=model,fold=fold,task=task,before_year=year,
                                         references=len(r0),controls=int(cv.sum()),available=len(r0)>=8 and cv.sum()>=8))
                    if len(r0)<8 or cv.sum()<8:continue
                    reference=unit(r0.mean(0));similarity=a[ix]@c0[cv].T
                    selected=np.argsort(-similarity,axis=1,kind='stable')[:,:8]
                    changes=(c1[cv]-c0[cv])@reference
                    matchscore[ix]=(b[ix]-a[ix])@reference-changes[selected].mean(1)
                directed={k:v if task=='gain' else -v for k,v in scores.items() if k!='embedding_matched_controls'}
                directed['embedding_matched_controls']=matchscore if task=='gain' else -matchscore
                relevant=t[f'{task}_task'].to_numpy(bool);truth=t[f'{task}_positive'].to_numpy(bool)
                for method,score in directed.items():
                    cidx=cal&relevant&~truth&np.isfinite(score);tidx=test&relevant&np.isfinite(score)
                    valid=cidx.sum()>=10;threshold=float(np.quantile(score[cidx],1-fpr,method='higher')) if valid else None
                    base=dict(availability_mode=mode,model=model,support='centre',fold=fold,seed=SEED,
                              reference_mode='global',task=task,method=method)
                    thresholds.append(dict(**base,calibration_negatives=int(cidx.sum()),threshold=threshold,
                        calibration_false_flags=int((score[cidx]>threshold).sum()) if valid else None,
                        calibration_ties=int((score[cidx]==threshold).sum()) if valid else None,
                        test_rows=int(tidx.sum()),available=bool(valid)))
                    if not valid:continue
                    for j in np.flatnonzero(tidx):
                        predictions.append(dict(**base,point_id=t.point_id[j],block=t.block[j],before_year=int(t.before_year[j]),
                                                truth=int(truth[j]),score=float(score[j]),threshold=threshold,flag=int(score[j]>threshold)))
    return pd.DataFrame(predictions),pd.DataFrame(thresholds),pd.DataFrame(fitting),pd.DataFrame(matching)

def label_audit(refs,controls,output):
    with zipfile.ZipFile(ROOT/'data/aef-evaluation.zip') as z:
        source=pd.read_csv(io.BytesIO(z.read('evaluation/lcmap/lcmap_lc/lcmap_lc.csv')))
    source['year']=pd.to_datetime(source.valid_time_start_ms,unit='ms',utc=True).dt.year
    project=Transformer.from_crs('EPSG:4326','EPSG:5070',always_xy=True)
    sx,sy=project.transform(source.x,source.y);tree=cKDTree(np.column_stack([sx,sy]))
    roles=allocation(refs,SEED)
    cohort=pd.concat([refs.assign(audit_role=np.where(roles=='R','reference','tree_control')),
                      controls.assign(audit_role='non_tree_control')],ignore_index=True)
    geod=Geod(ellps='WGS84');rows=[]
    for r in cohort.itertuples():
        x,y=project.transform(r.x,r.y);near=tree.query_ball_point([x,y],1.2)
        candidates=[]
        for j in near:
            s=source.iloc[j];distance=geod.inv(r.x,r.y,s.x,s.y)[2]
            if distance<=1:candidates.append((j,distance))
        rec=dict(point_id=r.point_id,role=r.audit_role,matches_within_1m=len(candidates),matched=len(candidates)==1,
                 year=None,label=None,distance_m=None,baseline_agreement=None,later_binary_cover_agreement=None)
        if len(candidates)==1:
            j,distance=candidates[0];s=source.iloc[j]
            rec.update(year=int(s.year),label=s.label_name,distance_m=distance)
            if s.year in [2017,2018]:rec['baseline_agreement']=s.label_name==r.label_name_before
            if s.year>=2019:rec['later_binary_cover_agreement']=(s.label_name=='Trees')==(r.audit_role!='non_tree_control')
        rows.append(rec)
    df=pd.DataFrame(rows);df.to_csv(output/'partial-label-audit.csv',index=False)
    grouped=[]
    for role,g in df.groupby('role'):
        late=g[g.year>=2019]
        grouped.append(dict(role=role,cohort=len(g),unique_matches=int(g.matched.sum()),
            later_labels=len(late),later_binary_agreement=int(late.later_binary_cover_agreement.fillna(False).sum()),
            later_binary_disagreement=int((~late.later_binary_cover_agreement.fillna(True).astype(bool)).sum()),
            baseline_labels=int(g.baseline_agreement.notna().sum()),
            baseline_conflicts=int((g.baseline_agreement==False).sum()),unknown_later=len(g)-len(late)))
    pd.DataFrame(grouped).to_csv(output/'partial-label-audit-summary.csv',index=False)

def robust(output,baseline,models):
    output.mkdir(parents=True,exist_ok=False);mode='model_specific' if len(models)==1 else 'paired'
    vec,av,hashes,_=load_features(include_controls=True,models=models)
    assert av.file_present.all(),'Close the chosen original/control acquisition first'
    t=pd.read_csv(ROOT/'data/prepared/targets.csv');refs=pd.read_csv(ROOT/'data/prepared/references.csv')
    controls=pd.read_csv(ROOT/'data/controls/controls.csv')
    base=pd.read_parquet(baseline/'predictions.parquet')
    base=base[(base.availability_mode==mode)&base.model.isin(models)&(base.support=='centre')&
              (base.seed==SEED)&(base.reference_mode=='global')].copy()
    assert len(base)>0
    bt=pd.read_csv(baseline/'thresholds.csv')
    bt=bt[(bt.availability_mode==mode)&bt.model.isin(models)&(bt.support=='centre')&
          (bt.seed==SEED)&(bt.reference_mode=='global')].copy()
    new,th,fit,match=additional_predictions(vec,t,refs,controls,models,mode,.1)
    combined=pd.concat([base,new],ignore_index=True)
    combined.to_parquet(output/'predictions.parquet',index=False)
    metrics,pairs,strata=summarize(combined)
    metrics.to_csv(output/'metrics.csv',index=False);pairs.to_csv(output/'paired-comparisons.csv',index=False)
    strata.to_csv(output/'strata.csv',index=False);th.to_csv(output/'thresholds.csv',index=False)
    fit.to_csv(output/'fitting-counts.csv',index=False);match.to_csv(output/'matching-counts.csv',index=False)
    curves=[];curve_thresholds=[]
    for fpr in [.05,.1,.2]:
        if fpr==.1:q=combined.copy();ct=pd.concat([bt,th],ignore_index=True)
        else:
            p,ct,*_=make_predictions(vec,t,refs,availability_mode=mode,seeds=[SEED],reference_modes=['global'],models=models,calibration_fpr=fpr)
            p=p[p.support=='centre'].copy();ct=ct[ct.support=='centre'].copy()
            more,mt,*_=additional_predictions(vec,t,refs,controls,models,mode,fpr)
            q=pd.concat([p,more],ignore_index=True);ct=pd.concat([ct,mt],ignore_index=True)
            keys=['model','fold','task','method','point_id']
            a=q.sort_values(keys).reset_index(drop=True);b=combined.sort_values(keys).reset_index(drop=True)
            assert a[keys].equals(b[keys]);np.testing.assert_allclose(a.score,b.score,rtol=0,atol=1e-12)
        q['availability_mode']=f'{mode}_fpr_{int(fpr*100):02d}';ct['nominal_fpr']=fpr
        curves.append(q);curve_thresholds.append(ct)
    curve=pd.concat(curves,ignore_index=True);cm,cp,cs=summarize(curve)
    curve.to_parquet(output/'calibration-predictions.parquet',index=False)
    cm.to_csv(output/'calibration-metrics.csv',index=False);cp.to_csv(output/'calibration-paired.csv',index=False)
    pd.concat(curve_thresholds,ignore_index=True).to_csv(output/'calibration-thresholds.csv',index=False)
    label_audit(refs,controls,output)
    (output/'input-sha256.json').write_text(json.dumps(hashes,sort_keys=True,indent=2)+'\n')
    (output/'summary.json').write_text(json.dumps(dict(exploratory=True,models=models,availability_mode=mode,
        calibration_score_invariance=True,nominal_fprs=[.05,.1,.2],added_methods=ADDED),indent=2)+'\n')
    print(metrics[metrics.method.isin(ADDED)].to_string(index=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--models',nargs='+',choices=MODELS,default=MODELS)
    a=p.parse_args();robust(a.output,a.baseline,a.models)
