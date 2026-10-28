"""Deterministic per-forecast information bounds, fixed protocol v1."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import time

import numpy as np

from bounds import evaluate,LP_OPTIONS
from record import ROOT,now

def analyze(folder,output,member_count=50):
    design=json.loads((ROOT/'protocol/design-v1.json').read_text());output=Path(output);output.mkdir(parents=True,exist_ok=True)
    source=Path(folder)/'temperatures.npz';saved=np.load(source,allow_pickle=False)
    values=saved['kelvin'];portfolios=json.loads(str(saved['portfolios_json']))
    assert values.shape==(50,12,12)
    date=Path(folder).parts[-3];model=Path(folder).parts[-2];lead=int(Path(folder).parts[-1])
    member_seed=int(hashlib.sha256(f'{design["seed"]}|{date}|{model}|{lead}'.encode()).hexdigest()[:16],16)
    order=np.random.default_rng(member_seed).permutation(50)
    members=np.arange(50) if member_count==50 else np.sort(order[:member_count])
    values=values[members]
    start=time.monotonic();results=[]
    for portfolio_idx,portfolio in enumerate(portfolios):
        for size,indices in design['sizes'].items():
            size=int(size);temperatures=values[:,portfolio_idx,:][:,indices]
            for threshold in design['thresholds_c']:
                X=(temperatures>=threshold+273.15).astype(np.uint8)
                rows=evaluate(X,[int(size*f) for f in design['capacity_fractions']])
                for row in rows:
                    key=f'{date}|{model}|{lead}|{portfolio["center"]}|{portfolio["geometry"]}|{size}|{threshold}|{row["k"]}|{member_count}'
                    row.update(date=date,model=model,lead=lead,**portfolio,n=size,threshold_c=threshold,
                               member_count=member_count,case_key=key,portfolio_index=portfolio_idx,
                               informative=int(row['uncertain_sites']>=4 and .1<=row['q']<=.9))
                    results.append(row)
        print(json.dumps({'portfolio':portfolio,'rows_so_far':len(results),'observed_at_utc':now()}),flush=True)
    path=output/f'bounds-{member_count}.csv'
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(results[0]));writer.writeheader();writer.writerows(results)
    summary={'completed_at_utc':now(),'source_path':str(source.relative_to(ROOT)) if source.is_relative_to(ROOT) else str(source),
             'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output_path':str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
             'output_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
             'date':date,'model':model,'lead':lead,'member_count':member_count,'member_ids':(members+1).tolist(),
             'rows':len(results),'elapsed_seconds':time.monotonic()-start,'lp_options':LP_OPTIONS,
             'lp_count':sum(x['lp_count'] for x in results),
             'max_primal_residual':max(x['max_primal_residual'] for x in results),
             'max_dual_violation':max(x['max_dual_violation'] for x in results),
             'max_duality_gap':max(x['max_duality_gap'] for x in results)}
    (output/f'summary-{member_count}.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary),flush=True)
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True)
    p.add_argument('--members',type=int,choices=[10,25,50],default=50);a=p.parse_args()
    analyze(ROOT/a.input,ROOT/a.output,a.members)
