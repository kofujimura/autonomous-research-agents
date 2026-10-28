"""Exhaustively check the established partial-overlap variance identity."""
import itertools,json,numpy as np
from records import ROOT,now
from rotating_core import partial_variance

N=7;n=4;m=2
u=np.array([0.,1.,2.,4.,6.,7.,9.]);v=np.array([1.,0.,3.,2.,5.,10.,8.])
aa=[];bb=[];oa=[];ob=[]
for a in itertools.combinations(range(N),n):
    rest=sorted(set(range(N))-set(a))
    for common in itertools.combinations(a,m):
        for fresh in itertools.combinations(rest,n-m):
            b=tuple(common)+tuple(fresh);aa.append(a);bb.append(b)
            oa.append([a.index(i) for i in common]);ob.append([b.index(i) for i in common])
aa=np.asarray(aa);bb=np.asarray(bb);oa=np.asarray(oa);ob=np.asarray(ob)
d=v[bb].mean(axis=1)-u[aa].mean(axis=1)
theory=(1/n-1/N)*(u.var(ddof=1)+v.var(ddof=1))-2*(m/n**2-1/N)*np.cov(u,v,ddof=1)[0,1]
estimated=partial_variance(u[aa],v[bb],oa,ob,N)
assert abs(d.mean()-(v.mean()-u.mean()))<1e-12
assert abs(d.var()-theory)<1e-12
assert abs(estimated.mean()-theory)<1e-12
full=np.broadcast_to(np.arange(n),(len(aa),n))
assert np.allclose(partial_variance(u[aa],v[aa],full,full,N),(1/n-1/N)*np.var(v[aa]-u[aa],axis=1,ddof=1))
out=ROOT/'results/validation-rotating';out.mkdir()
np.savez_compressed(out/'fixture.npz',u=u,v=v,a=aa,b=bb,overlap_a=oa,overlap_b=ob,estimates=d,variance_estimates=estimated)
result=dict(completed_at_utc=now(),status='passed',enumerated_pairs=len(aa),theoretical_variance=float(theory),
    exact_variance=float(d.var()),mean_estimated_variance=float(estimated.mean()),
    qualification='Exact linear fixed-value design validation, not entropy confidence-interval validation')
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
