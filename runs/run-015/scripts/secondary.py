"""Prespecified integer, moment-precision and member-count checks."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from analyze_unit import analyze
from bounds import matrices,interval
from record import ROOT,now

def jsonsafe(value):
    if isinstance(value,dict):return {k:jsonsafe(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [jsonsafe(v) for v in value]
    if isinstance(value,np.generic):value=value.item()
    if isinstance(value,float) and not np.isfinite(value):return {'nonfinite_solver_value':repr(value)}
    return value

def choose_cases(frame,design):
    part=frame[(frame['matched_date']==True)&(frame['n']==12)&(frame['informative']==1)].copy()
    part['selection_hash']=[hashlib.sha256(f'{design["seed"]}|{key}'.encode()).hexdigest() for key in part['case_key']]
    return part.sort_values('selection_hash',kind='stable').head(120)

def source_X(row,root):
    folder=root/'data/weather'/str(row['date'])/row['model']/str(int(row['lead']))
    source=folder/'temperatures.npz'
    assert hashlib.sha256(source.read_bytes()).hexdigest()==row['source_sha256']
    data=np.load(source,allow_pickle=False)['kelvin']
    return (data[:,int(row['portfolio_index']),:]>=row['threshold_c']+273.15).astype(np.uint8)

def run_selected(a,design,root,out):
    frame=pd.read_csv(a.cases,dtype={'date':str})
    cases_sha256=hashlib.sha256(Path(a.cases).read_bytes()).hexdigest()
    selected=choose_cases(frame,design);selected.to_csv(out/'selected-all.csv',index=False)
    selected=selected.iloc[a.start:a.start+a.count]
    for position,(_,row) in enumerate(selected.iterrows(),a.start):
        path=out/f'{position:03d}-{a.task}.json'
        if path.exists():raise RuntimeError('Refuse overwriting a completed secondary result')
        X=source_X(row,root)
        print(json.dumps({'task':a.task,'position':position,'case_key':row['case_key'],'status':'started','observed_at_utc':now()}),flush=True)
        result={'selection_position':position,'case_key':row['case_key'],'selection_hash':row['selection_hash'],
                'date':row['date'],'model':row['model'],'lead':int(row['lead']),
                'center':row['center'],'geometry':row['geometry'],'k':int(row['k']),
                'threshold_c':int(row['threshold_c']),'started_at_utc':now(),'source_sha256':row['source_sha256'],
                'cases_input_sha256':cases_sha256,
                'continuous_original':{mode:{'lower':row[mode+'_lower'],'upper':row[mode+'_upper']} for mode in ['aggregate','pair']}}
        if a.task=='integer':
            result['integer']={}
            for mode in ['aggregate','pair']:
                problem=matrices(X,mode)
                result['integer'][mode]=interval(problem,int(row['k']),integer=True)
                # Retain extremal continuous witnesses and dual multipliers for
                # this fixed subset, in addition to the all-case checks.
                result.setdefault('continuous_witness',{})[mode]=interval(problem,int(row['k']),save_witness=True)
        else:
            result['perturbed_pair']={}
            for epsilon in [.005,.02]:
                problem=matrices(X,'pair',epsilon)
                result['perturbed_pair'][str(epsilon)]=interval(problem,int(row['k']))
        result['completed_at_utc']=now();path.write_text(json.dumps(jsonsafe(result),indent=2,allow_nan=False)+'\n')
        print(json.dumps({'task':a.task,'position':position,'case_key':row['case_key'],'completed_at_utc':result['completed_at_utc']}),flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--task',choices=['integer','epsilon','members'],required=True)
    p.add_argument('--cases');p.add_argument('--start',type=int,default=0);p.add_argument('--count',type=int,default=30)
    p.add_argument('--root',default=str(ROOT));p.add_argument('--output',required=True);a=p.parse_args()
    root=Path(a.root).resolve();out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
    design=json.loads((root/'protocol/design-v1.json').read_text())
    if a.task in ['integer','epsilon']:
        if not a.cases:raise SystemExit('--cases is required')
        run_selected(a,design,root,out)
    else:
        # Enumerate only completed original units, in the fixed design order.
        units=[(date,model,lead) for date in design['dates'] for model in design['models'] for lead in design['leads']
               if (root/'data/weather'/date/model/str(lead)/'complete.json').exists()]
        for date,model,lead in units[a.start:a.start+a.count]:
            source=root/'data/weather'/date/model/str(lead)
            target=out/date/model/str(lead)
            for count in [10,25]:
                summary_path=target/f'summary-{count}.json'
                if summary_path.exists():
                    summary=json.loads(summary_path.read_text())
                    assert summary['source_sha256']==hashlib.sha256((source/'temperatures.npz').read_bytes()).hexdigest()
                    assert summary['output_sha256']==hashlib.sha256((target/f'bounds-{count}.csv').read_bytes()).hexdigest()
                    print(json.dumps({'member_count':count,'date':date,'model':model,'lead':lead,'status':'verified_cached_analysis','observed_at_utc':now()}),flush=True)
                    continue
                analyze(source,target,count)

if __name__=='__main__':main()
