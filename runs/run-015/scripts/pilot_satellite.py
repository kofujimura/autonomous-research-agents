"""Small anonymous representation-access pilot; no ecological inference."""
import argparse
import json
import numpy as np
from geotessera import GeoTesseraZarr
import geotessera.store as ts
import zarr
from record import ROOT, now, append

p=argparse.ArgumentParser();p.add_argument('mode',choices=['cropland','forest']);args=p.parse_args()
ts.POINT_CONCURRENCY=2
zarr.config.set({'async.concurrency':2})
gt=GeoTesseraZarr()
if args.mode=='cropland':centre=(-93.5,40.5);years=[2022,2023]
else:centre=(-122.25,44.5);years=[2021,2023]
points=[(centre[0]+dx,centre[1]+dy) for dx in np.linspace(-.1,.1,5) for dy in np.linspace(-.1,.1,5)]
out=ROOT/'data/pilot'/args.mode;out.mkdir(parents=True,exist_ok=True)
arrays=[]
metadata={'mode':args.mode,'store':gt.url,'dataset':{'version':gt.dataset.version,'variant':gt.dataset.variant},'model_version':gt.model_version,'build_version':gt.build_version,'years_available':gt.years,'sample_years':years,'points_lon_lat':points,'metadata_read_at_utc':now(),'licence_note':'Model authors advertise CC0; AWS registry for dClimate layer says CC-BY-SA without version. Conservative share-alike attribution retained; no external distribution and no main endpoint inference.'}
for year in years:
    cached=out/'embeddings.npz'
    array=np.load(cached)['vectors'][years.index(year)] if cached.exists() else gt.sample_points(points,year=year)
    arrays.append(array)
    print(json.dumps({'year':year,'shape':list(array.shape),'finite_vectors':int(np.isfinite(array).all(axis=1).sum()),'observed_at_utc':now()}),flush=True)
data=np.stack(arrays)
if not (out/'embeddings.npz').exists():
    np.savez_compressed(out/'embeddings.npz',vectors=data,points=np.array(points),years=np.array(years))
else:metadata['numeric_data_reused']='existing pilot raw vectors; original acquisition times in P02-cropland/stdout.txt'
metadata.update(ended_read_at_utc=now(),shape=list(data.shape),finite_vectors_by_year=[int(np.isfinite(x).all(axis=1).sum()) for x in data],interpretation='Access and finiteness only. No abandonment, disturbance or recovery labels obtained.')
(out/'summary.json').write_text(json.dumps(metadata,indent=2)+'\n')
append('sources.jsonl',dict(source_id='PILOT-TESSERA-'+args.mode,url=gt.url,observed_at_utc=now(),metadata_read_at_utc=metadata['metadata_read_at_utc'],obtained_at_utc=None if 'numeric_data_reused' in metadata else metadata['metadata_read_at_utc'],path=str((out/'embeddings.npz').relative_to(ROOT)),licence=metadata['licence_note'],access_range='25 fixed sample points in two years; representation vectors only',numeric_data_reused=metadata.get('numeric_data_reused')))
print(json.dumps(metadata))
