"""Classical finite-event probability LPs, not a new bounding method."""
from functools import lru_cache
import itertools
import warnings

import numpy as np
from scipy.optimize import linprog, milp, LinearConstraint, Bounds, OptimizeWarning

TOL=1e-7
LP_OPTIONS={'primal_feasibility_tolerance':1e-8,'dual_feasibility_tolerance':1e-8,
            'time_limit':15.0,'threads':1}

@lru_cache(maxsize=13)
def binary_states(n):
    return ((np.arange(1<<n,dtype=np.uint16)[:,None]>>np.arange(n,dtype=np.uint16))&1).astype(np.float64)

def marginal_upper(p,k):
    p=np.sort(np.asarray(p,dtype=np.float64));n=len(p)
    if k<=0:return 1.0
    if k>n:return 0.0
    prefix=np.cumsum(p)
    return float(min(1.0,min(prefix[n-t-1]/(k-t) for t in range(k))))

def marginal_interval(p,k):
    p=np.asarray(p,dtype=np.float64)
    if k<=0:return (1.0,1.0)
    if k>len(p):return (0.0,0.0)
    return (max(0.0,1-marginal_upper(1-p,len(p)-k+1)),marginal_upper(p,k))

def matrices(X,mode,epsilon=0.0):
    X=np.asarray(X,dtype=np.float64)
    if X.ndim!=2 or not np.isin(X,[0,1]).all():raise ValueError('Expected binary members by sites')
    M,n=X.shape;totals=X.sum(axis=0)
    if epsilon:
        active=np.ones(n,dtype=bool);fixed_ones=0
    else:
        active=(totals>0)&(totals<M);fixed_ones=int((totals==M).sum())
    Z=X[:,active];m=Z.shape[1];states=binary_states(m);p=Z.mean(axis=0)
    pairs=list(itertools.combinations(range(m),2))
    pair_values=np.array([(Z[:,i]*Z[:,j]).mean() for i,j in pairs])
    allowed=np.ones(len(states),dtype=bool)
    if mode=='pair' and not epsilon:
        counts=Z.sum(axis=0).astype(int)
        for i,j in pairs:
            both=int((Z[:,i]*Z[:,j]).sum())
            cells={(1,1):both,(1,0):counts[i]-both,(0,1):counts[j]-both,
                   (0,0):M-counts[i]-counts[j]+both}
            for (vi,vj),count in cells.items():
                if count==0:allowed&=~((states[:,i]==vi)&(states[:,j]==vj))
        states=states[allowed]
    state_sum=states.sum(axis=1)
    features=[np.ones(len(states))];rhs=[1.0]
    features.extend(states.T);rhs.extend(p)
    if mode=='aggregate':
        features.append(state_sum*(state_sum-1)/2)
        sums=Z.sum(axis=1);rhs.append(float(np.mean(sums*(sums-1)/2)))
    elif mode=='pair':
        features.extend(states[:,i]*states[:,j] for i,j in pairs);rhs.extend(pair_values)
    elif mode!='marginal':raise ValueError(mode)
    A=np.array(features,dtype=np.float64);b=np.array(rhs,dtype=np.float64)
    return {'A':A,'b':b,'state_sums':state_sum+fixed_ones,'states':states,
            'active':active,'fixed_ones':fixed_ones,'uncertain_sites':m,
            'possible_states':len(states),'unpruned_states':1<<m,'members':M,'epsilon':epsilon}

def integer_limits(problem):
    A=problem['A'];b=problem['b'];M=problem['members'];epsilon=problem['epsilon']
    if not epsilon:
        rhs=np.rint(b*M);assert np.max(np.abs(rhs-b*M))<1e-7
        return rhs,rhs
    allowance=np.asarray(problem.get('moment_allowance',epsilon),dtype=float)
    ceiling=np.max(A[1:],axis=1)
    lower=np.maximum(0,b[1:]-allowance);upper=np.minimum(ceiling,b[1:]+allowance)
    lo=np.r_[M,np.ceil(M*lower-1e-7)];hi=np.r_[M,np.floor(M*upper+1e-7)]
    assert np.all(lo<=hi)
    return lo,hi

def solve_objective(problem,k,sign=1,integer=False,save_witness=False):
    A=problem['A'];b=problem['b'];event=(problem['state_sums']>=k).astype(float);c=sign*event
    if np.all(event==event[0]):
        return {'value':float(event[0]),'status':0,'constant_objective':True,
                'primal_residual':0.0,'negative_mass':0.0,'dual_violation':0.0,'duality_gap':0.0}
    if integer:
        M=problem['members'];lower_counts,upper_counts=integer_limits(problem)
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore',message='Unrecognized options detected.*')
            r=milp(c,integrality=np.ones(len(c)),bounds=Bounds(0,np.inf),
                   constraints=LinearConstraint(A,lower_counts,upper_counts),
                   options={'time_limit':5.0,'mip_rel_gap':0.0,'threads':1})
        result={'value':None if r.fun is None else float(sign*r.fun/M),'status':int(r.status),
                'message':r.message,'optimal':bool(r.success),
                'objective_dual_bound':None if r.mip_dual_bound is None else float(sign*r.mip_dual_bound/M),
                'mip_gap':None if r.mip_gap is None else float(r.mip_gap)}
        if problem['epsilon']:
            result['constraint_lower_counts']=lower_counts.astype(int).tolist()
            result['constraint_upper_counts']=upper_counts.astype(int).tolist()
        if r.x is not None:
            activity=A@r.x
            result['primal_residual']=float(max(0,np.max(lower_counts-activity),np.max(activity-upper_counts)))
            result['integer_residual']=float(np.max(np.abs(r.x-np.rint(r.x))))
            counts=np.rint(r.x).astype(np.int64)
            rounded=A@counts
            assert np.all(counts>=0) and np.all(rounded>=lower_counts) and np.all(rounded<=upper_counts),'Rounded integer incumbent is not exactly feasible'
            exact_value=float(event@counts/M)
            assert abs(exact_value-result['value'])<=TOL
            result['value']=exact_value
            result['rounded_primal_residual']=float(max(0,np.max(lower_counts-rounded),np.max(rounded-upper_counts)))
            support=np.flatnonzero(counts)
            result['integer_witness']={'states':problem['states'][support].astype(int).tolist(),
                'counts':counts[support].tolist(),'active':problem['active'].tolist(),'fixed_ones':problem['fixed_ones'],'members':M}
        return result
    epsilon=problem['epsilon']
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore',category=OptimizeWarning,message='Unrecognized options detected.*')
        if epsilon:
            B=A[1:];v=b[1:]
            allowance=np.asarray(problem.get('moment_allowance',epsilon),dtype=float)
            assert np.all(allowance>=0)
            # Aggregate moments may exceed one; ordinary binary moments may not.
            ceiling=np.max(B,axis=1)
            ub=np.minimum(v+allowance,ceiling);lb=np.maximum(v-allowance,0.0)
            Aub=np.concatenate([B,-B]);bub=np.concatenate([ub,-lb])
            r=linprog(c,A_ub=Aub,b_ub=bub,A_eq=A[:1],b_eq=b[:1],bounds=(0,None),method='highs-ds',options=LP_OPTIONS)
        else:r=linprog(c,A_eq=A,b_eq=b,bounds=(0,None),method='highs-ds',options=LP_OPTIONS)
    if not r.success:raise RuntimeError(f'LP status {r.status}: {r.message}')
    if epsilon:
        y=r.eqlin.marginals;z=r.ineqlin.marginals
        reduced=c-A[:1].T@y-Aub.T@z
        dual=float(b[:1]@y+bub@z)
        primal_residual=max(float(np.max(np.abs(A[:1]@r.x-b[:1]))),float(max(0,np.max(Aub@r.x-bub))))
        dual_violation=max(float(max(0,-np.min(reduced))),float(max(0,np.max(z))))
    else:
        y=r.eqlin.marginals;reduced=c-A.T@y;dual=float(b@y)
        primal_residual=float(np.max(np.abs(A@r.x-b)))
        dual_violation=float(max(0,-np.min(reduced)))
    result={'value':float(sign*r.fun),'status':int(r.status),'constant_objective':False,
            'primal_residual':primal_residual,'negative_mass':float(max(0,-np.min(r.x))),
            'dual_violation':dual_violation,'duality_gap':float(abs(r.fun-dual)),
            'iterations':int(r.nit)}
    if max(result[x] for x in ['primal_residual','negative_mass','dual_violation','duality_gap'])>TOL:
        raise ArithmeticError(f'LP certificate failed: {result}')
    if save_witness:
        support=np.flatnonzero(r.x>1e-12)
        result['witness']={'states':problem['states'][support].astype(int).tolist(),'probability':r.x[support].tolist(),
                           'active':problem['active'].tolist(),'fixed_ones':problem['fixed_ones'],
                           'equality_dual':y.tolist()}
        if epsilon:result['witness']['inequality_dual']=z.tolist()
    return result

def interval(problem,k,integer=False,save_witness=False):
    lo=solve_objective(problem,k,1,integer,save_witness)
    hi=solve_objective(problem,k,-1,integer,save_witness)
    if not integer:
        assert lo['value']<=hi['value']+TOL
        assert lo['value']>=-TOL and hi['value']<=1+TOL
    return {'lower':lo,'upper':hi}

def independent_tail(p,k):
    pmf=np.array([1.0])
    for probability in p:pmf=np.convolve(pmf,[1-probability,probability])
    return float(pmf[k:].sum())

def evaluate(X,capacities,validate_marginal=False):
    X=np.asarray(X,dtype=np.float64);p=X.mean(axis=0)
    problems={mode:matrices(X,mode) for mode in ['aggregate','pair']}
    if validate_marginal:problems['marginal']=matrices(X,'marginal')
    result=[]
    for k in capacities:
        q=float(np.mean(X.sum(axis=1)>=k));lo,hi=marginal_interval(p,k)
        row={'k':k,'q':q,'marginal_lower':lo,'marginal_upper':hi,'independent_q':independent_tail(p,k),
             'uncertain_sites':int(((p>0)&(p<1)).sum()),'observed_patterns':int(len(np.unique(X,axis=0))),
             'pair_possible_states':problems['pair']['possible_states'],'unpruned_states':problems['pair']['unpruned_states']}
        diagnostics=[]
        if hi-lo<=1e-12:
            for mode in ['aggregate','pair']:
                row[mode+'_lower']=lo;row[mode+'_upper']=hi
        else:
            for mode in ['aggregate','pair']:
                bounds=interval(problems[mode],k)
                row[mode+'_lower']=bounds['lower']['value'];row[mode+'_upper']=bounds['upper']['value']
                diagnostics.extend(bounds.values())
        if validate_marginal:
            bounds=interval(problems['marginal'],k)
            assert abs(lo-bounds['lower']['value'])<TOL and abs(hi-bounds['upper']['value'])<TOL
            diagnostics.extend(bounds.values())
        for mode in ['marginal','aggregate','pair']:
            assert row[mode+'_lower']<=q+TOL and row[mode+'_upper']>=q-TOL, (mode,row)
        assert row['aggregate_lower']>=lo-TOL and row['aggregate_upper']<=hi+TOL
        assert row['pair_lower']>=row['aggregate_lower']-TOL and row['pair_upper']<=row['aggregate_upper']+TOL
        row['max_primal_residual']=max([d['primal_residual'] for d in diagnostics],default=0.0)
        row['max_dual_violation']=max([d['dual_violation'] for d in diagnostics],default=0.0)
        row['max_duality_gap']=max([d['duality_gap'] for d in diagnostics],default=0.0)
        row['lp_count']=sum(not d['constant_objective'] for d in diagnostics)
        result.append(row)
    return result
