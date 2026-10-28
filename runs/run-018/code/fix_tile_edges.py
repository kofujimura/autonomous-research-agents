"""Repair only verified geometrically-inside source-tile edge omissions."""
from pathlib import Path
import argparse,csv,hashlib,json
import numpy as np,rasterio
from rasterio.transform import Affine
from rasterio.windows import Window
from collect_embeddings import GDAL
from records import ROOT,now,append
from fetch import fetch

def fix(a):
 problems=json.loads(a.audit.read_text());assert problems and all(p['outside_centre_tile'] for p in problems);all_records=[]
 for rid in sorted(set(p['region'] for p in problems)):
  selected=[p for p in problems if p['region']==rid];source=ROOT/f'data/main/{rid}/aef-{a.year}.npz';old=np.load(source);arrays={k:old[k].copy() for k in old.files};ids=arrays['objectid'].tolist();indices=sorted(set(ids.index(p['objectid']) for p in selected));xy=arrays['xy'][indices].reshape(-1,2);info=json.loads((ROOT/f'data/main/{rid}/labels-record.json').read_text());zone=info['epsg']-32600;folder=ROOT/f'data/corrections/{rid}';folder.mkdir(parents=True,exist_ok=True);target=folder/f'aef-{a.year}.npz';assert not target.exists();raw=np.full((len(xy),64),-128,dtype=np.int8);done=np.zeros(len(xy),bool);reads=[]
  xmin,ymin=xy.min(axis=0);xmax,ymax=xy.max(axis=0);candidates=[]
  with (ROOT/'data/pilot/aef_index.csv').open() as stream:
   for row in csv.DictReader(stream):
    if int(row['year'])!=a.year or row['utm_zone']!=f'{zone}N':continue
    w,s,e,n=[float(row[k]) for k in ['utm_west','utm_south','utm_east','utm_north']]
    if e<xmin or w>xmax or n<ymin or s>ymax:continue
    ix=np.flatnonzero((xy[:,0]>=w)&(xy[:,0]<e)&(xy[:,1]>=s)&(xy[:,1]<n))
    if len(ix):candidates.append((row,ix))
  for ti,(row,ix) in enumerate(candidates):
   ix=ix[~done[ix]]
   if not len(ix):continue
   url=row['path'].replace('s3://us-west-2.opendata.source.coop/','https://data.source.coop/');vrt=folder/f'aef-{a.year}-{ti}-source.vrt'
   if not vrt.exists():
    if fetch(rid+f'-edge-vrt-{ti}',url.replace('.tiff','.vrt'),str(vrt.relative_to(ROOT)),licence='AEF CC BY4.0',timeout=90):raise RuntimeError('VRT fetch failure')
   with rasterio.Env(**GDAL),rasterio.open('/vsicurl/'+url) as src:
    assert src.crs.to_epsg()==info['epsg'] and src.count==64;rr,cc=rasterio.transform.rowcol(src.transform,xy[ix,0],xy[ix,1]);rr=np.asarray(rr);cc=np.asarray(cc);xx,yy=rasterio.transform.xy(src.transform,rr,cc);assert np.allclose(np.column_stack([xx,yy]),xy[ix],atol=1e-6);r0=int(rr.min());r1=int(rr.max())+1;c0=int(cc.min());c1=int(cc.max())+1;stamp=now();ar=src.read(window=Window(c0,r0,c1-c0,r1-r0));raw[ix]=ar[:,rr-r0,cc-c0].T;done[ix]=True;reads.append(dict(url=url,requested_at_utc=stamp,obtained_at_utc=now(),shape=list(src.shape),transform=list(src.transform),window=[c0,r0,c1-c0,r1-r0],source_window_sha256=hashlib.sha256(ar.tobytes()).hexdigest()));del ar
  assert done.all();fresh=raw.reshape(len(indices),9,64);old_selected=arrays['raw'][indices];valid=(old_selected!=-128).all(axis=2);assert np.array_equal(old_selected[valid],fresh[valid]),'A previously valid value changed';filled=[]
  for problem in selected:
   i=ids.index(problem['objectid']);j=problem['patch_index'];k=indices.index(i);assert arrays['inside'][i,j] and (arrays['raw'][i,j]==-128).all();assert (fresh[k,j]!=-128).all();arrays['raw'][i,j]=fresh[k,j];filled.append(problem)
  np.savez_compressed(target,**arrays);freshfile=folder/f'aef-{a.year}-fresh-edge-samples.npz';np.savez_compressed(freshfile,xy=xy,raw=raw,objectid=np.repeat(np.asarray(ids)[indices],9),patch_index=np.tile(np.arange(9),len(indices)))
  record=dict(region=rid,year=a.year,corrected_at_utc=now(),corrected_pixels=len(filled),affected_polygons=len(indices),previously_valid_pixels_checked=int(valid.sum()),previously_valid_values_exactly_equal=True,original_path=str(source.relative_to(ROOT)),original_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),corrected_path=str(target.relative_to(ROOT)),corrected_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),fresh_samples_path=str(freshfile.relative_to(ROOT)),fresh_samples_sha256=hashlib.sha256(freshfile.read_bytes()).hexdigest(),filled=filled,reads=reads)
  (folder/f'aef-{a.year}-correction-record.json').write_text(json.dumps(record,indent=2)+'\n');append('sources.jsonl',dict(source_id=f'{rid}-aef-{a.year}-edge-correction',**record,licence='AEF CC BY4.0',bundled=True));all_records.append(record);print(json.dumps({k:v for k,v in record.items() if k not in ['filled','reads']}),flush=True)
 a.output.write_text(json.dumps(all_records,indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--audit',type=Path,required=True);p.add_argument('--year',type=int,default=2024);p.add_argument('--output',type=Path,required=True);fix(p.parse_args())
