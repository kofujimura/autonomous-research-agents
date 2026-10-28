"""Exact enumeration validates the estimator code, not a research hypothesis."""
import itertools,json
import numpy as np
from records import ROOT,now
from inference_core import proportions,estimate_change,population_influence,influence_diagnostic

ya=np.array([0,0,0,1,1,2]);yb=np.array([2,1,1,0,0,0]);N=len(ya);k=3;n=2
pa=.8*np.eye(k)[ya]+.2/k;pb=.6*np.eye(k)[yb]+.4/k
samples=np.array(list(itertools.combinations(range(N),n)))
qa,raw,_,_=proportions(ya,pa,samples,k)
truth=np.bincount(ya,minlength=k)/N
unbiased_error=float(np.max(np.abs(raw.mean(axis=0)-truth)));assert unbiased_error<1e-14
_,fa=population_influence(ya,pa,k);_,fb=population_influence(yb,pb,k)
paired=fb[samples].mean(axis=1)-fa[samples].mean(axis=1)
independent=np.array([fb[b].mean()-fa[a].mean() for a in samples for b in samples])
diag=influence_diagnostic(ya,yb,pa,pb,k,n)
paired_error=abs(np.var(paired)-diag['paired_variance'])
independent_error=abs(np.var(independent)-diag['independent_variance'])
assert paired_error<1e-14 and independent_error<1e-14
census=np.arange(N)[None,:]
full=estimate_change(ya,yb,pa,pb,census,census,k,True)
assert abs(full['estimate'][0])<1e-12 and full['se'][0]==0 and full['direction'][0]==0
constant=np.tile([.5,.3,.2],(N,1))
direct=proportions(ya,None,samples,k)[0];assisted=proportions(ya,constant,samples,k)[0]
assert np.allclose(direct,assisted,atol=1e-14)
out=dict(observed_at_utc=now(),provenance='Constructed six-point synthetic validation fixture; not empirical crop evidence',
         labels_a=ya.tolist(),labels_b=yb.tolist(),predictions_a=pa.tolist(),predictions_b=pb.tolist(),
         sample_size=n,number_paired_samples=len(samples),number_independent_pairs=len(independent),
         maximum_mean_proportion_error=unbiased_error,paired_variance_error=paired_error,
         independent_variance_error=independent_error,census_exact=True,constant_prediction_equals_direct=True,
         diagnostic=diag,status='passed')
path=ROOT/'experiments/E05-inference-validation/result.json';path.parent.mkdir(parents=True,exist_ok=True)
if path.exists():raise FileExistsError('Keep previous validation result')
path.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
