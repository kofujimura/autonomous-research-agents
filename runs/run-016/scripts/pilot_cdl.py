import json
from pathlib import Path
import icechunk,xarray as xr,numpy as np
from pyproj import Transformer
from records import ROOT,now,digest

d=ROOT/'experiments/P02b-cdl';d.mkdir(parents=True,exist_ok=True)
start=now()
storage=icechunk.s3_storage(bucket='chill',prefix='usda-cropland-data-layer/v0.1.0.icechunk',
 endpoint_url='https://data.source.coop',region='us-east-1',anonymous=True,force_path_style=True)
repo=icechunk.Repository.open(storage);session=repo.readonly_session('main')
ds=xr.open_zarr(session.store,group='30m',chunks=None)
x,y=Transformer.from_crs(4326,5070,always_xy=True).transform(-93.5,42.0)
a=ds['crop_type'].sel(year=[2020,2021],x=slice(x-5000,x+5000),y=slice(y+5000,y-5000)).load()
np.savez_compressed(d/'crop-labels.npz',labels=a.values,x=a.x.values,y=a.y.values,year=a.year.values)
vals,counts=np.unique(a.values,return_counts=True)
stats=dict(started_at_utc=start,ended_at_utc=now(),snapshot_id=str(session.snapshot_id),shape=list(a.shape),
 classes={str(int(v)):int(n) for v,n in zip(vals,counts)},source='https://data.source.coop/chill/usda-cropland-data-layer/v0.1.0.icechunk',
 license='USDA NASS CDL public domain, checked official FAQ; mirror provenance in group attributes',
 output_sha256=digest(d/'crop-labels.npz'),attrs=dict(ds.attrs))
(d/'result.json').write_text(json.dumps(stats,indent=2,default=str)+'\n');print(json.dumps({k:v for k,v in stats.items() if k!='attrs'}),flush=True)
