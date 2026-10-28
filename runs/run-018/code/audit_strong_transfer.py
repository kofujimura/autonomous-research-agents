"""Check fixed cohorts, shared physical HGB decisions and copied augmentations."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
import pandas as pd
from records import ROOT,now

def audit(root,out):
 root=Path(root).resolve();out=Path(out);out.mkdir(parents=True,exist_ok=False);conditions=['rf-all-benchmark','hgb-raw','hgb-white'];pred={};hashes={};checks=[]
 for condition in conditions:
  base=root/f'analysis/transfer-strong-combined/{condition}';pred[condition]=pd.concat([pd.read_csv(base/f'r{r}/predictions.csv') for r in range(4)],ignore_index=True)
  for r in range(4):
   old=pd.read_csv(root/f'analysis/transfer-combined-corrected/r{r}/pools.csv').sort_values('query_id').reset_index(drop=True);new=pd.read_csv(base/f'r{r}/pools.csv').sort_values('query_id').reset_index(drop=True)
   columns=['region','rotation','query_id','vegetation','regime','candidate_n','candidate_categories','has_match','nontrivial_matchable'];assert old[columns].equals(new[columns]),(condition,r,'pool structure')
   for file in [base/f'r{r}/predictions.csv',base/f'r{r}/pools.csv']:hashes[str(file.relative_to(root))]=hashlib.sha256(file.read_bytes()).hexdigest()
  checks.append(dict(condition=condition,shared_query_pool_structure=True,queries=int(pred[condition].query_id.nunique())))
 left=pred['hgb-raw'];right=pred['hgb-white']
 for method in ['hydro_pair','hydro_decoder']:
  a=left[left.method==method].sort_values('query_id').reset_index(drop=True);b=right[right.method==method].sort_values('query_id').reset_index(drop=True)
  for col in ['query_id','reference_id','mismatch']:assert a[col].equals(b[col]),method
  assert np.allclose(a.confidence,b.confidence,atol=1e-12,rtol=0);checks.append(dict(method=method,hgb_physical_raw_white_equal=True))
 source=pd.read_csv(root/'analysis/transfer-corrected-summary/selected-050.csv');benchmark=pd.read_csv(root/'analysis/transfer-strong/rf-all-benchmark-summary/selected-050.csv')
 for method in ['pair_aef','pair_tessera']:
  a=source[source.method==method].sort_values('query_id').reset_index(drop=True);b=benchmark[benchmark.method==method].sort_values('query_id').reset_index(drop=True)
  for col in ['query_id','reference_id','mismatch']:assert a[col].equals(b[col]),('copied augmentation',method,col)
  assert np.allclose(a.confidence,b.confidence,atol=1e-12,rtol=0);checks.append(dict(method=method,copied_half_coverage_decisions_equal=True,n=len(a)))
 count=0
 for r in range(1,13):
  folder=root/f'analysis/transfer-strong/metadata/R{r:02}';q=pd.read_csv(folder/'whitening-equivalence.csv');assert (q.max_score_error<=1e-12).all() and (q.old_reference_gap<=1e-12).all();count+=len(q)
  for p in [folder/'record.json',folder/'whitening-equivalence.csv',folder/'vectors.npz']:hashes[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
 (out/'result.json').write_text(json.dumps(dict(audited_at_utc=now(),passed=True,checks=checks,whitening_query_checks=count,input_sha256=hashes,scope='Author consistency checks of exploratory transfer comparisons; no field validation or independent reproduction'),indent=2)+'\n');print(json.dumps(dict(passed=True,checks=len(checks),whitening_query_checks=count)))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--out',type=Path,required=True);a=p.parse_args();audit(a.root,a.out)
