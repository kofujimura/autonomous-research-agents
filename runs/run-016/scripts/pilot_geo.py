from pathlib import Path
import json,sys,time
import numpy as np
from geotessera import GeoTesseraZarr
from records import ROOT,now,digest

d=ROOT/'experiments/P02-geo';d.mkdir(parents=True,exist_ok=True)
start=now()
gt=GeoTesseraZarr(cache_dir=ROOT/'.cache/tessera',cache_max_size=256*1024**2)
print('STORE',gt.url,'YEARS',gt.years,'DATASET',gt.dataset,'MODEL',gt.model_version,flush=True)
patch,transform,crs=gt.read_patch(-93.5,42.0,year=2021,size_px=256)
np.save(d/'embedding.npy',patch)
stats=dict(pilot_id='P02',started_at_utc=start,ended_at_utc=now(),store_url=gt.url,
           model_version=gt.model_version,dataset=str(gt.dataset),year=2021,
           center_lon=-93.5,center_lat=42.,shape=list(patch.shape),crs=str(crs),
           transform=list(transform),finite_fraction=float(np.isfinite(patch).mean()),
           sha256=digest(d/'embedding.npy'),inference='none; published embedding data')
(d/'result.json').write_text(json.dumps(stats,indent=2)+'\n');print(json.dumps(stats),flush=True)
