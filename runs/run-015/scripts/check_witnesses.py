"""Check saved continuous witnesses against raw moments and dual inequalities."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from bounds import matrices,TOL
from record import ROOT
from secondary import source_X

def check(problem,result,k,sign,X,mode):
    if result.get('constant_objective'):
        event=(problem['state_sums']>=k).astype(float)
        assert np.all(event==event[0]) and abs(result['value']-event[0])<=TOL
        return {'constant':True,'primal_residual':0.0,'dual_violation':0.0,'gap':0.0}
    witness=result['witness'];states=np.asarray(witness['states'],dtype=float);weights=np.asarray(witness['probability'])
    assert np.array_equal(witness['active'],problem['active']) and witness['fixed_ones']==problem['fixed_ones']
    assert len(states)==len(weights) and np.isin(states,[0,1]).all() and np.min(weights)>=-TOL
    active=np.asarray(witness['active']);Z=X[:,active];features=[np.ones(len(weights))];rhs=[1.0]
    # Construct raw target moments independently of the solver's stored rhs.
    features.extend(states.T);rhs.extend(Z.mean(axis=0))
    if mode=='aggregate':
        sums=states.sum(axis=1);observed=Z.sum(axis=1)
        features.append(sums*(sums-1)/2);rhs.append(float(np.mean(observed*(observed-1)/2)))
    else:
        for i in range(Z.shape[1]):
            for j in range(i+1,Z.shape[1]):
                features.append(states[:,i]*states[:,j]);rhs.append(float(np.mean(Z[:,i]*Z[:,j])))
    residual=float(np.max(np.abs(np.asarray(features)@weights-np.asarray(rhs))))
    objective=(states.sum(axis=1)+witness['fixed_ones']>=k).astype(float)
    value=float(objective@weights);assert abs(value-result['value'])<=TOL and residual<=TOL
    state_ids=lambda values:(values.astype(np.uint64)*(2**np.arange(values.shape[1],dtype=np.uint64))).sum(axis=1)
    assert np.isin(state_ids(states),state_ids(problem['states'])).all()
    y=np.asarray(witness['equality_dual']);event=(problem['state_sums']>=k).astype(float)
    reduced=sign*event-problem['A'].T@y;violation=float(max(0,-reduced.min()))
    gap=float(abs(problem['b']@y-sign*value));assert violation<=TOL and gap<=TOL
    return {'constant':False,'primal_residual':residual,'dual_violation':violation,'gap':gap}

def main():
    p=argparse.ArgumentParser();p.add_argument('--cases',required=True);p.add_argument('--secondary',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    frame=pd.read_csv(a.cases,dtype={'date':str}).set_index('case_key',verify_integrity=True)
    checks=[];files=0;integer_checks=[]
    for path in sorted(Path(a.secondary).rglob('*-integer.json')):
        item=json.loads(path.read_text());row=frame.loc[item['case_key']];X=source_X(row,ROOT).astype(float);files+=1
        for mode,results in item['continuous_witness'].items():
            problem=matrices(X,mode)
            for side,sign in [('lower',1),('upper',-1)]:
                result=results[side]
                assert abs(result['value']-item['continuous_original'][mode][side])<=TOL
                checks.append({'case_key':item['case_key'],'mode':mode,'side':side,**check(problem,result,int(row['k']),sign,X,mode)})
        for mode,results in item['integer'].items():
            for side,result in results.items():
                if 'integer_witness' not in result:continue
                w=result['integer_witness'];counts=np.asarray(w['counts'],dtype=np.int64);M=w['members']
                assert np.array_equal(counts,np.asarray(w['counts'])) and M==len(X)
                assert np.all(counts>=0) and counts.sum()==M
                states=np.asarray(w['states'],dtype=float);assert np.isin(states,[0,1]).all()
                totals=X.sum(axis=0)
                assert np.array_equal(w['active'],(totals>0)&(totals<M)) and w['fixed_ones']==int((totals==M).sum())
                Z=X[:,w['active']];assert np.array_equal(states.T@counts,Z.sum(axis=0))
                if mode=='aggregate':
                    sums=states.sum(axis=1);original=Z.sum(axis=1)
                    assert np.sum(counts*sums*(sums-1)/2)==np.sum(original*(original-1)/2)
                else:
                    assert np.array_equal((states.T*counts)@states,Z.T@Z)
                value=float(np.sum(counts*(states.sum(axis=1)+w['fixed_ones']>=row['k']))/M)
                assert abs(value-result['value'])<=TOL
                integer_checks.append({'case_key':item['case_key'],'mode':mode,'side':side,'status':result['status'],'value':value})
    summary={'status':'passed','files_checked':files,'endpoint_witness_checks':len(checks),
             'max_primal_residual':max((r['primal_residual'] for r in checks),default=0),
             'max_dual_violation':max((r['dual_violation'] for r in checks),default=0),
             'max_gap':max((r['gap'] for r in checks),default=0),
             'integer_feasibility_witnesses_checked':len(integer_checks),
             'scope':'Continuous primal/dual and exact integer feasibility witnesses; integer optimality still uses saved solver bounds/status or an optional re-solve.'}
    Path(a.output).write_text(json.dumps({'summary':summary,'checks':checks,'integer_checks':integer_checks},indent=2)+'\n');print(json.dumps(summary))

if __name__=='__main__':main()
