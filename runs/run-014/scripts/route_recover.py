"""Offline recovery of v15 reporting from preserved raw transport-pilot arrays."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
from record import ROOT

def recover(output):
    output.mkdir(parents=True,exist_ok=False)
    pilot=ROOT/'experiments/route-check-v15/results'
    queries=json.loads((pilot/'queries.json').read_text());assert len(queries)==3
    rows=[];hashes={}
    for q in queries:
        assert q['status']=='error' and 'is not in the subpath' in q['error']
        a=pilot/f"{q['task_id']}.npz";b=ROOT/f"data/embeddings/tessera/{q['task_id']}.npz"
        for p in [a,b]:hashes[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
        with np.load(a,allow_pickle=False) as f:ar=f['raw'];am=json.loads(str(f['metadata']))
        with np.load(b,allow_pickle=False) as f:br=f['raw'];bm=json.loads(str(f['metadata']))
        equal=ar.dtype==br.dtype and ar.shape==br.shape and ar.tobytes()==br.tobytes()
        metadata_equal=all(am[k]==bm[k] for k in ['point_id','year','source_url','dataset','crs','transform'])
        rows.append(dict(task_id=q['task_id'],raw_bitwise_equal=equal,spatial_version_metadata_equal=metadata_equal,
            gateway_elapsed_with_reporting_overhead=q['gateway_elapsed_seconds'],
            historical_default_elapsed=q['default_historical_elapsed_seconds']))
    comparison=pd.DataFrame(rows);comparison.to_csv(output/'comparisons.csv',index=False)
    same=bool(comparison.raw_bitwise_equal.all() and comparison.spatial_version_metadata_equal.all())
    med=float(comparison.gateway_elapsed_with_reporting_overhead.median());old=float(comparison.historical_default_elapsed.median())
    summary=dict(recovered_from_saved_arrays=True,network_used=False,new_queries=0,patches=len(rows),
        same_raw_arrays_and_spatial_version_metadata=same,gateway_median_upper_bound_seconds=med,
        historical_default_median_seconds=old,switch_to_gateway=same and med<=.75*old,
        timing_caveat='Gateway logged durations include post-read save/reporting-failure overhead and upper-bound raw read times. Historical timings are confounded by time/network/cache; no causal speed claim.')
    hashes[str((pilot/'queries.json').relative_to(ROOT))]=hashlib.sha256((pilot/'queries.json').read_bytes()).hexdigest()
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (output/'input-sha256.json').write_text(json.dumps(hashes,sort_keys=True,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();recover(a.output)
