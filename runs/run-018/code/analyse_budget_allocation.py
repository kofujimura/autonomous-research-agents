"""Fixed saved-decision acceptance policies using only observable strata."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
import pandas as pd
from analysis_paths import paths
from summarize_matching import bootstrap,PRIMARY,BASES,COVERAGES
from records import ROOT,now

def allocate(total,counts,context):
 denominator=sum(counts.values())
 if not denominator:return {k:0 for k in counts}
 result={k:total*n//denominator for k,n in counts.items()}
 order=sorted(counts,key=lambda k:(-(total*counts[k]%denominator),hashlib.sha256((context+'|'+str(k)).encode()).hexdigest()))
 for k in order[:total-sum(result.values())]:result[k]+=1
 assert sum(result.values())==total and all(0<=result[k]<=counts[k] for k in counts)
 return result

def analyse(root,out):
 root=Path(root).resolve();out=Path(out);out.mkdir(parents=True,exist_ok=False);cp=paths(root);original=Path(json.loads((root/'manifest.json').read_text())['research_directory'])
 cases=[cp['primary_summary'],cp['hgb_summary']]+[f'analysis/metric-whitened/{condition}-{learner}-summary' for condition in ['primary','polygonC'] for learner in ['hgb','rf-all']]+[f'analysis/polygon/C-{learner}-summary' for learner in ['rf','hgb']]
 metrics=[];contrasts=[];regional=[];accepted=[];subgroups=[];completed=[];missing=[];hashes={}
 for case in cases:
  folder=root/case
  if not (folder/'summary.json').exists():missing.append(case);continue
  meta=json.loads((folder/'summary.json').read_text());source=Path(meta['source_predictions']);source=root/(source.relative_to(original) if source.is_absolute() else source)
  pred=pd.concat([pd.read_csv(source/f'r{r}/predictions.csv') for r in range(4)],ignore_index=True);assert not pred.duplicated(['region','query_id','method']).any();original_metrics=pd.read_csv(folder/'metrics.csv');methods=sorted(pred.method.unique());reference=pred[pred.method==methods[0]][['region','rotation','query_id','vegetation']].sort_values(['region','rotation','query_id']).reset_index(drop=True)
  for method in methods:assert pred[pred.method==method][reference.columns].sort_values(['region','rotation','query_id']).reset_index(drop=True).equals(reference)
  for policy in ['window-budget','vegetation-allocation']:
   for coverage in COVERAGES:
    selected=[]
    for (region,method),g in pred.groupby(['region','method'],sort=True):
     context=f'free-research-018|{policy}|{region}|{coverage}'
     if policy=='window-budget':
      counts={r:int((g.rotation==r).sum()) for r in range(4)};budgets=allocate(int(np.floor(coverage*len(g))),counts,context)
      for r,k in budgets.items():selected.append(g[g.rotation==r].sort_values(['confidence','query_id'],ascending=[False,True],kind='stable').iloc[:k])
     else:
      for rotation,part in g.groupby('rotation',sort=True):
       counts=part.vegetation.value_counts().to_dict();budgets=allocate(int(np.floor(coverage*len(part))),counts,context+'|'+str(rotation))
       for vegetation,k in budgets.items():selected.append(part[part.vegetation==vegetation].sort_values(['confidence','query_id'],ascending=[False,True],kind='stable').iloc[:k])
    selected=pd.concat(selected,ignore_index=True);assert not selected.duplicated(['region','query_id','method']).any();frame=[]
    for (method,region),g in selected.groupby(['method','region'],sort=True):
     row=dict(analysis=case,policy=policy,coverage=coverage,method=method,region=region,n=len(g),errors=int(g.mismatch.sum()),risk=float(g.mismatch.mean()));regional.append(row);frame.append(row)
    frame=pd.DataFrame(frame)
    for method in methods:
     g=selected[selected.method==method];risks=g.groupby('region').mismatch.mean();ci=bootstrap(risks.to_numpy());available=int((pred.method==method).sum());metrics.append(dict(analysis=case,policy=policy,coverage=coverage,method=method,selected_n=len(g),available_n=available,achieved_coverage=len(g)/available,window_n=len(risks),macro_risk=float(risks.mean()) if len(risks) else None,low=ci[0],high=ci[1],pooled_risk=float(g.mismatch.mean()) if len(g) else None))
     original_row=original_metrics[(original_metrics.coverage==coverage)&(original_metrics.method==method)].iloc[0]
     if policy=='vegetation-allocation':assert len(g)==int(original_row.selected_n),'Vegetation allocation changed total primary budget'
     if coverage==1:assert len(g)==available and abs(float(risks.mean())-float(original_row.macro_risk))<=1e-12,'Full-coverage policy differs from archived decisions'
    wide=frame.pivot(index='region',columns='method',values='risk')
    for method in [m for m in PRIMARY if m in wide]:
     for baseline in [b for b in BASES if b in wide]:
      d=(wide[method]-wide[baseline]).dropna();ci=bootstrap(d.to_numpy());contrasts.append(dict(analysis=case,policy=policy,coverage=coverage,method=method,baseline=baseline,window_n=len(d),difference=float(d.mean()) if len(d) else None,low=ci[0],high=ci[1]))
    if coverage==.5:
     q=selected[['region','rotation','query_id','vegetation','method','reference_id','mismatch']].copy();q.insert(0,'policy',policy);q.insert(0,'analysis',case);accepted.append(q)
     for (method,vegetation),base in pred.groupby(['method','vegetation'],sort=True):
      n=int(((selected.method==method)&(selected.vegetation==vegetation)).sum());available=len(base);subgroups.append(dict(analysis=case,policy=policy,method=method,vegetation=vegetation,available_n=available,selected_n=n,coverage=n/available))
  completed.append(case)
  for p in [folder/'summary.json',folder/'metrics.csv']+[source/f'r{r}/predictions.csv' for r in range(4)]:hashes[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
 for name,rows in [('metrics',metrics),('contrasts',contrasts),('region-metrics',regional),('vegetation-coverage',subgroups)]:pd.DataFrame(rows).to_csv(out/(name+'.csv'),index=False,float_format='%.17g')
 pd.concat(accepted,ignore_index=True).to_csv(out/'selected-050.csv',index=False,float_format='%.17g');record=dict(analysed_at_utc=now(),completed_conditions=completed,uncompleted_conditions=missing,input_sha256=hashes,scope='Post-primary acceptance-policy sensitivity on fixed archived references/confidence; no revised primary estimate or field validation')
 (out/'result.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(dict(completed=len(completed),uncompleted=len(missing),metric_rows=len(metrics))))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--out',type=Path,required=True);a=p.parse_args();analyse(a.root,a.out)
