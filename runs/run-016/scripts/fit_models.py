"""Fit the prospectively specified classifiers; preserve point predictions."""
import argparse,json,time,warnings
from pathlib import Path
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.exceptions import ConvergenceWarning
from records import ROOT,now,digest

def load_population(manifest_path,rep,taxonomy):
    m=json.loads((ROOT/manifest_path).read_text());ids=m[taxonomy+'_ids']
    lookup=np.full(256,-1,np.int16);lookup[ids]=np.arange(len(ids))
    data={}
    for r in m['landscapes']:
        if r['status']!='included':continue
        ix=np.array(r['valid_indices'],int)
        with np.load(ROOT/r['path']) as z:y=lookup[z[taxonomy][:,ix]]
        assert (y>=0).all()
        x={}
        for ti,year in enumerate(m['years']):
            entries=[e for e in r['feature_inputs'] if e['year']==year and e['representation']==rep]
            if not entries:continue
            entry=entries[0]
            with np.load(ROOT/entry['path']) as z:
                if rep=='tessera':
                    v=z['values'][ix] if 'values' in z else z['raw_values'][ix].astype(np.float32)*z['scales'][ix,None]
                else:
                    raw=z['raw_values'][ix].astype(np.float32)
                    v=np.sign(raw)*(raw/np.float32(127.5))**2
                    v[(raw==-128).any(axis=1)]=np.nan
            if ti==0 or r['split']=='test':assert np.isfinite(v).all()
            x[ti]=v
        data[r['landscape_id']]=dict(x=x,y=y,record=r)
    return m,data

def fit(manifest_path,rep,taxonomy,kind,destination,refreshed=False,max_iter=1000):
    out=ROOT/destination
    if out.exists():raise FileExistsError('Do not overwrite fitted results; use a new destination')
    out.mkdir(parents=True);(out/'predictions').mkdir()
    m,data=load_population(manifest_path,rep,taxonomy);k=len(m[taxonomy+'_ids'])
    assert not m['status_counts'].get('incomplete',0),'Complete planned acquisition before fitting'
    train=[v for v in data.values() if v['record']['split']=='train']
    cal=[v for v in data.values() if v['record']['split']=='calibration']
    assert train and cal
    fit_records=[];models={};scalers={};probabilities={lid:np.full((5,len(d['y'][0]),k),np.nan,np.float32) for lid,d in data.items()}
    years=range(5) if refreshed else [0]
    for ti in years:
        started=now();begin=time.monotonic()
        assert all(ti in v['x'] for v in train),'Future training features required for refreshed diagnostic'
        xx=np.concatenate([v['x'][ti] for v in train]);yy=np.concatenate([v['y'][ti] for v in train])
        available=np.isfinite(xx).all(axis=1);excluded_training_points=int((~available).sum())
        xx=xx[available];yy=yy[available]
        scaler=StandardScaler();xx=scaler.fit_transform(xx)
        model=(LogisticRegression(C=1.,fit_intercept=True,max_iter=max_iter,tol=1e-5,solver='lbfgs',random_state=16016)
               if kind=='logistic' else RandomForestClassifier(n_estimators=200,min_samples_leaf=5,
                         max_features='sqrt',random_state=16016,n_jobs=4))
        print('FIT',rep,taxonomy,kind,'year',2021+ti,'shape',xx.shape,'classes',len(np.unique(yy)),flush=True)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always');model.fit(xx,yy)
        conv=[str(w.message) for w in caught if issubclass(w.category,ConvergenceWarning)]
        fit_records.append(dict(year=2021+ti,started_at_utc=started,ended_at_utc=now(),
                                elapsed_seconds=time.monotonic()-begin,training_points=len(yy),
                                excluded_training_points=excluded_training_points,
                                class_counts=np.bincount(yy,minlength=k).tolist(),classes=model.classes_.tolist(),
                                warnings=[dict(category=w.category.__name__,message=str(w.message)) for w in caught],
                                convergence_warnings=conv,iterations=getattr(model,'n_iter_',np.array([])).tolist()))
        models[ti]=model;scalers[ti]=scaler
        if kind=='logistic':
            np.savez_compressed(out/f'coefficients-{2021+ti}.npz',classes=model.classes_,coef=model.coef_,
                                intercept=model.intercept_,mean=scaler.mean_,scale=scaler.scale_)
        use_years=[ti] if refreshed else range(5)
        for lid,d in data.items():
            for target in use_years:
                if target not in d['x']:continue
                good=np.isfinite(d['x'][target]).all(axis=1)
                pp=model.predict_proba(scaler.transform(d['x'][target][good]))
                assert np.isfinite(pp).all() and np.allclose(pp.sum(axis=1),1.,atol=1e-6)
                result=np.zeros((good.sum(),k),np.float32);result[:,model.classes_]=pp.astype(np.float32)
                probabilities[lid][target][good]=result
        print('DONE FIT',rep,taxonomy,2021+ti,'seconds',round(time.monotonic()-begin,3),flush=True)
    diagnostics=[];prediction_files=[]
    for lid,d in data.items():
        p=probabilities[lid];target=out/'predictions'/f'{lid}.npz'
        np.savez_compressed(target,probabilities=p,labels=d['y'])
        prediction_files.append(dict(landscape_id=lid,path=str(target.relative_to(ROOT)),sha256=digest(target)))
        for ti in range(5):
            if not np.isfinite(p[ti]).all():continue
            truth=d['y'][ti];pred=p[ti].argmax(axis=1)
            supported=np.isin(truth,models[ti if refreshed else 0].classes_)
            diagnostics.append(dict(landscape_id=lid,split=d['record']['split'],year=2021+ti,
                                    n=len(truth),correct=int((truth==pred).sum()),
                                    accuracy=float((truth==pred).mean()),unsupported_points=int((~supported).sum()),
                                    true_class_counts=np.bincount(truth,minlength=k).tolist(),
                                    hard_class_counts=np.bincount(pred,minlength=k).tolist(),soft_means=p[ti].mean(axis=0,dtype=np.float64).tolist()))
    # Calibration represents source-year held-out geography, not target labels.
    pc=np.concatenate([probabilities[v['record']['landscape_id']][0] for v in cal])
    yc=np.concatenate([v['y'][0] for v in cal]);counts=np.bincount(yc,minlength=k)
    confusion=np.zeros((k,k),np.float64)
    for c in range(k):
        if counts[c]:confusion[:,c]=pc[yc==c].mean(axis=0,dtype=np.float64)
    sv=np.linalg.svd(confusion,compute_uv=False)
    np.savez_compressed(out/'source-calibration.npz',soft_confusion=confusion,class_counts=counts,
                        prior=counts/counts.sum(),singular_values=sv)
    run=dict(started_at_utc=fit_records[0]['started_at_utc'],ended_at_utc=now(),
             manifest_path=manifest_path,manifest_sha256=digest(ROOT/manifest_path),representation=rep,
             taxonomy=taxonomy,class_names=m[taxonomy+'_names'],classifier=kind,refreshed=refreshed,
             parameters=dict(C=1.,max_iter=max_iter,tol=1e-5) if kind=='logistic' else dict(n_estimators=200,min_samples_leaf=5,max_features='sqrt',seed=16016),
             fit_records=fit_records,prediction_files=prediction_files,diagnostics=diagnostics,
             calibration=dict(class_counts=counts.tolist(),rank=int(np.linalg.matrix_rank(confusion)),
                              singular_values=sv.tolist(),condition_number=float(sv[0]/sv[-1]) if sv[-1]>0 else None),
             note='Retrospective frozen-head test; representation pretraining holdout from target geography/years is not established')
    (out/'fit.json').write_text(json.dumps(run,indent=2)+'\n')
    print(json.dumps(dict(completed_at_utc=now(),predicted_landscapes=len(data),destination=destination)),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--representation',choices=['tessera','alphaearth'],required=True)
    p.add_argument('--taxonomy',choices=['broad','fine'],required=True);p.add_argument('--classifier',choices=['logistic','forest'],default='logistic')
    p.add_argument('--refreshed',action='store_true');p.add_argument('--destination',required=True)
    p.add_argument('--max-iter',type=int,default=1000);a=p.parse_args()
    fit(a.manifest,a.representation,a.taxonomy,a.classifier,a.destination,a.refreshed,a.max_iter)
