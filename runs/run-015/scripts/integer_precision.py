"""Exploratory fixed-size/moment-imprecision interaction, with saved witnesses."""
import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

from bounds import binary_states,matrices,interval,integer_limits,TOL
from secondary import choose_cases,source_X
from record import ROOT,now
from summarize import clean,markdown_table


def finite(value):return float(value) if value is not None and np.isfinite(value) else None


def fixtures():
    X=np.array([[0,0],[1,1]],dtype=np.uint8);states=binary_states(2);tests=[]
    legacy=interval(matrices(X,'pair'),1,integer=True)
    assert legacy['lower']['status']==0 and legacy['upper']['status']==0
    for eps in [0,.1,.5]:
        # Use full support also at zero to test the count-bound implementation.
        problem=matrices(X,'pair',eps or 1e-12)
        if eps==0:problem['moment_allowance']=np.zeros(len(problem['b'])-1)
        lo,hi=integer_limits(problem);feasible=[]
        for choices in itertools.product(range(4),repeat=2):
            counts=np.bincount(choices,minlength=4);activity=problem['A']@counts
            if np.all(activity>=lo)&np.all(activity<=hi):
                feasible.append(float(np.mean(states[list(choices)].sum(axis=1)>=1)))
        result=interval(problem,1,integer=True)
        assert result['lower']['status']==0 and result['upper']['status']==0
        assert abs(result['lower']['value']-min(feasible))<=TOL
        assert abs(result['upper']['value']-max(feasible))<=TOL
        if eps==0:
            for side in ['lower','upper']:assert abs(result[side]['value']-legacy[side]['value'])<=TOL
        tests.append({'epsilon':eps,'enumerated_ensembles':16,'feasible_ensembles':len(feasible),'lower':min(feasible),'upper':max(feasible)})
    return tests


def case_bounds(item,free_width):
    lo=item['result']['lower'];hi=item['result']['upper']
    ldual=finite(lo.get('objective_dual_bound'));udual=finite(hi.get('objective_dual_bound'))
    low_value=finite(lo.get('value'));high_value=finite(hi.get('value'))
    lower_width=max(.04,(high_value-low_value) if low_value is not None and high_value is not None else 0)
    upper_width=min(free_width,min(1,udual) if udual is not None else 1)
    if ldual is not None:upper_width=min(upper_width,(min(1,udual) if udual is not None else 1)-max(0,ldual))
    assert lower_width<=upper_width+TOL
    optimal=lo['status']==0 and hi['status']==0
    width=high_value-low_value if optimal else None
    if optimal:assert abs(width-lower_width)<=TOL and abs(width-upper_width)<=TOL
    return {'case_key':item['case_key'],'optimal':optimal,'lower_status':lo['status'],'upper_status':hi['status'],
            'width':width,'width_lower_bound':max(0,lower_width),'width_upper_bound':max(0,upper_width),
            'free_width':free_width,'structural_floor':.04}


def check_item(item,row):
    X=source_X(row,ROOT);problem=matrices(X,'pair',.02);lo,hi=integer_limits(problem)
    tiny=matrices(X,'pair',.005);a,b=integer_limits(tiny)
    exact=np.rint(tiny['b']*50);assert np.array_equal(a,exact) and np.array_equal(b,exact)
    for side,result in item['result'].items():
        assert result['constraint_lower_counts']==lo.astype(int).tolist()
        assert result['constraint_upper_counts']==hi.astype(int).tolist()
        if 'integer_witness' not in result:continue
        w=result['integer_witness'];states=np.asarray(w['states'],dtype=float);counts=np.asarray(w['counts'],dtype=np.int64)
        assert w['members']==50 and w['active']==[True]*12 and w['fixed_ones']==0
        assert np.array_equal(counts,np.asarray(w['counts'])) and np.all(counts>=0) and counts.sum()==50
        assert np.isin(states,[0,1]).all() and states.shape[1]==12
        features=np.vstack([np.ones(len(counts)),states.T,
            *[states[:,i]*states[:,j] for i in range(12) for j in range(i+1,12)]])
        activity=features@counts;assert np.all(activity>=lo) and np.all(activity<=hi)
        value=float(np.sum(counts*(states.sum(axis=1)>=row['k']))/50)
        assert abs(value-result['value'])<=TOL
    event=X.sum(axis=1)>=row['k'];assert event.any() and (~event).any()
    for direction,index,value in [('lower',int(np.flatnonzero(event)[0]),0),('upper',int(np.flatnonzero(~event)[0]),1)]:
        changed=X.copy();changed[index]=value
        fresh=matrices(changed,'pair',.02)
        assert np.max(np.abs((fresh['b']-problem['b'])*50))<=1+TOL
        target=float(np.mean(changed.sum(axis=1)>=row['k']))
        assert abs(target-float(event.mean())-(-.02 if direction=='lower' else .02))<=TOL


def summarize(out,cases):
    frame=pd.read_csv(cases,dtype={'date':str});design=json.loads((ROOT/'protocol/design-v1.json').read_text())
    selected=choose_cases(frame,design).set_index('case_key',verify_integrity=True)
    old={};relaxed={}
    for path in (ROOT/'results/secondary-runs').rglob('*-integer.json'):
        x=json.loads(path.read_text());old[x['case_key']]=x['integer']['pair']
    for path in (ROOT/'results/secondary-runs').rglob('*-epsilon.json'):
        x=json.loads(path.read_text());relaxed[x['case_key']]=x['perturbed_pair']['0.02']
    exact_width=[];rows=[]
    for key,row in selected.iterrows():
        base=old[key];assert base['lower']['status']==0 and base['upper']['status']==0
        exact_width.append(base['upper']['value']-base['lower']['value'])
        path=out/'raw'/f"{int(row['selection_position']) if 'selection_position' in row else list(selected.index).index(key):03d}.json"
        if not path.exists():continue
        item=json.loads(path.read_text());assert item['case_key']==key;check_item(item,row)
        free=relaxed[key]['upper']['value']-relaxed[key]['lower']['value']
        rows.append(case_bounds(item,free))
    data=pd.DataFrame(rows);data.to_csv(out/'cases.csv',index=False)
    completed=data[data['optimal']] if len(data) else data
    report={'exploratory':True,'selected_cases':len(selected),'recorded_cases':len(data),
            'optimal_cases':len(completed),'unresolved_cases':int((~data['optimal']).sum()) if len(data) else 0,
            'exact_integer_width_mean':float(np.mean(exact_width)),'epsilon005_integer_width_mean':float(np.mean(exact_width)),
            'epsilon005_lattice_equivalent_cases':len(selected),
            'epsilon02_mean_width_lower_bound':float(data['width_lower_bound'].mean()) if len(data) else None,
            'epsilon02_mean_width_upper_bound':float(data['width_upper_bound'].mean()) if len(data) else None,
            'epsilon02_optimal_mean_width':float(completed['width'].mean()) if len(completed) else None,
            'epsilon02_structural_floor_cases':len(data),'status':'complete' if len(data)==len(selected) else 'incomplete_planned_cases'}
    (out/'summary.json').write_text(json.dumps(clean(report),indent=2)+'\n')
    table=[{'radius':.005,'attempted':len(selected),'optimal':len(selected),'unresolved':0,'low':report['epsilon005_integer_width_mean'],'high':report['epsilon005_integer_width_mean'],'basis':'Saved exact-count optima; lattice identity'},
           {'radius':.02,'attempted':len(data),'optimal':len(completed),'unresolved':report['unresolved_cases'],'low':report['epsilon02_mean_width_lower_bound'],'high':report['epsilon02_mean_width_upper_bound'],'basis':'New bounded integer solves and witnesses'}]
    (out/'table-integer-precision.md').write_text(markdown_table(table,[('radius','Moment radius'),('attempted','N'),('optimal','Both endpoints optimal'),('unresolved','Unresolved'),('low','Mean width lower bound'),('high','Mean width upper bound'),('basis','Basis')])+'\n')
    print(json.dumps(clean(report)))


def main():
    p=argparse.ArgumentParser();p.add_argument('--cases',required=True);p.add_argument('--output',required=True)
    p.add_argument('--summarize',action='store_true');a=p.parse_args();out=Path(a.output)
    if a.summarize:summarize(out,a.cases);return
    out.mkdir(parents=True,exist_ok=False);(out/'raw').mkdir()
    (out/'fixtures.json').write_text(json.dumps(fixtures(),indent=2)+'\n')
    frame=pd.read_csv(a.cases,dtype={'date':str});design=json.loads((ROOT/'protocol/design-v1.json').read_text())
    selected=choose_cases(frame,design);selected.to_csv(out/'selected.csv',index=False)
    for position,(_,row) in enumerate(selected.iterrows()):
        X=source_X(row,ROOT);problem=matrices(X,'pair',.02)
        result={'case_key':row['case_key'],'selection_position':position,'source_sha256':row['source_sha256'],
                'started_at_utc':now(),'result':interval(problem,int(row['k']),integer=True),'completed_at_utc':now()}
        (out/'raw'/f'{position:03d}.json').write_text(json.dumps(clean(result),indent=2)+'\n')
        check_item(result,row)
        print(json.dumps({'position':position,'completed_at_utc':now(),'statuses':[result['result'][side]['status'] for side in ['lower','upper']]}),flush=True)
    summarize(out,a.cases)


if __name__=='__main__':main()
