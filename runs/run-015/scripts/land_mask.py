"""Optional planned IFS land-fraction diagnostic; never filters locations."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import time

import eccodes as ec
import numpy as np
import requests

from acquire import BASES,points_for
from record import ROOT,append,now

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--offline',action='store_true');a=p.parse_args()
    out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
    source=ROOT/'data/cities/ifs-land-mask.grib2'
    index=ROOT/'data/weather/20260603/ifs/84/fields.index'
    rows=[json.loads(x) for x in index.read_text().splitlines()]
    field=min((r for r in rows if r.get('param')=='lsm'),key=lambda r:int(r['number']))
    relative='20260603/00z/ifs/0p25/enfo/20260603000000-84h-enfo-ef.grib2'
    start=field['_offset'];length=field['_length'];assert 0<length<2000000
    if not source.exists():
        if a.offline:raise RuntimeError('Optional mask not bundled; offline diagnostic unavailable')
        session=requests.Session();session.auth=lambda request:request
        session.headers.update({'User-Agent':'FreeResearch015/1.0 public-data-extraction','Accept-Encoding':'identity'})
        body=None
        for base in BASES:
            previous=[json.loads(line) for line in (out/'transfers.jsonl').read_text().splitlines()] if (out/'transfers.jsonl').exists() else []
            used={r['attempt'] for r in previous if r['url']==base+relative}
            for attempt in range(1,4):
                if attempt in used:continue
                stamp=now();record={'url':base+relative,'requested_start':start,'requested_end':start+length-1,
                                    'attempt':attempt,'requested_at_utc':stamp}
                try:
                    with session.get(base+relative,headers={'Range':f'bytes={start}-{start+length-1}'},timeout=(10,25),stream=True) as response:
                        record['http_status']=response.status_code;response.raise_for_status()
                        assert response.status_code==206
                        assert response.headers['Content-Range'].split('/')[0]==f'bytes {start}-{start+length-1}'
                        chunks=[];received=0
                        for chunk in response.iter_content(chunk_size=16384):
                            received+=len(chunk)
                            if received>length:raise RuntimeError('Range body exceeds indexed message length')
                            chunks.append(chunk)
                        candidate=b''.join(chunks);assert len(candidate)==length and candidate[:4]==b'GRIB' and candidate[-4:]==b'7777'
                        body=candidate;record['status']='completed'
                except Exception as error:
                    record.update(status='failed',error_type=type(error).__name__,error=str(error))
                record['observed_at_utc']=now();append(str((out/'transfers.jsonl').relative_to(ROOT)),record)
                if body is not None:break
                if record.get('http_status') in [200,403,404]:raise RuntimeError('Optional mask unavailable or range ignored; no alternate retrieval')
                time.sleep(1)
            if body is not None:break
        if body is None:raise RuntimeError('Optional land-mask retrieval failed within fixed bounds')
        source.write_bytes(body)
        append('sources.jsonl',{'source_id':'V4-IFS-LAND-MASK','url':record['url'],'obtained_at_utc':stamp,
               'path':str(source.relative_to(ROOT)),'sha256':hashlib.sha256(body).hexdigest(),
               'licence':'CC BY4.0 plus ECMWF general terms','access_range':'One indexed187kB-class GRIB message for land-sea mask; full field bundled',
               'field_index':field,'index_sha256':hashlib.sha256(index.read_bytes()).hexdigest()})
    design=json.loads((ROOT/'protocol/design-v4.json').read_text());portfolios,points=points_for(design)
    gid=ec.codes_new_from_message(source.read_bytes())
    try:
        metadata={key:ec.codes_get(gid,key) for key in ['shortName','dataDate','dataTime','endStep','perturbationNumber','units']}
        assert metadata['shortName']=='lsm' and metadata['dataDate']==20260603 and metadata['endStep']==84
        near=ec.codes_grib_find_nearest_multiple(gid,False,points[:,0].tolist(),(points[:,1]%360).tolist())
        values=np.array([r['value'] for r in near]);assert np.isfinite(values).all() and values.min()>=-1e-7 and values.max()<=1+1e-7
    finally:ec.codes_release(gid)
    rows=[]
    for i,(point,result) in enumerate(zip(points,near)):
        portfolio=portfolios[i//12]
        rows.append({'portfolio_index':i//12,'site_index':i%12,**{k:portfolio[k] for k in ['center','geometry','portfolio_type']},
                     'latitude':point[0],'longitude':point[1],'grid_latitude':result['lat'],'grid_longitude':result['lon'],
                     'land_fraction':result['value']})
    with (out/'land-fractions.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    summary={'completed_at_utc':now(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'grib_metadata':metadata,
             'scope':'One IFS mask field, no site exclusions; not an AIFS classification or urban microclimate validation','groups':[]}
    for kind in ['regular','city']:
        vals=np.array([r['land_fraction'] for r in rows if r['portfolio_type']==kind])
        summary['groups'].append({'portfolio_type':kind,'site_slots':len(vals),'below_half_land':int((vals<.5).sum()),
                                  'strictly_mixed':int(((vals>0)&(vals<1)).sum()),'min_land_fraction':float(vals.min()),'max_land_fraction':float(vals.max())})
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
