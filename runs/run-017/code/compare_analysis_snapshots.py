"""Compare two complete analysis snapshots without rerunning fitted models."""
import argparse
import json
from pathlib import Path
import pandas as pd
from freeze_expected import without_times
from verify import compare
from records import ROOT,now

def main():
    p=argparse.ArgumentParser();p.add_argument('--old',required=True);p.add_argument('--new',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    keys={'scores':['fit_id','version','condition','boundary_tolerance_m'],
        'regional-scores':['fit_id','version','condition','boundary_tolerance_m','size_bin','coverage_target','region_id'],
        'bootstrap-blocks':['fit_id','version','condition','boundary_tolerance_m','size_bin','core_id'],
        'strata-scores':['fit_id','stratum','region_id']}
    counts={}
    for name,order in keys.items():
        old=pd.read_csv(ROOT/a.old/(name+'.csv'));new=pd.read_csv(ROOT/a.new/(name+'.csv'))
        pd.testing.assert_frame_equal(new[old.columns].sort_values(order).reset_index(drop=True),
            old.sort_values(order).reset_index(drop=True),check_dtype=False,check_exact=False,atol=1e-12,rtol=0)
        counts[name]=len(old)
    failures=[]
    for name in ['summary.json','robustness/summary.json']:
        old=without_times(json.loads((ROOT/a.old/name).read_text()));new=without_times(json.loads((ROOT/a.new/name).read_text()))
        failures.extend(compare(new,old,name))
    result=dict(checked_at_utc=now(),status='PASS' if not failures else 'FAIL',failures=failures,
        rows_compared=counts,absolute_tolerance=1e-12,
        interpretation='Self-check of all reported counts/estimates/intervals after aggregation optimization; not independent reproduction')
    out=ROOT/a.out;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
    if failures:raise SystemExit(1)

if __name__=='__main__':main()
