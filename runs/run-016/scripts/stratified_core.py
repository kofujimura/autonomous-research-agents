"""Established weighted difference estimation for known sampling strata."""
import numpy as np
from inference_core import entropy,simplex,sample_influence,NUMERICAL_TOL

def weighted_proportions(labels,predictions,samples,weights,k):
    r=len(samples[0]);raw=np.zeros((r,k),np.float64)
    for indices,w in zip(samples,weights):
        n=indices.shape[1]
        np.add.at(raw,(np.repeat(np.arange(r),n),labels[indices].ravel()),w/n)
        if predictions is not None:raw-=w*predictions[indices].mean(axis=1,dtype=np.float64)
    if predictions is not None:raw+=predictions.mean(axis=0,dtype=np.float64)
    projected=((raw< -NUMERICAL_TOL)|(raw>1+NUMERICAL_TOL)).any(axis=1)
    return simplex(raw),raw,projected

def stratified_change(ya,yb,pa,pb,sa,sb,stratum_sizes,k,paired):
    N=len(ya);weights=np.asarray(stratum_sizes,dtype=float)/N
    assert sum(stratum_sizes)==N and len(sa)==len(sb)==len(weights)
    qa,rawa,proja=weighted_proportions(ya,pa,sa,weights,k)
    qb,rawb,projb=weighted_proportions(yb,pb,sb,weights,k)
    variance=np.zeros(len(sa[0]))
    for ia,ib,Nh,w in zip(sa,sb,stratum_sizes,weights):
        n=ia.shape[1];assert n==ib.shape[1] and 2<=n<=Nh
        va=sample_influence(ya,pa,ia,qa);vb=sample_influence(yb,pb,ib,qb)
        v=np.var(vb-va,axis=1,ddof=1) if paired else np.var(va,axis=1,ddof=1)+np.var(vb,axis=1,ddof=1)
        variance+=w*w*(1-n/Nh)*v/n
    estimate=entropy(qb)-entropy(qa);se=np.sqrt(np.maximum(variance,0))
    low=estimate-1.96*se;high=estimate+1.96*se
    direction=np.where(low>NUMERICAL_TOL,1,np.where(high< -NUMERICAL_TOL,-1,0)).astype(np.int8)
    return dict(estimate=estimate,se=se,low=low,high=high,direction=direction,
                projected_a=proja,projected_b=projb,raw_a=rawa,raw_b=rawb)
