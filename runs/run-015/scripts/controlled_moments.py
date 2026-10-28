"""Exploratory exact-margin/aggregate controls for pair-moment imprecision."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from bounds import matrices, interval, TOL
from secondary import choose_cases, source_X
from record import ROOT, now
from summarize import clean, markdown_table


def controlled(X,k,epsilon,aggregate=False):
    problem=matrices(X,'pair',epsilon)
    n=X.shape[1]
    allowance=np.full(len(problem['b'])-1,epsilon)
    allowance[:n]=0
    if aggregate:
        pair_sum=problem['A'][1+n:].sum(axis=0)
        target=float(problem['b'][1+n:].sum())
        problem['A']=np.vstack([problem['A'],pair_sum])
        problem['b']=np.append(problem['b'],target)
        allowance=np.append(allowance,0.0)
    problem['moment_allowance']=allowance
    return interval(problem,k)


def fixtures():
    X=np.random.default_rng(20261026).integers(0,2,size=(30,5),dtype=np.uint8)
    p=matrices(X,'pair',.005);baseline=interval(p,3)
    p['moment_allowance']=np.full(len(p['b'])-1,.005)
    same=interval(p,3)
    exact=interval(matrices(X,'pair'),3)
    p['moment_allowance']=np.zeros(len(p['b'])-1)
    zero=interval(p,3)
    for side in ['lower','upper']:
        assert abs(same[side]['value']-baseline[side]['value'])<=TOL
        assert abs(zero[side]['value']-exact[side]['value'])<=TOL
    return {'uniform_allowances_match':True,'zero_allowances_match':True}


def main():
    p=argparse.ArgumentParser();p.add_argument('--cases',required=True)
    p.add_argument('--output',required=True);a=p.parse_args()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
    fixture=fixtures()
    frame=pd.read_csv(a.cases,dtype={'date':str})
    design=json.loads((ROOT/'protocol/design-v1.json').read_text())
    selected=choose_cases(frame,design);rows=[]
    relaxed={}
    for path in (ROOT/'results/secondary-runs').rglob('*-epsilon.json'):
        item=json.loads(path.read_text());assert item['case_key'] not in relaxed
        relaxed[item['case_key']]=item['perturbed_pair']
    selected.to_csv(out/'selected.csv',index=False)
    for position,(_,row) in enumerate(selected.iterrows()):
        X=source_X(row,ROOT);q=float(np.mean(X.sum(axis=1)>=row['k']))
        details={'case_key':row['case_key'],'source_sha256':row['source_sha256'],
                 'started_at_utc':now(),'conditions':[]}
        for eps in [.005,.02]:
            previous=None
            for exact_aggregate in [False,True]:
                result=controlled(X,int(row['k']),eps,exact_aggregate)
                lo=result['lower']['value'];hi=result['upper']['value']
                assert lo-TOL<=q<=hi+TOL
                assert lo<=row['pair_lower']+TOL and hi>=row['pair_upper']-TOL
                broad=relaxed[row['case_key']][str(eps)]
                assert lo>=broad['lower']['value']-TOL and hi<=broad['upper']['value']+TOL
                if previous is not None:
                    assert lo>=previous[0]-TOL and hi<=previous[1]+TOL
                previous=(lo,hi)
                label='exact_margins_and_aggregate' if exact_aggregate else 'exact_margins'
                rows.append({'case_key':row['case_key'],'date':row['date'],'epsilon':eps,
                             'condition':label,'lower':lo,'upper':hi,'width':max(0,hi-lo),
                             'identified':int(hi-lo<=TOL)})
                details['conditions'].append({'epsilon':eps,'condition':label,'result':result})
        details['completed_at_utc']=now()
        (out/f'{position:03d}.json').write_text(json.dumps(clean(details),indent=2)+'\n')
    cases=pd.DataFrame(rows);cases.to_csv(out/'cases.csv',index=False)
    summaries=[]
    for (eps,condition),part in cases.groupby(['epsilon','condition'],sort=True):
        summaries.append({'epsilon':eps,'condition':condition,'cases':len(part),
                          'dates':int(part['date'].nunique()),'mean_width':float(part['width'].mean()),
                          'identified':int(part['identified'].sum())})
    pd.DataFrame(summaries).to_csv(out/'width-summary.csv',index=False)
    (out/'summary.json').write_text(json.dumps(clean({'exploratory':True,'fixtures':fixture,
        'selected_cases':len(selected),'rows':summaries,'cases_input_sha256':hashlib.sha256(Path(a.cases).read_bytes()).hexdigest()}),indent=2)+'\n')
    (out/'table-controlled-moments.md').write_text(markdown_table(summaries,[
        ('epsilon','Pair allowance'),('condition','Exact moments'),('cases','N'),
        ('dates','Dates'),('mean_width','Mean width'),('identified','Identified')])+'\n')
    print(json.dumps(clean(summaries)))


if __name__=='__main__':main()
