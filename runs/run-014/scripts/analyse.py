"""Offline prespecified transfer-screening evaluation from bundled patches."""
import os
os.environ['OMP_NUM_THREADS']='1'
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['MKL_NUM_THREADS']='1'
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Geod
from sklearn.ensemble import RandomForestClassifier,HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from features import load_features,matrix,unit,MODELS,SUPPORTS,target_coverage
from prepare import digest
from record import ROOT

SEED=14014
UNSUP=['start_fixed','end_fixed','pooled_fixed','concurrent','control_adjusted','standardized_concurrent',
       'subsequent_reference_similarity','cosine_change']

def reference_scores(a,b,ra,rb,ca,cb,nearest=False,dist_r=None,dist_c=None,paired_reference_membership=False):
    """Independent controls; use each year's valid reference means globally."""
    n,d=a.shape
    if nearest:
        rv=np.isfinite(ra).all(1)&np.isfinite(rb).all(1)
        cv=np.isfinite(ca).all(1)&np.isfinite(cb).all(1)
        if rv.sum()<8 or cv.sum()<8:return None
        ir=np.argsort(np.where(rv,dist_r,np.inf),axis=1)[:,:8]
        ic=np.argsort(np.where(cv,dist_c,np.inf),axis=1)[:,:8]
        r0=unit(ra[ir].mean(1));r1=unit(rb[ir].mean(1))
        c0=ca[ic];c1=cb[ic]
    else:
        rva=np.isfinite(ra).all(1);rvb=np.isfinite(rb).all(1)
        if paired_reference_membership:rva=rva&rvb;rvb=rva.copy()
        cv=np.isfinite(ca).all(1)&np.isfinite(cb).all(1)
        if min(rva.sum(),rvb.sum(),cv.sum())<8:return None
        r0=np.broadcast_to(unit(ra[rva].mean(0)),(n,d))
        r1=np.broadcast_to(unit(rb[rvb].mean(0)),(n,d))
        c0=np.broadcast_to(ca[cv],(n,int(cv.sum()),d));c1=np.broadcast_to(cb[cv],(n,int(cv.sum()),d))
    pooled=unit(r0+r1)
    dot=lambda x,y:np.einsum('ij,ij->i',x,y)
    start=dot(b-a,r0);end=dot(b-a,r1);conc=dot(b,r1)-dot(a,r0)
    c_start=np.einsum('ikd,id->ik',c1-c0,r0).mean(1)
    c_pre=np.einsum('ikd,id->ik',c0,r0);c_post=np.einsum('ikd,id->ik',c1,r1)
    sd0=c_pre.std(1,ddof=1);sd1=c_post.std(1,ddof=1)
    z=(dot(b,r1)-c_post.mean(1))/np.where(sd1>1e-8,sd1,np.nan)-(dot(a,r0)-c_pre.mean(1))/np.where(sd0>1e-8,sd0,np.nan)
    return dict(start_fixed=start,end_fixed=end,pooled_fixed=dot(b-a,pooled),concurrent=conc,
                control_adjusted=start-c_start,standardized_concurrent=z,subsequent_reference_similarity=dot(b,r1))

def allocation(refs,seed):
    hashes=np.array([digest(seed,'reference',p) for p in refs.point_id])
    order=np.argsort(hashes);roles=np.full(len(refs),'C');roles[order[:len(refs)//2]]='R'
    return roles

def spatial_distances(targets,refs):
    n,m=len(targets),len(refs)
    lon0=np.broadcast_to(targets.x.to_numpy()[:,None],(n,m))
    lat0=np.broadcast_to(targets.y.to_numpy()[:,None],(n,m))
    lon1=np.broadcast_to(refs.x.to_numpy()[None,:],(n,m))
    lat1=np.broadcast_to(refs.y.to_numpy()[None,:],(n,m))
    return Geod(ellps='WGS84').inv(lon0.ravel(),lat0.ravel(),lon1.ravel(),lat1.ravel())[2].reshape(n,m)

def fit_supervised(a,b,t,fit,task,include_initial=False):
    state=np.r_[a[fit],b[fit]]
    labels=np.r_[(t.label_name_before.to_numpy()[fit]=='Trees'),(t.label_name_after.to_numpy()[fit]=='Trees')].astype(int)
    scores={}
    if len(np.unique(labels))==2:
        rf=RandomForestClassifier(n_estimators=300,min_samples_leaf=3,max_features='sqrt',
                                  class_weight='balanced_subsample',random_state=SEED,n_jobs=1)
        rf.fit(state,labels,sample_weight=np.full(len(labels),.5))
        good=np.isfinite(a).all(1)&np.isfinite(b).all(1)
        s=np.full(len(t),np.nan);s[good]=rf.predict_proba(b[good])[:,1]-rf.predict_proba(a[good])[:,1]
        scores['state_random_forest']=s if task=='gain' else -s
        post=np.full(len(t),np.nan);post[good]=rf.predict_proba(b[good])[:,1]
        scores['subsequent_state_random_forest']=post if task=='gain' else -post
        if include_initial:
            initial=np.full(len(t),np.nan);initial[good]=rf.predict_proba(a[good])[:,1]
            scores['initial_state_random_forest']=initial if task=='gain' else -initial
        scaler=StandardScaler().fit(state)
        lr=LogisticRegression(C=1,class_weight='balanced',solver='lbfgs',max_iter=2000,random_state=SEED)
        lr.fit(scaler.transform(state),labels,sample_weight=np.full(len(labels),.5))
        post_lr=np.full(len(t),np.nan);post_lr[good]=lr.predict_proba(scaler.transform(b[good]))[:,1]
        scores['subsequent_state_logistic']=post_lr if task=='gain' else -post_lr
    relevant=t[f'{task}_task'].to_numpy(bool)&fit
    y=t[f'{task}_positive'].to_numpy(int)
    if len(np.unique(y[relevant]))==2:
        x=np.concatenate([a,b,b-a],axis=1)
        gb=HistGradientBoostingClassifier(max_iter=150,learning_rate=.05,max_leaf_nodes=7,
                                         min_samples_leaf=10,l2_regularization=1,early_stopping=False,
                                         class_weight='balanced',random_state=SEED)
        gb.fit(x[relevant],y[relevant])
        good=np.isfinite(x).all(1);s=np.full(len(t),np.nan)
        s[good]=gb.predict_proba(x[good])[:,1];scores['direct_gradient_boosting']=s
    return scores

def make_predictions(vectors,t,refs,availability_mode='paired',seeds=range(SEED,SEED+5),reference_modes=('global','nearest8'),models=MODELS,calibration_fpr=.1,gain_stable_negatives=False,paired_reference_membership=False,include_test_region_references=False):
    assert 0<calibration_fpr<1
    predictions=[];thresholds=[];folds=[];identities=[];near_dist=[]
    distances=spatial_distances(t,refs)
    feature_id=t['feature_point_id'] if 'feature_point_id' in t else t.point_id
    ids0=feature_id+'-'+t.before_year.astype(str);ids1=feature_id+'-'+t.after_year.astype(str)
    max_after=int(t.after_year.max());min_before=int(t.before_year.min())
    for support in SUPPORTS:
        arrays={(m,y):matrix(vectors,m,support,ids0 if y==0 else ids1) for m in MODELS for y in [0,1]}
        complete={m:np.isfinite(arrays[m,0]).all(1)&np.isfinite(arrays[m,1]).all(1) for m in MODELS}
        common=complete['aef']&complete['tessera']
        for model in models:
            a,b=arrays[model,0],arrays[model,1]
            good=common if availability_mode=='paired' else complete[model]
            ref_arrays={year:matrix(vectors,model,support,refs.point_id+'-'+str(year)) for year in range(2017,max_after+1)}
            for fold in range(5):
                early=(t.before_year.to_numpy()<=2018)&(t.region.to_numpy()!=fold)&good
                test=(t.before_year.to_numpy()>=2019)&(t.region.to_numpy()==fold)&good
                cal=early&t.calibration_cell.to_numpy(bool);fit=early&~t.calibration_cell.to_numpy(bool)
                sup={task:fit_supervised(a,b,t,fit,task) for task in ['gain','loss']}
                for seed in seeds:
                    role=allocation(refs,seed)
                    allowed=np.ones(len(refs),dtype=bool) if include_test_region_references else refs.region.to_numpy()!=fold
                    ri=(role=='R')&allowed;ci=(role=='C')&allowed
                    for refmode in reference_modes:
                        # Supervised models do not depend on allocation or reference mode.
                        scores={key:np.full(len(t),np.nan) for key in UNSUP}
                        scores['cosine_change']=1-np.einsum('ij,ij->i',a,b)
                        for year in range(min_before,max_after):
                            ix=np.flatnonzero(t.before_year.to_numpy()==year)
                            ra,rb=ref_arrays[year][ri],ref_arrays[year+1][ri]
                            ca,cb=ref_arrays[year][ci],ref_arrays[year+1][ci]
                            info=dict(availability_mode=availability_mode,model=model,support=support,fold=fold,
                                      seed=seed,reference_mode=refmode,before_year=year,
                                      reference_before=int(np.isfinite(ra).all(1).sum()),
                                      reference_after=int(np.isfinite(rb).all(1).sum()),
                                      control_pairs=int((np.isfinite(ca).all(1)&np.isfinite(cb).all(1)).sum()))
                            vals=reference_scores(a[ix],b[ix],ra,rb,ca,cb,refmode=='nearest8',distances[ix][:,ri],distances[ix][:,ci],paired_reference_membership=paired_reference_membership)
                            info['available']=vals is not None;folds.append(info)
                            if vals is None:continue
                            for key,value in vals.items():scores[key][ix]=value
                            active=good[ix]&test[ix]
                            if active.any():
                                s,e,c,adj=[vals[k][active] for k in ['start_fixed','end_fixed','concurrent','control_adjusted']]
                                identities.append(dict(**{k:info[k] for k in ['availability_mode','model','support','fold','seed','reference_mode','before_year']},
                                    n=int(active.sum()),start_end_equal=int(np.isclose(s,e,atol=1e-8,rtol=0).sum()),
                                    start_concurrent_equal=int(np.isclose(s,c,atol=1e-8,rtol=0).sum()),
                                    start_end_sign_reversed=int(((s*e<0)&(abs(s)>.01)&(abs(e)>.01)).sum()),
                                    start_concurrent_sign_reversed=int(((s*c<0)&(abs(s)>.01)&(abs(c)>.01)).sum()),
                                    adjustment_range=float(np.ptp(s-adj))))
                            if refmode=='nearest8' and seed==SEED:
                                rv=np.isfinite(ra).all(1)&np.isfinite(rb).all(1);cv=np.isfinite(ca).all(1)&np.isfinite(cb).all(1)
                                if rv.sum()>=8 and cv.sum()>=8:
                                    d8r=np.sort(distances[ix][:,ri][:,rv],axis=1)[:,7]
                                    d8c=np.sort(distances[ix][:,ci][:,cv],axis=1)[:,7]
                                    for j,dr,dc in zip(ix,d8r,d8c):
                                        if test[j]:near_dist.append(dict(model=model,support=support,point_id=t.point_id[j],before_year=year,reference_k8_m=dr,control_k8_m=dc))
                        for task in ['gain','loss']:
                            direction=1 if task=='gain' else -1
                            tscores={k:(v if k=='cosine_change' else v*direction) for k,v in scores.items()}
                            if seed==SEED and refmode=='global':tscores.update(sup[task])
                            relevant=t[f'{task}_task'].to_numpy(bool);truth=t[f'{task}_positive'].to_numpy(bool)
                            allowed_negative=(t.label_name_before.to_numpy()==t.label_name_after.to_numpy()) if task=='gain' and gain_stable_negatives else np.ones(len(t),bool)
                            for method,score in tscores.items():
                                cidx=cal&relevant&~truth&allowed_negative&np.isfinite(score)
                                tidx=test&relevant&(truth|allowed_negative)&np.isfinite(score)
                                base=dict(availability_mode=availability_mode,model=model,support=support,fold=fold,
                                          seed=seed,reference_mode=refmode,task=task,method=method)
                                valid=int(cidx.sum())>=10
                                threshold=float(np.quantile(score[cidx],1-calibration_fpr,method='higher')) if valid else None
                                thresholds.append(dict(**base,calibration_negatives=int(cidx.sum()),threshold=threshold,
                                                       calibration_false_flags=int((score[cidx]>threshold).sum()) if valid else None,
                                                       calibration_ties=int((score[cidx]==threshold).sum()) if valid else None,
                                                       test_rows=int(tidx.sum()),available=valid))
                                if not valid:continue
                                for j in np.flatnonzero(tidx):
                                    predictions.append(dict(**base,point_id=t.point_id[j],block=t.block[j],
                                                            before_year=int(t.before_year[j]),truth=int(truth[j]),
                                                            score=float(score[j]),threshold=threshold,flag=int(score[j]>threshold)))
    return pd.DataFrame(predictions),pd.DataFrame(thresholds),pd.DataFrame(folds),pd.DataFrame(identities),pd.DataFrame(near_dist)

GROUP=['availability_mode','model','support','seed','reference_mode','task']

def summarize(predictions):
    metrics=[];paired=[];strata=[]
    for key,g in predictions.groupby(GROUP,sort=True):
        base=dict(zip(GROUP,key));methods=sorted(g.method.unique(),key=lambda m:(m!='start_fixed',m))
        pivot=g.pivot(index='point_id',columns='method',values='flag')
        meta=g.drop_duplicates('point_id').set_index('point_id').loc[pivot.index]
        truth=meta.truth.to_numpy();blocks=meta.block.to_numpy();unique=np.unique(blocks)
        # Shared block bootstrap for all paired methods in this population.
        rng=np.random.default_rng(SEED)
        weights=rng.multinomial(len(unique),np.full(len(unique),1/len(unique)),size=2000)
        denp=np.array([((blocks==b)&(truth==1)).sum() for b in unique])
        denn=np.array([((blocks==b)&(truth==0)).sum() for b in unique])
        bp=weights@denp;bn=weights@denn;bootvalid=(bp>0)&(bn>0)
        boots={}
        for method in methods:
            mg=g[g.method==method];y=mg.truth.to_numpy();flag=mg.flag.to_numpy()
            tp=int(((y==1)&(flag==1)).sum());fp=int(((y==0)&(flag==1)).sum())
            pos=int((y==1).sum());neg=int((y==0).sum())
            tpr=tp/pos if pos else np.nan;fpr=fp/neg if neg else np.nan
            flags=pivot[method].to_numpy()
            # Unavailable per-row methods are not silently treated as negatives.
            allavailable=np.isfinite(flags).all()
            if allavailable:
                cntp=np.array([np.sum(flags[(blocks==b)&(truth==1)]) for b in unique])
                cntn=np.array([np.sum(flags[(blocks==b)&(truth==0)]) for b in unique])
                bt=(weights@cntp)[bootvalid]/bp[bootvalid];bf=(weights@cntn)[bootvalid]/bn[bootvalid]
                boots[method]=(bt,bf,bt-bf)
            intervals={}
            for name,arr in zip(['sensitivity','false_positive_rate','J'],boots.get(method,[[],[],[]])):
                lo,hi=np.quantile(arr,[.025,.975]) if len(arr) else (np.nan,np.nan)
                intervals.update({name+'_lo':lo,name+'_hi':hi})
            metrics.append(dict(**base,method=method,n_positive=pos,n_negative=neg,true_positive=tp,false_positive=fp,
                                sensitivity=tpr,false_positive_rate=fpr,J=tpr-fpr,
                                auroc=roc_auc_score(y,mg.score) if len(np.unique(y))==2 else np.nan,
                                bootstrap_valid=int(bootvalid.sum()) if allavailable else 0,
                                n_spatial_blocks=len(unique),threshold_ties=int((mg.score==mg.threshold).sum()),**intervals))
            for label,sg in list(mg.groupby('before_year'))+[(f'region_{f}',q) for f,q in mg.groupby('fold')]:
                sy=sg.truth.to_numpy();sf=sg.flag.to_numpy();sp=(sy==1).sum();sn=(sy==0).sum()
                strata.append(dict(**base,method=method,stratum=str(label),n_positive=int(sp),n_negative=int(sn),
                                   sensitivity=float(sf[sy==1].mean()) if sp else None,
                                   false_positive_rate=float(sf[sy==0].mean()) if sn else None))
            if method=='start_fixed' or 'start_fixed' not in pivot:continue
            both=mg.set_index('point_id').join(g[g.method=='start_fixed'].set_index('point_id')[['flag']],rsuffix='_start').dropna(subset=['flag_start'])
            same=int((both.flag==both.flag_start).sum())
            by=both.truth.to_numpy();bb=both.block.to_numpy();bd=(both.flag-both.flag_start).to_numpy()
            ub=np.unique(bb);pw=np.random.default_rng(SEED).multinomial(len(ub),np.full(len(ub),1/len(ub)),size=2000)
            pp=np.array([((bb==k)&(by==1)).sum() for k in ub]);pn=np.array([((bb==k)&(by==0)).sum() for k in ub])
            dp=np.array([bd[(bb==k)&(by==1)].sum() for k in ub]);dn=np.array([bd[(bb==k)&(by==0)].sum() for k in ub])
            bpp=pw@pp;bpn=pw@pn;ok=(bpp>0)&(bpn>0)
            dt=(pw@dp)[ok]/bpp[ok];df=(pw@dn)[ok]/bpn[ok]
            lo,hi=np.quantile(dt-df,[.025,.975]) if ok.any() else (np.nan,np.nan)
            ds=float(bd[by==1].mean()) if (by==1).any() else np.nan
            dfpr=float(bd[by==0].mean()) if (by==0).any() else np.nan
            paired.append(dict(**base,method=method,delta_J=ds-dfpr,delta_J_lo=lo,delta_J_hi=hi,
                               delta_sensitivity=ds,delta_false_positive_rate=dfpr,
                               paired_n_positive=int((by==1).sum()),paired_n_negative=int((by==0).sum()),
                               unchanged_flags=same,total_pairs=len(both),changed_flags=len(both)-same,
                               paired_bootstrap_valid=int(ok.sum())))
    return pd.DataFrame(metrics),pd.DataFrame(paired),pd.DataFrame(strata)

def analyse(output):
    output.mkdir(parents=True,exist_ok=False)
    vectors,availability,hashes,metadata=load_features()
    t=pd.read_csv(ROOT/'data/prepared/targets.csv');refs=pd.read_csv(ROOT/'data/prepared/references.csv')
    detail,coverage=target_coverage(vectors,t)
    detail.to_csv(output/'availability-targets.csv',index=False);coverage.to_csv(output/'coverage.csv',index=False)
    availability.to_csv(output/'availability.csv',index=False)
    (output/'input-sha256.json').write_text(json.dumps(hashes,sort_keys=True,indent=2)+'\n')
    (output/'embedding-metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    pred,threshold,folds,identities,near=make_predictions(vectors,t,refs)
    # Model-specific availability matters only if paired availability excluded cases.
    avc=availability.pivot(index='task_id',columns='model',values='centre_available')
    avp=availability.pivot(index='task_id',columns='model',values='patch_available')
    if not ((avc.aef==avc.tessera).all() and (avp.aef==avp.tessera).all()):
        extra=make_predictions(vectors,t,refs,'model_specific')
        pred=pd.concat([pred,extra[0]],ignore_index=True)
        threshold=pd.concat([threshold,extra[1]],ignore_index=True)
        folds=pd.concat([folds,extra[2]],ignore_index=True)
        identities=pd.concat([identities,extra[3]],ignore_index=True)
    pred.to_parquet(output/'predictions.parquet',index=False)
    threshold.to_csv(output/'thresholds.csv',index=False);folds.to_csv(output/'reference-availability.csv',index=False)
    identities.to_csv(output/'identities.csv',index=False);near.to_csv(output/'nearest-reference-distances.csv',index=False)
    metrics,paired,strata=summarize(pred)
    metrics.to_csv(output/'metrics.csv',index=False);paired.to_csv(output/'paired-comparisons.csv',index=False)
    strata.to_csv(output/'strata.csv',index=False)
    main=(metrics.availability_mode=='paired')&(metrics.support=='centre')&(metrics.seed==SEED)&(metrics.reference_mode=='global')
    metrics[main].to_csv(output/'main-table.csv',index=False)
    print(metrics[main].to_string(index=False),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    analyse(ap.parse_args().output)
