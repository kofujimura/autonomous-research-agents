"""Exploratory v4 acquisition and aligned snapshot/four-time-maximum analysis."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import time
import traceback

import numpy as np

import acquire
from bounds import evaluate,TOL
from subset_bounds import encoding_checks
from record import ROOT,append,now

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def analyze_endpoint(values,portfolios,identity,out):
    out.mkdir(parents=True,exist_ok=True);target=out/'bounds.csv';summary_path=out/'summary.json'
    if summary_path.exists():
        prior=json.loads(summary_path.read_text());assert prior['output_sha256']==sha(target)
        return prior
    start=time.monotonic();rows=[];pmfs=[];checks=[]
    for pi,portfolio in enumerate(portfolios):
        for threshold in [25,30,35]:
            X=(values[:,pi,:]>=threshold+273.15).astype(np.uint8)
            pmf=np.bincount(X.sum(axis=1).astype(int),minlength=13)/50
            pmfs.append({**identity,'portfolio_index':pi,'threshold_c':threshold,'pmf':pmf.tolist()})
            checks.append(encoding_checks(X))
            for row in evaluate(X,[3,6,9]):
                assert abs(row['q']-pmf[row['k']:].sum())<TOL
                row.update(**identity,portfolio_index=pi,center=portfolio['center'],geometry=portfolio['geometry'],
                           portfolio_type=portfolio['portfolio_type'],threshold_c=threshold,n=12,
                           informative=int(row['uncertain_sites']>=4 and .1<=row['q']<=.9),exploratory=True)
                rows.append(row)
    with target.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    with (out/'count-distributions.jsonl').open('w') as f:
        for row in pmfs:f.write(json.dumps(row)+'\n')
    summary={**identity,'rows':len(rows),'completed_at_utc':now(),'elapsed_seconds':time.monotonic()-start,
             'output_sha256':sha(target),'encoding_round_trip_errors':sum(c['round_trip_errors'] for c in checks),
             'max_primal_residual':max(r['max_primal_residual'] for r in rows),
             'max_dual_violation':max(r['max_dual_violation'] for r in rows),
             'max_duality_gap':max(r['max_duality_gap'] for r in rows),'exploratory':True}
    summary_path.write_text(json.dumps(summary,indent=2)+'\n');return summary

def derive(date,model,horizon,design,source_root=ROOT,output_root=ROOT):
    source_root=Path(source_root);output_root=Path(output_root)
    leads=[24*horizon+offset for offset in [0,6,12,18]]
    sources=[source_root/'data/weather-v4'/date/model/str(lead)/'temperatures.npz' for lead in leads]
    if not all((p.parent/'complete.json').exists() for p in sources):
        return {'status':'incomplete_horizon','date':date,'model':model,'horizon':horizon,
                'missing_leads':[lead for lead,p in zip(leads,sources) if not (p.parent/'complete.json').exists()]}
    arrays=[np.load(p,allow_pickle=False) for p in sources]
    for saved in arrays[1:]:
        assert np.array_equal(saved['members'],arrays[0]['members'])
        assert np.array_equal(saved['points'],arrays[0]['points'])
        assert np.array_equal(saved['grid_locations'],arrays[0]['grid_locations'])
        assert str(saved['portfolios_json'])==str(arrays[0]['portfolios_json'])
    assert np.array_equal(arrays[0]['members'],np.arange(1,51))
    stacked=np.stack([p['kelvin'] for p in arrays]);snapshot=stacked[2];maximum=stacked.max(axis=0)
    assert np.isfinite(stacked).all() and np.all(maximum>=snapshot)
    portfolios=json.loads(str(arrays[0]['portfolios_json']));snapshot_lead=leads[2]
    comparison={'old_members_compared':0,'temperature_value_mismatches':0,'grib_hash_mismatches':0}
    original=source_root/'data/weather'/date/model/str(snapshot_lead)
    for member in range(1,51):
        old=original/f'member-{member:02d}.npz';new=sources[2].parent/f'member-{member:02d}.npz'
        if not old.exists():continue
        old_saved=np.load(old,allow_pickle=False);new_saved=np.load(new,allow_pickle=False)
        comparison['old_members_compared']+=1
        comparison['temperature_value_mismatches']+=int(np.sum(old_saved['kelvin']!=snapshot[member-1,:12,:].reshape(-1)))
        old_info=json.loads(str(old_saved['metadata_json']));new_info=json.loads(str(new_saved['metadata_json']))
        comparison['grib_hash_mismatches']+=int(old_info['grib_sha256']!=new_info['grib_sha256'])
    outputs=[]
    for endpoint,values in [('snapshot12',snapshot),('maximum4',maximum)]:
        folder=output_root/'data/weather-v4-derived'/endpoint/date/model/str(snapshot_lead);folder.mkdir(parents=True,exist_ok=True)
        target=folder/'temperatures.npz'
        if target.exists():assert np.array_equal(np.load(target,allow_pickle=False)['kelvin'],values)
        else:np.savez_compressed(target,kelvin=values,points=arrays[0]['points'],grid_locations=arrays[0]['grid_locations'],members=arrays[0]['members'],portfolios_json=str(arrays[0]['portfolios_json']))
        provenance={'created_at_utc':now(),'date':date,'model':model,'horizon':horizon,'endpoint':endpoint,
                    'input_paths':[str(p.relative_to(source_root)) for p in sources],
                    'input_sha256':[sha(p) for p in sources],'output_sha256':sha(target),
                    'design_sha256':sha(source_root/'protocol/design-v4.json'),'leads':leads,
                    'operation':'12 UTC snapshot' if endpoint=='snapshot12' else 'member-aligned pointwise maximum across four six-hourly valid times',
                    'not_continuous_daily_maximum':True,'maximum_below_snapshot_count':int(np.sum(maximum<snapshot)),
                    'original_snapshot_comparison':comparison,'exploratory':True}
        if not (folder/'provenance.json').exists():(folder/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
        identity={'date':date,'model':model,'lead':snapshot_lead,'horizon':horizon,'endpoint':endpoint}
        result=analyze_endpoint(values,portfolios,identity,output_root/'results/city-time-units'/endpoint/date/model/str(snapshot_lead))
        outputs.append(result)
    return {'status':'completed_horizon','date':date,'model':model,'horizon':horizon,'outputs':outputs,
            'original_snapshot_comparison':comparison}

def main():
    p=argparse.ArgumentParser();p.add_argument('--date',required=True);p.add_argument('--model',choices=['aifs-ens','ifs'],required=True)
    p.add_argument('--horizon',type=int,choices=[3,7],action='append');p.add_argument('--log',required=True)
    p.add_argument('--chunk-bytes',type=int,choices=[32768,65536,262144,1048576],default=262144)
    p.add_argument('--indexed-extraction',action='store_true');p.add_argument('--retain-validation',action='store_true')
    p.add_argument('--cloudfront-first',action='store_true');a=p.parse_args()
    design=json.loads((ROOT/'protocol/design-v4.json').read_text());assert a.date in design['dates']
    failed=False
    for horizon in a.horizon or [3,7]:
        for lead in [24*horizon+offset for offset in [0,6,12,18]]:
            record={'date':a.date,'model':a.model,'lead':lead,'started_at_utc':now(),'stage':'raw_city_time_acquisition'}
            try:
                flags=(['--indexed-extraction'] if a.indexed_extraction else [])+(['--retain-validation'] if a.retain_validation else [])
                if a.cloudfront_first:flags.append('--cloudfront-first')
                acquire.main(['--date',a.date,'--model',a.model,'--lead',str(lead),
                              '--design','protocol/design-v4.json','--data-root','data/weather-v4','--chunk-bytes',str(a.chunk_bytes),*flags])
                record['status']='completed'
            except Exception as error:
                failed=True;record.update(status='failed',error_type=type(error).__name__,error=str(error));traceback.print_exc()
            record['ended_at_utc']=now();append(a.log,record);print(json.dumps(record),flush=True)
        result=derive(a.date,a.model,horizon,design);result['observed_at_utc']=now()
        append(a.log,result);print(json.dumps(result),flush=True)
        if result['status']!='completed_horizon':failed=True
    raise SystemExit(1 if failed else 0)

if __name__=='__main__':main()
