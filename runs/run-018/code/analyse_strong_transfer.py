"""Fixed stronger physical/boosted-tree comparators on archived transfer roles."""
from pathlib import Path
import argparse,hashlib,json,time
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from threadpoolctl import threadpool_limits
import analyse_matching as am
from analysis_paths import paths
from records import ROOT,now

def run(root,region,out):
 root=Path(root).resolve();out=Path(out);source=root/f'analysis/transfer-corrected/{region}';metaout=out/'metadata'/region;metaout.mkdir(parents=True,exist_ok=False);start=now();timer=time.monotonic();cp=paths(root);feature=root/cp['primary_features']/'features-2024.npz';feature_rows=root/cp['primary_features']/'rows-2024.json';full=np.load(feature);index={r['objectid']:i for i,r in enumerate(json.loads(feature_rows.read_text()))};source_rows=json.loads((source/'cohort.json').read_text());ids=np.array([v['objectid'] for v in source_rows]);all_rows=json.loads(feature_rows.read_text());rows=pd.DataFrame([all_rows[index[int(v)]] for v in ids]);ix=np.array([index[int(v)] for v in ids]);h=full['hydro'][ix];ae=full['aef'][ix];te=full['tessera'][ix];xy=rows[['x','y']].to_numpy();y=np.searchsorted(am.REGIMES,rows.regime.to_numpy());location={int(v):i for i,v in enumerate(ids)};roles=np.load(source/'training-pairs.npz');assert np.array_equal(roles['objectid'],ids);train=np.array([location[int(v)] for v in roles['training']]);pairs=np.array([[location[int(v)] for v in pair] for pair in roles['pair_objectids']]);pi,pj=pairs.T;target=(y[pi]==y[pj]).astype(int);assert np.array_equal(target,roles['pair_target']);assert (rows.region.to_numpy()[train]!=region).all();r=int(region[1:]);scaled,scaling=am.impute_scale(h,train,rows.region.to_numpy());cat=np.column_stack([rows.vegetation.eq(v).to_numpy() for v in am.VEGS]).astype(float);individual=np.column_stack([scaled,cat]);pair_features=am.pair_features(scaled,cat,xy,pi,pj);_,aw,astate=am.centred_whitened(ae,train);_,tw,tstate=am.centred_whitened(te,train);vectors=dict(raw_aef=ae,raw_tessera=te,white_aef=aw,white_tessera=tw);distances={name:1-np.einsum('ij,ij->i',v[pi],v[pj]) for name,v in vectors.items()};parameters={};models={};probs={}
 def hgb(leaf):return HistGradientBoostingClassifier(max_iter=200,learning_rate=.05,max_leaf_nodes=31,l2_regularization=1,min_samples_leaf=leaf,early_stopping=False,random_state=18018+r)
 rf=am.forest(r);rf.set_params(max_features=1.0);parameters['rf_pair']=rf.get_params();rf.fit(pair_features,target);rf.set_params(n_jobs=1);models['rf_pair']=(rf,None);rf_class=am.forest(r,10);rf_class.set_params(max_features=1.0);parameters['rf_decoder']=rf_class.get_params();rf_class.fit(individual[train],y[train]);rf_class.set_params(n_jobs=1);probs['rf_decoder']=am.probabilities(rf_class,individual);print(json.dumps(dict(region=region,stage='physical forest fitted',elapsed_seconds=time.monotonic()-timer)),flush=True)
 for name,extra in [('hgb_pair',None)]+[('hgb_'+name,name) for name in vectors]:
  xx=pair_features if extra is None else np.column_stack([pair_features,distances[extra]]);model=hgb(20);model.fit(xx,target);models[name]=(model,extra);parameters[name]=model.get_params()
 decoder=hgb(10);decoder.fit(individual[train],y[train]);probs['hgb_decoder']=am.probabilities(decoder,individual);parameters['hgb_decoder']=decoder.get_params();print(json.dumps(dict(region=region,stage='boosted trees fitted',elapsed_seconds=time.monotonic()-timer)),flush=True)
 np.savez_compressed(metaout/'vectors.npz',objectid=ids,training=ids[train],aef=aw,tessera=tw);np.savez_compressed(metaout/'physical-probabilities.npz',objectid=ids,y=y,**probs);(metaout/'transforms.json').write_text(json.dumps(dict(hydro=scaling,aef=astate,tessera=tstate),indent=2)+'\n');equivalence=[];hashes={}
 conditions=['rf-all-benchmark','hgb-raw','hgb-white']
 for rotation in range(4):
  role=np.load(source/f'r{rotation}/roles.npz');query=np.array([location[int(v)] for v in role['query']]);references=np.array([location[int(v)] for v in role['reference']]);assert np.array_equal(role['training'],ids[train]);pool=pd.read_csv(source/f'r{rotation}/pools.csv');original=pd.read_csv(source/f'r{rotation}/predictions.csv');records={c:[] for c in conditions};metadata=pool.set_index('query_id').to_dict('index')
  for i in query:
   oid=int(ids[i]);refs=references[rows.vegetation.to_numpy()[references]==rows.vegetation.iloc[i]];refs=refs[np.linalg.norm(xy[refs]-xy[i],axis=1)>=1000];refs=refs[np.argsort(ids[refs],kind='stable')];assert len(refs)==metadata[oid]['candidate_n']
   if not len(refs):continue
   qq=np.full(len(refs),i);base=am.pair_features(scaled,cat,xy,qq,refs);dd={name:1-v[refs]@v[i] for name,v in vectors.items()};scores={}
   for name,(model,extra) in models.items():
    pp=model.predict_proba(base if extra is None else np.column_stack([base,dd[extra]]));classes=model.classes_.tolist();scores[name]=pp[:,classes.index(1)] if 1 in classes else np.zeros(len(refs))
   for name,pr in probs.items():scores[name]=pr[refs]@pr[i]
   for name,old_method in [('white_aef','aef_whitened'),('white_tessera','tessera_whitened')]:
    similarity=1-dd[name];old=original[(original.query_id==oid)&(original.method==old_method)].iloc[0];maximum=float(similarity.max());position=int(np.flatnonzero(ids[refs]==int(old.reference_id))[0]);error=abs(maximum-float(old.confidence));gap=maximum-float(similarity[position]);assert error<=1e-12 and gap<=1e-12;equivalence.append(dict(rotation=rotation,query_id=oid,representation=name,max_score_error=error,old_reference_gap=gap,reference_agrees=bool(ids[refs[int(np.argmax(similarity))]]==int(old.reference_id))))
   mappings={'rf-all-benchmark':{'hydro_pair':'rf_pair','hydro_decoder':'rf_decoder'},'hgb-raw':{'hydro_pair':'hgb_pair','hydro_decoder':'hgb_decoder','pair_aef':'hgb_raw_aef','pair_tessera':'hgb_raw_tessera'},'hgb-white':{'hydro_pair':'hgb_pair','hydro_decoder':'hgb_decoder','pair_aef':'hgb_white_aef','pair_tessera':'hgb_white_tessera'}}
   for condition,mapping in mappings.items():
    for method,score_name in mapping.items():
     s=scores[score_name];assert np.isfinite(s).all();j=int(np.argmax(s));ref=int(refs[j]);records[condition].append(metadata[oid]|dict(query_id=oid,method=method,reference_id=int(ids[ref]),confidence=float(s[j]),best_score_tie_n=int((s==s[j]).sum()),candidate_score_range=float(s.max()-s.min()),mismatch=int(y[i]!=y[ref]),reference_regime=am.REGIMES[y[ref]],reference_distance_m=float(np.linalg.norm(xy[i]-xy[ref]))))
  for condition in conditions:
   folder=out/condition/region/f'r{rotation}';folder.mkdir(parents=True,exist_ok=False);frame=pd.DataFrame(records[condition])
   if condition=='rf-all-benchmark':frame=pd.concat([frame,original[original.method.isin(['pair_aef','pair_tessera'])]],ignore_index=True)
   frame.to_csv(folder/'predictions.csv',index=False,float_format='%.17g');pool.to_csv(folder/'pools.csv',index=False,float_format='%.17g')
 for p in [feature,feature_rows,source/'cohort.json',source/'training-pairs.npz']+[source/f'r{k}/{name}' for k in range(4) for name in ['roles.npz','predictions.csv','pools.csv']]:hashes[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
 pd.DataFrame(equivalence).to_csv(metaout/'whitening-equivalence.csv',index=False,float_format='%.17g');record=dict(start_time_utc=start,end_time_utc=now(),elapsed_seconds=time.monotonic()-timer,region=region,training_n=len(train),training_pairs=len(pairs),parameters=parameters,fit_threadpool_limit=2,prediction_forest_n_jobs=1,input_sha256=hashes,source=str(source.relative_to(root)),scope='Exploratory fixed stronger transfer comparisons; rf-all-benchmark copies original0.7augmentations and fits1.0physical comparators; HGB uses fixed raw/white distances and shared physical models')
 (metaout/'record.json').write_text(json.dumps(record,indent=2)+'\n')
 for condition in conditions:(out/condition/region/'transfer-record.json').write_text(json.dumps(dict(record,condition=condition),indent=2)+'\n')
 print(json.dumps({k:record[k] for k in ['region','elapsed_seconds','training_n','training_pairs']}),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--region',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 with threadpool_limits(limits=2):run(a.root,a.region,a.out)
