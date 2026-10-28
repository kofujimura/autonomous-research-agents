"""Exact regular-grid index reuse, with nearest-decoder cross-checks."""
import argparse
import hashlib
import json
from pathlib import Path

import eccodes as ec
import numpy as np

from record import ROOT,now


def grid_digest(content):
    assert content[:4]==b'GRIB' and content[7]==2
    assert int.from_bytes(content[8:16],'big')==len(content)
    offset=16;grids=[]
    while offset<len(content)-4:
        length=int.from_bytes(content[offset:offset+4],'big')
        assert length>=5 and offset+length<=len(content)-4
        if content[offset+4]==3:grids.append(content[offset:offset+length])
        offset+=length
    assert offset==len(content)-4 and content[-4:]==b'7777' and len(grids)==1
    return hashlib.sha256(grids[0]).hexdigest()


def extract(gid,content,points,mapping=None,validate=False):
    assert ec.codes_get(gid,'gridType')=='regular_ll'
    signature=grid_digest(content)
    values=np.asarray(ec.codes_get_values(gid),dtype=np.float64)
    assert len(values)==int(ec.codes_get(gid,'numberOfPoints'))
    checked=mapping is None or validate
    if mapping is not None:
        assert signature==mapping['grid_sha256'],'Grid definition changed; refuse index reuse'
        assert len(values)==mapping['point_count']
    if checked:
        nearest=ec.codes_grib_find_nearest_multiple(gid,False,points[:,0].tolist(),(points[:,1]%360).tolist())
        grid=np.array([[x['lat'],x['lon'],x['index'],x['distance']] for x in nearest],dtype=np.float64)
        direct=np.array([x['value'] for x in nearest],dtype=np.float64)
        indices=grid[:,2].astype(np.int64)
        assert np.array_equal(indices,grid[:,2]) and np.all(indices>=0) and np.all(indices<len(values))
        assert np.array_equal(values[indices],direct),'Indexed/nearest extraction value mismatch'
        if mapping is not None:assert np.allclose(grid,mapping['grid'],rtol=0,atol=1e-8)
        mapping={'grid_sha256':signature,'point_count':len(values),'grid':grid}
    else:grid=mapping['grid'];indices=grid[:,2].astype(np.int64)
    selected=values[indices]
    assert np.isfinite(selected).all()
    return selected,grid,mapping,{'grid_definition_sha256':signature,
        'decoded_point_count':len(values),'nearest_cross_check':checked,
        'selected_value_mismatches':0,'selected_method':'validated_grid_indices'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
    design=json.loads((ROOT/'protocol/design-v4.json').read_text())
    points=np.array([xy for portfolio in design['portfolios'] for xy in portfolio['points']])
    checks=[];mask=ROOT/'data/cities/ifs-land-mask.grib2'
    samples=[(mask,None)]
    for meta in sorted((ROOT/'data/extraction-validation').rglob('*.json')):
        item=json.loads(meta.read_text());samples.append((meta.with_suffix('.grib2'),item))
    for source,metadata in samples:
        content=source.read_bytes()
        if metadata:assert hashlib.sha256(content).hexdigest()==metadata['grib_sha256']
        gid=ec.codes_new_from_message(content)
        try:
            selected,grid,mapping,check=extract(gid,content,points)
            reused,grid2,_,second=extract(gid,content,points,mapping)
            assert np.array_equal(selected,reused) and np.array_equal(grid,grid2)
            if metadata:
                old=np.load(ROOT/metadata['selected_vector_path'],allow_pickle=False)
                assert np.array_equal(selected,old['kelvin'])
                assert np.allclose(grid,old['grid_locations'],rtol=0,atol=1e-8)
                for key in ['shortName','units','perturbationNumber','dataDate','dataTime','endStep']:
                    assert ec.codes_get(gid,key)==metadata['grib_metadata'][key]
            checks.append({'source':str(source.relative_to(ROOT)),**check,'reuse_check':second})
        finally:ec.codes_release(gid)
    report={'status':'passed','completed_at_utc':now(),'fields_checked':len(checks),
            'selected_slots_per_field':len(points),'checks':checks,'network_calls':0}
    (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='checks'}))


if __name__=='__main__':main()
