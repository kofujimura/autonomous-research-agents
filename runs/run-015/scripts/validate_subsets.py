"""Analytic and randomized validation of the exploratory subset-product LPs."""
import argparse
import json
from pathlib import Path
import time
import numpy as np

from bounds import matrices,interval,marginal_interval,TOL
from subset_bounds import count_problem,subset_problem,encoding_checks
from record import ROOT,now

def check_query(X,indices,k):
    subset=X[:,indices];q=float(np.mean(subset.sum(1)>=k))
    result={}
    for name,problem in [('count',count_problem(X)),('pair',matrices(X,'pair'))]:
        r=interval(subset_problem(problem,X,indices),k)
        result[name]=[r['lower']['value'],r['upper']['value']]
        assert result[name][0]<=q+TOL and result[name][1]>=q-TOL
    local=interval(matrices(subset,'pair'),k)
    result['restricted_pair']=[local['lower']['value'],local['upper']['value']]
    assert result['pair'][0]>=result['restricted_pair'][0]-TOL
    assert result['pair'][1]<=result['restricted_pair'][1]+TOL
    result['q']=q;return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True);start=time.monotonic();checks=[]
    # Same four marginals and same deterministic total count can hide which
    # two sites co-occur. Pair information fixes this two-site intersection.
    X=np.array([[1,1,0,0],[0,0,1,1]])
    r=check_query(X,[0,1],2)
    assert np.allclose(r['count'],[0,.5],atol=TOL,rtol=0)
    assert np.allclose(r['pair'],[.5,.5],atol=TOL,rtol=0)
    checks.append({'fixture':'pair-stronger','result':r,'X':X.tolist()})
    # A deterministic complement makes the full count PMF a shifted query PMF;
    # third-order parity remains unidentified by pairs. This is an explained
    # edge case and will be counted separately in empirical analyses.
    X=np.array([[0,0,0,0],[0,1,1,0],[1,0,1,0],[1,1,0,0]])
    r=check_query(X,[0,1,2],2)
    assert np.allclose(r['count'],[.75,.75],atol=TOL,rtol=0)
    assert np.allclose(r['pair'],[.25,.75],atol=TOL,rtol=0)
    checks.append({'fixture':'count-stronger-deterministic-complement','result':r,'X':X.tolist()})
    rng=np.random.default_rng(20261026)
    z=.65*rng.normal(size=(50,1))+.75*rng.normal(size=(50,12))
    X=(z>rng.normal(0,.7,12)).astype(int)
    queries=json.loads((ROOT/'protocol/subset-design-v3.json').read_text())['queries']
    for size,items in queries.items():
        n=int(size)
        for item in items:
            for k in [n//4,n//2,3*n//4]:
                checks.append({'fixture':'random-full-query-check','indices':item['indices'],'k':k,
                               'result':check_query(X,item['indices'],k)})
    full=count_problem(X)
    for k in range(1,13):
        r=interval(full,k);q=float(np.mean(X.sum(1)>=k))
        assert abs(r['lower']['value']-q)<TOL and abs(r['upper']['value']-q)<TOL
    encoding=encoding_checks(X)
    assert encoding['coherent_mask_bytes']==75 and encoding['pair_bytes']==59 and encoding['count_bytes']==18
    result={'status':'passed','completed_at_utc':now(),'elapsed_seconds':time.monotonic()-start,
            'checks':checks,'random_fixture':X.tolist(),'encoding':encoding,
            'scope':'Synthetic code/analytic validation, not empirical weather evidence'}
    (out/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['checks','random_fixture']}),flush=True)

if __name__=='__main__':main()
