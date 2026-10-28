"""Check fixed physical inputs, roles and predictions across archived years."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
import pandas as pd
from analysis_paths import paths
from records import ROOT,now

def audit(root,out):
 root=Path(root).resolve();out=Path(out);out.mkdir(parents=True,exist_ok=False)
 manifest=json.loads((root/'analysis/year-common/manifest.json').read_text())
 reference=root/paths(root)['primary_predictions'] if manifest['reuse_original_2024_fits'] else root/'analysis/year-2024'
 methods=['geography','hydro_euclidean','hydro_pair','hydro_decoder','label_oracle'];checks=[];hashes={}
 for year in [2023,2021]:
  for r in range(4):
   a=reference/f'r{r}';b=root/f'analysis/year-{year}/r{r}'
   x=np.load(a/'roles-pairs.npz');y=np.load(b/'roles-pairs.npz')
   assert set(x.files)==set(y.files)
   for key in x.files:assert np.array_equal(x[key],y[key]),(year,r,key)
   x=pd.read_csv(a/'predictions.csv');y=pd.read_csv(b/'predictions.csv')
   x=x[x.method.isin(methods)].sort_values(['query_id','method']).reset_index(drop=True)
   y=y[y.method.isin(methods)].sort_values(['query_id','method']).reset_index(drop=True)
   assert x.columns.tolist()==y.columns.tolist() and x.shape==y.shape
   maximum=0.
   for key in x:
    if pd.api.types.is_float_dtype(x[key]):
     assert np.allclose(x[key],y[key],atol=1e-12,rtol=0,equal_nan=True),(year,r,key)
     finite=np.isfinite(x[key])&np.isfinite(y[key])
     if finite.any():maximum=max(maximum,float(np.max(np.abs(x.loc[finite,key]-y.loc[finite,key]))))
    else:assert x[key].fillna('<NA>').equals(y[key].fillna('<NA>')),(year,r,key)
   checks.append(dict(year=year,rotation=r,rows=len(x),physical_methods=methods,maximum_float_error=maximum,roles_pairs_exact=True))
   for folder in [a,b]:
    for name in ['roles-pairs.npz','predictions.csv']:
     p=folder/name;hashes[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
 record=dict(checked_at_utc=now(),passed=True,common_n=manifest['common_n'],reference_2024=str(reference.relative_to(root)),checks=checks,input_sha256=hashes,scope='Fixed labels,2024physical covariates, cohort, roles and seeds; embedding-year comparison only, without annual field-hydrology validation')
 (out/'result.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(dict(passed=True,comparisons=len(checks),common_n=manifest['common_n'])))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--out',type=Path,required=True);a=p.parse_args();audit(a.root,a.out)
