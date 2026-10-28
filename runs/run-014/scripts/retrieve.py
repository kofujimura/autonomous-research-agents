"""Bounded public embedding patch retrieval. No AI inference or API credentials."""
import os
import certifi
os.environ['SSL_CERT_FILE']=certifi.where()
os.environ.setdefault('OMP_NUM_THREADS','1')
import argparse, hashlib, json, time
from pathlib import Path
import numpy as np
import pandas as pd
import zarr
from rasterio.transform import Affine
from record import ROOT, now, append

zarr.config.set({'async.concurrency':2})
AEF='https://data.source.coop/tge-labs/aef-mosaic/'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('model',choices=['aef','tessera']);ap.add_argument('batch',type=int)
    ap.add_argument('--tasks',type=Path,default=ROOT/'data/prepared/tasks.csv')
    ap.add_argument('--batch-count',type=int,default=1)
    ap.add_argument('--repair-metadata-failures',action='store_true')
    ap.add_argument('--via-gateway',action='store_true')
    a=ap.parse_args();assert 1<=a.batch_count<=4
    a.tasks=a.tasks.resolve()
    task_source=str(a.tasks.relative_to(ROOT)) # Validate before making any public requests.
    alltasks=pd.read_csv(a.tasks);tasks=alltasks[alltasks.batch.between(a.batch,a.batch+a.batch_count-1)]
    if not len(tasks):raise ValueError('Empty batch')
    dest=ROOT/'data/embeddings'/a.model; dest.mkdir(parents=True,exist_ok=True)
    history=ROOT/f'data/{a.model}-retrievals.jsonl'
    old=[json.loads(x) for x in history.read_text().splitlines()] if history.exists() else []
    attempts={}
    for row in old:attempts[row['task_id']]=max(attempts.get(row['task_id'],0),row['attempt'])
    software_failed={r['task_id'] for r in old if r.get('status')=='error' and
                     "is not in the subpath" in (r.get('error') or '')}
    if a.model=='aef':
        group=zarr.open_group(AEF,mode='r',use_consolidated=False)
        array=group['embeddings']; transform=Affine(*group.attrs['spatial:transform'])
        source=AEF; dataset='AlphaEarth Foundations V1, unofficial geographic mosaic'
    else:
        from geotessera import GeoTesseraZarr
        import geotessera.store as tessera_store
        tessera_store.POINT_CONCURRENCY=2
        from geotessera.registry import zarr_store_url
        source=zarr_store_url('v1')
        gt=GeoTesseraZarr(source,cache_dir=ROOT/'.cache/tessera-main',cache_max_size=128*1024**2,via_gateway=a.via_gateway)
        dataset=str(gt.dataset)
    succeeded=failed=skipped=0
    for t in tasks.itertuples():
        path=dest/f'{t.task_id}.npz'
        if path.exists():skipped+=1;continue
        success=False
        first_attempt=attempts.get(t.task_id,0)+1
        repairing=a.repair_metadata_failures and t.task_id in software_failed
        limit=first_attempt if repairing and first_attempt<=4 else 3
        for attempt in range(first_attempt,limit+1):
            started=now(); tick=time.monotonic();raw=None
            try:
                if a.model=='aef':
                    colf,rowf=(~transform)*(t.x,t.y); row=int(np.floor(rowf));col=int(np.floor(colf))
                    raw=np.asarray(array[t.year-2017,:,row-1:row+2,col-1:col+2]).transpose(1,2,0)
                    tr=transform*Affine.translation(col-1,row-1);crs='EPSG:4326'
                    assert raw.shape==(3,3,64) and raw.dtype==np.int8
                else:
                    raw,tr,crs=gt.read_patch(float(t.x),float(t.y),year=int(t.year),size_px=3)
                    assert raw.shape==(3,3,128)
                metadata=dict(task_id=t.task_id,model=a.model,source_url=source,dataset=dataset,
                              point_id=t.point_id,lon=t.x,lat=t.y,year=int(t.year),task_source=task_source,
                              requested_at_utc=started,obtained_at_utc=now(),transform=list(tr),crs=str(crs),
                              licence='CC BY 4.0' if a.model=='aef' else 'CC0',zarr_version=zarr.__version__)
                if a.model=='tessera':metadata['access_route']='documented gateway' if a.via_gateway else 'default direct public mirror'
                temp=path.with_suffix('.tmp.npz')
                np.savez_compressed(temp,raw=raw,metadata=json.dumps(metadata));temp.replace(path)
                sha=hashlib.sha256(path.read_bytes()).hexdigest()
                rec=dict(task_id=t.task_id,model=a.model,batch=int(t.batch),attempt=attempt,requested_at_utc=started,
                         ended_at_utc=now(),elapsed_seconds=time.monotonic()-tick,status='saved',
                         path=str(path.relative_to(ROOT)),sha256=sha,bytes=path.stat().st_size,error=None)
                append(f'data/{a.model}-retrievals.jsonl',rec)
                print(json.dumps(rec),flush=True);succeeded+=1;success=True;break
            except Exception as e:
                failure_path=None;failure_sha=None
                if raw is not None:
                    failure=ROOT/'data/retrieval-failures'/a.model/f'{t.task_id}-attempt{attempt}.npz'
                    failure.parent.mkdir(parents=True,exist_ok=True)
                    np.savez_compressed(failure,raw=raw)
                    failure_path=str(failure.relative_to(ROOT));failure_sha=hashlib.sha256(failure.read_bytes()).hexdigest()
                rec=dict(task_id=t.task_id,model=a.model,batch=int(t.batch),attempt=attempt,requested_at_utc=started,
                         ended_at_utc=now(),elapsed_seconds=time.monotonic()-tick,status='error',
                         path=None,sha256=None,bytes=None,error=f'{type(e).__name__}: {e}',
                         raw_failure_path=failure_path,raw_failure_sha256=failure_sha,
                         metadata_repair=bool(repairing))
                append(f'data/{a.model}-retrievals.jsonl',rec);print(json.dumps(rec),flush=True)
                if attempt<limit:time.sleep(min(8,2**attempt))
        if not success:failed+=1
    print(json.dumps(dict(model=a.model,first_batch=a.batch,batch_count=a.batch_count,saved=succeeded,failed=failed,existing=skipped,
                          checked_at_utc=now())),flush=True)

if __name__=='__main__':main()
