"""Exploratory fixed-query product comparison on one saved forecast file."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import tempfile
import time

import numpy as np

from bounds import matrices,interval,marginal_interval,TOL
from subset_bounds import count_problem,subset_problem,encoding_checks
from record import ROOT,now

def analyze(folder,output):
    folder=Path(folder);output=Path(output);output.mkdir(parents=True,exist_ok=True)
    source=folder/'temperatures.npz';source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    summary_path=output/'summary.json';target=output/'bounds.csv'
    if summary_path.exists():
        summary=json.loads(summary_path.read_text());assert summary['source_sha256']==source_hash
        assert summary['output_sha256']==hashlib.sha256(target.read_bytes()).hexdigest()
        return summary
    if target.exists():
        target.rename(output/('orphan-bounds-'+now().replace(':','')+'.csv'))
    design=json.loads((ROOT/'protocol/design-v1.json').read_text())
    queries=json.loads((ROOT/'protocol/subset-design-v3.json').read_text())['queries']
    saved=np.load(source,allow_pickle=False);values=saved['kelvin'];portfolios=json.loads(str(saved['portfolios_json']))
    date=folder.parts[-3];model=folder.parts[-2];lead=int(folder.parts[-1]);start=time.monotonic()
    count_rows=0;max_primal=0.0;max_dual=0.0;max_gap=0.0;lp_count=0;encodings=[]
    with tempfile.NamedTemporaryFile('w',dir=output,prefix='bounds-',suffix='.partial.csv',delete=False,newline='') as f:
        partial=Path(f.name);writer=None
        for pi,portfolio in enumerate(portfolios):
            for threshold in design['thresholds_c']:
                X=(values[:,pi,:]>=threshold+273.15).astype(np.uint8)
                p=X.mean(axis=0);uncertain=(p>0)&(p<1)
                parents={'pair':matrices(X,'pair'),'count':count_problem(X)}
                encodings.append(encoding_checks(X))
                restored=np.unpackbits(np.packbits(X.reshape(-1),bitorder='big'),count=X.size,bitorder='big').reshape(X.shape)
                for size,items in queries.items():
                    size=int(size)
                    for qi,item in enumerate(items):
                        indices=item['indices'];outside=[i for i in range(12) if i not in indices]
                        query_X=X[:,indices];query_sum=query_X.sum(axis=1)
                        outside_sum=X[:,outside].sum(axis=1)
                        problems={mode:subset_problem(problem,X,indices) for mode,problem in parents.items()}
                        problems['restricted_pair']=matrices(query_X,'pair')
                        query_pmf=np.bincount(query_sum.astype(int),minlength=size+1)/len(X)
                        for k in [size//4,size//2,3*size//4]:
                            q=float(np.mean(query_sum>=k));qcount=float(query_pmf[k:].sum())
                            qmask=float(np.mean(restored[:,indices].sum(axis=1)>=k))
                            assert abs(q-qcount)<1e-12 and q==qmask
                            row={'date':date,'model':model,'lead':lead,**portfolio,'portfolio_index':pi,
                                 'threshold_c':threshold,'query_size':size,'query_id':qi,'query_type':item['type'],
                                 'query_indices':json.dumps(indices),'k':k,'q':q,'count_oracle_q':qcount,'mask_oracle_q':qmask,
                                 'query_uncertain_sites':int(uncertain[indices].sum()),
                                 'complement_uncertain_sites':int(uncertain[outside].sum()),
                                 'complement_sites_deterministic':int(not uncertain[outside].any()),
                                 'empirical_complement_count_constant':int(np.ptp(outside_sum)==0),
                                 'empirical_total_count_constant':int(np.ptp(X.sum(axis=1))==0),
                                 'total_count_nonzero_bins':len(np.unique(X.sum(axis=1))),
                                 'pair_possible_states':parents['pair']['possible_states'],
                                 'count_possible_states':parents['count']['possible_states']}
                            lo,hi=marginal_interval(query_X.mean(axis=0),k)
                            row['marginal_lower']=lo;row['marginal_upper']=hi
                            diagnostics=[]
                            for mode,problem in problems.items():
                                r=interval(problem,k)
                                row[mode+'_lower']=r['lower']['value'];row[mode+'_upper']=r['upper']['value']
                                row[mode+'_width']=max(0,r['upper']['value']-r['lower']['value'])
                                assert r['lower']['value']<=q+TOL and r['upper']['value']>=q-TOL
                                assert r['lower']['value']>=lo-TOL and r['upper']['value']<=hi+TOL
                                diagnostics.extend(r.values())
                            assert row['pair_lower']>=row['restricted_pair_lower']-TOL
                            assert row['pair_upper']<=row['restricted_pair_upper']+TOL
                            if row['complement_sites_deterministic']:
                                assert row['count_width']<=TOL
                            row['informative']=int(row['query_uncertain_sites']>=4 and row['complement_uncertain_sites']>=2 and .1<=q<=.9)
                            row['count_minus_pair_width']=row['count_width']-row['pair_width']
                            row['max_primal_residual']=max(d['primal_residual'] for d in diagnostics)
                            row['max_dual_violation']=max(d['dual_violation'] for d in diagnostics)
                            row['max_duality_gap']=max(d['duality_gap'] for d in diagnostics)
                            lp_count+=sum(not d['constant_objective'] for d in diagnostics)
                            max_primal=max(max_primal,row['max_primal_residual']);max_dual=max(max_dual,row['max_dual_violation']);max_gap=max(max_gap,row['max_duality_gap'])
                            if writer is None:writer=csv.DictWriter(f,fieldnames=list(row));writer.writeheader()
                            writer.writerow(row);count_rows+=1
                f.flush()
                print(json.dumps({'portfolio':portfolio,'threshold_c':threshold,'completed_rows':count_rows,'observed_at_utc':now()}),flush=True)
    assert count_rows==1728
    partial.rename(target)
    summary={'completed_at_utc':now(),'source_path':str(source),'source_sha256':source_hash,'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
             'date':date,'model':model,'lead':lead,'rows':count_rows,'elapsed_seconds':time.monotonic()-start,
             'max_primal_residual':max_primal,'max_dual_violation':max_dual,'max_duality_gap':max_gap,'lp_count':lp_count,
             'parent_encoding_checks':len(encodings),'encoding':encodings[0],'mask_round_trip_errors':sum(e['round_trip_errors'] for e in encodings),
             'exploratory':True,'plan':'protocol/plan-v3.1-subset-clarification.md'}
    assert all(e==encodings[0] for e in encodings)
    summary_path.write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True)
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    analyze(ROOT/a.input,ROOT/a.output)
