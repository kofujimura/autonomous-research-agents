"""Finite-population partial-overlap variance and entropy linearization."""
import numpy as np
from inference_core import proportions,sample_influence,entropy

def partial_variance(va,vb,positions_a,positions_b,N):
    n=va.shape[1];m=positions_a.shape[1]
    assert m>=2 and positions_a.shape==positions_b.shape
    a=np.take_along_axis(va,positions_a,axis=1);b=np.take_along_axis(vb,positions_b,axis=1)
    covariance=((a-a.mean(axis=1,keepdims=True))*(b-b.mean(axis=1,keepdims=True))).sum(axis=1)/(m-1)
    return (1/n-1/N)*(va.var(axis=1,ddof=1)+vb.var(axis=1,ddof=1))-2*(m/n**2-1/N)*covariance

def change(ya,yb,pa,pb,ia,ib,k,positions_a,positions_b):
    qa,_,proja,_=proportions(ya,pa,ia,k);qb,_,projb,_=proportions(yb,pb,ib,k)
    va=sample_influence(ya,pa,ia,qa);vb=sample_influence(yb,pb,ib,qb)
    variance=partial_variance(va,vb,positions_a,positions_b,len(ya))
    return dict(estimate=entropy(qb)-entropy(qa),se=np.sqrt(np.maximum(variance,0)),
                negative_variance=variance< -1e-14,projected_a=proja,projected_b=projb)
