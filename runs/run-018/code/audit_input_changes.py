"""Magnitude of fixed polygon measurement changes, without fitting models."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
import pandas as pd
from analysis_paths import paths
from records import ROOT,now

def audit(root,out):
 root=Path(root).resolve();out=Path(out);out.mkdir(parents=True,exist_ok=False);base=root/paths(root)['polygon_features'];data={};ids={};hashes={}
 for c in 'ABCD':
  p=base/c/'features-2024.npz';r=base/c/'rows-2024.json';data[c]=np.load(p);ids[c]=np.array([v['objectid'] for v in json.loads(r.read_text())]);assert np.array_equal(ids[c],ids['A']);assert np.array_equal(data[c]['hydro_names'],data['A']['hydro_names'])
  for file in [p,r]:hashes[str(file.relative_to(root))]=hashlib.sha256(file.read_bytes()).hexdigest()
 b=data['B']['hydro'];c=data['C']['hydro'];finite=np.isfinite(b)&np.isfinite(c);maskchange=np.isfinite(b)!=np.isfinite(c);difference=np.where(finite,np.abs(c-b),0.);changed=(finite&(b!=c))|maskchange;physical=[];feature=[];wetlands=[]
 for rotation in range(4):
  p=root/f'analysis/polygon/B-rf/r{rotation}/transforms.json';state=json.loads(p.read_text());scale=np.array(state['hydro']['iqr']);assert len(scale)==b.shape[1] and (scale>0).all();scaled=difference/scale;maximum=scaled.max(axis=1)
  physical.append(dict(rotation=rotation,wetland_n=len(b),exactly_unchanged_n=int((~changed.any(axis=1)).sum()),missingness_changed_n=int(maskchange.any(axis=1).sum()),maximum_scaled_le001_n=int((maximum<=.01).sum()),maximum_scaled_le01_n=int((maximum<=.1).sum()),maximum_scaled_gt1_n=int((maximum>1).sum())))
  wetlands.extend(dict(rotation=rotation,objectid=int(oid),changed_feature_n=int(n),missingness_changed=bool(m),maximum_scaled_difference=float(d)) for oid,n,m,d in zip(ids['B'],changed.sum(axis=1),maskchange.any(axis=1),maximum))
  for j,name in enumerate(data['B']['hydro_names']):
   v=scaled[finite[:,j],j];feature.append(dict(rotation=rotation,feature=str(name),jointly_finite_n=len(v),finite_value_changed_n=int((finite[:,j]&(b[:,j]!=c[:,j])).sum()),missingness_changed_n=int(maskchange[:,j].sum()),median_scaled_difference=float(np.median(v)) if len(v) else None,q95_scaled_difference=float(np.quantile(v,.95)) if len(v) else None))
  hashes[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
 embedding=[];vectors=[]
 for product in ['aef','tessera']:
  for condition in ['B','D']:
   left=np.asarray(data['A'][product],dtype=float);right=np.asarray(data[condition][product],dtype=float);left=left/np.linalg.norm(left,axis=1)[:,None];right=right/np.linalg.norm(right,axis=1)[:,None];distance=np.clip(1-np.einsum('ij,ij->i',left,right),0,2)
   embedding.append(dict(product=product,comparison='A-'+condition,wetland_n=len(distance),median=float(np.median(distance)),q95=float(np.quantile(distance,.95)),distance_le1e12_n=int((distance<=1e-12).sum()),distance_le1e4_n=int((distance<=1e-4).sum()),distance_le1e3_n=int((distance<=1e-3).sum())))
   vectors.extend(dict(product=product,comparison='A-'+condition,objectid=int(oid),cosine_distance=float(d)) for oid,d in zip(ids['A'],distance))
 for name,rows in [('physical-summary',physical),('physical-features',feature),('physical-wetlands',wetlands),('embedding-summary',embedding),('embedding-wetlands',vectors)]:pd.DataFrame(rows).to_csv(out/(name+'.csv'),index=False,float_format='%.17g')
 record=dict(audited_at_utc=now(),physical=physical,embedding=embedding,input_sha256=hashes,scope='Exploratory input magnitude check; robust scales are archived B training transforms, including unit fallback; thresholds do not establish ecological equivalence or independent observations')
 (out/'result.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(dict(wetlands=len(b),physical_rotations=len(physical),embedding_comparisons=len(embedding))))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--out',type=Path,required=True);a=p.parse_args();audit(a.root,a.out)
