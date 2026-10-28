"""Extract exact raw 3x3 embedding patches; no outcome-dependent site choice."""
from pathlib import Path
import argparse,csv,hashlib,json,os,ssl,subprocess,time,traceback
from urllib.parse import urlencode
import certifi,numpy as np,rasterio
from rasterio.windows import Window
from pyproj import Transformer
from shapely.geometry import shape,Point
from shapely.ops import transform
from records import ROOT,now,append
from fetch import fetch

GDAL=dict(GDAL_HTTP_TIMEOUT='90',GDAL_HTTP_MAX_RETRY='1',CURL_CA_BUNDLE=certifi.where(),GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',GDAL_CACHEMAX=128000000,VSI_CACHE=False)

def load(rid):
 folder=ROOT/'data/main'/rid
 info=json.loads((folder/'labels-record.json').read_text())
 fs=json.loads((folder/'selected.geojson').read_text())['features']
 points=np.array([[f['properties']['x'],f['properties']['y']] for f in fs])
 forward=Transformer.from_crs(4326,info['epsg'],always_xy=True).transform
 geoms=[transform(forward,shape(f['geometry'])) for f in fs]
 return folder,info,fs,points,geoms

def masks(geoms,xy):
 return np.array([[g.covers(Point(*p)) for p in pp] for g,pp in zip(geoms,xy)],dtype=bool)

def save(folder,name,raw,xy,inside,extra,meta):
 path=folder/(name+'.npz')
 assert not path.exists(),'Preserve existing raw measurement; select only an uncompleted acquisition'
 np.savez_compressed(path,raw=raw,xy=xy,inside=inside,**extra)
 meta.update(saved_at_utc=now(),path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size,raw_sha256=hashlib.sha256(raw.tobytes()).hexdigest())
 (folder/(name+'-record.json')).write_text(json.dumps(meta,indent=2)+'\n')
 append('sources.jsonl',dict(source_id=name+'-'+folder.name,**meta,bundled=True,licence='AEF CC BY4.0' if name.startswith('aef') else 'TESSERA permissive research reuse; preserve attribution/share-alike due conflicting statements'))
 print(json.dumps(dict(region=folder.name,product=name,shape=list(raw.shape),bytes=path.stat().st_size,saved_at_utc=meta['saved_at_utc'])),flush=True)

def aef(rid,year,use_native=True,suffix=""):
 import xml.etree.ElementTree as ET
 from rasterio.transform import Affine,rowcol
 base=f"aef-{year}{suffix}"
 folder,info,fs,points,geoms=load(rid)
 assert not (folder/(base+'.npz')).exists(),'Raw patch already archived'
 if not fs:raise RuntimeError('No selected polygons')
 zone=info['epsg']-32600
 candidates=[]
 with (ROOT/'data/pilot/aef_index.csv').open() as stream:
  for row in csv.DictReader(stream):
   if int(row['year'])!=year or row['utm_zone']!=f'{zone}N':continue
   w,s,e,n=[float(row[k]) for k in ['utm_west','utm_south','utm_east','utm_north']]
   ind=np.flatnonzero((points[:,0]>=w)&(points[:,0]<e)&(points[:,1]>=s)&(points[:,1]<n))
   if len(ind):candidates.append((row,ind))
 (folder/f'{base}-tiles.json').write_text(json.dumps([x[0] for x in candidates],indent=2)+'\n')
 raw=np.full((len(fs),9,64),-128,dtype=np.int8);xy=np.full((len(fs),9,2),np.nan)
 done=np.zeros(len(fs),bool);reads=[];tile_edge=np.zeros((len(fs),9),bool)
 for ti,(row,indices) in enumerate(candidates):
  indices=indices[~done[indices]]
  if not len(indices):continue
  source=row['path'].replace('s3://us-west-2.opendata.source.coop/','https://data.source.coop/')
  vrturl=source.replace('.tiff','.vrt');vrtfile=folder/f'{base}-{ti}-source.vrt'
  if fetch(f'{rid}-aef-{year}-vrt{ti}',vrturl,str(vrtfile.relative_to(ROOT)),licence='CC BY4.0 AEF',timeout=90):raise RuntimeError('Provider VRT fetch failed')
  vrt=vrtfile.read_text().replace('/vsis3/us-west-2.opendata.source.coop/','/vsicurl/https://data.source.coop/')
  local=folder/f'{base}-{ti}-https.vrt';local.write_text(vrt)
  with rasterio.Env(**GDAL):
   with rasterio.open('/vsicurl/'+source if use_native else local) as src:
    assert src.count==64 and src.crs.to_epsg()==info['epsg']
    provider_gt=Affine.from_gdal(*[float(v) for v in ET.fromstring(vrt).findtext('GeoTransform').split(',')])
    assert provider_gt.e<0
    if use_native:
     expected_src=Affine.from_gdal(*[float(v) for v in ET.fromstring(vrt).findtext('.//SrcGeoTransform').split(',')])
     assert np.allclose(tuple(src.transform),tuple(expected_src),atol=1e-8)
    # Choose the provider VRT's pixel even for a point exactly on a pixel edge.
    vrt_rc=[rowcol(provider_gt,*points[i]) for i in indices]
    centres=[provider_gt*(cc+.5,rr+.5) for rr,cc in vrt_rc]
    rc=np.array([src.index(*point) for point in centres]);r0=max(0,int(rc[:,0].min())-1);r1=min(src.height,int(rc[:,0].max())+2);c0=max(0,int(rc[:,1].min())-1);c1=min(src.width,int(rc[:,1].max())+2)
    stamp=now();arr=src.read(window=Window(c0,r0,c1-c0,r1-r0))
    for i,(r,c) in zip(indices,rc):
     for k,(dr,dc) in enumerate(( (dr,dc) for dr in [-1,0,1] for dc in [-1,0,1])):
      rr,cc=r+(-dr if src.transform.e>0 else dr),c+dc;xy[i,k]=src.xy(rr,cc)
      if r0<=rr<r1 and c0<=cc<c1:raw[i,k]=arr[:,rr-r0,cc-c0]
      if not (0<=rr<src.height and 0<=cc<src.width):tile_edge[i,k]=True
     done[i]=True
    reads.append(dict(url=source,native_transport=use_native,provider_transform=list(provider_gt),requested_at_utc=stamp,obtained_at_utc=now(),window=[c0,r0,c1-c0,r1-r0],transform=list(src.transform),shape=list(src.shape),source_window_sha256=hashlib.sha256(arr.tobytes()).hexdigest(),full_remote_object_sha256=None))
    del arr
 inside=masks(geoms,xy)
 # Neighbouring native tiles own patch pixels beyond a centre tile's bounds.
 # Fill only these omissions, preserving all values read above and genuine nodata.
 edge_locations=np.argwhere(tile_edge&inside&(raw==-128).all(axis=2));edge_done=np.zeros(len(edge_locations),bool);edge_reads=[]
 if len(edge_locations):
  edge_xy=np.asarray([xy[i,j] for i,j in edge_locations]);edge_tiles=[]
  with (ROOT/'data/pilot/aef_index.csv').open() as stream:
   for row in csv.DictReader(stream):
    if int(row['year'])!=year or row['utm_zone']!=f'{zone}N':continue
    w,s,e,n=[float(row[k]) for k in ['utm_west','utm_south','utm_east','utm_north']]
    indices=np.flatnonzero((edge_xy[:,0]>=w)&(edge_xy[:,0]<e)&(edge_xy[:,1]>=s)&(edge_xy[:,1]<n))
    if len(indices):edge_tiles.append((row,indices))
  for ti,(row,indices) in enumerate(edge_tiles):
   indices=indices[~edge_done[indices]]
   if not len(indices):continue
   source=row['path'].replace('s3://us-west-2.opendata.source.coop/','https://data.source.coop/');vrtfile=folder/f'{base}-edge-{ti}-source.vrt'
   if fetch(f'{rid}-aef-{year}-edge-vrt{ti}',source.replace('.tiff','.vrt'),str(vrtfile.relative_to(ROOT)),licence='CC BY4.0 AEF',timeout=90):raise RuntimeError('Edge provider VRT fetch failed')
   expected=Affine.from_gdal(*[float(v) for v in ET.fromstring(vrtfile.read_text()).findtext('.//SrcGeoTransform').split(',')])
   with rasterio.Env(**GDAL),rasterio.open('/vsicurl/'+source) as src:
    assert src.count==64 and src.crs.to_epsg()==info['epsg'] and np.allclose(tuple(src.transform),tuple(expected),atol=1e-8)
    rr,cc=rowcol(src.transform,edge_xy[indices,0],edge_xy[indices,1]);rr=np.asarray(rr);cc=np.asarray(cc);xx,yy=rasterio.transform.xy(src.transform,rr,cc);assert np.allclose(np.column_stack([xx,yy]),edge_xy[indices],atol=1e-6)
    assert (rr>=0).all() and (rr<src.height).all() and (cc>=0).all() and (cc<src.width).all()
    r0=int(rr.min());r1=int(rr.max())+1;c0=int(cc.min());c1=int(cc.max())+1;stamp=now();arr=src.read(window=Window(c0,r0,c1-c0,r1-r0));values=arr[:,rr-r0,cc-c0].T
    for k,value in zip(indices,values):i,j=edge_locations[k];assert (raw[i,j]==-128).all();raw[i,j]=value
    edge_done[indices]=True;edge_reads.append(dict(url=source,requested_at_utc=stamp,obtained_at_utc=now(),window=[c0,r0,c1-c0,r1-r0],transform=list(src.transform),source_window_sha256=hashlib.sha256(arr.tobytes()).hexdigest()));del arr
  assert edge_done.all(),'An inside patch pixel had no adjacent source tile'
 reads.extend(edge_reads)
 save(folder,base,raw,xy,inside,dict(objectid=np.array([f['properties']['objectid'] for f in fs])),dict(url=[r['url'] for r in reads],reads=reads,unassigned=int((~done).sum()),edge_pixels_checked=len(edge_locations),edge_pixels_recovered=int(sum((raw[i,j]!=-128).all() for i,j in edge_locations)),decode='sign(q)*(q/127.5)^2; q=-128 missing',sample='3x3 native pixel centres; inside polygon mask; adjacent-tile ownership filled',year=year,epsg=info['epsg'],full_remote_object_sha256=None))

def tessera(rid,year):
 import zarr,aiohttp
 from zarr.storage import FsspecStore
 zarr.config.set({'async.concurrency':4,'threading.max_workers':4})
 folder,info,fs,points,geoms=load(rid)
 assert not (folder/f'tessera-{year}.npz').exists(),'Raw patch already archived'
 if not fs:raise RuntimeError('No selected polygons')
 zone=info['epsg']-32600
 url=f'https://data.source.coop/tessera/tessera/zarr/v1.1-dclimate/utm{zone:02}'
 opts={'ssl':ssl.create_default_context(cafile=certifi.where()),'client_kwargs':{'timeout':aiohttp.ClientTimeout(total=120)}}
 store=FsspecStore.from_url(url,storage_options=opts,read_only=True)
 group=zarr.open_group(store=store,mode='r',use_consolidated=False)
 meta_prefix='tessera' if year==2024 else f'tessera-{year}'
 attrs=dict(group.attrs);(folder/f'{meta_prefix}-zone-metadata.json').write_text(json.dumps(attrs,indent=2)+'\n')
 if year!=2024 and (folder/'tessera-zone-metadata.json').exists():assert attrs==json.loads((folder/'tessera-zone-metadata.json').read_text()),'Alternate-year zone metadata differ from primary product snapshot'
 transform_=attrs['spatial:transform'];assert transform_[0]==10 and transform_[4]==-10
 assert attrs['proj:code']==f"EPSG:{info['epsg']}"
 source_group=attrs.get('geotessera:source_groups',{}).get(f'{zone:02}N',attrs.get('geotessera:source_groups',{}).get(f'{zone}N',{}))
 complete_years=source_group.get('years_complete',attrs.get('years_complete'))
 if complete_years is not None and year not in [int(v) for v in complete_years]:raise RuntimeError(f'Year{year} is not declared complete for nominal north zone')
 # Plain consolidated-zone migration has 2017..2025 slots. Preserve the coordinate array.
 years=np.asarray(group['time'][:]);np.save(folder/f'{meta_prefix}-time-coordinate.npy',years)
 yearints=[]
 for value in years:
  if 1900<=int(value)<=2100:yearints.append(int(value))
  else:
   units=dict(group['time'].attrs).get('units','')
   if 'days since 1970' in units:yearints.append(int(str(np.datetime64('1970-01-01')+np.timedelta64(int(value),'D'))[:4]))
   elif np.issubdtype(years.dtype,np.datetime64):yearints.append(int(str(value)[:4]))
   else:raise RuntimeError(f'Unrecognized time coordinate {years.dtype}, units {units}')
 assert len(set(yearints))==len(yearints)
 t=yearints.index(year)
 c=np.floor((points[:,0]-transform_[2])/10).astype(int);r=np.floor((transform_[5]-points[:,1])/10).astype(int)
 offsets=np.array([(dr,dc) for dr in [-1,0,1] for dc in [-1,0,1]])
 rr=(r[:,None]+offsets[:,0]).ravel();cc=(c[:,None]+offsets[:,1]).ravel()
 xy=np.stack([transform_[2]+(cc+.5)*10,transform_[5]-(rr+.5)*10],axis=-1).reshape(len(fs),9,2)
 # Coordinate selection reads only chunks touched by the sample, grouped internally by Zarr.
 emb=group['embeddings'];sc=group['scales']
 for name,ar in [('embeddings',emb),('scales',sc)]:
  (folder/f'{meta_prefix}-{name}-metadata.json').write_text(json.dumps(ar.metadata.to_dict(),indent=2,default=str)+'\n')
 stamp=now();n=len(rr)
 # Band-major broadcast coordinate arrays, flattened for Zarr's point selection.
 values=emb.get_coordinate_selection((np.full(n*128,t),np.repeat(np.arange(128),n),np.tile(rr,128),np.tile(cc,128)))
 raw=np.asarray(values,dtype=np.int8).reshape(128,len(fs),9).transpose(1,2,0)
 scales=np.asarray(sc.get_coordinate_selection((np.full(n,t),rr,cc))).reshape(len(fs),9)
 inside=masks(geoms,xy)
 extras=dict(scales=scales,objectid=np.array([f['properties']['objectid'] for f in fs]))
 # Observation counts diagnose imagery availability without setting outcome-based thresholds.
 obs_errors={}
 for name in ['s2_obs_count','s1_asc_obs_count','s1_desc_obs_count']:
  try:extras[name]=np.asarray(group[name].get_coordinate_selection((np.full(n,t),rr,cc))).reshape(len(fs),9)
  except Exception as e:obs_errors[name]=str(e)
 save(folder,f'tessera-{year}',raw,xy,inside,extras,dict(url=url,requested_at_utc=stamp,obtained_at_utc=now(),time_index=t,time_coordinate=yearints,decode='int8 * per-pixel float32 scale; NaN scale missing',year=year,epsg=info['epsg'],observation_count_errors=obs_errors,full_remote_object_sha256=None,root_metadata='sources/tessera-root.json'))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('product',choices=['aef','tessera']);p.add_argument('region');p.add_argument('--year',type=int,default=2024);a=p.parse_args()
 try:globals()[a.product](a.region,a.year)
 except Exception as e:
  folder=ROOT/'data/main'/a.region
  (folder/f'{a.product}-{a.year}-failure-{int(time.time())}.json').write_text(json.dumps(dict(observed_at_utc=now(),error=str(e),traceback=traceback.format_exc()),indent=2)+'\n')
  raise
