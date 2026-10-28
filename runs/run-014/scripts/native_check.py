"""Prespecified native/mosaic co-location check using ordinary public COG reads."""
import os
import certifi
os.environ['CURL_CA_BUNDLE']=certifi.where();os.environ['SSL_CERT_FILE']=certifi.where()
import argparse,hashlib,json,time
from pathlib import Path
import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import Window
from pyproj import Transformer,Geod
from shapely import from_wkb,Point
from prepare import digest
from features import unit
from record import ROOT,now,append

def prepare(dest=ROOT/'data/native-check'):
    dest.mkdir(parents=True,exist_ok=False)
    t=pd.concat([pd.read_csv(ROOT/'data/prepared/tasks.csv'),pd.read_csv(ROOT/'data/controls/tasks.csv')],ignore_index=True)
    t['selection_hash']=[digest(14014,'native_check',i) for i in t.task_id]
    sample=t.sort_values('selection_hash').groupby(['role','year']).head(8).sort_values('selection_hash').reset_index(drop=True)
    sample.to_csv(dest/'tasks.csv',index=False)
    print(json.dumps(dict(sample_point_years=len(sample),role_year_counts=sample.groupby(['role','year']).size().to_string())))

def retrieve(start,count,tasks=None):
    assert 1<=count<=64
    dest=ROOT/'data/native-check';t=pd.read_csv(tasks if tasks is not None else dest/'tasks.csv').iloc[start:start+count]
    index=pd.read_parquet(ROOT/'data/aef-native-index.parquet')
    history=ROOT/'data/native-check/retrievals.jsonl'
    old=[json.loads(s) for s in history.read_text().splitlines()] if history.exists() else []
    attempts={}
    for r in old:attempts[r['task_id']]=max(attempts.get(r['task_id'],0),r['attempt'])
    saved=0
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',GDAL_HTTP_TIMEOUT='30',GDAL_HTTP_MAX_RETRY='0',
                      GDAL_CACHEMAX=64*1024**2,CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tiff',
                      GDAL_HTTP_MULTIRANGE='SERIAL',GDAL_NUM_THREADS='1'):
        for q in t.itertuples():
            path=dest/f'{q.task_id}.npz'
            if path.exists():continue
            zone=f'{int(np.floor((q.x+180)/6))+1}'+('N' if q.y>=0 else 'S')
            possible=index[(index.year==q.year)&(index.wgs84_west<=q.x)&(index.wgs84_east>=q.x)
                           &(index.wgs84_south<=q.y)&(index.wgs84_north>=q.y)].copy()
            possible=possible.loc[np.array([from_wkb(g).covers(Point(q.x,q.y)) for g in possible.geom],dtype=bool)]
            possible['zone_preference']=possible.utm_zone!=zone
            possible=possible.sort_values(['zone_preference','path'])
            if not len(possible):
                append('data/native-check/retrievals.jsonl',dict(task_id=q.task_id,attempt=1,status='unavailable',error='No covering published index geometry',ended_at_utc=now()));continue
            src=possible.iloc[0];url=src.path.replace('gs://','https://storage.googleapis.com/',1)
            for attempt in range(attempts.get(q.task_id,0)+1,4):
                started=now();tick=time.monotonic()
                try:
                    with rasterio.open(url) as ds:
                        e,n=Transformer.from_crs('EPSG:4326',ds.crs,always_xy=True).transform(q.x,q.y)
                        row,col=ds.index(e,n);window=Window(col-1,row-1,3,3)
                        raw=ds.read(window=window,boundless=True,fill_value=-128).transpose(1,2,0)
                        assert raw.shape==(3,3,64) and raw.dtype==np.int8
                        cx,cy=ds.xy(row,col)
                        clon,clat=Transformer.from_crs(ds.crs,'EPSG:4326',always_xy=True).transform(cx,cy)
                        meta=dict(task_id=q.task_id,source_url=url,crs=str(ds.crs),transform=list(ds.window_transform(window)),
                                  lon=q.x,lat=q.y,year=int(q.year),role=q.role,pixel_centre_lon=clon,pixel_centre_lat=clat,
                                  requested_at_utc=started,obtained_at_utc=now(),licence='CC BY 4.0',
                                  rasterio_version=rasterio.__version__,gdal_version=rasterio.__gdal_version__)
                    tmp=path.with_suffix('.tmp.npz');np.savez_compressed(tmp,raw=raw,metadata=json.dumps(meta));tmp.replace(path)
                    rec=dict(task_id=q.task_id,attempt=attempt,status='saved',source_url=url,requested_at_utc=started,
                             ended_at_utc=now(),elapsed_seconds=time.monotonic()-tick,path=str(path.relative_to(ROOT)),
                             sha256=hashlib.sha256(path.read_bytes()).hexdigest(),error=None)
                    append('data/native-check/retrievals.jsonl',rec);print(json.dumps(rec),flush=True);saved+=1;break
                except Exception as e:
                    rec=dict(task_id=q.task_id,attempt=attempt,status='error',source_url=url,requested_at_utc=started,
                             ended_at_utc=now(),elapsed_seconds=time.monotonic()-tick,error=f'{type(e).__name__}: {e}')
                    append('data/native-check/retrievals.jsonl',rec);print(json.dumps(rec),flush=True)
                    if attempt<3:time.sleep(2**attempt)
    print(json.dumps(dict(start=start,count=count,saved=saved,ended_at_utc=now())),flush=True)

def analyse(output):
    output.mkdir(parents=True,exist_ok=False);tasks=pd.read_csv(ROOT/'data/native-check/tasks.csv');rows=[]
    geod=Geod(ellps='WGS84');hashes={}
    for t in tasks.itertuples():
        p=ROOT/f'data/native-check/{t.task_id}.npz';m=ROOT/f'data/embeddings/aef/{t.task_id}.npz'
        rec=dict(task_id=t.task_id,role=t.role,year=t.year,latitude=t.y,native_present=p.exists(),mosaic_present=m.exists())
        if p.exists() and m.exists():
            for source in [p,m]:hashes[str(source.relative_to(ROOT))]=hashlib.sha256(source.read_bytes()).hexdigest()
            with np.load(p,allow_pickle=False) as f:raw=f['raw'];meta=json.loads(str(f['metadata']))
            with np.load(m,allow_pickle=False) as f:mr=f['raw'];mm=json.loads(str(f['metadata']))
            def decode(x):
                a=x.astype(float);good=(x!=-128).all(-1);a=np.sign(a)*(a/127.5)**2;a[~good]=np.nan;return unit(a)
            a,b=decode(raw),decode(mr);centre=bool(np.isfinite(a[1,1]).all() and np.isfinite(b[1,1]).all())
            rec.update(centre_valid=centre,centre_cosine=float(a[1,1]@b[1,1]) if centre else None,
                       raw_centre_equal=bool(np.array_equal(raw[1,1],mr[1,1])) if centre else None,
                       patch_cosine=float(unit(a.mean((0,1)))@unit(b.mean((0,1)))) if np.isfinite(a).all() and np.isfinite(b).all() else None)
            from rasterio.transform import Affine
            mlon,mlat=Affine(*mm['transform'][:6])*(1.5,1.5)
            rec['pixel_centres_distance_m']=geod.inv(mlon,mlat,meta['pixel_centre_lon'],meta['pixel_centre_lat'])[2]
            rec['native_centre_to_requested_m']=geod.inv(t.x,t.y,meta['pixel_centre_lon'],meta['pixel_centre_lat'])[2]
        rows.append(rec)
    df=pd.DataFrame(rows)
    df['latitude_quartile']=pd.qcut(df.latitude,4,labels=False,duplicates='drop')
    df.to_csv(output/'comparisons.csv',index=False)
    summaries=[]
    groups=[('overall',df)]+[(f'role:{k}',v) for k,v in df.groupby('role')]+[(f'year:{k}',v) for k,v in df.groupby('year')]
    groups += [(f'latitude_quartile:{k}',v) for k,v in df.groupby('latitude_quartile')]
    for label,g in groups:
        for metric in ['centre_cosine','patch_cosine','pixel_centres_distance_m']:
            values=g[metric].dropna() if metric in g else pd.Series(dtype=float)
            summaries.append(dict(group=label,metric=metric,n=len(values),minimum=values.min() if len(values) else None,
                                  q05=values.quantile(.05) if len(values) else None,median=values.median() if len(values) else None,
                                  maximum=values.max() if len(values) else None))
    pd.DataFrame(summaries).to_csv(output/'summary.csv',index=False)
    (output/'input-sha256.json').write_text(json.dumps(hashes,sort_keys=True,indent=2)+'\n')
    print(pd.DataFrame(summaries).to_string(index=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','retrieve','analyse']);p.add_argument('--start',type=int,default=0)
    p.add_argument('--count',type=int,default=1);p.add_argument('--output',type=Path);p.add_argument('--tasks',type=Path);a=p.parse_args()
    if a.action=='prepare':prepare()
    elif a.action=='retrieve':retrieve(a.start,a.count,a.tasks)
    else:analyse(a.output)
