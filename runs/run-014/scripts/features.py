"""Offline construction of centre and patch features from bundled measurements."""
import hashlib,json
import numpy as np
import pandas as pd
from record import ROOT

MODELS=['aef','tessera']
SUPPORTS=['centre','patch']

def unit(x):
    n=np.linalg.norm(x,axis=-1,keepdims=True)
    return np.divide(x,n,out=np.full_like(x,np.nan,dtype=float),where=np.isfinite(n)&(n>1e-12))

def load_features(include_nlcd=False,include_controls=False,models=MODELS):
    tasks=pd.read_csv(ROOT/'data/prepared/tasks.csv')
    extra=ROOT/'data/controls/tasks.csv'
    if include_controls and extra.exists():tasks=pd.concat([tasks,pd.read_csv(extra)],ignore_index=True).drop_duplicates('task_id')
    future=ROOT/'data/nlcd/prepared/tasks.csv'
    if include_nlcd and future.exists():tasks=pd.concat([tasks,pd.read_csv(future)],ignore_index=True).drop_duplicates('task_id')
    vectors={(m,s):{} for m in MODELS for s in SUPPORTS}; availability=[]; hashes={}; metadata=[]
    for model in models:
        for t in tasks.itertuples():
            p=ROOT/f'data/embeddings/{model}/{t.task_id}.npz'
            if p.exists():
                with np.load(p,allow_pickle=False) as f:
                    raw=f['raw']; meta=json.loads(str(f['metadata']))
                if model=='aef':
                    vals=raw.astype(float);valid=(raw!=-128).all(axis=-1)
                    vals=np.sign(vals)*(vals/127.5)**2;vals[~valid]=np.nan
                else:vals=raw.astype(float)
                u=unit(vals)
                centre=u[1,1]
                patch=unit(u.mean(axis=(0,1))) if np.isfinite(u).all() else np.full(u.shape[-1],np.nan)
                vectors[model,'centre'][t.task_id]=centre
                vectors[model,'patch'][t.task_id]=patch
                hashes[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
                metadata.append(meta)
                cs=bool(np.isfinite(centre).all());ps=bool(np.isfinite(patch).all())
            else:cs=ps=False
            availability.append(dict(model=model,task_id=t.task_id,point_id=t.point_id,year=t.year,
                                     role=t.role,centre_available=cs,patch_available=ps,file_present=p.exists()))
    return vectors,pd.DataFrame(availability),hashes,metadata

def matrix(vectors,model,support,ids):
    d=64 if model=='aef' else 128
    return np.array([vectors[model,support].get(str(i),np.full(d,np.nan)) for i in ids],dtype=float)

def target_coverage(vectors,t):
    records=[]
    feature_id=t['feature_point_id'] if 'feature_point_id' in t else t.point_id
    ids0=feature_id+'-'+t.before_year.astype(str);ids1=feature_id+'-'+t.after_year.astype(str)
    for support in SUPPORTS:
        valid={}
        for model in MODELS:
            a=matrix(vectors,model,support,ids0);b=matrix(vectors,model,support,ids1)
            valid[model]=(np.isfinite(a).all(1),np.isfinite(b).all(1))
        common=np.logical_and.reduce([v for pair in valid.values() for v in pair])
        for model in MODELS:
            q=t[['point_id','region','before_year','label_name_before','label_name_after']].copy()
            q['model']=model;q['support']=support
            q['before_available']=valid[model][0];q['after_available']=valid[model][1]
            q['model_pair_available']=valid[model][0]&valid[model][1];q['common_pair_available']=common
            records.append(q)
    detail=pd.concat(records,ignore_index=True)
    groups=['model','support','before_year','region','label_name_before','label_name_after']
    aggregate=detail.groupby(groups).agg(n=('point_id','size'),model_available=('model_pair_available','sum'),
                                        common_available=('common_pair_available','sum')).reset_index()
    return detail,aggregate
