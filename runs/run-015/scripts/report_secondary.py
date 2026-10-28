"""Summarize completed prespecified sensitivity runs, retaining unresolved cases."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from bounds import TOL
from record import ROOT
from summarize import clean,markdown_table
from secondary import choose_cases

def source_reference(path):
    path=Path(path).resolve()
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)

def main():
    p=argparse.ArgumentParser();p.add_argument('--cases',required=True);p.add_argument('--secondary',required=True)
    p.add_argument('--members',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    primary=pd.read_csv(a.cases,dtype={'date':str});design=json.loads((ROOT/'protocol/design-v1.json').read_text())
    expected=choose_cases(primary,design);expected_keys=set(expected['case_key'])
    integer=[];epsilon=[];seen={}
    for path in sorted(Path(a.secondary).rglob('*.json')):
        if not (path.name.endswith('-integer.json') or path.name.endswith('-epsilon.json')):continue
        item=json.loads(path.read_text());key=item['case_key'];assert key in expected_keys
        task='integer' if 'integer' in item else 'epsilon';assert (task,key) not in seen;seen[task,key]=str(path)
        if task=='integer':
            for mode,result in item['integer'].items():
                complete=result['lower']['status']==0 and result['upper']['status']==0
                old=item['continuous_original'][mode]
                row={'case_key':key,'date':item['date'],'mode':mode,'completed_optimal':complete,
                     'lower_status':result['lower']['status'],'upper_status':result['upper']['status'],
                     'continuous_width':old['upper']-old['lower'],'integer_width':None,'width_reduction':None,
                     'source_path':source_reference(path)}
                if complete:
                    lo=result['lower']['value'];hi=result['upper']['value']
                    assert lo>=old['lower']-TOL and hi<=old['upper']+TOL
                    row.update(integer_width=max(0,hi-lo),width_reduction=(old['upper']-old['lower'])-(hi-lo))
                integer.append(row)
        else:
            old=item['continuous_original']['pair']
            epsilon.append({'case_key':key,'date':item['date'],'epsilon':0.0,'width':old['upper']-old['lower'],'source_path':source_reference(path)})
            for eps,result in item['perturbed_pair'].items():
                lo=result['lower']['value'];hi=result['upper']['value']
                assert lo<=old['lower']+TOL and hi>=old['upper']-TOL
                epsilon.append({'case_key':key,'date':item['date'],'epsilon':float(eps),'width':max(0,hi-lo),'source_path':source_reference(path)})
    integer_frame=pd.DataFrame(integer);epsilon_frame=pd.DataFrame(epsilon)
    integer_frame.to_csv(out/'integer-cases.csv',index=False);epsilon_frame.to_csv(out/'epsilon-cases.csv',index=False)
    integer_summary=[]
    if len(integer_frame):
        for mode,part in integer_frame.groupby('mode'):
            completed=part[part['completed_optimal']]
            integer_summary.append({'mode':mode,'attempted':len(part),'optimal_cases':len(completed),
                'unresolved_cases':int((~part['completed_optimal']).sum()),
                'mean_continuous_width_on_completed':float(completed['continuous_width'].mean()) if len(completed) else None,
                'mean_integer_width':float(completed['integer_width'].mean()) if len(completed) else None,
                'mean_width_reduction':float(completed['width_reduction'].mean()) if len(completed) else None,
                'max_width_reduction':float(completed['width_reduction'].max()) if len(completed) else None,
                'nonzero_reduction_cases':int((completed['width_reduction']>TOL).sum())})
    epsilon_summary=[]
    if len(epsilon_frame):
        for eps,part in epsilon_frame.groupby('epsilon'):
            epsilon_summary.append({'epsilon':float(eps),'cases':len(part),'dates':int(part['date'].nunique()),
                                    'mean_width':float(part['width'].mean()),'identified_count':int((part['width']<=TOL).sum()),
                                    'min_width':float(part['width'].min()),'max_width':float(part['width'].max())})
    pd.DataFrame(integer_summary).to_csv(out/'integer-summary.csv',index=False)
    pd.DataFrame(epsilon_summary).to_csv(out/'epsilon-summary.csv',index=False)
    keys=['date','model','lead','center','geometry','n','threshold_c','k']
    matched=primary[primary['matched_date']==True]
    frames=[matched]
    for M in [10,25]:
        for path in sorted(Path(a.members).rglob(f'bounds-{M}.csv')):
            part=pd.read_csv(path,dtype={'date':str})
            part=part[part['date'].isin(set(matched['date']))]
            if len(part):frames.append(part)
    members=pd.concat(frames,ignore_index=True)
    assert not members.duplicated(keys+['member_count']).any()
    members.to_csv(out/'member-cases.csv',index=False)
    member_summary=[]
    for M,part in members[members['n']==12].groupby('member_count'):
        for stratum in ['all','informative']:
            sub=part if stratum=='all' else part[part['informative']==1]
            row={'members':int(M),'stratum':stratum,'cases':len(sub),'dates':int(sub['date'].nunique()),
                 'q_zero':int((sub['q']==0).sum()),'q_one':int((sub['q']==1).sum()),
                 'at_most_two_uncertain':int((sub['uncertain_sites']<=2).sum())}
            for mode in ['marginal','aggregate','pair']:
                width=np.maximum(0,sub[mode+'_upper']-sub[mode+'_lower'])
                row[mode+'_width']=float(width.mean()) if len(sub) else None
                row[mode+'_identified_count']=int((width<=TOL).sum())
            member_summary.append(row)
    pd.DataFrame(member_summary).to_csv(out/'member-summary.csv',index=False)
    report={'expected_selected_cases':len(expected),'integer_cases_recorded':len({key for task,key in seen if task=='integer'}),
            'epsilon_cases_recorded':len({key for task,key in seen if task=='epsilon'}),
            'integer':integer_summary,'epsilon':epsilon_summary,'members':member_summary,
            'scope':'Integer optimality only claimed for status0; moment perturbations are not confidence sets; member informative strata use each sample own criterion and may differ in composition.'}
    (out/'summary.json').write_text(json.dumps(clean(report),indent=2,allow_nan=False)+'\n')
    (out/'table-integer.md').write_text(markdown_table(clean(integer_summary),[('mode','Information'),('attempted','Attempted'),('optimal_cases','Optimal'),('unresolved_cases','Unresolved'),('mean_width_reduction','Mean width reduction'),('max_width_reduction','Maximum reduction')])+'\n')
    (out/'table-epsilon.md').write_text(markdown_table(clean(epsilon_summary),[('epsilon','Moment tolerance'),('cases','N'),('dates','Dates'),('mean_width','Mean pair width'),('identified_count','Identified count')])+'\n')
    (out/'table-members.md').write_text(markdown_table(clean(member_summary),[('members','Members'),('stratum','Stratum'),('cases','N'),('dates','Dates'),('q_zero','q=0'),('q_one','q=1'),('at_most_two_uncertain','≤2 uncertain'),('marginal_width','Marginal width'),('aggregate_width','Aggregate width'),('pair_width','Pair width'),('pair_identified_count','Pair identified')])+'\n')
    print(json.dumps(clean(report),indent=2))

if __name__=='__main__':main()
