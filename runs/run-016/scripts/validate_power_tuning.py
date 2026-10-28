"""Exact finite-population checks for crossfitted scalar correction."""
import itertools,json
import numpy as np
from records import ROOT,now
from power_tuning_core import evaluate
from inference_core import estimate_change,entropy

out=ROOT/'results/validation-power-tuning'
if out.exists():raise FileExistsError('Preserve validation')
out.mkdir(parents=True)
ya=np.array([0,0,0,1,1,2,2]);yb=np.array([0,0,1,1,2,2,2]);N=7;k=3
rng=np.random.default_rng(16088)
pa=.8*np.eye(k)[ya]+.2*rng.dirichlet([1,2,3],N)
pb=.7*np.eye(k)[yb]+.3*rng.dirichlet([3,2,1],N)
partitions=[]
for a in itertools.combinations(range(N),3):
    rest=[i for i in range(N) if i not in a]
    for b in itertools.combinations(rest,3):partitions.append(a+b)
base=np.array(partitions);checks=[]
for paired in [True,False]:
    ia=base if paired else np.repeat(base,len(base),axis=0)
    ib=base if paired else np.tile(base,(len(base),1))
    result=evaluate(ya,yb,pa,pb,ia,ib,k,paired,'crossfit')
    qa=np.bincount(ya,minlength=k)/N;qb=np.bincount(yb,minlength=k)/N
    error=max(float(np.abs(result['raw_a'].mean(axis=0)-qa).max()),float(np.abs(result['raw_b'].mean(axis=0)-qb).max()))
    assert error<1e-11,(paired,error)
    assert np.ptp(result['lambda_a'])>.5,'Fixture must exercise data-dependent, nonconstant weights'
    checks.append(dict(paired=paired,enumerated_ordered_fold_samples=len(ia),unprojected_proportion_bias_max=error,
                        minimum_lambda=float(result['lambda_a'].min()),maximum_lambda=float(result['lambda_a'].max())))
simple=base[:8];other=base[-8:]
for paired in [True,False]:
    bb=simple if paired else other
    for lam in [0.,1.]:
        expected=estimate_change(ya,yb,None if lam==0 else pa,None if lam==0 else pb,simple,bb,k,paired)
        for mode in ['same_sample','crossfit']:
            got=evaluate(ya,yb,pa,pb,simple,bb,k,paired,mode,fixed_lambda=lam)
            for name in ['estimate','se']:assert np.allclose(got[name],expected[name],atol=1e-11),(paired,lam,mode,name)
whole=np.arange(6)[None,:];qa=np.bincount(ya[:6],minlength=k)/6;qb=np.bincount(yb[:6],minlength=k)/6
for paired in [True,False]:
    bb=whole if paired else whole[:,::-1]
    for mode in ['same_sample','crossfit']:
        got=evaluate(ya[:6],yb[:6],pa[:6],pb[:6],whole,bb,k,paired,mode)
        assert np.allclose(got['estimate'],entropy(qb)-entropy(qa),atol=1e-12) and np.all(got['se']==0)
constant=np.tile([.2,.3,.5],(N,1));expected=estimate_change(ya,yb,None,None,simple,simple,k,True)
for mode in ['same_sample','crossfit']:
    got=evaluate(ya,yb,constant,constant,simple,simple,k,True,mode)
    assert np.allclose(got['estimate'],expected['estimate'],atol=1e-12) and np.allclose(got['se'],expected['se'],atol=1e-12)
np.savez_compressed(out/'fixture.npz',ya=ya,yb=yb,pa=pa,pb=pb,ordered_fold_samples=base)
result=dict(completed_at_utc=now(),status='passed',checks=checks,fixed_weight_endpoint_equivalence=True,
            constant_predictor_equivalence=True,census_recovery=True,
            fixture_generation='Seven-point fixed labels; .8/.7 one-hot signal plus seeded Dirichlet noise, seed16088. Six-point prefix for census checks. Synthetic validation only.',
            scope='Exact raw-proportion design checks, not independent reproduction or a guarantee for projected entropy intervals')
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
