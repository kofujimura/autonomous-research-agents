"""Prespecified ECMWF extraction; selected temperatures are the raw data.

Global GRIB messages are read using ordinary documented ranges, hashed and
decoded in memory. No forecast probabilities or decision results are inspected.
"""
import argparse
import hashlib
import json
import time
from pathlib import Path

import eccodes as ec
import numpy as np
import requests

from record import ROOT, append, now

BASES=['https://ecmwf-forecasts.s3.eu-central-1.amazonaws.com/',
       'https://d2zvc0wgha4k2l.cloudfront.net/']

def digest(body):return hashlib.sha256(body).hexdigest()

def points_for(design):
    portfolios=[];points=[]
    if 'portfolios' in design:
        for portfolio in design['portfolios']:
            assert len(portfolio['points'])==12
            portfolios.append({key:value for key,value in portfolio.items() if key!='points'})
            points.extend(portfolio['points'])
        return portfolios,np.array(points,dtype=np.float64)
    for name,lat,lon in design['centers']:
        for geometry,offsets in design['geometries'].items():
            portfolios.append({'center':name,'geometry':geometry})
            points.extend((lat+y,lon+x) for y in offsets['lat_offsets'] for x in offsets['lon_offsets'])
    return portfolios,np.array(points,dtype=np.float64)

def main(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument('--date',required=True)
    parser.add_argument('--model',required=True,choices=['aifs-ens','ifs'])
    parser.add_argument('--lead',required=True,type=int)
    parser.add_argument('--design',default='protocol/design-v1.json')
    parser.add_argument('--data-root',default='data/weather')
    parser.add_argument('--chunk-bytes',type=int,choices=[32768,65536,262144,1048576],default=65536)
    parser.add_argument('--indexed-extraction',action='store_true')
    parser.add_argument('--retain-validation',action='store_true')
    parser.add_argument('--cloudfront-first',action='store_true')
    a=parser.parse_args(argv);design_path=ROOT/a.design;design=json.loads(design_path.read_text())
    assert not a.retain_validation or a.indexed_extraction
    bases=list(reversed(BASES)) if a.cloudfront_first else BASES
    assert a.date in design['dates'] and a.lead in design['leads']
    portfolios,points=points_for(design)
    folder=ROOT/a.data_root/a.date/a.model/str(a.lead);folder.mkdir(parents=True,exist_ok=True)
    attempts_path=folder/'unit-attempts.jsonl'
    if not (folder/'complete.json').exists():
        attempts=[json.loads(x) for x in attempts_path.read_text().splitlines()] if attempts_path.exists() else []
        if len(attempts)>=2:raise RuntimeError('Two unit acquisition attempts already recorded; no further network attempt permitted')
        append(str(attempts_path.relative_to(ROOT)),{'attempt':len(attempts)+1,'started_at_utc':now(),'chunk_bytes':a.chunk_bytes,'indexed_extraction':a.indexed_extraction,'retain_validation':a.retain_validation,'cloudfront_first':a.cloudfront_first,'retrospective':False})
    transfers=folder/'transfers.jsonl';records=folder/'measurements.jsonl'
    def log(record):
        record.update(observed_at_utc=now())
        append(str(transfers.relative_to(ROOT)),record)
    session=requests.Session();session.auth=lambda request:request
    session.headers.update({'User-Agent':'FreeResearch015/1.0 public-data-extraction','Accept-Encoding':'identity'})
    relative=f'{a.date}/00z/{a.model}/0p25/enfo/{a.date}000000-{a.lead}h-enfo-'+('pf' if a.model=='aifs-ens' else 'ef')
    index_path=folder/'fields.index'
    original_index=ROOT/'data/weather'/a.date/a.model/str(a.lead)/'fields.index'
    if not index_path.exists() and original_index!=index_path and original_index.exists():
        body=original_index.read_bytes();index_path.write_bytes(body)
        origin={}
        for line in (ROOT/'sources.jsonl').read_text().splitlines():
            item=json.loads(line)
            if item.get('path')==str(original_index.relative_to(ROOT)) and item.get('sha256')==digest(body):origin=item
        append('sources.jsonl',dict(source_id=f'WEATHER-INDEX-REUSED-{a.date}-{a.model}-{a.lead}',
            url=origin.get('url',BASES[0]+relative+'.index'),path=str(index_path.relative_to(ROOT)),
            obtained_at_utc=origin.get('obtained_at_utc'),reused_at_utc=now(),
            reused_from=str(original_index.relative_to(ROOT)),sha256=digest(body),bytes=len(body),
            licence='CC BY4.0 plus ECMWF general open-data terms',access_range='byte-identical saved public index reused, not downloaded again'))
    if not index_path.exists():
        failure=None
        for base in bases:
            url=base+relative+'.index';stamp=now()
            try:
                response=session.get(url,timeout=(10,40));response.raise_for_status()
                body=response.content
                if len(body)>8_000_000:raise ValueError('Index exceeds safe size cap')
                rows=[json.loads(x) for x in body.splitlines()]
                if not rows or not all('_offset' in x and '_length' in x for x in rows):raise ValueError('Invalid index')
                index_path.write_bytes(body)
                append('sources.jsonl',dict(source_id=f'WEATHER-INDEX-{a.date}-{a.model}-{a.lead}',url=url,obtained_at_utc=stamp,completed_at_utc=now(),path=str(index_path.relative_to(ROOT)),sha256=digest(body),bytes=len(body),licence='CC BY 4.0 plus ECMWF general open-data terms',access_range='complete GRIB field index'))
                break
            except (requests.RequestException,ValueError) as error:
                failure=error;log({'operation':'index','url':url,'status':'failed','error_type':type(error).__name__,'http_status':getattr(getattr(error,'response',None),'status_code',None)})
        else:
            from index_ranges import recover
            body,url,stamp=recover(session,bases,relative,log)
            recovered_rows=[json.loads(x) for x in body.splitlines()]
            if not recovered_rows or not all('_offset' in x and '_length' in x for x in recovered_rows):raise ValueError('Invalid recovered index')
            index_path.write_bytes(body)
            append('sources.jsonl',dict(source_id=f'WEATHER-INDEX-{a.date}-{a.model}-{a.lead}',url=url,obtained_at_utc=stamp,completed_at_utc=now(),path=str(index_path.relative_to(ROOT)),sha256=digest(body),bytes=len(body),licence='CC BY4.0 plus ECMWF general open-data terms',access_range='complete index recovered by bounded byte ranges after full-GET errors'))
    rows=[json.loads(x) for x in index_path.read_text().splitlines()]
    rows=sorted([x for x in rows if x.get('param')=='2t' and x.get('number') is not None and 1<=int(x['number'])<=50],key=lambda x:int(x['number']))
    assert len(rows)==50 and [int(x['number']) for x in rows]==list(range(1,51)), 'Expected exactly fifty perturbed surface-temperature fields'

    def byte_range(start,end,field_id,depth=0):
        failure=None;collected=b'';restricted=False;ignored_range=False;recoverable=False
        for base in bases:
            url=base+relative+'.grib2'
            for attempt in range(3):
                pending=start+len(collected);before=len(collected);status=None;crange=None
                try:
                    with session.get(url,headers={'Range':f'bytes={pending}-{end}'},timeout=(10,25),stream=True) as response:
                        status=response.status_code;crange=response.headers.get('Content-Range');response.raise_for_status()
                        if status!=206:
                            ignored_range=True
                            raise ValueError('Server did not honor range; whole-object read refused')
                        if not (crange or '').startswith(f'bytes {pending}-{end}/'):
                            ignored_range=True
                            raise ValueError('Incorrect Content-Range')
                        # Retain short final fragments. Our own exact-length
                        # check below still rejects incomplete range responses.
                        response.raw.enforce_content_length=False
                        for block in response.iter_content(4096):
                            if len(collected)+len(block)>end-start+1:raise ValueError('Range response exceeds request')
                            collected+=block
                        if len(collected)!=end-start+1:raise ValueError('Truncated range body')
                    log({'operation':'range','member':field_id,'url':url,'requested_start':pending,'requested_end':end,'attempt':attempt+1,'status':'completed','http_status':status,'content_range':crange,'bytes_received':len(collected)-before})
                    return collected
                except (requests.RequestException,ValueError) as error:
                    failure=error
                    recoverable=(status is not None and status>=500) or isinstance(error,(requests.Timeout,requests.ConnectionError,requests.exceptions.ChunkedEncodingError)) or (isinstance(error,ValueError) and 'Truncated' in str(error))
                    log({'operation':'range','member':field_id,'url':url,'requested_start':pending,'requested_end':end,'attempt':attempt+1,'status':'failed','http_status':status,'content_range':crange,'bytes_retained':len(collected),'error_type':type(error).__name__})
                    if len(collected)==end-start+1:return collected
                    if status in [403,404]:restricted=True;break
                    if attempt<2:time.sleep(2**attempt)
        pending=start+len(collected)
        if recoverable and not restricted and not ignored_range and depth<2 and end-pending+1>16384:
            middle=(pending+end)//2
            log({'operation':'range_split','member':field_id,'requested_start':pending,
                 'requested_end':end,'depth':depth,'reason':'Bounded attempts failed; split same unresolved public-file range'})
            return collected+byte_range(pending,middle,field_id,depth+1)+byte_range(middle+1,end,field_id,depth+1)
        raise RuntimeError(f'Range failed after bounded retries, member {field_id}') from failure

    values=[];all_metadata=[];locations=None;mapping=None
    for row in rows:
        member=int(row['number']);target=folder/f'member-{member:02d}.npz'
        if target.exists():
            saved=np.load(target,allow_pickle=False)
            v=saved['kelvin'];metadata=json.loads(str(saved['metadata_json']))
            assert v.shape==(len(points),) and metadata['member']==member
            locations=saved['grid_locations'];values.append(v);all_metadata.append(metadata)
            print(json.dumps({'member':member,'cached':True,'observed_at_utc':now()}),flush=True)
            continue
        stamp=now();start=row['_offset'];length=row['_length']
        assert 0<length<2_000_000
        content=b''.join(byte_range(offset,min(offset+a.chunk_bytes-1,start+length-1),member) for offset in range(start,start+length,a.chunk_bytes))
        assert len(content)==length and content[:4]==b'GRIB' and content[-4:]==b'7777'
        gid=ec.codes_new_from_message(content)
        try:
            keys=['shortName','units','perturbationNumber','dataDate','dataTime','endStep','gridType','Ni','Nj','centre','edition','generatingProcessIdentifier','experimentVersionNumber']
            info={key:ec.codes_get(gid,key) for key in keys if ec.codes_is_defined(gid,key)}
            assert info['shortName']=='2t' and info['units']=='K' and info['perturbationNumber']==member
            assert info['dataDate']==int(a.date) and info['dataTime']==0 and info['endStep']==a.lead
            extraction={}
            if a.indexed_extraction:
                from extract_points import extract
                v,grid,mapping,extraction=extract(gid,content,points,mapping,validate=member==50)
            else:
                near=ec.codes_grib_find_nearest_multiple(gid,False,points[:,0].tolist(),(points[:,1]%360).tolist())
                v=np.array([x['value'] for x in near],dtype=np.float64)
                grid=np.array([[x['lat'],x['lon'],x['index'],x['distance']] for x in near],dtype=np.float64)
            assert np.isfinite(v).all() and ((v>180)&(v<350)).all()
            if locations is not None:assert np.allclose(grid,locations,rtol=0,atol=1e-8)
            locations=grid
        finally:ec.codes_release(gid)
        metadata={'date':a.date,'model_requested':a.model,'lead':a.lead,'member':member,'obtained_at_utc':stamp,'completed_at_utc':now(),'grib_metadata':info,'grib_sha256':digest(content),'grib_bytes':length,'byte_range':[start,start+length-1],'source_path':relative+'.grib2','index_sha256':digest(index_path.read_bytes()),'design_path':a.design,'design_sha256':digest(design_path.read_bytes()),'global_grib_retained':False,'reason':'Analysis raw input is complete prespecified selected-site vector, saved losslessly; global transport values not analyzed','licence':'CC BY 4.0 plus ECMWF general terms'}
        if extraction:metadata['extraction']=extraction
        if a.retain_validation and extraction.get('nearest_cross_check'):
            fixture=ROOT/'data/extraction-validation'/a.date/a.model/str(a.lead)/f'member-{member:02d}'
            fixture.parent.mkdir(parents=True,exist_ok=True)
            assert not fixture.with_suffix('.grib2').exists()
            fixture.with_suffix('.grib2').write_bytes(content)
            metadata['global_grib_retained']=True
            metadata['validation_grib_path']=str(fixture.with_suffix('.grib2').relative_to(ROOT))
            fixture.with_suffix('.json').write_text(json.dumps({**metadata,'selected_vector_path':str(target.relative_to(ROOT)),
                'purpose':'Offline decoder cross-validation only; outside selected-site values not analyzed'},indent=2)+'\n')
        temp=target.with_suffix('.tmp.npz')
        np.savez_compressed(temp,kelvin=v,metadata_json=json.dumps(metadata,sort_keys=True),grid_locations=grid)
        temp.rename(target)
        record={**metadata,'path':str(target.relative_to(ROOT)),'sha256':digest(target.read_bytes())}
        append(str(records.relative_to(ROOT)),record)
        values.append(v);all_metadata.append(metadata)
        print(json.dumps({'member':member,'cached':False,'observed_at_utc':now()}),flush=True)
    array=np.array(values).reshape(50,len(portfolios),12)
    target=folder/'temperatures.npz'
    if not target.exists():np.savez_compressed(target,kelvin=array,points=points,grid_locations=locations,members=np.arange(1,51),portfolios_json=json.dumps(portfolios))
    else:assert np.array_equal(np.load(target)['kelvin'],array)
    summary={'completed_at_utc':now(),'date':a.date,'model_requested':a.model,'lead':a.lead,'shape':list(array.shape),'units':'K','finite_values':int(np.isfinite(array).sum()),'measurements':str(records.relative_to(ROOT)),'selected_data_sha256':digest(target.read_bytes()),'index_sha256':digest(index_path.read_bytes()),'metadata':all_metadata}
    complete_path=folder/'complete.json'
    if complete_path.exists():
        previous=json.loads(complete_path.read_text())
        assert previous['selected_data_sha256']==summary['selected_data_sha256']
        summary=previous
    else:complete_path.write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='metadata'}),flush=True)

if __name__=='__main__':main()
