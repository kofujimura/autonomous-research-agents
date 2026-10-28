"""Saved-decision diagnostics of nontrivial fixed screens and window influence."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
import pandas as pd
from summarize_matching import bootstrap,PRIMARY,BASES
from records import ROOT,now
from score_ambiguity import diagnose

def audit(root,out):
 root=Path(root).resolve();out=Path(out);out.mkdir(parents=True,exist_ok=False)
 original=Path(json.loads((root/'manifest.json').read_text())['research_directory']);fixed=[];influence=[];windows=[];hashes={};conditions=[];ambiguity=[]
 for summary in sorted(p.parent for p in (root/'analysis').rglob('summary.json') if p.parent.name.endswith('-summary')):
  key=str(summary.relative_to(root));meta=json.loads((summary/'summary.json').read_text());source=meta.get('source_predictions')
  if source:raw=Path(source)
  elif key=='analysis/primary-summary':raw=Path('analysis/main')
  elif key=='analysis/transfer-summary':raw=Path('analysis/transfer-combined')
  else:raw=summary.relative_to(root).parent/summary.name.removesuffix('-summary')
  raw=root/(raw.relative_to(original) if raw.is_absolute() else raw)
  predictions=pd.concat([pd.read_csv(raw/f'r{r}/predictions.csv') for r in range(4)],ignore_index=True)
  ambiguity.extend(dict(analysis=key,**row) for row in diagnose(predictions));selected=pd.read_csv(summary/'selected-050.csv');regional=pd.read_csv(summary/'region-metrics.csv');regional=regional[regional.coverage==.5];conditions.append(key)
  for selector in BASES:
   if selector not in selected.method.unique():continue
   keys=selected.loc[(selected.method==selector)&selected.nontrivial_matchable,['region','query_id']]
   common=predictions.merge(keys,on=['region','query_id'],how='inner',validate='many_to_one')
   base=common[common.method==selector].groupby('region').mismatch.mean()
   for region in sorted(predictions.region.unique()):windows.append(dict(analysis=key,selector=selector,region=region,conditional_selected_n=int((keys.region==region).sum())))
   for method in sorted(predictions.method.unique()):
    g=common[common.method==method];risks=g.groupby('region').mismatch.mean();assert risks.index.equals(base.index)
    delta=risks-base;ci=bootstrap(delta.to_numpy())
    fixed.append(dict(analysis=key,selector=selector,method=method,conditional_selected_n=len(g),window_n=len(risks),macro_risk=float(risks.mean()) if len(risks) else None,pooled_risk=float(g.mismatch.mean()) if len(g) else None,difference=float(delta.mean()) if len(delta) else None,low=ci[0],high=ci[1]))
  wide=regional.pivot(index='region',columns='method',values='risk')
  for method in [m for m in PRIMARY if m in wide]:
   for baseline in [b for b in BASES if b in wide]:
    paired=wide[[method,baseline]].dropna();delta=paired[method]-paired[baseline];full=float(delta.mean())
    for region in delta.index:
     omitted=float(delta.drop(region).mean()) if len(delta)>1 else None
     influence.append(dict(analysis=key,method=method,baseline=baseline,omitted_window=region,remaining_window_n=len(delta)-1,full_difference=full,omission_difference=omitted,sign_changed=bool(np.sign(full)!=np.sign(omitted)) if omitted is not None else None,benchmark_changed=bool((full<=-.02)!=(omitted<=-.02)) if omitted is not None else None))
  for p in [summary/'summary.json',summary/'selected-050.csv',summary/'region-metrics.csv']+[raw/f'r{r}/predictions.csv' for r in range(4)]:hashes[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
 pd.DataFrame(ambiguity).to_csv(out/'score-ambiguity.csv',index=False);pd.DataFrame(fixed).to_csv(out/'fixed-nontrivial.csv',index=False,float_format='%.17g');pd.DataFrame(influence).to_csv(out/'leave-window-out.csv',index=False,float_format='%.17g');pd.DataFrame(windows).to_csv(out/'window-counts.csv',index=False)
 record=dict(checked_at_utc=now(),conditions=conditions,condition_n=len(conditions),fixed_screen_rows=len(fixed),influence_rows=len(influence),input_sha256=hashes,scope='Exploratory label-conditional fixed-query diagnosis and all leave-one-window-out own-screen contrasts; no rescreening, replacement primary or field validation')
 (out/'result.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:record[k] for k in ['condition_n','fixed_screen_rows','influence_rows']}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--out',type=Path,required=True);a=p.parse_args();audit(a.root,a.out)
