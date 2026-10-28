"""Second-dataset access component of the C3 pilot; no recovery test."""
import os,json,certifi
os.environ['SSL_CERT_FILE']=certifi.where()
from pathlib import Path
import numpy as np
import zarr
from geotessera import GeoTesseraZarr
from geotessera.registry import zarr_store_url
from record import ROOT,now

zarr.config.set({'async.concurrency':2})
dest=ROOT/'experiments/pilot-c3-tessera'
url=zarr_store_url('v1')
gt=GeoTesseraZarr(url,cache_dir=ROOT/'.cache/tessera-pilot',cache_max_size=64*1024**2)
coords=[(-119.6,37.7)]
values=np.stack([gt.sample_points(coords,year=y,progress=False,search_px=0) for y in [2017,2024]])
np.savez_compressed(dest/'vectors.npz',values=values,coords=coords,years=[2017,2024])
result=dict(checked_at_utc=now(),candidate='C3 second dataset',url=url,dataset=str(getattr(gt,'dataset',None)),
            shape=list(values.shape),finite_by_year=np.isfinite(values).all(axis=(1,2)).tolist(),
            norm_by_year=np.linalg.norm(values,axis=-1).tolist(),
            note='Access only; no cross-year recovery effect calculated; pilot coordinate excluded from main study')
(dest/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
