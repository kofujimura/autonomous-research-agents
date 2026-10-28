"""Ordinary anonymous data reads for the committed wetland protocol.

Each invocation is run through run_process.py (<= 30 minutes). Completed cores
are immutable and reusable. This script does not train or evaluate map models.
"""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import time
import os
import urllib.parse
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import from_origin
from rasterio.vrt import WarpedVRT
from shapely.geometry import shape, box
from records import ROOT, now, append
from web_record import fetch

FWS='https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer/0/query'
STAC='https://earth-search.aws.element84.com/v1/search'
BANDS=['blue','green','red','nir','rededge1','rededge2','swir16','swir22']
SEASONS=[('spring','2020-04-01T00:00:00Z','2020-05-31T23:59:59Z','2020-05-01T00:00:00Z'),
         ('summer','2020-06-01T00:00:00Z','2020-07-31T23:59:59Z','2020-07-01T00:00:00Z'),
         ('late','2020-08-01T00:00:00Z','2020-09-30T23:59:59Z','2020-09-01T00:00:00Z')]
GDAL=dict(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',GDAL_HTTP_TIMEOUT='45',
          GDAL_HTTP_CONNECTTIMEOUT='15',GDAL_HTTP_MAX_RETRY='1',
          GDAL_CACHEMAX=128*1024*1024,CPL_VSIL_CURL_CACHE_SIZE=128*1024*1024)

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def atomic_array(path,**arrays):
    temporary=path.with_name(path.stem+f'.partial-{os.getpid()}.npz')
    np.savez_compressed(temporary,**arrays)
    temporary.replace(path)

def json_read(url,path,sid,license,purpose):
    r=fetch(url,str(path.relative_to(ROOT)),sid,license,purpose)
    data=json.loads(path.read_text())
    if data.get('error'):raise RuntimeError(f'Public data endpoint error, saved in {path.relative_to(ROOT)}: {data["error"]}')
    return data

def record_array(path,url,details,license):
    append('sources.jsonl',dict(source_id='INPUT-'+path.parent.name+'-'+path.stem,
        url=url,path=str(path.relative_to(ROOT)),obtained_at_utc=now(),sha256=digest(path),
        license=license,retrieval='anonymous HTTPS COG range read; clipped/resampled input is bundled',
        full_remote_file_hash=None,hash_scope='retained clipped input; full remote COG not downloaded',
        details=details,bundled=True))

def read_warped(url,core,categorical=False):
    west,south,east,north=core['buffer_bounds']
    transform=from_origin(west,north,10,10)
    with rasterio.Env(**GDAL):
        with rasterio.open(url) as src:
            with WarpedVRT(src,crs=core['crs'],transform=transform,width=288,height=288,
                           resampling=Resampling.nearest if categorical else Resampling.bilinear,
                           src_nodata=0,nodata=0,dtype='uint8' if categorical else 'float32') as vrt:
                values=vrt.read(1)
    return values

def wetlands(core,directory):
    common=dict(geometry=','.join(map(str,core['wgs84_bounds'])),
                geometryType='esriGeometryEnvelope',inSR=4326,
                spatialRel='esriSpatialRelIntersects',where='1=1')
    params=dict(common,f='json',returnIdsOnly='true')
    ids_data=json_read(FWS+'?'+urllib.parse.urlencode(params),directory/'nwi-ids.json',
        'NWI-IDS-'+core['core_id'],'USFWS/NWI metadata: no access/use constraints; acknowledgement requested',
        'Complete reference IDs for buffered core')
    ids=ids_data.get('objectIds') or []
    if len(ids)!=len(set(ids)):raise RuntimeError('Duplicate reference IDs')
    obtained=[]
    for j in range(0,len(ids),500):
        params=dict(f='geojson',objectIds=','.join(map(str,ids[j:j+500])),outSR=4326,
                    outFields='OBJECTID,ATTRIBUTE,WETLAND_TYPE,ACRES',returnGeometry='true')
        path=directory/f'nwi-batch-{j//500:03d}.geojson'
        data=json_read(FWS+'?'+urllib.parse.urlencode(params),path,'NWI-'+core['core_id']+f'-{j//500:03d}',
            'USFWS/NWI: no use constraints; acknowledge source; map omissions/boundary error apply',
            'Complete public mapped-wetland reference, no personal attributes')
        if data.get('exceededTransferLimit'):raise RuntimeError('Reference response truncated')
        obtained.extend(int(x['properties']['OBJECTID']) for x in data.get('features',[]))
    if sorted(obtained)!=sorted(ids):raise RuntimeError('Reference IDs do not match completed geometry retrieval')
    print(core['core_id'],'complete NWI polygons',len(ids),flush=True)
    return len(ids)

def embedding(core,directory):
    path=directory/'embedding.npz'
    if path.exists():return
    west,south,east,north=core['buffer_bounds']
    with rasterio.Env(**GDAL):
        with rasterio.open(core['aef_url']) as src:
            if str(src.crs)!=core['crs']:raise RuntimeError('Unexpected embedding CRS')
            if src.transform.b!=0 or src.transform.d!=0:
                raise RuntimeError('Rotated embedding grid requires explicit review')
            # The public COGs may have increasing northing with image row.
            # Read the exact native cells, then flip axes without interpolation.
            corners=[(~src.transform)*(west,south),(~src.transform)*(east,north)]
            col0=min(x[0] for x in corners);row0=min(x[1] for x in corners)
            col1=max(x[0] for x in corners);row1=max(x[1] for x in corners)
            if any(abs(v-round(v))>1e-5 for v in [col0,row0,col1,row1]):
                raise RuntimeError('Target bounds are not aligned to native embedding cells')
            win=rasterio.windows.Window(round(col0),round(row0),round(col1-col0),round(row1-row0))
            values=src.read(window=win)
            native_transform=tuple(src.transform)[:6]
            if src.transform.e>0:values=values[:,::-1,:]
            if src.transform.a<0:values=values[:,:,::-1]
            transform=from_origin(west,north,10,10)
            if values.shape!=(64,288,288):raise RuntimeError(f'Unexpected embedding shape {values.shape}')
            if not np.allclose(tuple(transform)[:6],tuple(from_origin(west,north,10,10))[:6]):
                raise RuntimeError('Embedding grid alignment mismatch')
    atomic_array(path,values=values)
    record_array(path,core['aef_url'],dict(shape=list(values.shape),bounds=core['buffer_bounds'],
        crs=core['crs'],resolution_m=10,quantized=True,native_transform=native_transform,
        orientation='exact native cells, axis flip to north-up; no interpolation'),
        'CC BY 4.0; The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind.')
    print(core['core_id'],'embedding saved',path.stat().st_size,flush=True)

def choose_scenes(core,directory,season):
    name,start,end,mid=season
    params=dict(collections='sentinel-2-l2a',bbox=','.join(map(str,core['wgs84_bounds'])),
                datetime=start+'/'+end,limit=100)
    data=json_read(STAC+'?'+urllib.parse.urlencode(params),directory/f'stac-{name}.json',
        'STAC-'+core['core_id']+'-'+name,'Copernicus Sentinel free/full/open terms; AWS public access without account',
        'Source-scene selection by geometry/cloud metadata, before model outcomes')
    features=data.get('features',[])
    # Limit is enough for two months over one core in the normal two-satellite archive.
    # Preserve and flag any extra page rather than silently truncate available scenes.
    page=1
    for _ in range(5):
        nxt=next((x for x in data.get('links',[]) if x.get('rel')=='next'),None)
        if not nxt:break
        if nxt.get('method','GET')!='GET':raise RuntimeError('Unexpected POST pagination; stop for documented review')
        data=json_read(nxt['href'],directory/f'stac-{name}-page{page}.json',
            'STAC-'+core['core_id']+'-'+name+str(page),'Public Copernicus/STAC metadata',
            'Complete ordinary public STAC pagination')
        features.extend(data.get('features',[]));page+=1
    if any(x.get('rel')=='next' for x in data.get('links',[])):raise RuntimeError('STAC pagination bound reached')
    footprint=box(*core['wgs84_bounds'])
    midpoint=dt.datetime.fromisoformat(mid.replace('Z','+00:00'))
    qualified=[]
    for f in features:
        if not shape(f['geometry']).covers(footprint):continue
        if any(b not in f.get('assets',{}) for b in BANDS+['scl']):continue
        when=dt.datetime.fromisoformat(f['properties']['datetime'].replace('Z','+00:00'))
        qualified.append((float(f['properties'].get('eo:cloud_cover',100)),
                          abs((when-midpoint).total_seconds()),f['id'],f))
    qualified.sort(key=lambda x:x[:3])
    chosen=[];days=set()
    for _,_,_,f in qualified:
        day=f['properties']['datetime'][:10]
        if day in days:continue
        chosen.append(f);days.add(day)
        if len(chosen)==2:break
    (directory/f'scenes-{name}.json').write_text(json.dumps(chosen,indent=2)+'\n')
    return chosen

def optical(core,directory):
    for season in SEASONS:
        name=season[0]
        selected=directory/f'scenes-{name}.json'
        scenes=json.loads(selected.read_text()) if selected.exists() else choose_scenes(core,directory,season)
        print(core['core_id'],name,'scenes',[f['id'] for f in scenes],flush=True)
        for k,f in enumerate(scenes):
            path=directory/f'optical-{name}-{k}.npz'
            if path.exists():continue
            channels=[];scales=[];offsets=[];urls=[]
            for b in BANDS:
                asset=f['assets'][b];url=asset['href'];urls.append(url)
                values=read_warped(url,core)
                spec=(asset.get('raster:bands') or [{}])[0]
                scales.append(float(spec.get('scale',0.0001)))
                offsets.append(float(spec.get('offset',0.0)))
                channels.append(values)
                print(core['core_id'],name,k,b,flush=True)
            scl=read_warped(f['assets']['scl']['href'],core,categorical=True)
            atomic_array(path,dn=np.stack(channels),scl=scl,scale=np.array(scales),offset=np.array(offsets))
            record_array(path,urls,dict(scene_id=f['id'],datetime=f['properties']['datetime'],
                bands=BANDS,scale=scales,offset=offsets,shape=[8,288,288],
                source_processing=f['properties'],reprojection='bilinear float32 DN; nearest SCL',crs=core['crs']),
                'Contains modified Copernicus Sentinel data (2020); free/full/open Sentinel reuse terms')

def quality(core,directory):
    raw=np.load(directory/'embedding.npz')['values']
    embedding_valid=np.all(raw!=-128,axis=0)
    counts=[]
    for season in SEASONS:
        mask=np.zeros((288,288),dtype=bool)
        for p in directory.glob('optical-'+season[0]+'-*.npz'):
            a=np.load(p)
            mask|=np.isin(a['scl'],[2,4,5,6,7])&np.all(a['dn']>0,axis=0)
        counts.append(mask)
    season_count=np.sum(np.stack(counts),axis=0)
    core_slice=np.s_[16:272,16:272]
    frac=float(np.mean((embedding_valid&(season_count>=2))[core_slice]))
    return dict(common_valid_fraction=frac,seasonal_clear_fractions=[float(np.mean(m[core_slice])) for m in counts],
                technical_coverage_pass=frac>=.9,minimum_seasons=2,
                embedding_valid_fraction=float(np.mean(embedding_valid[core_slice])))

def run_core(core,region):
    directory=ROOT/'data/main/cores'/core['core_id'];directory.mkdir(parents=True,exist_ok=True)
    if (directory/'complete.json').exists():print(core['core_id'],'already complete',flush=True);return
    (directory/'core.json').write_text(json.dumps(dict(core=core,project=region['project']),indent=2)+'\n')
    started=now()
    try:
        n=wetlands(core,directory)
        embedding(core,directory)
        optical(core,directory)
        q=quality(core,directory)
        result=dict(core_id=core['core_id'],started_at_utc=started,ended_at_utc=now(),
            reference_polygons=n,quality=q,input_hashes={p.name:digest(p) for p in sorted(directory.iterdir())
                if p.is_file() and p.name not in ['complete.json','attempts.jsonl']})
        (directory/'complete.json').write_text(json.dumps(result,indent=2)+'\n')
        print(core['core_id'],'COMPLETE',json.dumps(q),flush=True)
    except Exception as exc:
        result=dict(started_at_utc=started,ended_at_utc=now(),status='failure',
                    error_type=type(exc).__name__,error=str(exc))
        with (directory/'attempts.jsonl').open('a') as out:out.write(json.dumps(result)+'\n')
        print(core['core_id'],'FAILED',type(exc).__name__,str(exc),flush=True)
        raise

def main():
    p=argparse.ArgumentParser();p.add_argument('--region',required=True);p.add_argument('--start',type=int,default=0)
    p.add_argument('--count',type=int,default=4);a=p.parse_args()
    selection=json.loads((ROOT/'data/main/core-selection.json').read_text())
    region=next(r for r in selection['regions'] if r['region_id']==a.region)
    cores=region['cores'][a.start:a.start+a.count]
    for c in cores:
        size=sum(x.stat().st_size for x in ROOT.rglob('*') if x.is_file() and not x.is_symlink())
        if size>=8*1024**3:raise RuntimeError('8 GiB retrieval stop threshold reached')
        run_core(c,region)

if __name__=='__main__':main()
