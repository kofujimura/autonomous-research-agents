"""Exact enumeration and SRS special case validate stratum weights/variance."""
import itertools,json
import numpy as np
from records import ROOT,now
from stratified_core import stratified_change
from inference_core import estimate_change,entropy

out=ROOT/'results/validation-stratified'
if out.exists():raise FileExistsError('Preserve validation')
out.mkdir(parents=True)
ya=np.array([0,0,1,1,2,2]);yb=np.array([0,1,1,2,2,2]);N=6;k=3
pa=np.random.default_rng(16067).dirichlet([1,2,3],N)
pb=np.random.default_rng(16068).dirichlet([3,2,1],N)
hi=np.array([0,1]);lo=np.array([2,3,4,5]);combinations=list(itertools.combinations(lo,2))
ia=[np.tile(hi,(len(combinations),1)),np.array(combinations)]
checks=[]
for assisted in [False,True]:
    ppa,ppb=(pa,pb) if assisted else (None,None)
    result=stratified_change(ya,yb,ppa,ppb,ia,ia,[2,4],k,True)
    truth_a=np.bincount(ya,minlength=k)/N;truth_b=np.bincount(yb,minlength=k)/N
    error=max(float(np.abs(result['raw_a'].mean(axis=0)-truth_a).max()),float(np.abs(result['raw_b'].mean(axis=0)-truth_b).max()))
    assert error<1e-12
    whole=[hi[None,:],lo[None,:]]
    census=stratified_change(ya,yb,ppa,ppb,whole,whole,[2,4],k,True)
    assert np.allclose(census['estimate'],entropy(truth_b)-entropy(truth_a),atol=1e-12) and np.all(census['se']==0)
    simple_a=np.array([[0,2,4],[1,3,5]]);simple_b=np.array([[1,2,5],[0,3,4]])
    for paired in [False,True]:
        bb=simple_a if paired else simple_b
        ordinary=estimate_change(ya,yb,ppa,ppb,simple_a,bb,k,paired)
        single=stratified_change(ya,yb,ppa,ppb,[simple_a],[bb],[N],k,paired)
        for name in ['estimate','se','direction']:assert np.allclose(single[name],ordinary[name],atol=1e-12)
    checks.append(dict(assisted=assisted,unprojected_proportion_unbiasedness_error=error,census_recovery=True,SRS_special_case=True))
np.savez_compressed(out/'fixture.npz',ya=ya,yb=yb,pa=pa,pb=pb,high_population=hi,low_population=lo)
result=dict(completed_at_utc=now(),status='passed',checks=checks,enumerated_combinations=len(combinations),
            scope='Exact finite-population software self-check; no assertion that nonlinear entropy is unbiased')
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
