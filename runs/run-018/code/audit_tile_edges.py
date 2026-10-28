"""Find inside-polygon missing pixels and distinguish source-tile clipping."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
from rasterio.transform import Affine,rowcol
from records import ROOT,now
p=argparse.ArgumentParser();p.add_argument('--year',type=int,default=2024);p.add_argument('--pattern',default='[RS]??');p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);rows=[];sources={}
for folder in sorted((ROOT/'data/main').glob(a.pattern)):
 file=folder/f'aef-{a.year}.npz'
 if not file.exists():continue
 x=np.load(file);meta=folder/f'aef-{a.year}-record.json';all_reads=json.loads(meta.read_text())['reads'];reads=[];seen=set()
 # Main full-tile records cover every centre. Appended edge-window records may
 # omit full dimensions or repeat the same source tile; neither adds an owner.
 for item in all_reads:
  if 'shape' not in item:continue
  key=(item['url'],tuple(item['transform']),tuple(item['shape']))
  if key not in seen:reads.append(item);seen.add(key)
 bad=x['inside']&~(x['raw']!=-128).all(axis=2);sources[str(file.relative_to(ROOT))]=hashlib.sha256(file.read_bytes()).hexdigest();sources[str(meta.relative_to(ROOT))]=hashlib.sha256(meta.read_bytes()).hexdigest()
 for i,j in zip(*np.where(bad)):
  owners=[]
  for k,r in enumerate(reads):
   rr,cc=rowcol(Affine(*r['transform'][:6]),*x['xy'][i,4]);h,w=r['shape']
   if 0<=rr<h and 0<=cc<w:owners.append(k)
  outside=None
  if len(owners)==1:
   r=reads[owners[0]];rr,cc=rowcol(Affine(*r['transform'][:6]),*x['xy'][i,j]);h,w=r['shape'];outside=bool(not(0<=rr<h and 0<=cc<w))
  rows.append(dict(region=folder.name,objectid=int(x['objectid'][i]),patch_index=int(j),xy=x['xy'][i,j].tolist(),centre_owner_read_indices=owners,outside_centre_tile=outside))
(a.out/'missing-pixels.json').write_text(json.dumps(rows,indent=2)+'\n');edges=[v for v in rows if v['outside_centre_tile']];(a.out/'tile-edge-pixels.json').write_text(json.dumps(edges,indent=2)+'\n');record=dict(audited_at_utc=now(),year=a.year,pattern=a.pattern,missing_inside_pixels=len(rows),tile_edge_pixels=len(edges),affected_edge_polygons=len(set((v['region'],v['objectid']) for v in edges)),input_sha256=sources);(a.out/'record.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
