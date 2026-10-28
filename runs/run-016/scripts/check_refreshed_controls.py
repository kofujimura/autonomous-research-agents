"""Check fixed source-year controls and print completed comparison tables."""
import argparse,json
import numpy as np,pandas as pd
from records import ROOT,now,digest

def run(destination):
    out=ROOT/destination
    if out.exists():raise FileExistsError('Preserve previous control checks')
    out.mkdir(parents=True);checks=[];rows=[]
    for rep in ['tessera','alphaearth']:
        old=ROOT/f'results/source-models-v2/logistic-broad-{rep}'
        new=ROOT/f'results/models/logistic-broad-refreshed-{rep}'
        a=old/'coefficients-2021.npz';b=new/'coefficients-2021.npz';maximum=0.;identical=True
        with np.load(a) as x,np.load(b) as y:
            assert set(x.files)==set(y.files)
            for key in x.files:
                assert x[key].shape==y[key].shape
                identical=identical and np.array_equal(x[key],y[key])
                maximum=max(maximum,float(np.abs(x[key]-y[key]).max(initial=0)))
                assert np.allclose(x[key],y[key],atol=2e-6,rtol=2e-6)
        oldcal=old/'source-calibration.npz';newcal=new/'source-calibration.npz'
        with np.load(oldcal) as x,np.load(newcal) as y:
            assert set(x.files)==set(y.files)
            for key in x.files:assert np.allclose(x[key],y[key],atol=2e-6,rtol=2e-6)
        checks.append(dict(representation=rep,source_year_coefficient_arrays_identical=identical,
            maximum_coefficient_difference=maximum,source_path=str(a.relative_to(ROOT)),source_sha256=digest(a),
            refreshed_path=str(b.relative_to(ROOT)),refreshed_sha256=digest(b),calibration_equal_within_2e_minus6=True))
        for name in [f'logistic-broad-refreshed-{rep}',f'forest-broad-{rep}']:
            frame=pd.read_csv(ROOT/f'results/tables/{name}/audit-performance.csv')
            rows+=frame[(frame.subset=='all')&(frame.n==128)&(frame.method=='model_assisted')].to_dict('records')
    pd.DataFrame(rows).to_csv(out/'comparison.csv',index=False)
    result=dict(completed_at_utc=now(),status='passed',checks=checks,
        scope='Source-year numerical control validation after refreshed execution, not a newly selected scientific metric or independent reproduction.')
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result));print(pd.DataFrame(rows)[['label','design','rmse','coverage','report_rate','wrong_report_rate']].to_string(index=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--destination',required=True);a=p.parse_args();run(a.destination)
