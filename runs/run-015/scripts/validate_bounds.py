"""Prespecified mathematical checks; synthetic fixtures are not study evidence."""
import argparse
import json
from pathlib import Path
import time

import numpy as np
import scipy

from bounds import binary_states,evaluate,matrices,interval,marginal_interval,TOL,LP_OPTIONS
from record import now

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);a=parser.parse_args()
    output=Path(a.output);output.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(20261026);start=time.monotonic();checks=[]
    even=np.array([[0,0,0],[0,1,1],[1,0,1],[1,1,0]])
    odd=1-even
    assert np.array_equal(even.mean(0),odd.mean(0))
    assert np.array_equal(even.T@even,odd.T@odd)
    assert np.mean(even.sum(1)>=2)==.75 and np.mean(odd.sum(1)>=2)==.25
    for name,X,k,expected in [
        ('deterministic',np.tile([1,0,1,0],(50,1)),2,(1,1)),
        ('deterministic-below',np.tile([1,0,1,0],(50,1)),3,(0,0)),
        ('mutually-exclusive',np.eye(4),2,(0,0)),
        ('comonotone',np.array([[0]*8,[1]*8]),4,(.5,.5)),
        ('even-parity',even,2,(.25,.75)),
        ('odd-parity',odd,2,(.25,.75))]:
        row=evaluate(X,[k],validate_marginal=True)[0]
        for mode in ['aggregate','pair']:
            actual=(row[mode+'_lower'],row[mode+'_upper'])
            assert np.allclose(actual,expected,rtol=0,atol=TOL),(name,mode,actual,expected)
        checks.append({'fixture':name,'result':row,'expected':list(expected)})
    for trial in range(40):
        n=int(rng.integers(1,13));M=50
        # Independent and latent common-factor samples, including constants.
        probabilities=rng.uniform(.02,.98,n)
        if trial%2:X=(rng.random((M,n))<probabilities).astype(int)
        else:
            field=.8*rng.standard_normal((M,1))+.6*rng.standard_normal((M,n))
            X=(field>rng.normal(0,1,n)).astype(int)
        capacities=sorted(set([1,max(1,n//2),n]))
        rows=evaluate(X,capacities,validate_marginal=True)
        if trial<8:
            perm=rng.permutation(n);permuted=evaluate(X[:,perm],capacities)
            complemented=evaluate(1-X,[n-k+1 for k in capacities])
            for r,p,c in zip(rows,permuted,complemented):
                for mode in ['marginal','aggregate','pair']:
                    assert abs(r[mode+'_lower']-p[mode+'_lower'])<TOL
                    assert abs(r[mode+'_upper']-p[mode+'_upper'])<TOL
                    assert abs(r[mode+'_lower']-(1-c[mode+'_upper']))<TOL
                    assert abs(r[mode+'_upper']-(1-c[mode+'_lower']))<TOL
        checks.append({'fixture':f'random-{trial:02d}','sites':n,'rows':rows})
    # All binary states are an exactly independent sample, but pair independence
    # does not generally determine capacity tails; check containment rather than
    # incorrectly requiring exact identification.
    X=binary_states(5);independent=evaluate(X,[1,2,3,4,5],True)
    for row in independent:assert abs(row['q']-row['independent_q'])<TOL
    checks.append({'fixture':'exact-independent','rows':independent})
    # Integer feasibility and relaxed moment sets on an analytically checked
    # higher-order counterexample. Integer bounds here attain the same endpoints.
    for mode in ['aggregate','pair']:
        r=interval(matrices(even,mode),2,integer=True)
        assert r['lower']['status']==0 and r['upper']['status']==0
        assert abs(r['lower']['value']-.25)<TOL and abs(r['upper']['value']-.75)<TOL
        checks.append({'fixture':f'parity-integer-{mode}','bounds':r})
    last_width=.5
    for epsilon in [.005,.02]:
        r=interval(matrices(even,'pair',epsilon),2)
        width=r['upper']['value']-r['lower']['value'];assert width>=last_width-TOL
        assert r['lower']['value']<=.25+TOL and r['upper']['value']>=.75-TOL
        checks.append({'fixture':f'parity-epsilon-{epsilon}','bounds':r});last_width=width
    result={'status':'passed','completed_at_utc':now(),'elapsed_seconds':time.monotonic()-start,
            'numpy':np.__version__,'scipy':scipy.__version__,'lp_options':LP_OPTIONS,
            'fixture_count':len(checks),'checks':checks,
            'scope':'Mathematical/code validation; not empirical meteorological or social evidence'}
    (output/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='checks'}),flush=True)

if __name__=='__main__':main()
