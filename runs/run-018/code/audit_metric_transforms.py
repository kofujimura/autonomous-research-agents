"""Author SVD algebra check of saved training-only whitening inputs."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np,pandas as pd
from threadpoolctl import threadpool_limits
from records import ROOT,now

def audit(root,out):
 root=Path(root).resolve();out=Path(out);out.mkdir(parents=True,exist_ok=False);original_root=Path(json.loads((root/'manifest.json').read_text())['research_directory']);results=[];hashes={}
 def locate(value):
  p=Path(value);return root/(p.relative_to(original_root) if p.is_absolute() else p)
 for condition in ['primary','polygonC']:
  for learner in ['hgb','rf-all']:
   for r in range(4):
    folder=root/f'analysis/metric-whitened/{condition}-{learner}/r{r}';record=json.loads((folder/'control-record.json').read_text());assert record['mode']=='metric' and record['distance_transform']=='whitened'
    feature_path=next(locate(p) for p in record['source_hashes'] if p.endswith('/features-2024.npz'));rows_path=feature_path.with_name('rows-2024.json');data=np.load(feature_path);rows=json.loads(rows_path.read_text());source=locate(record['primary_source']);cohort=json.loads((source/'cohort.json').read_text());ids=np.array([v['objectid'] for v in cohort]);mapping={int(v['objectid']):i for i,v in enumerate(rows)};ix=np.array([mapping[int(v)] for v in ids]);roles=np.load(source/'roles-pairs.npz');saved=np.load(folder/'distance-vectors.npz');state=json.loads((folder/'distance-transforms.json').read_text());loc={int(v):i for i,v in enumerate(ids)};train=np.array([loc[int(v)] for v in roles['training']]);assert np.array_equal(saved['objectid'],ids) and np.array_equal(saved['training'],roles['training'])
    for name in ['aef','tessera']:
     v=data[name][ix];assert len(train)>=v.shape[1];mean=v[train].mean(axis=0);_,s,vt=np.linalg.svd(v[train]-mean,full_matrices=False);eigen=s*s/(len(train)-1);floor=max(float(eigen.max())*.01,1e-12);matrix=(vt.T*(1/np.sqrt(np.maximum(eigen,floor))))@vt;expected=(v-mean)@matrix;expected/=np.maximum(np.sqrt((expected*expected).sum(axis=1))[:,None],1e-12)
     err=float(np.max(np.abs(expected-saved[name])));mean_error=float(np.max(np.abs(mean-np.asarray(state[name]['mean']))));floor_error=abs(floor-state[name]['eigenvalue_floor']);assert err<=1e-10 and mean_error<=1e-12 and floor_error<=1e-12,(condition,learner,r,name,err,mean_error,floor_error)
     results.append(dict(condition=condition,learner=learner,rotation=r,representation=name,training_n=len(train),vector_max_error=err,mean_max_error=mean_error,floor_error=floor_error))
    q=pd.read_csv(folder/'distance-equivalence.csv');assert (q.max_score_error<=1e-12).all() and (q.old_reference_gap<=1e-12).all()
    for p in [feature_path,rows_path,source/'roles-pairs.npz',folder/'distance-vectors.npz',folder/'distance-equivalence.csv']:hashes[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
 (out/'result.json').write_text(json.dumps(dict(checked_at_utc=now(),passed=True,vector_tolerance=1e-10,mean_floor_tolerance=1e-12,checks=results,input_sha256=hashes,scope='Separate SVD calculation by study author; no independent reproduction or field validation'),indent=2)+'\n');pd.DataFrame(results).to_csv(out/'discrepancies.csv',index=False,float_format='%.17g');print(json.dumps(dict(passed=True,checks=len(results),maximum_vector_error=max(v['vector_max_error'] for v in results))))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 with threadpool_limits(limits=2):audit(a.root,a.out)
