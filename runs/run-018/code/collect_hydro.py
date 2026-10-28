"""Save numerical public DEM export and exact JRC source windows, then warp locally."""
from pathlib import Path
import argparse,hashlib,json,math,traceback,time
from urllib.parse import urlencode
import numpy as np,rasterio
from rasterio.windows import Window,from_bounds
from rasterio.warp import transform_bounds,reproject,Resampling
from rasterio.transform import from_origin
from fetch import fetch
from records import ROOT,now,append
from collect_embeddings import GDAL


def collect(rid):
 folder=ROOT/'data/main'/rid;info=json.loads((folder/'labels-record.json').read_text());epsg=info['epsg']
 b=info['bounds'];left=math.floor((b[0]-2100)/30)*30;bottom=math.floor((b[1]-2100)/30)*30;right=math.ceil((b[2]+2100)/30)*30;top=math.ceil((b[3]+2100)/30)*30
 width=int((right-left)/30);height=int((top-bottom)/30);tr=from_origin(left,top,30,30)
 params=dict(bbox=','.join(map(str,[left,bottom,right,top])),bboxSR=epsg,imageSR=epsg,size=f'{width},{height}',adjustAspectRatio='false',format='tiff',pixelType='F32',bandIds=0,interpolation='RSP_BilinearInterpolation',renderingRule=json.dumps({'rasterFunction':'None'}),f='image',compression='LZ77')
 url='https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage?'+urlencode(params)
 dem=folder/'dem-30m.tif'
 if not dem.exists():
  if fetch(rid+'-dem-export',url,str(dem.relative_to(ROOT)),licence='USGS public domain; 3DEP',timeout=180):raise RuntimeError('DEM export download failed')
 with rasterio.open(dem) as src:
  assert src.count==1 and src.dtypes[0]=='float32' and src.crs.to_epsg()==epsg
  assert src.shape==(height,width) and np.allclose(tuple(src.transform),tuple(tr),atol=1e-4)
  heights=src.read(1,masked=True).filled(np.nan)
  assert np.isfinite(heights).any() and np.nanmin(heights)>-500 and np.nanmax(heights)<7000
 demchecks=[]
 for k,(rf,cf) in enumerate([(0.25,0.25),(0.5,0.5),(0.75,0.75)]):
  row=int(height*rf);col=int(width*cf);x,y=tr*(col+.5,row+.5)
  qp=dict(geometry=json.dumps({'x':x,'y':y,'spatialReference':{'wkid':epsg}}),geometryType='esriGeometryPoint',returnGeometry='false',returnCatalogItems='false',renderingRule=json.dumps({'rasterFunction':'None'}),f='json')
  identify='https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/identify?'+urlencode(qp)
  dst=folder/f'dem-check-explicit-crs-{k}.json'
  if not dst.exists():fetch(rid+f'-dem-identify-explicit-crs-{k}',identify,str(dst.relative_to(ROOT)),licence='USGS public domain',timeout=60)
  result=json.loads(dst.read_text());value=result.get('value')
  demchecks.append(dict(x=x,y=y,export_height=float(heights[row,col]),identify_value=value,absolute_difference=abs(float(value)-float(heights[row,col])) if value not in [None,'NoData'] else None))
 lon,lat=info['centre'];tilewest=int(math.floor(lon/10)*10);tilenorth=int(math.ceil(lat/10)*10)
 tile=f'{abs(tilewest)}W_{tilenorth}N'
 source_bounds=transform_bounds(epsg,4326,left,bottom,right,top,densify_pts=21)
 layer_records=[]
 for layer in ['occurrence','recurrence','seasonality']:
  public=f'https://s3.waw4-1.cloudferro.com/swift/v1/global-surface-water/download2024/Aggregated/VER1-5/{layer}/{layer}_{tile}_v1_5_2024.tif'
  dst=folder/f'gsw-{layer}-source.tif';stamp=now()
  if not dst.exists():
   with rasterio.Env(**GDAL):
    with rasterio.open('/vsicurl/'+public) as src:
     win=from_bounds(*source_bounds,transform=src.transform)
     c0=max(0,math.floor(win.col_off)-2);r0=max(0,math.floor(win.row_off)-2);c1=min(src.width,math.ceil(win.col_off+win.width)+2);r1=min(src.height,math.ceil(win.row_off+win.height)+2)
     window=Window(c0,r0,c1-c0,r1-r0);data=src.read(1,window=window)
     profile=dict(driver='GTiff',height=data.shape[0],width=data.shape[1],count=1,dtype=data.dtype,crs=src.crs,transform=src.window_transform(window),nodata=255,compress='deflate')
     orig=dict(url=public,requested_at_utc=stamp,obtained_at_utc=now(),window=[c0,r0,c1-c0,r1-r0],source_shape=list(src.shape),source_transform=list(src.transform),source_declared_nodata=src.nodata,values_sha256=hashlib.sha256(data.tobytes()).hexdigest(),full_remote_object_sha256=None)
   with rasterio.open(dst,'w',**profile) as out:out.write(data,1)
   orig.update(path=str(dst.relative_to(ROOT)),sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),bytes=dst.stat().st_size,bundled=True,licence='Copernicus free reuse; Source EC JRC/Google; cite Pekel2016')
   append('sources.jsonl',dict(source_id=rid+'-gsw-'+layer,**orig))
   (folder/f'gsw-{layer}-source-record.json').write_text(json.dumps(orig,indent=2)+'\n')
  with rasterio.open(dst) as src:
   arr=np.full((height,width),255,np.uint8)
   reproject(rasterio.band(src,1),arr,src_transform=src.transform,src_crs=src.crs,src_nodata=255,dst_transform=tr,dst_crs=epsg,dst_nodata=255,resampling=Resampling.nearest)
  limit=12 if layer=='seasonality' else 100
  invalid=(arr>limit)&(arr!=255);invalid_count=int(invalid.sum())
  # Original source window is preserved; physically out-of-range pixels are missing.
  arr[invalid]=255
  target=folder/f'gsw-{layer}-30m.tif'
  with rasterio.open(target,'w',driver='GTiff',height=height,width=width,count=1,dtype='uint8',crs=epsg,transform=tr,nodata=255,compress='deflate') as out:out.write(arr,1)
  layer_records.append(dict(layer=layer,out_of_range_grid_pixels=invalid_count,valid_pixels=int((arr!=255).sum()),total_pixels=int(arr.size),min=int(arr.min()),max=int(arr.max()),source_path=str(dst.relative_to(ROOT)),source_sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),grid_path=str(target.relative_to(ROOT)),grid_sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
 meta=dict(region=rid,obtained_at_utc=now(),epsg=epsg,grid_bounds=[left,bottom,right,top],grid_transform=list(tr),shape=[height,width],dem_url=url,dem_sha256=hashlib.sha256(dem.read_bytes()).hexdigest(),dem_checks=demchecks,layers=layer_records)
 (folder/'hydro-record.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('region');a=p.parse_args()
 try:collect(a.region)
 except Exception as e:
  (ROOT/'data/main'/a.region/f'hydro-failure-{int(time.time())}.json').write_text(json.dumps(dict(observed_at_utc=now(),error=str(e),traceback=traceback.format_exc()),indent=2)+'\n');raise
