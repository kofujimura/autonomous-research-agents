"""Bounded scalar control variates; conditional design-unbiased crossfit means."""
import numpy as np
from inference_core import entropy,simplex,NUMERICAL_TOL,GRADIENT_EPS

def label_mean(y,indices,k):
    r,n=indices.shape;result=np.zeros((r,k),np.float64)
    np.add.at(result,(np.repeat(np.arange(r),n),y[indices].ravel()),1/n)
    return result

def tune(ya,yb,pa,pb,ia,ib,k,paired):
    ga=-(np.log(np.maximum(label_mean(ya,ia,k),GRADIENT_EPS))+1)
    gb=-(np.log(np.maximum(label_mean(yb,ib,k),GRADIENT_EPS))+1)
    wa=np.take_along_axis(ga,ya[ia],axis=1);wb=np.take_along_axis(gb,yb[ib],axis=1)
    va=np.einsum('rk,rnk->rn',ga,pa[ia],optimize=True);vb=np.einsum('rk,rnk->rn',gb,pb[ib],optimize=True)
    def cov(a,b):return np.mean((a-a.mean(axis=1,keepdims=True))*(b-b.mean(axis=1,keepdims=True)),axis=1)
    if paired:
        w=wb-wa;v=vb-va;numerator=cov(w,v);denominator=cov(v,v)
    else:numerator=cov(wa,va)+cov(wb,vb);denominator=cov(va,va)+cov(vb,vb)
    return np.clip(np.divide(numerator,denominator,out=np.zeros_like(numerator),where=denominator>1e-14),0,1)

def evaluate(ya,yb,pa,pb,ia,ib,k,paired,mode,fixed_lambda=None):
    n=ia.shape[1];N=len(ya);r=len(ia);assert n%2==0 and n>=4 and len(yb)==N
    qa=pa.mean(axis=0,dtype=np.float64);qb=pb.mean(axis=0,dtype=np.float64)
    if mode=='same_sample':
        lam=tune(ya,yb,pa,pb,ia,ib,k,paired) if fixed_lambda is None else np.full(r,fixed_lambda)
        rawa=label_mean(ya,ia,k)+lam[:,None]*(qa-pa[ia].mean(axis=1,dtype=np.float64))
        rawb=label_mean(yb,ib,k)+lam[:,None]*(qb-pb[ib].mean(axis=1,dtype=np.float64))
        coefficient=np.broadcast_to(lam[:,None],ia.shape);la=lb=lam
    elif mode=='crossfit':
        m=n//2;fraction=m/N;aa,ab=ia[:,:m],ia[:,m:];ba,bb=ib[:,:m],ib[:,m:]
        la=tune(ya,yb,pa,pb,aa,ba,k,paired) if fixed_lambda is None else np.full(r,fixed_lambda)
        lb=tune(ya,yb,pa,pb,ab,bb,k,paired) if fixed_lambda is None else np.full(r,fixed_lambda)
        def raw(y,p,a,b,q):
            yaa=label_mean(y,a,k);ybb=label_mean(y,b,k)
            paa=p[a].mean(axis=1,dtype=np.float64);pbb=p[b].mean(axis=1,dtype=np.float64)
            q_without_a=(N*q-m*paa)/(N-m);q_without_b=(N*q-m*pbb)/(N-m)
            first=fraction*yaa+(1-fraction)*(ybb+la[:,None]*(q_without_a-pbb))
            second=fraction*ybb+(1-fraction)*(yaa+lb[:,None]*(q_without_b-paa))
            return (first+second)/2
        rawa=raw(ya,pa,aa,ab,qa);rawb=raw(yb,pb,ba,bb,qb)
        ca=fraction*la+(1-fraction)*lb;cb=fraction*lb+(1-fraction)*la
        coefficient=np.concatenate([np.repeat(ca[:,None],m,axis=1),np.repeat(cb[:,None],m,axis=1)],axis=1)
    else:raise ValueError(mode)
    phata=simplex(rawa);phatb=simplex(rawb)
    ga=-(np.log(np.maximum(phata,GRADIENT_EPS))+1);gb=-(np.log(np.maximum(phatb,GRADIENT_EPS))+1)
    va=np.take_along_axis(ga,ya[ia],axis=1)-coefficient*np.einsum('rk,rnk->rn',ga,pa[ia],optimize=True)
    vb=np.take_along_axis(gb,yb[ib],axis=1)-coefficient*np.einsum('rk,rnk->rn',gb,pb[ib],optimize=True)
    variance=np.var(vb-va,axis=1,ddof=1) if paired else np.var(va,axis=1,ddof=1)+np.var(vb,axis=1,ddof=1)
    se=np.sqrt(np.maximum(variance*(1-n/N)/n,0));estimate=entropy(phatb)-entropy(phata)
    low=estimate-1.96*se;high=estimate+1.96*se
    return dict(estimate=estimate,se=se,low=low,high=high,
                direction=np.where(low>NUMERICAL_TOL,1,np.where(high< -NUMERICAL_TOL,-1,0)).astype(np.int8),
                lambda_a=la,lambda_b=lb,raw_a=rawa,raw_b=rawb,
                projected_a=((rawa< -NUMERICAL_TOL)|(rawa>1+NUMERICAL_TOL)).any(axis=1),
                projected_b=((rawb< -NUMERICAL_TOL)|(rawb>1+NUMERICAL_TOL)).any(axis=1))
