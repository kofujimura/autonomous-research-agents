"""Reproducible geography-only exploratory panel; no wetland source access."""
from pathlib import Path
import argparse,hashlib,io,json,zipfile
import numpy as np,shapefile,shapely
from pyproj import CRS,Transformer
from shapely.geometry import shape,Point,mapping
from shapely.ops import transform,unary_union
from records import ROOT,now

def select(root,out,records):
 root=Path(root);out=Path(out);records=Path(records);assert not out.exists();records.mkdir(parents=True,exist_ok=False)
 path=root/'data/frame/tl_2024_us_state.zip';exclude={'02','15','60','66','69','72','78'};geoms=[];state_ids=[]
 with zipfile.ZipFile(path) as z:
  names=z.namelist();base=next(n[:-4] for n in names if n.endswith('.shp'))
  crs=CRS.from_wkt(z.read(base+'.prj').decode());forward=Transformer.from_crs(crs,5070,always_xy=True).transform
  reader=shapefile.Reader(shp=io.BytesIO(z.read(base+'.shp')),shx=io.BytesIO(z.read(base+'.shx')),dbf=io.BytesIO(z.read(base+'.dbf')))
  for record in reader.iterShapeRecords():
   props=record.record.as_dict();state=props['STATEFP']
   if state in exclude:continue
   geom=shape(record.shape.__geo_interface__);geom=shapely.make_valid(geom) if not geom.is_valid else geom
   geoms.append(transform(forward,geom));state_ids.append(state)
 assert len(state_ids)==49 and len(set(state_ids))==49
 frame=unary_union(geoms);assert frame.is_valid
 (records/'frame-epsg5070.wkb').write_bytes(frame.wkb)
 forward_ll=Transformer.from_crs(4326,5070,always_xy=True).transform;inverse=Transformer.from_crs(5070,4326,always_xy=True).transform
 previous=[]
 for name in ['panel.json','panel-recent.json']:
  for rid,lon,lat in json.loads((root/'protocol'/name).read_text())['regions']:previous.append(forward_ll(lon,lat))
 accepted=[];log=[];rng=np.random.default_rng(48018);minx,miny,maxx,maxy=frame.bounds
 for draw in range(100000):
  x,y=rng.uniform([minx,miny],[maxx,maxy]);entry=dict(draw_id=draw+1,x5070=float(x),y5070=float(y));point=Point(x,y)
  if not frame.contains(point):entry['rejection']='outside_frame'
  elif np.linalg.norm(np.asarray(previous+[v['xy5070'] for v in accepted])-[x,y],axis=1).min()<25000:entry['rejection']='distance_before_snap'
  else:
   lon,lat=inverse(x,y);epsg=32600+int((lon+180)//6)+1;to_utm=Transformer.from_crs(4326,epsg,always_xy=True).transform;from_utm=Transformer.from_crs(epsg,4326,always_xy=True).transform
   ux,uy=to_utm(lon,lat);ux=round(ux/10)*10;uy=round(uy/10)*10;lon,lat=from_utm(ux,uy);xx,yy=forward_ll(lon,lat)
   entry.update(lon=lon,lat=lat,epsg=epsg,utm_centre=[ux,uy],snapped_xy5070=[xx,yy])
   if not frame.contains(Point(xx,yy)):entry['rejection']='outside_after_snap'
   elif np.linalg.norm(np.asarray(previous+[v['xy5070'] for v in accepted])-[xx,yy],axis=1).min()<24990:entry['rejection']='distance_after_snap'
   else:
    rid=f'B{len(accepted)+1:02}';accepted.append(dict(region=rid,lon=lon,lat=lat,xy5070=[xx,yy],epsg=epsg,utm_centre=[ux,uy],draw_id=draw+1));entry.update(rejection=None,region=rid)
  log.append(entry)
  if len(accepted)==48:break
 assert len(accepted)==48
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(dict(regions=[[v['region'],v['lon'],v['lat']] for v in accepted],scope='Exploratory random administrative-geography windows; not a national wetland-population sample',seed=48018,frame='2024 TIGER/Line State and Equivalent Entities, contiguous48states+DC, including state waters'),indent=2)+'\n')
 (records/'draws.json').write_text(json.dumps(log,indent=2)+'\n');(records/'accepted.json').write_text(json.dumps(accepted,indent=2)+'\n')
 record=dict(selected_at_utc=now(),seed=48018,draws=len(log),accepted_n=len(accepted),frame_statefp=sorted(state_ids),frame_crs_source=crs.to_string(),frame_bounds5070=list(frame.bounds),frame_wkb_sha256=hashlib.sha256(frame.wkb).hexdigest(),source_zip_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),panel_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),numpy_version=np.__version__,pyshp_version=shapefile.__version__,shapely_version=shapely.__version__,used_wetland_labels_or_counts=False)
 (records/'selection-record.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--out',type=Path,required=True);p.add_argument('--records',type=Path,required=True);a=p.parse_args();select(a.root,a.out,a.records)
