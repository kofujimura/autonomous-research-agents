"""Hand-computed properties of thresholds, coverage, smoothing and allocation."""
import numpy as np
from evaluate import threshold_for, coverage_counts, normalized_smooth, count_metrics
from fit_models import draw_groups,inverse_object_weights,quota_matched_positions
from summarize import primary_bootstrap
from threshold_bootstrap import core_histograms,weighted_thresholds
from alignment_stress import translate
import pandas as pd

def main():
    # Strict thresholds conservatively handle a tied upper tail.
    scores=np.array([0,0,1,1,1],dtype=float)
    t=threshold_for(scores,.4)
    assert t==1 and np.mean(scores>t)==0
    # Four pixels at 50%: two hits recover it, despite a median that averages scores.
    obj=np.array([[1,1,1,1],[2,2,2,0]])
    valid=np.ones_like(obj,dtype=bool)
    pred=np.array([[0,0,1,1],[0,0,1,0]],dtype=bool)
    total,hit=coverage_counts(obj,valid,pred)
    assert total.tolist()==[1,4,3] and hit.tolist()==[0,2,1]
    assert (2*hit[1]>=total[1]) and not (2*hit[2]>=total[2])
    assert not (4*hit[1]>=3*total[1])
    # A masked hit is excluded from both numerator and denominator.
    valid[0,3]=False;total,hit=coverage_counts(obj,valid,pred)
    assert total[1]==3 and hit[1]==1
    p=np.array([[.7,.7,np.nan],[.7,.7,np.nan],[.7,.7,np.nan]],dtype=np.float32)
    smooth=normalized_smooth(p,1)
    assert np.allclose(smooth[np.isfinite(p)],.7) and np.array_equal(np.isnan(p),np.isnan(smooth))
    # Finite object pools deplete without duplicated or invented positions.
    selected=draw_groups([np.array([11,12]),np.array([20])],5,np.random.default_rng(2))
    assert sorted(selected.tolist())==[11,12,20]
    y=np.array([[True,False],[True,False]]);valid=np.array([[1,1],[0,1]],bool)
    pred=np.array([[True,True],[False,False]])
    assert count_metrics(y,valid,pred)==dict(tp=1,fn=0,fp=1,tn=1)
    rows=[]
    for region in ['R1','R2','R3','R4']:
        for core in range(2):
            for seed in [101,202,303,404,505]:
                for representation,policy,recovered in [('aef','area',1),('aef','object',3),('optical','area',2),('optical','object',4)]:
                    rows.append(dict(scope='within',decoder='rf',budget=2000,version='raw',
                        condition='standardized_0.05',boundary_tolerance_m=0,size_bin='small',seed=seed,
                        region_id=region,core_id=region+str(core),representation=representation,
                        policy=policy,n=4,recovered=recovered))
    bootstrap=primary_bootstrap(pd.DataFrame(rows),replicates=20)
    assert bootstrap['H1_interaction']['estimate']==0
    assert bootstrap['H1_interaction']['conditional_block_bootstrap_95_percent_interval']==[0,0]
    assert bootstrap['aef_oracle_gain']['estimate']==.5
    assert bootstrap['optical_oracle_gain']['estimate']==.5
    negative=[np.array([0.,0.,.4]),np.array([.2,.2,.9,1.])]
    levels,histogram=core_histograms(negative);weights=np.array([[2,1],[0,3],[3,0],[1,1]])
    actual=weighted_thresholds(levels,histogram,weights,q=.7)
    expected=[np.quantile(np.concatenate([np.repeat(a,w) for a,w in zip(negative,row)]),.7,method='higher') for row in weights]
    assert np.array_equal(actual,expected)
    class WeightFixture:
        def object_groups(self,train):return [np.array([0,1]),np.array([2,3,4,5])]
        def labels(self,positions):return np.array([1 if x<6 else 0 for x in positions])
    positions=np.array([0,2,8,9]);w,info=inverse_object_weights(WeightFixture(),[],positions)
    assert np.allclose(w,[4/3,2/3,1,1],rtol=0,atol=1e-15)
    assert np.isclose(info['positive_effective_sample_size'],1.8)
    w,_=inverse_object_weights(WeightFixture(),[],positions,cap=1)
    assert np.allclose(w,[1.2,.8,1,1],rtol=0,atol=1e-15)
    pool=np.array([0,1,2,3,65536,65537,65538,65539])
    negatives=np.array([10,65540]);oracle=np.array([0,1,2,65537])
    chosen,quotas=quota_matched_positions(pool,oracle,negatives,{0:'A',1:'B'},17)
    assert quotas=={'A':3,'B':1} and len(np.unique(chosen))==6
    assert np.array_equal(chosen[-2:],negatives)
    assert np.sum(chosen[:-2]//65536==0)==3 and np.sum(chosen[:-2]//65536==1)==1
    a=np.arange(1,10).reshape(3,3)
    assert np.array_equal(translate(a,-1,0),[[4,5,6],[7,8,9],[0,0,0]])
    assert np.array_equal(translate(a,0,1),[[0,1,2],[0,4,5],[0,7,8]])
    assert np.array_equal(translate(a,0,0),a)
    print('PASS: tied threshold; even/odd patch coverage; common mask; normalized smoothing; unique finite object allocation; confusion counts; hand-computed factorial contrast/bootstrap; exact weighted quantiles; inverse-size weights, normalization, truncation and ESS; geographical quota matching and negative identity')

if __name__=='__main__':main()
