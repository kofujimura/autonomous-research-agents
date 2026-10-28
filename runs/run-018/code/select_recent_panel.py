"""Exploratory recency-only site selection; commit output before wetland access."""
import hashlib,json,math
import numpy as np
from pyproj import Transformer
from shapely.geometry import shape,Point,mapping
from shapely.ops import transform,nearest_points
from shapely import make_valid
from collect_labels import request,BASE
from records import ROOT,now

ANCHORS=['R01','R03','R04','R06','R09','R12']

def main():
 panel=json.loads((ROOT/'protocol/panel.json').read_text());original={rid:(lon,lat) for rid,lon,lat in panel['regions']};chosen=[];audit=[]
 folder=ROOT/'data/recent-selection';folder.mkdir(parents=True,exist_ok=True)
 for slot,anchor in enumerate(ANCHORS,1):
  lon,lat=original[anchor];epsg=32600+int((lon+180)//6)+1;f=Transformer.from_crs(4326,epsg,always_xy=True).transform;inv=Transformer.from_crs(epsg,4326,always_xy=True).transform;point=Point(*f(lon,lat))
  params=dict(f='geojson',where='IMAGE_YR>=2020',geometry=f'{point.x-400000},{point.y-400000},{point.x+400000},{point.y+400000}',geometryType='esriGeometryEnvelope',inSR=epsg,spatialRel='esriSpatialRelIntersects',outSR=4326,outFields='OBJECTID,IMAGE_YR,IMAGE_DATE,PROJECT_NAME,STATUS',returnGeometry='true',resultRecordCount=2000,geometryPrecision=7)
  data,source=request(BASE+'Data_Source/MapServer/3/query',folder/f'{anchor}-projects.geojson',params,'recent-projects-'+anchor)
  if data.get('exceededTransferLimit') or data.get('properties',{}).get('exceededTransferLimit'):raise RuntimeError('Metadata pagination required; no truncated selection')
  exclusions=[Point(*f(*ll)).buffer(25000) for ll in list(original.values())+[tuple(x[1:]) for x in chosen]]
  options=[]
  for feat in data.get('features',[]):
   if not feat.get('geometry'):continue
   g=transform(f,shape(feat['geometry']))
   if not g.is_valid:g=make_valid(g)
   g=g.buffer(-11500)
   for disc in exclusions:g=g.difference(disc)
   if g.is_empty:continue
   near=nearest_points(point,g)[1];distance=point.distance(near)
   if distance>400000:continue
   oid=feat['properties']['OBJECTID'];options.append((distance,oid,near,feat['properties']))
  if not options:audit.append(dict(slot=slot,anchor=anchor,status='no_qualifying_project',source=source));continue
  distance,oid,near,props=min(options,key=lambda x:(x[0],x[1]));longitude,latitude=inv(near.x,near.y);rid=f'S{slot:02}';chosen.append([rid,longitude,latitude])
  audit.append(dict(slot=slot,region=rid,anchor=anchor,distance_m=distance,selected_project=props,centre=[longitude,latitude],source=source,criterion='recency,geometry,distance only; no wetland categories or embedding outcomes'))
 result=dict(created_at_utc=now(),width_m=16000,max_polygons=1200,exploratory=True,regions=chosen,selection_audit=audit)
 (ROOT/'protocol/panel-recent.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main()
