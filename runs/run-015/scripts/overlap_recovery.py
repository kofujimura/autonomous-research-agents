"""Exploratory coverage check from already scheduled v4 data; no network."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np

from acquire import points_for
from analyze_unit import analyze
from record import ROOT,now

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def link(source,target):
    target.parent.mkdir(parents=True,exist_ok=True)
    target.symlink_to(os.path.relpath(source.resolve(),target.parent.resolve()),target_is_directory=source.is_dir())

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
    out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
    date='20260709';model='aifs-ens';lead=84;original=ROOT/'data/weather'/date/model/str(lead)
    new=ROOT/'data/weather-v4'/date/model/str(lead)
    if not (new/'complete.json').exists():
        (out/'recovery.json').write_text(json.dumps({'status':'v4_input_not_complete','date':date,'model':model,'lead':lead,'observed_at_utc':now()},indent=2)+'\n')
        print('Scheduled overlapping input incomplete; no recovery attempted');return
    assert not (original/'complete.json').exists(),'The predefined exhausted original unit unexpectedly changed'
    ledger_before=sha(original/'unit-attempts.jsonl');assert len((original/'unit-attempts.jsonl').read_text().splitlines())==2
    assert (original/'fields.index').read_bytes()==(new/'fields.index').read_bytes()
    saved=np.load(new/'temperatures.npz',allow_pickle=False)
    assert saved['kelvin'].shape==(50,24,12) and np.array_equal(saved['members'],np.arange(1,51))
    design=json.loads((ROOT/'protocol/design-v1.json').read_text());portfolios,points=points_for(design)
    assert np.array_equal(saved['points'][:144],points)
    values=saved['kelvin'][:,:12,:];checks=[]
    for old_path in sorted(original.glob('member-*.npz')):
        old=np.load(old_path,allow_pickle=False);old_info=json.loads(str(old['metadata_json']))
        member=int(old_info['member']);fresh=np.load(new/f'member-{member:02d}.npz',allow_pickle=False)
        fresh_info=json.loads(str(fresh['metadata_json']))
        assert np.array_equal(old['kelvin'],values[member-1].reshape(-1))
        assert np.allclose(old['grid_locations'],saved['grid_locations'][:144],atol=1e-8,rtol=0)
        assert old_info['grib_sha256']==fresh_info['grib_sha256']
        for key,expected in [('shortName','2t'),('units','K'),('dataDate',int(date)),('dataTime',0),('endStep',lead),('perturbationNumber',member)]:
            assert fresh_info['grib_metadata'][key]==expected
        checks.append({'member':member,'original_vector_sha256':sha(old_path),'new_vector_sha256':sha(new/f'member-{member:02d}.npz'),
                       'matching_global_field_sha256':old_info['grib_sha256']})
    assert len(checks)==41,'Expected the frozen41retained original members'
    folder=out/'derived-input'/date/model/str(lead);folder.mkdir(parents=True,exist_ok=True)
    target=folder/'temperatures.npz'
    if target.exists():raise RuntimeError('Refuse overwriting recovered input; use a fresh output location')
    np.savez_compressed(target,kelvin=values,points=points,grid_locations=saved['grid_locations'][:144],
                        members=saved['members'],portfolios_json=json.dumps(portfolios))
    provenance={'status':'checks_passed','created_at_utc':now(),'exploratory':True,'date':date,'model':model,'lead':lead,
                'new_raw_source':str((new/'temperatures.npz').relative_to(ROOT)),'new_raw_sha256':sha(new/'temperatures.npz'),
                'derived_sha256':sha(target),'old_attempt_ledger_sha256':ledger_before,'index_sha256':sha(original/'fields.index'),
                'original_members_compared':len(checks),'member_checks':checks,
                'index_check_scope':'The v4 index was reused byte-for-byte from the original cached index, not independently downloaded; identity is a cache-consistency check, not evidence of archive stability for unobserved fields.',
                'scope':'Original v1exclusion preserved; new inputs already required by v4; no independent forecast sample or guarantee for never-observed original fields.'}
    (folder/'complete.json').write_text(json.dumps(provenance,indent=2)+'\n')
    result=out/'derived-bounds'/date/model/str(lead);analyze(folder,result,50)
    replay=out/'calendar-input';replay.mkdir();link(ROOT/'protocol',replay/'protocol')
    for day in design['dates']:
        for product in design['models']:
            for step in design['leads']:
                raw=ROOT/'data/weather'/day/product/str(step);bounds=ROOT/'results/units'/day/product/str(step)
                if (day,product,step)==(date,model,lead):raw=folder;bounds=result
                if raw.exists():link(raw,replay/'data/weather'/day/product/str(step))
                if bounds.exists():link(bounds,replay/'results/units'/day/product/str(step))
    subprocess.run([sys.executable,str(ROOT/'scripts/summarize.py'),'--root',str(replay),'--output',str(out/'summary')],check=True,timeout=300)
    assert sha(original/'unit-attempts.jsonl')==ledger_before and not (original/'complete.json').exists()
    (out/'recovery.json').write_text(json.dumps(provenance,indent=2)+'\n');print(json.dumps({k:v for k,v in provenance.items() if k!='member_checks'}),flush=True)

if __name__=='__main__':main()
