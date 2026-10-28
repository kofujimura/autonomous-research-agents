"""Exploratory v3 product constraints and query objectives, using classical LPs."""
import itertools
import math
import numpy as np

from bounds import matrices

def count_problem(X):
    X=np.asarray(X,dtype=float);base=matrices(X,'marginal')
    totals=X.sum(axis=1).astype(int);support=np.unique(totals)
    keep=np.isin(base['state_sums'],support)
    result={**base,'states':base['states'][keep],
            'state_sums':base['state_sums'][keep],
            'A':base['A'][:,keep].copy(),'b':base['b'].copy(),
            'possible_states':int(keep.sum())}
    features=np.array([(result['state_sums']==s).astype(float) for s in support])
    probabilities=np.array([np.mean(totals==s) for s in support])
    result['A']=np.concatenate([result['A'],features])
    result['b']=np.concatenate([result['b'],probabilities])
    assert abs(np.dot(np.arange(X.shape[1]+1),np.bincount(totals,minlength=X.shape[1]+1)/len(X))-X.mean(0).sum())<1e-10
    return result

def subset_problem(problem,X,indices):
    X=np.asarray(X);mask=np.zeros(X.shape[1],dtype=bool);mask[indices]=True
    selected_active=mask[problem['active']]
    fixed=int(np.sum((X.sum(axis=0)==len(X))&mask))
    return {**problem,'state_sums':problem['states'][:,selected_active].sum(axis=1)+fixed}

def pack_counters(values,maximum):
    values=[int(v) for v in values];bits=math.ceil(math.log2(maximum+1));number=0
    for value in values:
        assert 0<=value<=maximum
        number=(number<<bits)|value
    total_bits=len(values)*bits;pad=(-total_bits)%8
    body=(number<<pad).to_bytes((total_bits+7)//8,'big')
    recovered=int.from_bytes(body,'big')>>pad;decoded=[]
    for _ in values:
        decoded.append(recovered&((1<<bits)-1));recovered>>=bits
    decoded.reverse();assert decoded==values and recovered==0
    return body,total_bits

def encoding_checks(X):
    X=np.asarray(X,dtype=np.uint8);M,n=X.shape
    mask=np.packbits(X.reshape(-1),bitorder='big')
    restored=np.unpackbits(mask,count=M*n,bitorder='big').reshape(M,n)
    assert np.array_equal(X,restored)
    p=X.sum(axis=0).astype(int);Z=X.astype(np.int64);pairs=[int(np.sum(Z[:,i]*Z[:,j])) for i,j in itertools.combinations(range(n),2)]
    hist=np.bincount(X.sum(axis=1).astype(int),minlength=n+1)
    marginal,marginal_bits=pack_counters(p,M)
    pair,pair_bits=pack_counters(list(p)+pairs,M)
    count,count_bits=pack_counters(list(p)+list(hist[:-1]),M)
    assert M-int(hist[:-1].sum())==hist[-1]
    return {'members':M,'universe_sites':n,'bits_per_counter':math.ceil(math.log2(M+1)),
            'marginal_bits':marginal_bits,'marginal_bytes':len(marginal),
            'pair_bits':pair_bits,'pair_bytes':len(pair),'pair_scalar_entries':len(p)+len(pairs),
            'count_bits':count_bits,'count_bytes':len(count),'count_scalar_entries':len(p)+len(hist)-1,
            'coherent_mask_bits':M*n,'coherent_mask_bytes':len(mask),
            'round_trip_errors':0,'scope':'Analytic fixed-width payload budgets, excluding headers/metadata/general compression; no optimal coding or measured traffic claim'}
