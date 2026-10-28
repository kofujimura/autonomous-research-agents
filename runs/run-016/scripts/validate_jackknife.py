"""Check vectorized delete-one computations against explicit recalculation."""
import json
import numpy as np
from records import ROOT,now
from inference_core import entropy,simplex
from jackknife_core import jackknife_change

out=ROOT/'results/validation-jackknife'
if out.exists():raise FileExistsError('Preserve validation')
out.mkdir(parents=True)
ya=np.array([0,0,1,1,2,2]);yb=np.array([0,1,1,2,2,2]);k=3;N=6
rng=np.random.default_rng(16066);pa=rng.dirichlet([1,2,3],N);pb=rng.dirichlet([3,2,1],N)
ia=np.array([[0,2,4],[1,3,5]]);ib=np.array([[1,2,5],[0,3,4]])
def h(y,p,s):
    v=np.eye(k)[y[s]]
    estimate=v.mean(axis=0) if p is None else p.mean(axis=0)+(v-p[s]).mean(axis=0)
    return float(entropy(simplex(estimate)))
checks=[]
for assisted in [False,True]:
    ppa,ppb=(pa,pb) if assisted else (None,None)
    for paired in [False,True]:
        bb=ia if paired else ib
        got=jackknife_change(ya,yb,ppa,ppb,ia,bb,k,paired)
        expected=[]
        for sa,sb in zip(ia,bb):
            n=len(sa);full=h(yb,ppb,sb)-h(ya,ppa,sa)
            la=np.array([h(ya,ppa,np.delete(sa,i)) for i in range(n)])
            lb=np.array([h(yb,ppb,np.delete(sb,i)) for i in range(n)])
            delta=lb-la;point=full+(1-n/N)*(n-1)*(full-delta.mean())
            variance=(n-1)*(np.var(delta) if paired else np.var(la)+np.var(lb))*(1-n/N)
            expected.append([point,np.sqrt(variance)])
        expected=np.asarray(expected);error=float(np.abs(np.column_stack([got['fpc_estimate'],got['se']])-expected).max())
        assert error<1e-12;checks.append(dict(assisted=assisted,paired=paired,maximum_explicit_difference=error))
    whole=np.arange(N)[None,:]
    got=jackknife_change(ya,yb,ppa,ppb,whole,whole,k,True)
    truth=float(entropy(np.bincount(yb,minlength=k)/N)-entropy(np.bincount(ya,minlength=k)/N))
    assert np.allclose(got['fpc_estimate'],truth,atol=1e-12) and np.all(got['se']==0)
    if not assisted:assert np.abs(got['ordinary_estimate']-truth).max()>1e-6,'Fixture must detect an omitted finite-population bias correction'
constant=np.tile([.2,.3,.5],(N,1))
a=jackknife_change(ya,yb,None,None,ia,ia,k,True)
b=jackknife_change(ya,yb,constant,constant,ia,ia,k,True)
assert np.allclose(a['fpc_estimate'],b['fpc_estimate'],atol=1e-12) and np.allclose(a['se'],b['se'],atol=1e-12)
np.savez_compressed(out/'fixture.npz',ya=ya,yb=yb,pa=pa,pb=pb,ia=ia,ib=ib)
result=dict(completed_at_utc=now(),status='passed',checks=checks,census_recovery=True,constant_predictor_equivalence=True,
            scope='Software/mathematical self-check, not independent reproduction or an empirical crop result')
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
