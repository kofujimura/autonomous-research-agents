"""V15 transport check, not a representation-performance experiment."""
import os
import certifi
os.environ['SSL_CERT_FILE']=certifi.where()
import argparse,hashlib,json,time
from pathlib import Path
import numpy as np
import pandas as pd
import geotessera.store as tessera_store
from geotessera import GeoTesseraZarr
from geotessera.registry import zarr_store_url
from record import ROOT,now

def check(output):
    output=output.resolve();output.relative_to(ROOT)
    output.mkdir(parents=True,exist_ok=False)
    tasks=pd.read_csv(ROOT/'data/controls/tasks.csv').query('batch==0').head(3)
    history={}
    for line in (ROOT/'data/tessera-retrievals.jsonl').read_text().splitlines():
        r=json.loads(line)
        if r['status']=='saved':history[r['task_id']]=r
    tessera_store.POINT_CONCURRENCY=2
    gt=GeoTesseraZarr(zarr_store_url('v1'),cache_dir=ROOT/'.cache/tessera-gateway-v15',
                     cache_max_size=128*1024**2,via_gateway=True)
    rows=[];hashes={}
    for t in tasks.itertuples():
        expected=ROOT/f'data/embeddings/tessera/{t.task_id}.npz'
        hashes[str(expected.relative_to(ROOT))]=hashlib.sha256(expected.read_bytes()).hexdigest()
        start=now();tick=time.monotonic();raw=None
        try:
            raw,transform,crs=gt.read_patch(float(t.x),float(t.y),year=int(t.year),size_px=3)
            elapsed=time.monotonic()-tick
            with np.load(expected,allow_pickle=False) as f:old=f['raw']
            equal=raw.dtype==old.dtype and np.array_equal(raw,old,equal_nan=True)
            path=output/f'{t.task_id}.npz'
            metadata=dict(source_url=zarr_store_url('v1'),access_route='documented gateway',dataset=str(gt.dataset),
                point_id=t.point_id,lon=float(t.x),lat=float(t.y),year=int(t.year),transform=list(transform),crs=str(crs),
                requested_at_utc=start,obtained_at_utc=now(),licence='CC0')
            np.savez_compressed(path,raw=raw,metadata=json.dumps(metadata))
            rec=dict(task_id=t.task_id,status='saved',equal=equal,requested_at_utc=start,ended_at_utc=now(),
                gateway_elapsed_seconds=elapsed,default_historical_elapsed_seconds=history[t.task_id]['elapsed_seconds'],
                path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),error=None)
        except Exception as e:
            if raw is not None:np.savez_compressed(output/f'{t.task_id}-failed.npz',raw=raw)
            rec=dict(task_id=t.task_id,status='error',equal=False,requested_at_utc=start,ended_at_utc=now(),
                gateway_elapsed_seconds=time.monotonic()-tick,default_historical_elapsed_seconds=history[t.task_id]['elapsed_seconds'],
                path=None,sha256=None,error=f'{type(e).__name__}: {e}')
        rows.append(rec);print(json.dumps(rec),flush=True)
        (output/'queries.json').write_text(json.dumps(rows,indent=2)+'\n')
    agreed=len(rows)==3 and all(r['equal'] for r in rows)
    median_new=float(np.median([r['gateway_elapsed_seconds'] for r in rows]))
    median_old=float(np.median([r['default_historical_elapsed_seconds'] for r in rows]))
    summary=dict(checked_at_utc=now(),same_raw_arrays=agreed,gateway_median_seconds=median_new,
        historical_default_median_seconds=median_old,switch_to_gateway=agreed and median_new<=.75*median_old,
        timing_caveat='Historical times are confounded by date, network and caches; no causal speed claim.')
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (output/'input-sha256.json').write_text(json.dumps(hashes,sort_keys=True,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();check(a.output)
