"""Prespecified spatial wetland matching analysis, offline from saved features."""
from pathlib import Path
import argparse,hashlib,json,time
import numpy as np,pandas as pd
from scipy.spatial import cKDTree
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import balanced_accuracy_score,log_loss
from records import ROOT,now

REGIMES=np.array(['A','C','F'])
VEGS=['PEM1','PFO1','PSS1']
REGIONS=[f'R{i:02}' for i in range(1,13)]

def normalized(x):
 n=np.linalg.norm(x,axis=1);return x/np.maximum(n[:,None],1e-12)

def probabilities(model,x):
 pred=model.predict_proba(x);out=np.zeros((len(x),3))
 for j,c in enumerate(model.classes_):out[:,int(c)]=pred[:,j]
 return out

def forest(r,leaf=20):
 return RandomForestClassifier(n_estimators=200,max_depth=12,min_samples_leaf=leaf,max_features=.7,n_jobs=2,random_state=18018+r)

def impute_scale(h,train,regions,within=False):
 med=np.nanmedian(h[train],axis=0);med=np.where(np.isfinite(med),med,0)
 missing=~np.isfinite(h);filled=np.where(missing,med,h)
 q1,q3=np.quantile(filled[train],[.25,.75],axis=0);scale=q3-q1;scale=np.where(scale>1e-9,scale,1)
 values=(filled-med)/scale
 per={}
 if within:
  for rid in REGIONS:
   ix=train[regions[train]==rid]
   if not len(ix):continue
   mm=np.nanmedian(h[ix],axis=0);mm=np.where(np.isfinite(mm),mm,med)
   ff=np.where(missing,mm,h);a,b=np.quantile(ff[ix],[.25,.75],axis=0);ss=np.where(b-a>1e-9,b-a,1)
   choose=regions==rid;values[choose]=(ff[choose]-mm)/ss;per[rid]=dict(median=mm.tolist(),iqr=ss.tolist())
 return np.concatenate([values,missing.astype(float)],axis=1),dict(median=med.tolist(),iqr=scale.tolist(),per_region=per)

def categories(rows):
 return np.column_stack([rows.vegetation.eq(v).to_numpy() for v in VEGS]+[rows.region.eq(r).to_numpy() for r in REGIONS]).astype(float)

def pair_features(h,cat,xy,i,j):
 d=np.linalg.norm(xy[i]-xy[j],axis=1)
 return np.column_stack([(h[i]+h[j])*.5,np.abs(h[i]-h[j]),np.log1p(d),cat[i]])

def pairs_for_training(rows,train,xy,r):
 rng=np.random.default_rng(18018+r);pairs=set()
 for rid in REGIONS:
  for veg in VEGS:
   indices=train[(rows.region.to_numpy()[train]==rid)&(rows.vegetation.to_numpy()[train]==veg)]
   if len(indices)<2:continue
   for i in indices:
    valid=indices[np.linalg.norm(xy[indices]-xy[i],axis=1)>=1000]
    if len(valid)>30:valid=rng.choice(valid,30,replace=False)
    for j in valid:pairs.add((min(int(i),int(j)),max(int(i),int(j))))
 return np.array(sorted(pairs),dtype=int).reshape(-1,2)

def centred_whitened(v,train):
 mean=v[train].mean(axis=0);c=v-mean
 cov=np.cov(c[train],rowvar=False) if len(train)>1 else np.eye(v.shape[1])
 eig,u=np.linalg.eigh(cov);floor=max(float(eig.max())*.01,1e-12);w=(u*(1/np.sqrt(np.maximum(eig,floor))))@u.T
 return normalized(c),normalized(c@w),dict(mean=mean.tolist(),eigenvalue_floor=floor,train_n=len(train))

def run(a):
 global REGIONS
 start=now();t0=time.monotonic();out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
 rows=pd.DataFrame(json.loads((a.inputs/f'rows-{a.year}.json').read_text()))
 REGIONS=sorted(rows.region.unique().tolist())
 data=np.load(a.inputs/f'features-{a.year}.npz');h=data['hydro'];ae=data['aef'];te=data['tessera'];names=data['hydro_names'].tolist()
 if a.exclude_hand:
  use=np.array([not s.startswith('log_hand_') for s in names]);h=h[:,use];names=[s for s in names if not s.startswith('log_hand_')]
 complete=np.isfinite(ae).all(axis=1)&np.isfinite(te).all(axis=1)&np.isfinite(h[:,names.index('elevation_mean90')])&(rows.interior_margin_m.to_numpy()>=a.min_margin)
 exclusions=rows.loc[~complete,['region','objectid','attribute','aef_valid','tessera_valid']].to_dict(orient='records')
 rows=rows.loc[complete].reset_index(drop=True);h=h[complete];ae=ae[complete];te=te[complete]
 xy=rows[['x','y']].to_numpy();region=rows.region.to_numpy();vegetation=rows.vegetation.to_numpy();fold=rows.fold.to_numpy();ids=rows.objectid.to_numpy();y=np.searchsorted(REGIMES,rows.regime.to_numpy());n=len(rows);r=a.rotation
 query=np.flatnonzero(fold==r);reference=np.flatnonzero(fold==(r+1)%4);nominal=np.flatnonzero((fold!=r)&(fold!=(r+1)%4));train=[];nearest=np.full(n,np.inf)
 for rid in REGIONS:
  tr=nominal[region[nominal]==rid];held=np.concatenate([query[region[query]==rid],reference[region[reference]==rid]])
  if len(held) and len(tr):nearest[tr]=cKDTree(xy[held]).query(xy[tr])[0]
  train.extend(tr[nearest[tr]>=a.training_buffer])
 train=np.array(sorted(train),int)
 if not len(train):raise RuntimeError('No retained training wetlands')
 transform_h,scale=impute_scale(h,train,region,a.within_region_scale);cat=categories(rows);individual=np.column_stack([transform_h,cat])
 train_pairs=pairs_for_training(rows,train,xy,r)
 if not len(train_pairs):raise RuntimeError('No admissible training pairs')
 pi,pj=train_pairs.T;target=(y[pi]==y[pj]).astype(int);pf=pair_features(transform_h,cat,xy,pi,pj)
 distances={'aef':1-np.einsum('ij,ij->i',ae[pi],ae[pj]),'tessera':1-np.einsum('ij,ij->i',te[pi],te[pj])}
 pair_models={}
 for name,extra in [('hydro_pair',[]),('pair_aef',['aef']),('pair_tessera',['tessera']),('pair_both',['aef','tessera'])]:
  xx=np.column_stack([pf]+[distances[k] for k in extra])
  model=forest(r).fit(xx,target);model.set_params(n_jobs=1);pair_models[name]=(model,extra)
  print(json.dumps(dict(stage='fit',method=name,training_wetlands=len(train),pairs=len(target),elapsed_seconds=time.monotonic()-t0)),flush=True)
 classifiers={};probs={}
 aef_full=ae*data['aef_norm'][complete,None];tessera_full=te*data['tessera_norm'][complete,None]
 for name,xx in [('hydro_decoder',individual),('aef_decoder',np.column_stack([aef_full,cat])),('tessera_decoder',np.column_stack([tessera_full,cat])),('hydro_aef_decoder',np.column_stack([individual,aef_full])),('hydro_tessera_decoder',np.column_stack([individual,tessera_full]))]:
  model=forest(r,leaf=10).fit(xx[train],y[train]);model.set_params(n_jobs=1);classifiers[name]=model;probs[name]=probabilities(model,xx)
 ac,aw,astate=centred_whitened(ae,train);tc,tw,tstate=centred_whitened(te,train)
 vectors={'aef_cosine':ae,'tessera_cosine':te,'aef_centred':ac,'aef_whitened':aw,'tessera_centred':tc,'tessera_whitened':tw}
 rows.to_json(out/'cohort.json',orient='records',indent=2)
 np.savez_compressed(out/'roles-pairs.npz',objectid=ids,query=ids[query],reference=ids[reference],nominal_training=ids[nominal],training=ids[train],training_nearest_heldout=nearest[nominal],pair_objectids=ids[train_pairs],pair_target=target)
 (out/'transforms.json').write_text(json.dumps(dict(hydro=scale,aef=astate,tessera=tstate),indent=2)+'\n')
 # Save probabilities once; matching and diagnostics can be recomputed without refitting.
 np.savez_compressed(out/'decoder-probabilities.npz',objectid=ids,y=y,query_indices=query,**probs)
 diagnostics=[]
 for name,pred in probs.items():
  q=pred[query];truth=y[query]
  diagnostics.append(dict(method=name,query_n=len(query),balanced_accuracy=float(balanced_accuracy_score(truth,q.argmax(axis=1))),log_loss=float(log_loss(truth,np.clip(q,1e-15,1),labels=np.arange(3))),training_classes=classifiers[name].classes_.tolist()))
 predictions=[];pool_rows=[]
 training_global_classes=set(y[train]);training_local_classes={rid:set(y[train[region[train]==rid]]) for rid in REGIONS}
 for count,i in enumerate(query):
  refs=reference[(region[reference]==region[i])&(vegetation[reference]==vegetation[i])]
  d=np.linalg.norm(xy[refs]-xy[i],axis=1);refs=refs[d>=a.reference_buffer]
  refs=refs[np.argsort(ids[refs],kind='stable')]
  labels=y[refs];has_match=bool((labels==y[i]).any());nc=len(np.unique(labels));nontrivial=nc>=2 and has_match
  meta=dict(region=region[i],rotation=r,query_id=int(ids[i]),vegetation=vegetation[i],regime=REGIMES[y[i]],image_year=None if pd.isna(rows.image_year.iloc[i]) else int(rows.image_year.iloc[i]),area_m2=float(rows.area_m2.iloc[i]),margin_m=float(rows.interior_margin_m.iloc[i]),training_support_global=bool(y[i] in training_global_classes),training_support_local=bool(y[i] in training_local_classes[region[i]]),candidate_n=len(refs),candidate_categories=nc,has_match=has_match,nontrivial_matchable=nontrivial,uniform_expected_mismatch=float(np.mean(labels!=y[i])) if len(refs) else None)
  pool_rows.append(meta)
  if not len(refs):continue
  qq=np.full(len(refs),i);base=pair_features(transform_h,cat,xy,qq,refs)
  dd={'aef':1-ae[refs]@ae[i],'tessera':1-te[refs]@te[i]}
  scores={'geography':-np.linalg.norm(xy[refs]-xy[i],axis=1),'hydro_euclidean':-np.linalg.norm(transform_h[refs]-transform_h[i],axis=1)}
  for name,(model,extra) in pair_models.items():
   pred=model.predict_proba(np.column_stack([base]+[dd[k] for k in extra]));classes=model.classes_.tolist()
   scores[name]=pred[:,classes.index(1)] if 1 in classes else np.zeros(len(refs))
  for name,pr in probs.items():scores[name]=pr[refs]@pr[i]
  for name,v in vectors.items():scores[name]=v[refs]@v[i]
  scores['label_oracle']=(labels==y[i]).astype(float)
  for name,s in scores.items():
   assert np.isfinite(s).all(),name
   j=int(np.argmax(s));ref=refs[j]
   predictions.append(meta|dict(method=name,reference_id=int(ids[ref]),confidence=float(s[j]),best_score_tie_n=int((s==s[j]).sum()),candidate_score_range=float(s.max()-s.min()),mismatch=int(y[i]!=y[ref]),reference_regime=REGIMES[y[ref]],reference_distance_m=float(np.linalg.norm(xy[i]-xy[ref]))))
  if (count+1)%100==0:print(json.dumps(dict(stage='predict',queries=count+1,total=len(query),elapsed_seconds=time.monotonic()-t0)),flush=True)
 pd.DataFrame(predictions).to_csv(out/'predictions.csv',index=False,float_format='%.17g')
 pd.DataFrame(pool_rows).to_csv(out/'pools.csv',index=False,float_format='%.17g')
 (out/'decoder-diagnostics.json').write_text(json.dumps(diagnostics,indent=2)+'\n')
 (out/'exclusions.json').write_text(json.dumps(exclusions,indent=2)+'\n')
 summary=dict(start_time_utc=start,end_time_utc=now(),elapsed_seconds=time.monotonic()-t0,rotation=r,year=a.year,training_buffer=a.training_buffer,reference_buffer=a.reference_buffer,min_margin=a.min_margin,within_region_scale=a.within_region_scale,cohort_n=n,training_nominal_n=len(nominal),training_retained_n=len(train),training_pairs=len(train_pairs),query_n=len(query),reference_n=len(reference),prediction_rows=len(predictions),feature_names=names,input_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.inputs/f'rows-{a.year}.json',a.inputs/f'features-{a.year}.npz']})
 (out/'analysis-record.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,default=ROOT/'analysis/features');p.add_argument('--output',required=True);p.add_argument('--rotation',type=int,choices=range(4),required=True);p.add_argument('--year',type=int,default=2024);p.add_argument('--training-buffer',type=float,default=1000);p.add_argument('--reference-buffer',type=float,default=1000);p.add_argument('--min-margin',type=float,default=15);p.add_argument('--within-region-scale',action='store_true');p.add_argument('--exclude-hand',action='store_true');run(p.parse_args())
