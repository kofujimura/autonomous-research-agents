"""Delete-one entropy change checks, including finite-population bias scaling."""
import numpy as np
from inference_core import entropy,simplex,proportions,NUMERICAL_TOL

def leave_one_entropy(labels,predictions,indices,k,raw):
    n=indices.shape[1]
    residual=np.eye(k,dtype=np.float64)[labels[indices]]
    q=np.zeros(k) if predictions is None else predictions.mean(axis=0,dtype=np.float64)
    if predictions is not None:residual-=predictions[indices]
    loo=q+(n*(raw-q)[:,None,:]-residual)/(n-1)
    projected=simplex(loo.reshape(-1,k)).reshape(loo.shape)
    return entropy(projected)

def jackknife_change(ya,yb,pa,pb,ia,ib,k,paired):
    n=ia.shape[1];N=len(ya);assert n>=2 and len(yb)==N
    qa,rawa,proja,_=proportions(ya,pa,ia,k);qb,rawb,projb,_=proportions(yb,pb,ib,k)
    full=entropy(qb)-entropy(qa)
    la=leave_one_entropy(ya,pa,ia,k,rawa);lb=leave_one_entropy(yb,pb,ib,k,rawb)
    delta_loo=lb-la;bias_correction=(n-1)*(full-delta_loo.mean(axis=1))
    iid=full+bias_correction;fpc=1-n/N;corrected=full+fpc*bias_correction
    if paired:variance=(n-1)*np.var(delta_loo,axis=1,ddof=0)
    else:variance=(n-1)*(np.var(la,axis=1,ddof=0)+np.var(lb,axis=1,ddof=0))
    se=np.sqrt(np.maximum(fpc*variance,0))
    result=dict(base_estimate=full,ordinary_estimate=iid,fpc_estimate=corrected,se=se,
                base_projected_a=proja,base_projected_b=projb)
    for name,value in [('ordinary',iid),('fpc',corrected)]:
        lo=value-1.96*se;hi=value+1.96*se
        result[name+'_low']=lo;result[name+'_high']=hi
        result[name+'_direction']=np.where(lo>NUMERICAL_TOL,1,np.where(hi< -NUMERICAL_TOL,-1,0)).astype(np.int8)
    return result
