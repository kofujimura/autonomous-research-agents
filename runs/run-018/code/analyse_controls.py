"""Fixed seed, permuted-feature and second-learner controls on archived primary splits."""
from pathlib import Path
import argparse,hashlib,json,time
import numpy as np,pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from threadpoolctl import threadpool_limits
import analyse_matching as am
from records import ROOT,now

LEARNED=['hydro_pair','pair_aef','pair_tessera','pair_both','hydro_decoder','aef_decoder','tessera_decoder','hydro_aef_decoder','hydro_tessera_decoder']

def noise_feature(a_ids,b_ids,seed):
 values=[]
 for aa,bb in zip(a_ids,b_ids):
  lo,hi=sorted([int(aa),int(bb)]);digest=hashlib.sha256(f'free-research-018|noise|{seed}|{lo}|{hi}'.encode()).digest();values.append((int.from_bytes(digest[:8],'big')>>11)/2**53)
 return np.asarray(values,dtype=np.float64)

def run(a):
 start=now();t0=time.monotonic();out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
 source=a.primary/f'r{a.rotation}';full_rows=pd.DataFrame(json.loads((a.inputs/'rows-2024.json').read_text()));data=np.load(a.inputs/'features-2024.npz');cohort=pd.DataFrame(json.loads((source/'cohort.json').read_text()))
 index={int(v):i for i,v in enumerate(full_rows.objectid)};ix=np.array([index[int(v)] for v in cohort.objectid]);rows=full_rows.iloc[ix].reset_index(drop=True);ids=rows.objectid.to_numpy();loc={int(v):i for i,v in enumerate(ids)}
 h=data['hydro'][ix];vectors={'aef':data['aef'][ix].copy(),'tessera':data['tessera'][ix].copy()};norms={'aef':data['aef_norm'][ix],'tessera':data['tessera_norm'][ix]};xy=rows[['x','y']].to_numpy();region=rows.region.to_numpy();veg=rows.vegetation.to_numpy();y=np.searchsorted(am.REGIMES,rows.regime.to_numpy());r=a.rotation
 if a.forest_all_features and a.mode in ['noise','metric']:assert a.baselines is not None,'Need matching max_features1.0 baseline predictions'
 assert a.distance_transform=='raw' or a.mode=='metric','Existing controls keep their original distance definition'
 if a.mode=='metric':assert a.baselines is not None and a.distance_transform=='whitened'
 roles=np.load(source/'roles-pairs.npz');train=np.array([loc[int(v)] for v in roles['training']]);query=np.array([loc[int(v)] for v in roles['query']]);reference=np.array([loc[int(v)] for v in roles['reference']]);pairs=np.array([[loc[int(v)] for v in pair] for pair in roles['pair_objectids']]);pi,pj=pairs.T;target=(y[pi]==y[pj]).astype(int);assert np.array_equal(target,roles['pair_target'])
 am.REGIONS=sorted(rows.region.unique());scaled,scaling=am.impute_scale(h,train,region);cat=am.categories(rows);individual=np.column_stack([scaled,cat]);mapping_record={}
 if a.mode=='permute':
  for en,name in enumerate(['aef','tessera']):
   mapping=np.arange(len(rows));rng=np.random.default_rng(28018+r+1000*a.permutation+500000*en)
   for role_name,role_ix in [('training',train),('query',query),('reference',reference)]:
    for rid in am.REGIONS:
     for v in am.VEGS:
      group=role_ix[(region[role_ix]==rid)&(veg[role_ix]==v)];mapping[group]=rng.permutation(group)
    assert np.isin(mapping[role_ix],role_ix).all()
   vectors[name]=vectors[name][mapping];mapping_record[name]=dict(seed=28018+r+1000*a.permutation+500000*en,fixed_points_training=int((mapping[train]==train).sum()),fixed_points_query=int((mapping[query]==query).sum()),fixed_points_reference=int((mapping[reference]==reference).sum()))
   np.savez_compressed(out/f'permutation-{name}.npz',objectid=ids,source_objectid=ids[mapping],training=ids[train],query=ids[query],reference=ids[reference])
 distance_vectors=vectors;distance_state={}
 if a.mode=='metric':
  distance_vectors={}
  for name,v in vectors.items():
   _,w,state=am.centred_whitened(v,train);distance_vectors[name]=w;distance_state[name]=state|dict(zero_norm_rows=int((np.linalg.norm(w,axis=1)==0).sum()))
  np.savez_compressed(out/'distance-vectors.npz',objectid=ids,training=ids[train],**distance_vectors)
  (out/'distance-transforms.json').write_text(json.dumps(distance_state,indent=2)+'\n')
 pf=am.pair_features(scaled,cat,xy,pi,pj);distances={name:1-np.einsum('ij,ij->i',v[pi],v[pj]) for name,v in distance_vectors.items()};parameters={};feature_checks={}
 noise_seed=28018+r+1000*a.permutation
 if a.mode=='noise':
  distances['noise']=np.zeros(len(pi)) if a.constant_feature else noise_feature(ids[pi],ids[pj],noise_seed);np.savez_compressed(out/'noise-training.npz',pair_objectids=ids[pairs],noise=distances['noise'])
 def estimator(leaf):
  if a.mode=='hgb' or (a.mode=='noise' and a.scalar_learner=='hgb') or (a.mode=='metric' and a.metric_learner=='hgb'):return HistGradientBoostingClassifier(max_iter=200,learning_rate=.05,max_leaf_nodes=31,l2_regularization=1,max_bins=255,early_stopping=False,random_state=18018+r,min_samples_leaf=leaf)
  return am.forest(r+a.seed_offset,leaf).set_params(max_features=1.0 if a.forest_all_features else .7)
 def fit(name,x,truth,leaf):
  model=estimator(leaf);parameters[name]=model.get_params(deep=False);model.fit(x,truth)
  if a.mode=='noise' and a.constant_feature:
   assert np.all(x[:,-1]==0);used=sum(int((tree.tree_.feature==x.shape[1]-1).sum()) for tree in model.estimators_) if hasattr(model,'estimators_') else None
   if used is not None:assert used==0
   feature_checks[name]=dict(training_added_feature_min=0.0,training_added_feature_max=0.0,added_feature_used_splits=used)
  if 'n_jobs' in model.get_params():model.set_params(n_jobs=1)
  print(json.dumps(dict(stage='fit',method=name,mode=a.mode,elapsed_seconds=time.monotonic()-t0)),flush=True);return model
 specs=[('hydro_pair',[]),('pair_aef',['aef']),('pair_tessera',['tessera']),('pair_both',['aef','tessera'])]
 if a.mode=='seed':specs=specs[:3]
 if a.mode in ['permute','metric']:specs=specs[1:3]
 if a.mode=='noise':specs=[('pair_constant' if a.constant_feature else 'pair_noise',['noise'])]
 pair_models={name:(fit(name,np.column_stack([pf]+[distances[k] for k in extra]),target,20),extra) for name,extra in specs}
 probs={};diagnostics=[]
 decoder_specs=[] if a.mode in ['permute','noise','metric'] else [('hydro_decoder',individual)]
 if a.mode=='hgb':
  aa=vectors['aef']*norms['aef'][:,None];tt=vectors['tessera']*norms['tessera'][:,None]
  decoder_specs += [('aef_decoder',np.column_stack([aa,cat])),('tessera_decoder',np.column_stack([tt,cat])),('hydro_aef_decoder',np.column_stack([individual,aa])),('hydro_tessera_decoder',np.column_stack([individual,tt]))]
 for name,x in decoder_specs:
  model=fit(name,x[train],y[train],10);probs[name]=am.probabilities(model,x)
 original=pd.read_csv(source/'predictions.csv');pools=pd.read_csv(source/'pools.csv');pool_by_id=pools.set_index('query_id')
 baseline_source=a.baselines/f'r{r}/predictions.csv' if a.baselines is not None else source/'predictions.csv';baseline_predictions=pd.read_csv(baseline_source)
 reused=baseline_predictions[baseline_predictions.method.isin(['hydro_pair','hydro_decoder'])] if a.mode in ['permute','noise','metric'] else original[~original.method.isin(LEARNED)]
 predicted=[];metric_checks=[];whitened_original=original[original.method.isin(['aef_whitened','tessera_whitened'])].set_index(['query_id','method']) if a.mode=='metric' else None
 for count,i in enumerate(query):
  refs=reference[(region[reference]==region[i])&(veg[reference]==veg[i])];refs=refs[np.linalg.norm(xy[refs]-xy[i],axis=1)>=1000];refs=refs[np.argsort(ids[refs],kind='stable')];meta=pool_by_id.loc[int(ids[i])].to_dict();meta['query_id']=int(ids[i]);assert len(refs)==int(meta['candidate_n'])
  if not len(refs):continue
  qq=np.full(len(refs),i);base=am.pair_features(scaled,cat,xy,qq,refs);dd={name:1-v[refs]@v[i] for name,v in distance_vectors.items()};scores={}
  if a.mode=='metric':
   for name,v in distance_vectors.items():
    cosine=v[refs]@v[i];old=whitened_original.loc[(int(ids[i]),name+'_whitened')];old_index=np.flatnonzero(ids[refs]==int(old.reference_id));assert len(old_index)==1;gap=float(cosine.max()-cosine[old_index[0]]);error=abs(float(cosine.max())-float(old.confidence));assert gap<=1e-12 and error<=1e-12
    metric_checks.append(dict(query_id=int(ids[i]),representation=name,reference_equal=int(ids[refs[int(np.argmax(cosine))]])==int(old.reference_id),max_score_error=error,old_reference_gap=gap))
  if a.mode=='noise':dd['noise']=np.zeros(len(refs)) if a.constant_feature else noise_feature(ids[qq],ids[refs],noise_seed)
  for name,(model,extra) in pair_models.items():
   pr=model.predict_proba(np.column_stack([base]+[dd[k] for k in extra]));cl=model.classes_.tolist();scores[name]=pr[:,cl.index(1)] if 1 in cl else np.zeros(len(refs))
  for name,pr in probs.items():scores[name]=pr[refs]@pr[i]
  for name,s in scores.items():
   assert np.isfinite(s).all();j=int(np.argmax(s));ref=refs[j];predicted.append(meta|dict(method=name,reference_id=int(ids[ref]),confidence=float(s[j]),best_score_tie_n=int((s==s[j]).sum()),candidate_score_range=float(s.max()-s.min()),mismatch=int(y[i]!=y[ref]),reference_regime=am.REGIMES[y[ref]],reference_distance_m=float(np.linalg.norm(xy[i]-xy[ref]))))
  if (count+1)%200==0:print(json.dumps(dict(stage='predict',queries=count+1,elapsed_seconds=time.monotonic()-t0)),flush=True)
 result=pd.concat([reused,pd.DataFrame(predicted)],ignore_index=True);assert not result.duplicated(['query_id','method']).any();result.to_csv(out/'predictions.csv',index=False,float_format='%.17g');pools.to_csv(out/'pools.csv',index=False,float_format='%.17g')
 if probs:np.savez_compressed(out/'decoder-probabilities.npz',objectid=ids,y=y,query_indices=query,**probs)
 if metric_checks:pd.DataFrame(metric_checks).to_csv(out/'distance-equivalence.csv',index=False,float_format='%.17g')
 record=dict(mode=a.mode,distance_transform=a.distance_transform,metric_learner=a.metric_learner,constant_feature=a.constant_feature,scalar_learner=a.scalar_learner,feature_checks=feature_checks,forest_all_features=a.forest_all_features,baseline_source=str(baseline_source),noise_seed=noise_seed if a.mode=='noise' and not a.constant_feature else None,rotation=r,seed_offset=a.seed_offset,permutation=a.permutation,start_time_utc=start,end_time_utc=now(),elapsed_seconds=time.monotonic()-t0,parameters=parameters,permutation_mappings=mapping_record,reused_methods=sorted(reused.method.unique().tolist()),primary_source=str(source),source_hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [source/'roles-pairs.npz',source/'pools.csv',source/'predictions.csv',a.inputs/'features-2024.npz',a.inputs/'rows-2024.json',baseline_source]},training_n=len(train),training_pairs=len(pairs),predictions=len(result))
 (out/'control-record.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items() if k not in ['parameters','source_hashes','permutation_mappings']}),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--mode',choices=['seed','permute','hgb','noise','metric'],required=True);p.add_argument('--rotation',type=int,choices=range(4),required=True);p.add_argument('--seed-offset',type=int,default=0);p.add_argument('--permutation',type=int,choices=range(3),default=0);p.add_argument('--inputs',type=Path,default=ROOT/'analysis/features');p.add_argument('--primary',type=Path,default=ROOT/'analysis/main');p.add_argument('--constant-feature',action='store_true');p.add_argument('--scalar-learner',choices=['forest','hgb'],default='forest');p.add_argument('--metric-learner',choices=['forest','hgb'],default='forest');p.add_argument('--distance-transform',choices=['raw','whitened'],default='raw');p.add_argument('--baselines',type=Path);p.add_argument('--forest-all-features',action='store_true');p.add_argument('--output',required=True);a=p.parse_args()
 with threadpool_limits(limits=2):run(a)
