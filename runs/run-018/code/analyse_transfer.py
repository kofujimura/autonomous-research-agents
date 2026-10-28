"""Leave-one-window-out screening, fixed in protocol/plan-v6-robustness.md."""
from pathlib import Path
import argparse,hashlib,json,time
import numpy as np,pandas as pd
from sklearn.metrics import balanced_accuracy_score,log_loss
from threadpoolctl import threadpool_limits
import analyse_matching as am
from records import ROOT,now

def run(a):
 start=now();t0=time.monotonic();out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
 rows=pd.DataFrame(json.loads((a.inputs/'rows-2024.json').read_text()));data=np.load(a.inputs/'features-2024.npz')
 names=data['hydro_names'].tolist();complete=np.isfinite(data['aef']).all(axis=1)&np.isfinite(data['tessera']).all(axis=1)&np.isfinite(data['hydro'][:,names.index('elevation_mean90')])&(rows.interior_margin_m.to_numpy()>=15)
 rows=rows.loc[complete].reset_index(drop=True);h=data['hydro'][complete];ae=data['aef'][complete];te=data['tessera'][complete]
 am.REGIONS=sorted(rows.region.unique().tolist());assert a.region in am.REGIONS
 xy=rows[['x','y']].to_numpy();regions=rows.region.to_numpy();vegs=rows.vegetation.to_numpy();ids=rows.objectid.to_numpy();fold=rows.fold.to_numpy();y=np.searchsorted(am.REGIMES,rows.regime.to_numpy())
 train=np.flatnonzero(regions!=a.region);held=np.flatnonzero(regions==a.region);r=am.REGIONS.index(a.region)+1
 scaled,scaling=am.impute_scale(h,train,regions)
 cat=np.column_stack([rows.vegetation.eq(v).to_numpy() for v in am.VEGS]).astype(float)
 individual=np.column_stack([scaled,cat]);pairs=am.pairs_for_training(rows,train,xy,r);pi,pj=pairs.T;target=(y[pi]==y[pj]).astype(int);pf=am.pair_features(scaled,cat,xy,pi,pj)
 distances={'aef':1-np.einsum('ij,ij->i',ae[pi],ae[pj]),'tessera':1-np.einsum('ij,ij->i',te[pi],te[pj])};pair_models={};parameters={}
 for name,extra in [('hydro_pair',[]),('pair_aef',['aef']),('pair_tessera',['tessera']),('pair_both',['aef','tessera'])]:
  xx=np.column_stack([pf]+[distances[k] for k in extra]);model=am.forest(r);parameters[name]=model.get_params();model.fit(xx,target);model.set_params(n_jobs=1);pair_models[name]=(model,extra)
  print(json.dumps(dict(stage='fit',method=name,elapsed_seconds=time.monotonic()-t0)),flush=True)
 probs={};diagnostics=[];aa=ae*data['aef_norm'][complete,None];tt=te*data['tessera_norm'][complete,None]
 for name,xx in [('hydro_decoder',individual),('aef_decoder',np.column_stack([aa,cat])),('tessera_decoder',np.column_stack([tt,cat])),('hydro_aef_decoder',np.column_stack([individual,aa])),('hydro_tessera_decoder',np.column_stack([individual,tt]))]:
  model=am.forest(r,10);parameters[name]=model.get_params();model.fit(xx[train],y[train]);model.set_params(n_jobs=1);probs[name]=am.probabilities(model,xx)
  diagnostics.append(dict(method=name,query_n=len(held),balanced_accuracy=float(balanced_accuracy_score(y[held],probs[name][held].argmax(axis=1))),log_loss=float(log_loss(y[held],np.clip(probs[name][held],1e-15,1),labels=np.arange(3))),training_classes=model.classes_.tolist()))
 ac,aw,astate=am.centred_whitened(ae,train);tc,tw,tstate=am.centred_whitened(te,train);vectors={'aef_cosine':ae,'tessera_cosine':te,'aef_centred':ac,'aef_whitened':aw,'tessera_centred':tc,'tessera_whitened':tw}
 np.savez_compressed(out/'training-pairs.npz',objectid=ids,training=ids[train],heldout=ids[held],pair_objectids=ids[pairs],pair_target=target)
 np.savez_compressed(out/'decoder-probabilities.npz',objectid=ids,y=y,**probs)
 (out/'transforms.json').write_text(json.dumps(dict(hydro=scaling,aef=astate,tessera=tstate),indent=2)+'\n')
 (out/'decoder-diagnostics.json').write_text(json.dumps(diagnostics,indent=2)+'\n');rows.to_json(out/'cohort.json',orient='records',indent=2)
 for rotation in range(4):
  folder=out/f'r{rotation}';folder.mkdir();query=held[fold[held]==rotation];reference=held[fold[held]==(rotation+1)%4];predictions=[];pools=[]
  np.savez_compressed(folder/'roles.npz',query=ids[query],reference=ids[reference],training=ids[train])
  for i in query:
   refs=reference[vegs[reference]==vegs[i]];refs=refs[np.linalg.norm(xy[refs]-xy[i],axis=1)>=1000];refs=refs[np.argsort(ids[refs],kind='stable')];labels=y[refs];has_match=bool((labels==y[i]).any());nc=len(np.unique(labels))
   meta=dict(region=a.region,rotation=rotation,query_id=int(ids[i]),vegetation=vegs[i],regime=am.REGIMES[y[i]],image_year=None if pd.isna(rows.image_year.iloc[i]) else int(rows.image_year.iloc[i]),area_m2=float(rows.area_m2.iloc[i]),margin_m=float(rows.interior_margin_m.iloc[i]),training_support_global=bool(y[i] in set(y[train])),training_support_local=False,candidate_n=len(refs),candidate_categories=nc,has_match=has_match,nontrivial_matchable=bool(nc>=2 and has_match),uniform_expected_mismatch=float(np.mean(labels!=y[i])) if len(refs) else None)
   pools.append(meta)
   if not len(refs):continue
   qq=np.full(len(refs),i);base=am.pair_features(scaled,cat,xy,qq,refs);dd={'aef':1-ae[refs]@ae[i],'tessera':1-te[refs]@te[i]}
   scores={'geography':-np.linalg.norm(xy[refs]-xy[i],axis=1),'hydro_euclidean':-np.linalg.norm(scaled[refs]-scaled[i],axis=1)}
   for name,(model,extra) in pair_models.items():
    pr=model.predict_proba(np.column_stack([base]+[dd[k] for k in extra]));cl=model.classes_.tolist();scores[name]=pr[:,cl.index(1)] if 1 in cl else np.zeros(len(refs))
   for name,pr in probs.items():scores[name]=pr[refs]@pr[i]
   for name,v in vectors.items():scores[name]=v[refs]@v[i]
   scores['label_oracle']=(labels==y[i]).astype(float)
   for name,s in scores.items():
    assert np.isfinite(s).all();j=int(np.argmax(s));ref=refs[j];predictions.append(meta|dict(method=name,reference_id=int(ids[ref]),confidence=float(s[j]),best_score_tie_n=int((s==s[j]).sum()),candidate_score_range=float(s.max()-s.min()),mismatch=int(y[i]!=y[ref]),reference_regime=am.REGIMES[y[ref]],reference_distance_m=float(np.linalg.norm(xy[i]-xy[ref]))))
  pd.DataFrame(predictions).to_csv(folder/'predictions.csv',index=False,float_format='%.17g');pd.DataFrame(pools).to_csv(folder/'pools.csv',index=False,float_format='%.17g')
  print(json.dumps(dict(stage='rotation',rotation=rotation,query_n=len(query),elapsed_seconds=time.monotonic()-t0)),flush=True)
 record=dict(start_time_utc=start,end_time_utc=now(),elapsed_seconds=time.monotonic()-t0,region=a.region,forest_seed=18018+r,training_n=len(train),training_pairs=len(pairs),heldout_n=len(held),region_indicators=False,training_classes={am.REGIMES[k]:int((y[train]==k).sum()) for k in range(3)},parameters=parameters,input_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.inputs/'rows-2024.json',a.inputs/'features-2024.npz']})
 (out/'transfer-record.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items() if k!='parameters'}),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,default=ROOT/'analysis/features');p.add_argument('--region',required=True);p.add_argument('--output',required=True);a=p.parse_args()
 with threadpool_limits(limits=2):run(a)
