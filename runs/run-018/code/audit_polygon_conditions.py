"""Verify factor isolation in all four common-cohort polygon conditions."""
from pathlib import Path
import argparse,json
import numpy as np,pandas as pd
from analysis_paths import paths
from records import ROOT,now

def audit(root,out):
 root=Path(root);out=Path(out);out.mkdir(parents=True,exist_ok=False);base=root/paths(root)['polygon_features'];arrays={c:np.load(base/c/'features-2024.npz') for c in 'ABCD'};checks=[]
 def check(name,condition):
  checks.append(dict(check=name,passed=bool(condition)));assert condition,name
 for c in 'BD':check('Physical inputs A='+c,np.array_equal(arrays['A']['hydro'],arrays[c]['hydro'],equal_nan=True))
 for key in ['aef','tessera','aef_norm','tessera_norm']:check('Embedding inputs B=C '+key,np.array_equal(arrays['B'][key],arrays['C'][key],equal_nan=True))
 ids={c:[r['objectid'] for r in json.loads((base/c/'rows-2024.json').read_text())] for c in 'ABCD'}
 for c in 'BCD':check('Ordered cohort A='+c,ids['A']==ids[c])
 for learner in ['rf','hgb']:
  for r in range(4):
   predictions={c:pd.read_csv(root/f'analysis/polygon/{c}-{learner}/r{r}/predictions.csv').set_index(['query_id','method']) for c in 'ABCD'}
   for left,right,methods in [('A','B',['hydro_pair','hydro_decoder']),('A','D',['hydro_pair','hydro_decoder']),('B','C',['aef_decoder','tessera_decoder','aef_cosine','tessera_cosine','aef_centred','tessera_centred','aef_whitened','tessera_whitened'])]:
    for method in methods:
     a=predictions[left].xs(method,level='method').sort_index();b=predictions[right].xs(method,level='method').sort_index();equal=a.index.equals(b.index) and a.reference_id.equals(b.reference_id) and a.mismatch.equals(b.mismatch) and np.allclose(a.confidence,b.confidence,rtol=0,atol=1e-12)
     check(f'{learner} rotation{r} {method} {left}={right}',equal)
 record=dict(checked_at_utc=now(),checks=checks,passed=all(c['passed'] for c in checks),scope='Factor isolation in archived common-cohort feature arrays and prediction outputs; no field or independent validation')
 (out/'result.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(dict(passed=record['passed'],checks=len(checks))))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--out',type=Path,required=True);a=p.parse_args();audit(a.root,a.out)
