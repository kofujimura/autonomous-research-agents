"""Finite-population generalized-difference estimation and entropy linearization."""
import numpy as np

GRADIENT_EPS=1e-6
NUMERICAL_TOL=1e-10

def entropy(p):
    p=np.asarray(p,dtype=np.float64)
    return -(p*np.log(np.maximum(p,np.finfo(np.float64).tiny))).sum(axis=-1)

def simplex(v):
    v=np.asarray(v,dtype=np.float64);shape=v.shape;v=np.atleast_2d(v)
    assert np.isfinite(v).all()
    u=np.sort(v,axis=1)[:,::-1];cssv=np.cumsum(u,axis=1)-1
    count=np.arange(1,v.shape[1]+1)
    rho=(u-cssv/count>0).sum(axis=1)-1
    theta=cssv[np.arange(len(v)),rho]/(rho+1)
    w=np.maximum(v-theta[:,None],0)
    w[w<1e-12]=0;w/=w.sum(axis=1,keepdims=True)
    return w.reshape(shape)

def proportions(labels,predictions,indices,k):
    """One estimator per row of indices; direct estimator has predictions=None."""
    r,n=indices.shape;counts=np.zeros((r,k),np.float64)
    sample=labels[indices]
    np.add.at(counts,(np.repeat(np.arange(r),n),sample.ravel()),1/n)
    raw=counts
    if predictions is not None:
        raw=counts+predictions.mean(axis=0,dtype=np.float64)-predictions[indices].mean(axis=1,dtype=np.float64)
    phat=simplex(raw)
    projected=((raw< -NUMERICAL_TOL)|(raw>1+NUMERICAL_TOL)).any(axis=1)
    return phat,raw,projected,np.abs(phat-raw).sum(axis=1)

def sample_influence(labels,predictions,indices,phat,gradient_eps=GRADIENT_EPS):
    gradient=-(np.log(np.maximum(phat,gradient_eps))+1)
    yy=labels[indices]
    values=np.take_along_axis(gradient,yy,axis=1)
    if predictions is not None:
        values-=np.einsum('rk,rnk->rn',gradient,predictions[indices],optimize=True)
    return values

def estimate_change(ya,yb,pa,pb,ia,ib,k,paired,gradient_eps=GRADIENT_EPS):
    assert len(ya)==len(yb)
    n=ia.shape[1];N=len(ya)
    qa,rawa,proja,l1a=proportions(ya,pa,ia,k)
    qb,rawb,projb,l1b=proportions(yb,pb,ib,k)
    delta=entropy(qb)-entropy(qa)
    va=sample_influence(ya,pa,ia,qa,gradient_eps);vb=sample_influence(yb,pb,ib,qb,gradient_eps)
    var=np.var(vb-va,axis=1,ddof=1) if paired else np.var(va,axis=1,ddof=1)+np.var(vb,axis=1,ddof=1)
    se=np.sqrt(np.maximum(var*(1-n/N)/n,0))
    low=delta-1.96*se;high=delta+1.96*se
    direction=np.where(low>NUMERICAL_TOL,1,np.where(high< -NUMERICAL_TOL,-1,0)).astype(np.int8)
    return dict(estimate=delta,se=se,low=low,high=high,direction=direction,
                projected_a=proja,projected_b=projb,projection_l1_a=l1a,projection_l1_b=l1b)

def population_influence(labels,predictions,k):
    p=np.bincount(labels,minlength=k)/len(labels)
    gradient=-(np.log(np.maximum(p,GRADIENT_EPS))+1)
    phi=gradient[labels].astype(np.float64)
    if predictions is not None:phi-=predictions@gradient
    return p,phi

def influence_diagnostic(ya,yb,pa,pb,k,n):
    qa,a=population_influence(ya,pa,k);qb,b=population_influence(yb,pb,k)
    av=float(np.var(a,ddof=1));bv=float(np.var(b,ddof=1));cov=float(np.cov(a,b,ddof=1)[0,1])
    paired=float(np.var(b-a,ddof=1));independent=av+bv;fpc=(1-n/len(ya))/n
    assert np.isclose(paired,independent-2*cov,atol=1e-10)
    return dict(variance_a=av,variance_b=bv,covariance=cov,
                paired_variance=paired*fpc,independent_variance=independent*fpc,
                paired_independent_ratio=paired/independent if independent>1e-14 else None,
                mdc80_paired=(1.96+.8416212336)*np.sqrt(paired*fpc),
                mdc80_independent=(1.96+.8416212336)*np.sqrt(independent*fpc))
