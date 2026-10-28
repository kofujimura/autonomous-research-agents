"""ASF public HAND v1/2021, preserve source windows and reproject locally."""
import argparse,hashlib,json,math,time,traceback
import numpy as np,rasterio
from rasterio.windows import Window,from_bounds
from rasterio.warp import transform_bounds,reproject,Resampling
from collect_embeddings import GDAL
from records import ROOT,now,append

def collect(rid):
 folder=ROOT/'data/main'/rid;info=json.loads((folder/'labels-record.json').read_text())
 with rasterio.open(folder/'dem-30m.tif') as src:
  profile=src.profile.copy();bounds=src.bounds;tr=src.transform;crs=src.crs;shape_=src.shape
 left,bottom,right,top=transform_bounds(crs,4326,*bounds,densify_pts=21)
 result=np.full(shape_,np.nan,np.float32);records=[]
 for south in range(math.floor(bottom),math.floor(top)+1):
  for west in range(math.floor(left),math.floor(right)+1):
   lat=('N' if south>=0 else 'S')+f'{abs(south):02}_00';lon=('E' if west>=0 else 'W')+f'{abs(west):03}_00'
   filename=f'Copernicus_DSM_COG_10_{lat}_{lon}_HAND.tif'
   url='https://glo-30-hand.s3.us-west-2.amazonaws.com/v1/2021/'+filename
   path=folder/f'hand-source-{south}-{west}.tif';stamp=now()
   with rasterio.Env(**GDAL):
    with rasterio.open('/vsicurl/'+url) as src:
     bb=transform_bounds(crs,src.crs,*bounds,densify_pts=21);win=from_bounds(*bb,transform=src.transform)
     c0=max(0,math.floor(win.col_off)-2);r0=max(0,math.floor(win.row_off)-2);c1=min(src.width,math.ceil(win.col_off+win.width)+2);r1=min(src.height,math.ceil(win.row_off+win.height)+2)
     if c1<=c0 or r1<=r0:continue
     window=Window(c0,r0,c1-c0,r1-r0);raw=src.read(1,window=window)
     rec=dict(url=url,requested_at_utc=stamp,obtained_at_utc=now(),window=[c0,r0,c1-c0,r1-r0],source_transform=list(src.transform),source_shape=list(src.shape),declared_nodata=src.nodata,source_values_sha256=hashlib.sha256(raw.tobytes()).hexdigest(),full_remote_object_sha256=None)
     pp=dict(driver='GTiff',height=raw.shape[0],width=raw.shape[1],count=1,dtype='float32',crs=src.crs,transform=src.window_transform(window),nodata=np.nan,compress='deflate')
     cleaned=raw.astype(np.float32);invalid=~np.isfinite(cleaned)|(cleaned<0)
     if src.nodata is not None:invalid|=cleaned==src.nodata
     # Store original raw source pixels with their declared no-data value.
     rawprofile=pp.copy();rawprofile['nodata']=src.nodata
     with rasterio.open(path,'w',**rawprofile) as out:out.write(raw,1)
     cleaned[invalid]=np.nan;temp=np.full(shape_,np.nan,np.float32)
     reproject(cleaned,temp,src_transform=pp['transform'],src_crs=pp['crs'],src_nodata=np.nan,dst_transform=tr,dst_crs=crs,dst_nodata=np.nan,resampling=Resampling.bilinear)
     use=np.isfinite(temp)&~np.isfinite(result);result[use]=temp[use]
   rec.update(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size,negative_or_nodata_pixels=int(invalid.sum()),bundled=True,licence='ASF HAND CC0 1.0; preserve Copernicus acknowledgement')
   records.append(rec);append('sources.jsonl',dict(source_id=rid+'-HAND-'+lat+'-'+lon,**rec))
 profile.update(dtype='float32',nodata=np.nan,compress='deflate',count=1)
 target=folder/'hand-30m.tif'
 with rasterio.open(target,'w',**profile) as out:out.write(result,1)
 record=dict(region=rid,created_at_utc=now(),sources=records,grid_path=str(target.relative_to(ROOT)),grid_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),finite_pixels=int(np.isfinite(result).sum()),total_pixels=int(result.size),minimum=float(np.nanmin(result)),maximum=float(np.nanmax(result)))
 (folder/'hand-record.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('region');a=p.parse_args()
 try:collect(a.region)
 except Exception as e:
  (ROOT/'data/main'/a.region/f'hand-failure-{int(time.time())}.json').write_text(json.dumps(dict(observed_at_utc=now(),error=str(e),traceback=traceback.format_exc()),indent=2)+'\n');raise
