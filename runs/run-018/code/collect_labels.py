"""Fixed-panel public NWI retrieval and deterministic polygon sampling."""
from pathlib import Path
import argparse,hashlib,json,subprocess,time
from urllib.parse import urlencode
import numpy as np
from pyproj import Transformer
from shapely.geometry import shape,mapping,Point,box
from shapely.ops import transform,polylabel
from shapely import make_valid
from records import ROOT,now,append

BASE='https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/'
PAGE_SIZE=500
PREFIX=''
TIMEOUT=90
REQUEST_PACE=0
CODES=[v+r for v in ['PEM1','PFO1','PSS1'] for r in ['A','C','F']]

class RemoteUnavailable(RuntimeError):pass

def request(url,path,params,source_id):
 path.parent.mkdir(parents=True,exist_ok=True)
 full=url+'?'+urlencode(params);attempts=[]
 previous=[json.loads(line) for line in (ROOT/'sources.jsonl').read_text().splitlines() if line.strip()]
 previous=[item for item in previous if item.get('url')==full]
 for item in reversed(previous):
  cached=ROOT/item['path'] if item.get('path') else None
  if item.get('exit_code')==0 and cached and cached.exists():
   try:
    data=json.loads(cached.read_text())
    if 'error' not in data and hashlib.sha256(cached.read_bytes()).hexdigest()==item.get('sha256'):return data,item
   except Exception:pass
 remaining=3-len(previous)
 if remaining<=0:raise RuntimeError('Cumulative3-request source limit reached: '+source_id)
 for attempt in range(min(2,remaining)):
  time.sleep(REQUEST_PACE)
  stamp=now();overall_attempt=len(previous)+attempt+1;target=path if overall_attempt==1 else path.with_name(path.stem+f'-attempt{overall_attempt}'+path.suffix)
  p=subprocess.run(['curl','--fail','--silent','--show-error','--location','--max-time',str(TIMEOUT),'--output',str(target),full],capture_output=True,text=True,timeout=TIMEOUT+10)
  item=dict(source_id=source_id,url=full,requested_at_utc=stamp,obtained_at_utc=now(),path=str(target.relative_to(ROOT)),exit_code=p.returncode,error=p.stderr.strip() or None,licence='NWI unrestricted reuse per saved official metadata',sha256=hashlib.sha256(target.read_bytes()).hexdigest() if target.exists() else None,bytes=target.stat().st_size if target.exists() else 0,bundled=True)
  append('sources.jsonl',item);attempts.append(item)
  if 'error: 503' in p.stderr or 'error: 429' in p.stderr:raise RemoteUnavailable('Remote service unavailable/rate limited; stop batch, defer retry: '+source_id)
  if p.returncode==0:
   try:
    data=json.loads(target.read_text())
    if 'error' not in data:return data,item
   except Exception:pass
  time.sleep(1)
 raise RuntimeError('Public NWI query failed: '+source_id)

def collect(rid,lon,lat):
 folder=ROOT/'data/main'/rid;folder.mkdir(parents=True,exist_ok=True)
 epsg=32600+int((lon+180)//6)+1
 forward=Transformer.from_crs(4326,epsg,always_xy=True).transform
 inverse=Transformer.from_crs(epsg,4326,always_xy=True).transform
 cx,cy=forward(lon,lat);cx=round(cx/10)*10;cy=round(cy/10)*10
 bounds=[cx-8000,cy-8000,cx+8000,cy+8000]
 common=dict(geometry=','.join(map(str,bounds)),geometryType='esriGeometryEnvelope',inSR=epsg,spatialRel='esriSpatialRelIntersects')
 stats,_=request(BASE+'Wetlands/MapServer/0/query',folder/(PREFIX+'attribute-counts.json'),dict(common,f='json',where='1=1',returnGeometry='false',groupByFieldsForStatistics='ATTRIBUTE',outStatistics=json.dumps([{'statisticType':'count','onStatisticField':'OBJECTID','outStatisticFieldName':'n'}]),orderByFields='ATTRIBUTE'),rid+'-all-attribute-counts')
 raw=[];pages=[]
 for page in range(100):
  data,item=request(BASE+'Wetlands/MapServer/0/query',folder/f'{PREFIX}nwi-page-{page:03}.geojson',dict(common,f='geojson',where='ATTRIBUTE IN ('+','.join("'"+c+"'" for c in CODES)+')',outFields='OBJECTID,ATTRIBUTE,ACRES',outSR=4326,returnGeometry='true',orderByFields='OBJECTID',resultOffset=page*PAGE_SIZE,resultRecordCount=PAGE_SIZE,geometryPrecision=7),rid+f'-wetlands-{page}')
  features=data.get('features',[]);raw.extend(features);pages.append(item)
  if len(features)<PAGE_SIZE:break
 else:raise RuntimeError('Pagination bound reached')
 dates,date_source=request(BASE+'Data_Source/MapServer/3/query',folder/(PREFIX+'imagery.geojson'),dict(common,f='geojson',where='1=1',outFields='OBJECTID,IMAGE_YR,IMAGE_DATE,PROJECT_NAME,STATUS',outSR=4326,returnGeometry='true',resultRecordCount=2000),rid+'-imagery')
 if dates.get('exceededTransferLimit'):raise RuntimeError('Image metadata pagination required')
 date_geoms=[(shape(f['geometry']),f['properties']) for f in dates.get('features',[]) if f.get('geometry')]
 seen=set();elig=[];audit=[];square=box(*bounds)
 for feature in raw:
  props=feature['properties'];oid=props['OBJECTID']
  if oid in seen:continue
  seen.add(oid);entry=dict(objectid=oid,attribute=props['ATTRIBUTE'])
  if not feature.get('geometry'):
   entry['excluded']='missing_geometry';audit.append(entry);continue
  geom=transform(forward,shape(feature['geometry'])); repaired=not geom.is_valid
  if repaired:geom=make_valid(geom)
  if geom.geom_type=='GeometryCollection':
   polys=[g for g in geom.geoms if g.geom_type in ['Polygon','MultiPolygon']]
   if not polys:entry['excluded']='nonpolygon';audit.append(entry);continue
   geom=max(polys,key=lambda g:g.area)
  area=geom.area;entry.update(area_m2=area,repaired=repaired)
  if not 1000<=area<=1000000:entry['excluded']='area';audit.append(entry);continue
  components=list(geom.geoms) if geom.geom_type=='MultiPolygon' else [geom]
  poly=max(components,key=lambda g:g.area)
  point=polylabel(poly,tolerance=2);margin=point.distance(geom.boundary)
  if not square.covers(point):entry['excluded']='point_outside_window';audit.append(entry);continue
  if margin<15:entry['excluded']='interior_margin';audit.append(entry);continue
  lonp,latp=inverse(point.x,point.y);ll=Point(lonp,latp)
  if -99.1<=lonp<=-99.0 and 46.9<=latp<=47.0:entry['excluded']='pilot';audit.append(entry);continue
  matched=[props for g,props in date_geoms if g.covers(ll)]
  years=[int(p['IMAGE_YR']) for p in matched if p.get('IMAGE_YR') and 1900<=int(p['IMAGE_YR'])<=2026]
  entry.update(excluded=None,x=point.x,y=point.y,lon=lonp,lat=latp,interior_margin_m=margin,vegetation=props['ATTRIBUTE'][:-1],regime=props['ATTRIBUTE'][-1],image_year=max(years) if years else None,image_matches=matched,hash=hashlib.sha256(f'free-research-018|{oid}'.encode()).hexdigest(),block_x=int((point.x-bounds[0])//4000),block_y=int((point.y-bounds[1])//4000))
  entry['fold']=(entry['block_x']+2*entry['block_y'])%4
  elig.append(dict(type='Feature',geometry=mapping(transform(inverse,geom)),properties=entry));audit.append(entry)
 selected=sorted(elig,key=lambda f:f['properties']['hash'])[:1200]
 selected_ids={f['properties']['objectid'] for f in selected}
 for e in audit:e['selected']=e['objectid'] in selected_ids
 (folder/'eligibility.json').write_text(json.dumps(audit,indent=2)+'\n')
 (folder/'selected.geojson').write_text(json.dumps(dict(type='FeatureCollection',features=selected))+'\n')
 record=dict(region_id=rid,centre=[lon,lat],epsg=epsg,bounds=bounds,raw_unique=len(seen),eligible=len(elig),selected=len(selected),selected_ids=sorted(selected_ids),pages=pages,image_source=date_source,created_at_utc=now())
 (folder/'labels-record.json').write_text(json.dumps(record,indent=2)+'\n')
 print(json.dumps({k:v for k,v in record.items() if k not in ['pages','image_source','selected_ids']}),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('regions',nargs='+');p.add_argument('--page-size',type=int,default=500);p.add_argument('--prefix',default='');p.add_argument('--request-timeout',type=int,default=90);p.add_argument('--panel',default='protocol/panel.json');p.add_argument('--request-pace',type=float,default=0);args=p.parse_args();PAGE_SIZE=args.page_size;PREFIX=args.prefix;TIMEOUT=args.request_timeout;REQUEST_PACE=args.request_pace
 panel=json.loads((ROOT/args.panel).read_text())
 failures=[]
 for rid,lon,lat in panel['regions']:
  if rid not in args.regions:continue
  try:collect(rid,lon,lat)
  except Exception as e:
   failures.append(dict(region=rid,error=str(e),observed_at_utc=now()));print(json.dumps(failures[-1]),flush=True)
   if isinstance(e,RemoteUnavailable):break
 if failures:
  (ROOT/'data/main'/('failures-labels-'+'-'.join(args.regions)+'.json')).write_text(json.dumps(failures,indent=2)+'\n')
  raise SystemExit(1)
