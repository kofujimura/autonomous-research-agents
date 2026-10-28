"""Offline consistency of selected vectors, source indexes and combined arrays."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from acquire import points_for
from record import ROOT,now


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
    reports=[];members_checked=0;legacy_design_metadata=0
    for phase,design_path in [('weather','protocol/design-v1.json'),('weather-v4','protocol/design-v4.json')]:
        base=ROOT/'data'/phase
        if not base.exists():continue
        design=json.loads((ROOT/design_path).read_text());portfolios,points=points_for(design)
        for folder in sorted(base.glob('*/*/*')):
            if not folder.is_dir():continue
            files=sorted(folder.glob('member-[0-9][0-9].npz'))
            if not files:continue
            date,model,lead=folder.relative_to(base).parts;lead=int(lead)
            assert date in design['dates'] and model in design['models'] and lead in design['leads']
            index=folder/'fields.index';index_hash=sha(index)
            fields=[json.loads(x) for x in index.read_text().splitlines()]
            fields={int(x['number']):x for x in fields if x.get('param')=='2t' and x.get('number') is not None and 1<=int(x['number'])<=50}
            assert set(fields)==set(range(1,51))
            measurements={}
            for line in (folder/'measurements.jsonl').read_text().splitlines():
                item=json.loads(line);path=item['path']
                if path in measurements:assert item['sha256']==measurements[path]['sha256']
                measurements[path]=item
            values={};grid=None
            for path in files:
                saved=np.load(path,allow_pickle=False);metadata=json.loads(str(saved['metadata_json']))
                member=int(path.stem.split('-')[1]);assert metadata['member']==member
                assert metadata['date']==date and metadata['model_requested']==model and metadata['lead']==lead
                field=fields[member];start=int(field['_offset']);length=int(field['_length'])
                assert metadata['byte_range']==[start,start+length-1] and metadata['grib_bytes']==length
                assert metadata['index_sha256']==index_hash
                info=metadata['grib_metadata']
                for key,expected in [('shortName','2t'),('units','K'),('perturbationNumber',member),('dataDate',int(date)),('dataTime',0),('endStep',lead)]:
                    assert info[key]==expected,(str(path),key)
                assert len(metadata['grib_sha256'])==64
                if 'design_path' in metadata:
                    assert metadata['design_path']==design_path and metadata['design_sha256']==sha(ROOT/design_path)
                else:legacy_design_metadata+=1
                v=saved['kelvin'];locations=saved['grid_locations']
                assert v.shape==(len(points),) and locations.shape==(len(points),4)
                assert np.isfinite(v).all() and ((v>180)&(v<350)).all()
                if grid is not None:assert np.allclose(locations,grid,rtol=0,atol=1e-8)
                grid=locations;values[member]=v
                relative=str(path.relative_to(ROOT));assert measurements[relative]['sha256']==sha(path)
                assert measurements[relative]['grib_sha256']==metadata['grib_sha256']
                members_checked+=1
            complete=folder/'complete.json'
            if complete.exists():
                assert set(values)==set(range(1,51))
                summary=json.loads(complete.read_text());target=folder/'temperatures.npz'
                assert summary['selected_data_sha256']==sha(target) and summary['index_sha256']==index_hash
                combined=np.load(target,allow_pickle=False)
                assert np.array_equal(combined['members'],np.arange(1,51))
                assert np.array_equal(combined['points'],points)
                assert np.allclose(combined['grid_locations'],grid,rtol=0,atol=1e-8)
                assert np.array_equal(combined['kelvin'].reshape(50,-1),np.stack([values[i] for i in range(1,51)]))
            reports.append({'phase':phase,'date':date,'model':model,'lead':lead,'members':len(values),'complete':complete.exists()})
    report={'status':'passed','completed_at_utc':now(),'forecast_folders_checked':len(reports),
            'member_vectors_checked':members_checked,'complete_forecast_units':sum(x['complete'] for x in reports),
            'legacy_member_records_without_design_fields':legacy_design_metadata,
            'legacy_scope':'Earlier records lack optional design fields; complete combined points and fixed-design geometry are checked directly. No metadata is retrospectively filled.',
            'units':reports,'network_calls':0,'ai_api_calls':0}
    Path(a.output).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='units'}))


if __name__=='__main__':main()
