"""Exploratory exact change-count bounds; no claim of a new theorem."""
from functools import lru_cache
import numpy as np
from scipy.stats import hypergeom

@lru_cache(maxsize=None)
def changed_count_upper(N,n,observed,alpha=.05):
    """Largest population changed count not rejected by lower-tail inversion."""
    N,n,x=int(N),int(n),int(observed)
    assert 0<=x<=n<=N and 0<alpha<1
    if x==n:return N
    lo=x;hi=N-n+x+1
    while hi-lo>1:
        mid=(hi+lo)//2
        if hypergeom.cdf(x,N,mid,n)>=alpha-1e-14:lo=mid
        else:hi=mid
    return lo

def entropy_envelope(upper_fraction,k):
    x=np.asarray(upper_fraction,dtype=float)
    assert k>=2 and ((x>=0)&(x<=1)).all()
    t=np.minimum(x,1-1/k)
    h=-t*np.log(np.maximum(t,np.finfo(float).tiny))-(1-t)*np.log1p(-t)
    return t*np.log(k-1)+h

def no_change_probability(N,changed,n):
    return float(hypergeom.pmf(0,N,changed,n))
