"""Bounded single-case access pilot, not a main result."""
import hashlib
import argparse
import json
from pathlib import Path
import time
import numpy as np
import requests
import eccodes as ec
from record import ROOT, append, now

p=argparse.ArgumentParser();p.add_argument('--date',default='20260701');p.add_argument('--members',type=int,default=50);a=p.parse_args()
assert 1<=a.members<=50
centres=[(40.,-4.),(46.,2.),(37.,-98.),(33.,-85.),(24.,80.),(-20.,-50.),(-30.,145.),(-28.,26.)]
points=[(lat+dy,lon+dx) for lat,lon in centres for dy in [-1.,0.,1.] for dx in [-1.5,-.5,.5,1.5]]
out=ROOT/'data/pilot'/('weather' if a.date=='20260701' else 'weather-'+a.date);out.mkdir(exist_ok=True,parents=True)
index=ROOT/'data/pilot'/('aifs-168.index' if a.date=='20260701' else 'aifs-'+a.date+'-168.index')
rows=sorted([json.loads(x) for x in index.read_text().splitlines() if json.loads(x).get('param')=='2t'],key=lambda x:int(x['number']))
assert len(rows)==50 and [int(x['number']) for x in rows]==list(range(1,51))
rows=rows[:a.members]
url=f'https://ecmwf-forecasts.s3.eu-central-1.amazonaws.com/{a.date}/00z/aifs-ens/0p25/enfo/{a.date}000000-168h-enfo-pf.grib2'
session=requests.Session();session.auth=lambda request:request
results=[];metadata=[]
for row in rows:
    member=int(row['number']);path=out/f'member-{member:02d}.grib2';start=row['_offset'];length=row['_length']
    if not path.exists():
        fetched=now()
        pieces=[]
        for offset in range(start,start+length,65536):
            end=min(offset+65535,start+length-1)
            collected=b''
            for attempt in range(3):
                pending_start=offset+len(collected)
                try:
                    with session.get(url,headers={'Range':f'bytes={pending_start}-{end}'},timeout=(15,30),stream=True) as response:
                        response.raise_for_status()
                        if response.status_code!=206:raise ValueError('Server did not honour Range; whole-object read refused')
                        expected=f'bytes {pending_start}-{end}/'
                        if not response.headers.get('Content-Range','').startswith(expected):raise ValueError('Incorrect Content-Range')
                        for block in response.iter_content(4096):collected+=block
                        if len(collected)!=end-offset+1:raise ValueError('Range length mismatch')
                        pieces.append(collected)
                    break
                except requests.RequestException as error:
                    print(json.dumps({'member':member,'offset':offset,'attempt':attempt+1,'bytes_retained':len(collected),'error':type(error).__name__,'observed_at_utc':now()}),flush=True)
                    if attempt==2:raise
                    time.sleep(2**(attempt+1))
        content=b''.join(pieces)
        if len(content)!=length:raise ValueError('Assembled GRIB length mismatch')
        path.write_bytes(content)
        append('sources.jsonl',dict(source_id=f'PILOT-AIFS-M{member:02d}',url=url,byte_range=[start,start+length-1],path=str(path.relative_to(ROOT)),obtained_at_utc=fetched,sha256=hashlib.sha256(content).hexdigest(),bytes=length,licence='CC BY 4.0 plus ECMWF open-data terms; see literature/ecmwf-general-terms.html',access_range='one complete GRIB message for 2m temperature'))
    gid=ec.codes_new_from_message(path.read_bytes())
    try:
        info={key:ec.codes_get(gid,key) for key in ['shortName','units','perturbationNumber','dataDate','dataTime','endStep','gridType','Ni','Nj','centre']}
        assert info['shortName']=='2t' and info['units']=='K' and info['perturbationNumber']==member
        near=ec.codes_grib_find_nearest_multiple(gid,False,[p[0] for p in points],[p[1]%360 for p in points])
        results.append([p['value'] for p in near]);metadata.append(info)
        if member==1:
            (out/'locations.json').write_text(json.dumps([dict(requested_lat=p[0],requested_lon=p[1],grid_lat=x['lat'],grid_lon=x['lon'],index=x['index'],distance_km=x['distance']) for p,x in zip(points,near)],indent=2)+'\n')
    finally:ec.codes_release(gid)
    print(json.dumps({'member':member,'observed_at_utc':now()}),flush=True)
array=np.array(results,dtype=np.float64).reshape(a.members,len(centres),12)
np.savez_compressed(out/'temperatures.npz',kelvin=array,centres=np.array(centres),points=np.array(points))
summary={'observed_at_utc':now(),'shape':list(array.shape),'finite_values':int(np.isfinite(array).sum()),'min_kelvin':float(array.min()),'max_kelvin':float(array.max()),'units':'K','metadata':metadata,
         'threshold_checks':{}}
summary['threshold_checks']={str(t):{'uncertain_sites':int(np.sum(((array>=t+273.15).mean(axis=0)>0)&((array>=t+273.15).mean(axis=0)<1))), 'sites_with_any_member_exceedance':int(np.sum((array>=t+273.15).any(axis=0)))} for t in [25,30,35]}
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='metadata'}))
