"""Validate a local derivative; explicitly retain its boundary limitation."""
import argparse,itertools,json
import numpy as np,pandas as pd
from records import ROOT,now
from inference_core import simplex,entropy
from projection_derivative import local_gradient,face_estimate

def run(destination):
    out=ROOT/destination
    if out.exists():raise FileExistsError('Preserve local derivative validation')
    out.mkdir(parents=True);rng=np.random.default_rng(16016);rows=[];rejected=[]
    for k in [3,7,17,54]:
        accepted=0;attempts=0
        while accepted<32:
            attempts+=1;assert attempts<10000
            v=rng.normal(0,.3,k);q=simplex(v);active=q>0;theta=(v[active].sum()-1)/active.sum()
            distance=float(np.abs(v-theta).min());minimum=float(q[active].min())
            if distance<1e-4 or minimum<1e-4:
                rejected.append(dict(k=k,attempt=attempts,v=v.tolist(),distance=distance,minimum_positive=minimum));continue
            gradient=local_gradient(q[None])[0];step=1e-7;fd=[]
            for j in range(k):
                d=np.zeros(k);d[j]=step
                assert np.array_equal(simplex(v+d)>0,active) and np.array_equal(simplex(v-d)>0,active)
                fd.append(float((entropy(simplex(v+d))-entropy(simplex(v-d)))/(2*step)))
            difference=float(np.max(np.abs(gradient-np.array(fd))))
            assert difference<1e-5 and abs(gradient.sum())<1e-12
            rows.append(dict(k=k,case=accepted,positive_support=int(active.sum()),maximum_gradient_difference=difference,
                minimum_threshold_distance=distance,minimum_positive=minimum))
            accepted+=1
    v=np.array([.6,.4,0.]);d=np.array([-.5,-.5,1.]);boundary=[]
    for step in [1e-3,1e-5,1e-7]:
        right=float((entropy(simplex(v+step*d))-entropy(simplex(v)))/step)
        left=float((entropy(simplex(v))-entropy(simplex(v-step*d)))/step)
        boundary.append(dict(step=step,right_difference=right,left_difference=left,local_face_gradient_dot_direction=float(local_gradient(v[None])[0]@d)))
        assert abs(left)<1e-7
    assert all(b['right_difference']>a['right_difference'] for a,b in zip(boundary,boundary[1:]))
    assert np.array_equal(local_gradient(np.array([[1.,0.,0.]])),np.zeros((1,3)))
    ya=np.array([0,1,0,2,1,0,2]);yb=np.array([1,0,0,2,2,0,1]);indices=np.array(list(itertools.combinations(range(7),3)))
    constant=np.tile([.4,.2,.4],(7,1))
    for paired in [False,True]:
        ib=indices if paired else np.roll(indices,5,axis=0)
        direct=face_estimate(ya,yb,None,None,indices,ib,3,paired)
        assisted=face_estimate(ya,yb,constant,constant,indices,ib,3,paired)
        assert np.allclose(direct['estimate'],assisted['estimate'],atol=1e-12,rtol=1e-12)
        assert np.allclose(direct['se'],assisted['se'],atol=1e-12,rtol=1e-12)
        census=np.arange(7)[None]
        result=face_estimate(ya,yb,constant,constant,census,census,3,paired)
        assert (result['se']==0).all()
    pd.DataFrame(rows).to_csv(out/'finite-differences.csv',index=False)
    pd.DataFrame(boundary).to_csv(out/'boundary-fixture.csv',index=False)
    result=dict(completed_at_utc=now(),status='passed',seed=16016,cases=len(rows),dimensions=[3,7,17,54],
        rejected_fixtures=rejected,singleton_tested_cases=sum(r['positive_support']==1 for r in rows),
        maximum_gradient_difference=max(r['maximum_gradient_difference'] for r in rows),
        checks='Local finite differences, zero-sum gradient, singleton face, census and constant-predictor equivalence passed.',
        scope='Boundary fixture shows entropy composition lacks a finite derivative when an absent category enters. This validation does not establish statistical calibration.')
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--destination',required=True);a=p.parse_args();run(a.destination)
