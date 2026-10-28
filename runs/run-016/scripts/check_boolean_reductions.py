"""Resolve an observed case-summary discrepancy against Python counting."""
import json
import numpy as np
from records import ROOT,now
from summarize_inference import probability_summary

source=ROOT/'results/reference-frames';out=ROOT/'results/validation-boolean-reductions'
if out.exists():raise FileExistsError('Keep validation record')
out.mkdir(parents=True)
uu=[u for u in map(json.loads,(source/'units.jsonl').read_text().splitlines()) if u['frame']=='full_reference' and u['taxonomy']=='broad']
checks=[];details=[]
for subset in ['all','nonzero_change']:
    selected=uu if subset=='all' else [u for u in uu if not u['zero_change']]
    arrays=[]
    for u in selected:
        with np.load(source/u['raw_path']) as z:arrays.append(z['paired_128_wrong'])
    stack=np.stack(arrays)
    before=stack.copy()
    python=np.array([sum(bool(v) for v in row)/len(row) for row in arrays])
    axis_bool=stack.mean(axis=1);axis_float=stack.astype(np.float64).mean(axis=1)
    axis_int=stack.sum(axis=1,dtype=np.int64)/stack.shape[1]
    probability_summary(stack)
    assert np.array_equal(stack,before),'Summary function mutated input'
    checks.append(dict(subset=subset,shape=list(stack.shape),dtype=str(stack.dtype),
                       python_max=float(python.max()),bool_mean_max=float(axis_bool.max()),float_mean_max=float(axis_float.max()),int_sum_max=float(axis_int.max()),
                       bool_mean_max_difference_from_python=float(np.abs(axis_bool-python).max()),
                       float_mean_max_difference_from_python=float(np.abs(axis_float-python).max()),
                       int_sum_max_difference_from_python=float(np.abs(axis_int-python).max()),
                       storage_byte_values=np.unique(stack.view(np.uint8)).tolist()))
    for i,u in enumerate(selected):
        details.append(dict(subset=subset,unit_id=u['unit_id'],python=float(python[i]),bool_mean=float(axis_bool[i]),float_mean=float(axis_float[i]),int_sum=float(axis_int[i])))
    np.savez_compressed(out/f'{subset}.npz',stack=stack,python=python,bool_mean=axis_bool,float_mean=axis_float,int_sum=axis_int)
result=dict(completed_at_utc=now(),numpy_version=np.__version__,checks=checks,details=details)
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['completed_at_utc','numpy_version','checks']}))
