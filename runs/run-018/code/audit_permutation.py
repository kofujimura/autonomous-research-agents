"""Plan-v11 audit of fixed assignments and unchanged cosine inputs."""
from pathlib import Path
import argparse,json,hashlib
import numpy as np,pandas as pd
from threadpoolctl import threadpool_limits
from records import ROOT,now

def audit(out):
 out=Path(out);out.mkdir(parents=True,exist_ok=False);full=pd.DataFrame(json.loads((ROOT/'analysis/features/rows-2024.json').read_text()));data=np.load(ROOT/'analysis/features/features-2024.npz');full_loc={int(v):i for i,v in enumerate(full.objectid)};groups=[];distances=[]
 for rep in range(3):
  for r in range(4):
   source=ROOT/f'analysis/main/r{r}';cohort=pd.DataFrame(json.loads((source/'cohort.json').read_text()));ix=np.array([full_loc[int(v)] for v in cohort.objectid]);rows=full.iloc[ix].reset_index(drop=True);ids=rows.objectid.to_numpy();loc={int(v):i for i,v in enumerate(ids)};rid=rows.region.to_numpy();veg=rows.vegetation.to_numpy();xy=rows[['x','y']].to_numpy();roles=np.load(source/'roles-pairs.npz');role_indices={name:np.array([loc[int(v)] for v in roles[key]]) for name,key in [('training','training'),('query','query'),('reference','reference')]};pairs=np.array([[loc[int(v)] for v in p] for p in roles['pair_objectids']]);pi,pj=pairs.T
   for name in ['aef','tessera']:
    saved=np.load(ROOT/f'analysis/controls/permute-{rep}/r{r}/permutation-{name}.npz');assert np.array_equal(saved['objectid'],ids);mapping=np.array([loc[int(v)] for v in saved['source_objectid']]);v=data[name][ix];permuted=v[mapping]
    for role,ri in role_indices.items():
     assert np.isin(mapping[ri],ri).all()
     for window in sorted(set(rid)):
      for vv in ['PEM1','PFO1','PSS1']:
       g=ri[(rid[ri]==window)&(veg[ri]==vv)]
       if len(g):groups.append(dict(repetition=rep,rotation=r,representation=name,region=window,vegetation=vv,role=role,n=len(g),fixed=int((mapping[g]==g).sum())))
    old=1-np.einsum('ij,ij->i',v[pi],v[pj]);new=1-np.einsum('ij,ij->i',permuted[pi],permuted[pj]);unchanged=np.abs(old-new)<=1e-12
    for window in sorted(set(rid)):
     take=rid[pi]==window;distances.append(dict(repetition=rep,rotation=r,representation=name,region=window,role='training_pairs',n=int(take.sum()),unchanged=int(unchanged[take].sum()),nonempty_queries=None,all_cosines_unchanged_queries=None))
    reference=role_indices['reference']
    for window in sorted(set(rid)):
     nn=uu=qq=aa=0
     for i in role_indices['query'][rid[role_indices['query']]==window]:
      refs=reference[(rid[reference]==window)&(veg[reference]==veg[i])];refs=refs[np.linalg.norm(xy[refs]-xy[i],axis=1)>=1000]
      if not len(refs):continue
      old=1-v[refs]@v[i];new=1-permuted[refs]@permuted[i];same=np.abs(old-new)<=1e-12;nn+=len(refs);uu+=int(same.sum());qq+=1;aa+=int(same.all())
     distances.append(dict(repetition=rep,rotation=r,representation=name,region=window,role='query_candidate_pairs',n=nn,unchanged=uu,nonempty_queries=qq,all_cosines_unchanged_queries=aa))
   print(json.dumps(dict(repetition=rep,rotation=r,stage='audited')),flush=True)
 g=pd.DataFrame(groups);d=pd.DataFrame(distances);g.to_csv(out/'strata.csv',index=False);d.to_csv(out/'distances.csv',index=False)
 gg=g.assign(singleton=g.n==1).groupby(['repetition','representation','role']).agg(assignments=('n','sum'),fixed_assignments=('fixed','sum'),nonempty_strata=('n','size'),singleton_strata=('singleton','sum')).reset_index();gg['fixed_fraction']=gg.fixed_assignments/gg.assignments;gg.to_csv(out/'assignment-summary.csv',index=False,float_format='%.17g')
 dd=d.groupby(['repetition','representation','role']).agg(feature_values=('n','sum'),unchanged_feature_values=('unchanged','sum'),nonempty_queries=('nonempty_queries','sum'),all_cosines_unchanged_queries=('all_cosines_unchanged_queries','sum')).reset_index();dd['unchanged_fraction']=dd.unchanged_feature_values/dd.feature_values;dd.to_csv(out/'distance-summary.csv',index=False,float_format='%.17g')
 input_paths=[ROOT/'analysis/features/rows-2024.json',ROOT/'analysis/features/features-2024.npz']+list((ROOT/'analysis/main').glob('r*/cohort.json'))+list((ROOT/'analysis/main').glob('r*/roles-pairs.npz'))+list((ROOT/'analysis/controls').glob('permute-[012]/r*/permutation-*.npz'))
 (out/'audit-record.json').write_text(json.dumps(dict(input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in input_paths},audited_at_utc=now(),tolerance=1e-12,repetitions=3,rotations=4,scope='Assignment/pair counts across rotations, not unique independent wetlands; no formal p-value'),indent=2)+'\n');print(dd.to_string(index=False))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 with threadpool_limits(limits=2):audit(a.out)
