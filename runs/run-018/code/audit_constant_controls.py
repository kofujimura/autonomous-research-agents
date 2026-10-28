"""Plan-v13 choice/confidence/screen audit of a genuinely constant input."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np,pandas as pd
from records import ROOT,now

def audit(root,out,corrected=False):
 root=Path(root);out=Path(out);out.mkdir(parents=True,exist_ok=False);records=[];hashes={}
 cases=[('constant-corrected-seed-0','main-corrected'),('constant-corrected-all','controls/all-corrected-seed-0'),('constant-corrected-hgb','controls/hgb-corrected')] if corrected else [('constant-seed-0','main'),('constant-seed-1000','controls/seed-1000'),('constant-seed-2000','controls/seed-2000'),('constant-all','controls/full-features'),('constant-hgb','controls/hgb')]
 for tag,baseline in cases:
  different_refs=0;different_conf=0;total=0;split_count=0;rotation_records=[];replay_changes=dict(reference=0,confidence=0,mismatch=0)
  for rotation in range(4):
   folder=root/f'analysis/controls/{tag}/r{rotation}';cp=folder/'predictions.csv';bp=root/f'analysis/{baseline}/r{rotation}/predictions.csv';meta=json.loads((folder/'control-record.json').read_text());x=pd.read_csv(cp);y=pd.read_csv(bp);x=x[x.method=='pair_constant'].set_index('query_id');y=y[y.method=='hydro_pair'].set_index('query_id').loc[x.index];assert x.index.is_unique and y.index.is_unique
   dref=int(x.reference_id.ne(y.reference_id).sum());dconf=int((~np.isclose(x.confidence,y.confidence,rtol=0,atol=1e-12)).sum());total+=len(x);different_refs+=dref;different_conf+=dconf
   if corrected:
    old_path=root/f"analysis/controls/{tag.replace('constant-corrected-','constant-')}/r{rotation}/predictions.csv";old=pd.read_csv(old_path);old=old[old.method=='pair_constant'].set_index('query_id');assert set(old.index)==set(x.index);old=old.loc[x.index]
    replay_changes['reference']+=int(x.reference_id.ne(old.reference_id).sum());replay_changes['confidence']+=int((~np.isclose(x.confidence,old.confidence,rtol=0,atol=1e-12)).sum());replay_changes['mismatch']+=int(x.mismatch.ne(old.mismatch).sum());hashes[str(old_path.relative_to(root))]=hashlib.sha256(old_path.read_bytes()).hexdigest()
   added=np.load(folder/'noise-training.npz')['noise'];assert np.all(added==0)
   feature=meta['feature_checks']['pair_constant'];used=feature['added_feature_used_splits']
   if used is not None:assert used==0;split_count+=used
   rotation_records.append(dict(rotation=rotation,nonempty_queries=len(x),changed_reference_n=dref,changed_confidence_n=dconf,training_added_values_all_zero=True,added_feature_used_splits=used))
   for p in [cp,bp,folder/'noise-training.npz',folder/'control-record.json']:hashes[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
  selected=pd.read_csv(root/f'analysis/controls/{tag}-summary/selected-050.csv');xx=set(selected.loc[selected.method=='pair_constant','query_id']);yy=set(selected.loc[selected.method=='hydro_pair','query_id']);assert len(xx)==len(yy)
  record=dict(condition=tag,nonempty_queries=total,changed_reference_n=different_refs,changed_confidence_n=different_conf,screened_n=len(xx),screened_overlap_n=len(xx&yy),screened_changed_n=len(xx-yy),training_added_values_all_zero=True,added_feature_used_splits=None if tag.endswith('hgb') else split_count,rotations=rotation_records)
  if corrected:record.update({'replay_changed_'+k+'_n':v for k,v in replay_changes.items()})
  records.append(record)
 (out/'audit.json').write_text(json.dumps(dict(audited_at_utc=now(),confidence_tolerance=1e-12,conditions=records,input_sha256=hashes),indent=2)+'\n');pd.DataFrame([{k:v for k,v in r.items() if k!='rotations'} for r in records]).to_csv(out/'counts.csv',index=False);print(json.dumps(records))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--out',type=Path,required=True);p.add_argument('--corrected',action='store_true');a=p.parse_args();audit(a.root,a.out,a.corrected)
