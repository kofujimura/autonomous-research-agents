"""Exploratory deterministic dispersed within-polygon samples, plan-v10."""
from pathlib import Path
import argparse,csv,hashlib,json,ssl,time,xml.etree.ElementTree as ET
import certifi,numpy as np,rasterio,shapely
from rasterio.windows import Window
from rasterio.transform import Affine
from records import ROOT,now,append
from fetch import fetch
from collect_embeddings import load,GDAL

def points(rid,outbase=None):
 original,info,fs,centres,geoms=load(rid);folder=(Path(outbase)/rid if outbase is not None else ROOT/'data/polygon'/rid);folder.mkdir(parents=True,exist_ok=True);assert not (folder/'points.npz').exists()
 inside=np.load(original/'aef-2024.npz')['inside'];flat=[];owners=[];offsets=[0];totals=[];examined=[]
 for i,(f,g) in enumerate(zip(fs,geoms)):
  seen=set();count=0;components=list(g.geoms) if g.geom_type=='MultiPolygon' else [g]
  for geom in components:
   x0,y0,x1,y1=geom.bounds;xs=np.arange(np.ceil((x0-5)/10),np.floor((x1-5)/10)+1,dtype=np.int64)*10+5;ys=np.arange(np.ceil((y0-5)/10),np.floor((y1-5)/10)+1,dtype=np.int64)*10+5
   if not len(xs) or not len(ys):continue
   strips=max(1,100000//len(xs))
   for start in range(0,len(ys),strips):
    xx,yy=np.meshgrid(xs,ys[start:start+strips]);xx=xx.ravel();yy=yy.ravel();mask=shapely.covers(geom,shapely.points(xx,yy));seen.update(zip(xx[mask].tolist(),yy[mask].tolist()));count+=len(xx)
  oid=f['properties']['objectid'];ranked=sorted((hashlib.sha256(f'free-research-018|polygon-pixel|{oid}|{x}|{y}'.encode()).digest(),x,y) for x,y in seen)[:256]
  assert len(ranked)>=int(inside[i].sum()),(rid,oid,len(ranked),inside[i].sum())
  chosen=[(x,y) for _,x,y in ranked];flat.extend(chosen);owners.extend([i]*len(chosen));offsets.append(len(flat));totals.append(len(seen));examined.append(count)
 path=folder/'points.npz';np.savez_compressed(path,xy=np.asarray(flat,dtype=np.float64),owners=np.asarray(owners),offsets=np.asarray(offsets),objectid=np.array([f['properties']['objectid'] for f in fs]),total_interior_pixels=np.asarray(totals),original_inside_n=inside.sum(axis=1),grid_cells_examined=np.asarray(examined))
 record=dict(region=rid,sampled_at_utc=now(),polygon_n=len(fs),sample_n=len(flat),total_interior_pixels=sum(totals),max_sample_per_polygon=256,ranking='SHA256 free-research-018|polygon-pixel|OBJECTID|integer_x|integer_y',source_selected_sha256=hashlib.sha256((original/'selected.geojson').read_bytes()).hexdigest(),path=str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),epsg=info['epsg'])
 (folder/'points-record.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)

def save(rid,product,raw,extra,record):
 folder=ROOT/'data/polygon'/rid;path=folder/f'{product}-2024.npz';assert not path.exists();np.savez_compressed(path,raw=raw,**extra);record.update(region=rid,product=product,year=2024,saved_at_utc=now(),path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),raw_sha256=hashlib.sha256(raw.tobytes()).hexdigest(),points_sha256=hashlib.sha256((folder/'points.npz').read_bytes()).hexdigest())
 (folder/f'{product}-2024-record.json').write_text(json.dumps(record,indent=2)+'\n');append('sources.jsonl',dict(source_id=f'{rid}-polygon-{product}-2024',**record,bundled=True,licence='AEF CC BY4.0' if product=='aef' else 'TESSERA permissive research reuse; attribution/share-alike preserved due conflicting licence statements'));print(json.dumps({k:v for k,v in record.items() if k not in ['reads','urls','coordinate_batches']}),flush=True)

def aef(rid):
 folder=ROOT/'data/polygon'/rid;p=np.load(folder/'points.npz');xy=p['xy'];_,info,_,_,_=load(rid);zone=info['epsg']-32600;bounds=[xy[:,0].min(),xy[:,1].min(),xy[:,0].max(),xy[:,1].max()];candidates=[]
 with (ROOT/'data/pilot/aef_index.csv').open() as stream:
  for row in csv.DictReader(stream):
   if int(row['year'])!=2024 or row['utm_zone']!=f'{zone}N':continue
   w,s,e,n=[float(row[k]) for k in ['utm_west','utm_south','utm_east','utm_north']]
   if e<bounds[0] or w>bounds[2] or n<bounds[1] or s>bounds[3]:continue
   ix=np.flatnonzero((xy[:,0]>=w)&(xy[:,0]<e)&(xy[:,1]>=s)&(xy[:,1]<n))
   if len(ix):candidates.append((row,ix))
 (folder/'aef-tiles.json').write_text(json.dumps([r for r,_ in candidates],indent=2)+'\n');raw=np.full((len(xy),64),-128,dtype=np.int8);done=np.zeros(len(xy),bool);reads=[]
 for k,(row,indices) in enumerate(candidates):
  indices=indices[~done[indices]]
  if not len(indices):continue
  url=row['path'].replace('s3://us-west-2.opendata.source.coop/','https://data.source.coop/');vrt=folder/f'aef-{k}-source.vrt'
  if not vrt.exists():
   if fetch(f'{rid}-polygon-aef-vrt-{k}',url.replace('.tiff','.vrt'),str(vrt.relative_to(ROOT)),licence='AEF CC BY4.0',timeout=90):raise RuntimeError('Provider VRT failure')
  expected=Affine.from_gdal(*[float(v) for v in ET.fromstring(vrt.read_text()).findtext('.//SrcGeoTransform').split(',')])
  with rasterio.Env(**GDAL),rasterio.open('/vsicurl/'+url) as src:
   assert src.crs.to_epsg()==info['epsg'] and src.count==64 and np.allclose(tuple(src.transform),tuple(expected),atol=1e-8)
   rr,cc=rasterio.transform.rowcol(src.transform,xy[indices,0],xy[indices,1]);rr=np.asarray(rr);cc=np.asarray(cc);xx,yy=rasterio.transform.xy(src.transform,rr,cc);assert np.allclose(np.column_stack([xx,yy]),xy[indices],atol=1e-6)
   r0=max(0,int(rr.min()));r1=min(src.height,int(rr.max())+1);c0=max(0,int(cc.min()));c1=min(src.width,int(cc.max())+1);stamp=now();arr=src.read(window=Window(c0,r0,c1-c0,r1-r0));raw[indices]=arr[:,rr-r0,cc-c0].T;done[indices]=True
   reads.append(dict(url=url,requested_at_utc=stamp,obtained_at_utc=now(),window=[c0,r0,c1-c0,r1-r0],transform=list(src.transform),source_window_sha256=hashlib.sha256(arr.tobytes()).hexdigest(),full_remote_object_sha256=None));del arr
 save(rid,'aef',raw,{},dict(reads=reads,unassigned=int((~done).sum()),decode='sign(q)*(q/127.5)^2; -128 missing'))

def tessera(rid):
 import zarr,aiohttp
 from zarr.storage import FsspecStore
 zarr.config.set({'async.concurrency':4,'threading.max_workers':4});folder=ROOT/'data/polygon'/rid;p=np.load(folder/'points.npz');xy=p['xy'];_,info,_,_,_=load(rid);zone=info['epsg']-32600;url=f'https://data.source.coop/tessera/tessera/zarr/v1.1-dclimate/utm{zone:02}'
 opts={'ssl':ssl.create_default_context(cafile=certifi.where()),'client_kwargs':{'timeout':aiohttp.ClientTimeout(total=120)}};group=zarr.open_group(store=FsspecStore.from_url(url,storage_options=opts,read_only=True),mode='r',use_consolidated=False);attrs=dict(group.attrs)
 (folder/'tessera-zone-metadata.json').write_text(json.dumps(attrs,indent=2)+'\n');assert attrs==json.loads((ROOT/f'data/main/{rid}/tessera-zone-metadata.json').read_text()),'Zone metadata changed from primary snapshot'
 gt=attrs['spatial:transform'];assert attrs['proj:code']==f"EPSG:{info['epsg']}" and gt[0]==10 and gt[4]==-10
 times=np.asarray(group['time'][:]);assert np.array_equal(times,np.load(ROOT/f'data/main/{rid}/tessera-time-coordinate.npy'));t=times.tolist().index(2024)
 rr=np.floor((gt[5]-xy[:,1])/10).astype(int);cc=np.floor((xy[:,0]-gt[2])/10).astype(int);assert np.allclose(np.column_stack([gt[2]+(cc+.5)*10,gt[5]-(rr+.5)*10]),xy,atol=1e-6)
 emb=group['embeddings'];sc=group['scales']
 for name,ar in [('embeddings',emb),('scales',sc)]:(folder/f'tessera-{name}-metadata.json').write_text(json.dumps(ar.metadata.to_dict(),indent=2,default=str)+'\n')
 raw=np.zeros((len(xy),128),dtype=np.int8);scales=np.full(len(xy),np.nan,dtype=np.float32);batches=[]
 for lo in range(0,len(xy),4096):
  hi=min(lo+4096,len(xy));n=hi-lo;stamp=now();values=emb.get_coordinate_selection((np.full(n*128,t),np.repeat(np.arange(128),n),np.tile(rr[lo:hi],128),np.tile(cc[lo:hi],128)));raw[lo:hi]=np.asarray(values,dtype=np.int8).reshape(128,n).T;scales[lo:hi]=sc.get_coordinate_selection((np.full(n,t),rr[lo:hi],cc[lo:hi]));batches.append(dict(start=lo,end=hi,requested_at_utc=stamp,obtained_at_utc=now()));print(json.dumps(dict(region=rid,product='tessera',points_done=hi,total=len(xy))),flush=True)
 save(rid,'tessera',raw,dict(scales=scales),dict(url=url,coordinate_batches=batches,time_index=t,decode='int8 * float32 scale; NaN scale missing',checkpoint='tessera_v1_1_aws_encoder.pt',primary_metadata_exactly_equal=True))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('product',choices=['points','aef','tessera']);p.add_argument('regions',nargs='+');p.add_argument('--output-base',type=Path);a=p.parse_args()
 for rid in a.regions:
  if a.product=='points':points(rid,a.output_base)
  else:
   assert a.output_base is None;globals()[a.product](rid)
