"""Offline input checks; no field validation and no outcome-driven data selection."""
from pathlib import Path
import argparse,ast,hashlib,json,re
import numpy as np,rasterio
from pyproj import Transformer
from shapely.geometry import shape,Point
from shapely.ops import transform
from shapely import make_valid
from derive_features import embedding

def dictionaries(path):
 text=path.read_text();result={}
 for name in ['waterRegimeDict','waterRegimeExclusions']:
  match=re.search(r'\b'+name+r'\s*=\s*(\{.*?\n\s*\})',text,re.S)
  if not match:raise RuntimeError('Official code table not found: '+name)
  result[name]=ast.literal_eval(match.group(1))
 return result

def audit(root,out,pattern='R??'):
 root=Path(root);out=Path(out);out.mkdir(parents=True,exist_ok=True)
 tables=dictionaries(root/'sources/nwi-code-interpreter.py.txt');definition_checks=[]
 for veg in ['PEM1','PFO1','PSS1']:
  for regime in ['A','C','F']:
   valid=regime in tables['waterRegimeDict'][veg[:3]] and regime not in tables['waterRegimeExclusions'].get(veg,[])
   definition_checks.append(dict(code=veg+regime,allowed_by_official_interpreter=valid));assert valid
 sampled=[];regions=[];global_ids=set()
 for folder in sorted((root/'data/main').glob(pattern)):
  if not (folder/'labels-record.json').exists():continue
  record=json.loads((folder/'labels-record.json').read_text());selected=json.loads((folder/'selected.geojson').read_text())['features'];fs=sorted(selected,key=lambda f:f['properties']['hash']);forward=Transformer.from_crs(4326,record['epsg'],always_xy=True).transform
  ids=[f['properties']['objectid'] for f in selected];assert not(global_ids&set(ids));global_ids.update(ids)
  original={}
  for page in record['pages']:
   for f in json.loads((root/page['path']).read_text())['features']:original[f['properties']['OBJECTID']]=f
  imagery=json.loads((root/record['image_source']['path']).read_text())['features']
  for f in fs[:3]:
   p=f['properties'];raw=original[p['objectid']];g=transform(forward,shape(raw['geometry']));g=make_valid(g) if not g.is_valid else g;point=Point(p['x'],p['y']);expected=hashlib.sha256(f"free-research-018|{p['objectid']}".encode()).hexdigest();assert p['hash']==expected
   ll=Point(p['lon'],p['lat']);matches=[v['properties'] for v in imagery if v.get('geometry') and shape(v['geometry']).covers(ll)];years=[int(v['IMAGE_YR']) for v in matches if v.get('IMAGE_YR') and 1900<=int(v['IMAGE_YR'])<=2026];joined=max(years) if years else None
   assert joined==p['image_year']
   sample=dict(image_join_recomputed=joined,imagery_match_count=len(matches),region=folder.name,objectid=p['objectid'],original_attribute=raw['properties']['ATTRIBUTE'],parsed_vegetation=p['vegetation'],parsed_regime=p['regime'],code_matches_original=p['attribute']==raw['properties']['ATTRIBUTE'],point_inside_original_polygon=g.covers(point),boundary_distance_m=point.distance(g.boundary),saved_margin_m=p['interior_margin_m'],projected_area_m2=g.area,saved_area_m2=p['area_m2'],source_acres=raw['properties'].get('ACRES'),image_year=p['image_year'])
   assert sample['code_matches_original'] and sample['point_inside_original_polygon'];assert abs(sample['boundary_distance_m']-sample['saved_margin_m'])<.1
   sampled.append(sample)
  info=dict(region=folder.name,selected_n=len(selected),image_years=sorted(set(f['properties']['image_year'] for f in selected if f['properties']['image_year'] is not None)))
  for product in ['aef','tessera']:
   path=folder/f'{product}-2024.npz'
   if not path.exists():info[product]=dict(status='missing');continue
   x=np.load(path);assert np.array_equal(x['objectid'],ids)
   v,n=embedding(path);raw=x['raw'].astype(float)
   offsets=np.array([(dc*10,-dr*10) for dr in [-1,0,1] for dc in [-1,0,1]])
   delta=x['xy']-x['xy'][:,4,None,:]
   finite=np.isfinite(delta).all(axis=2);assert np.allclose(delta[finite],np.broadcast_to(offsets,delta.shape)[finite],atol=1e-6)
   valid=x['inside']&((raw!=-128).all(axis=2) if product=='aef' else np.isfinite(x['scales']))
   decoded=np.sign(raw)*(raw/127.5)**2 if product=='aef' else raw*x['scales'][...,None]
   norms=np.linalg.norm(decoded[valid],axis=1)
   info[product]=dict(status='present',finite_mean_vectors=int(np.isfinite(v).all(axis=1).sum()),valid_patch_pixels=int(valid.sum()),inside_pixels=int(x['inside'].sum()),pixel_norm_min=float(norms.min()) if len(norms) else None,pixel_norm_max=float(norms.max()) if len(norms) else None,pixel_norm_mean=float(norms.mean()) if len(norms) else None)
  if (folder/'aef-2024.npz').exists() and (folder/'tessera-2024.npz').exists():
   aa=np.load(folder/'aef-2024.npz');tt=np.load(folder/'tessera-2024.npz');dist=np.linalg.norm(aa['xy'][:,4]-tt['xy'][:,4],axis=1);info['centre_alignment_max_m']=float(np.nanmax(dist));info['centre_alignment_mean_m']=float(np.nanmean(dist))
  if (folder/'hydro-record.json').exists():
   hy=json.loads((folder/'hydro-record.json').read_text());diff=[c.get('absolute_difference') for c in hy['dem_checks'] if c.get('absolute_difference') is not None];info['dem_identify_numerical_checks']=len(diff);info['dem_identify_max_difference_m']=max(diff) if diff else None;info['water_range_exclusions']=sum(v.get('out_of_range_grid_pixels',0) for v in hy['layers'])
   for name,limit in [('occurrence',100),('recurrence',100),('seasonality',12)]:
    with rasterio.open(folder/f'gsw-{name}-30m.tif') as src:a=src.read(1)
    assert ((a<=limit)|(a==255)).all()
  if (folder/'hand-record.json').exists():
   hh=json.loads((folder/'hand-record.json').read_text());info['hand_coverage_fraction']=hh['finite_pixels']/hh['total_pixels']
  regions.append(info)
 result=dict(definition_checks=definition_checks,sample_n=len(sampled),sample=sampled,regions=regions,scope='Self-check of saved input/category path; not field-hydrology validation, independent annotation or independent reproduction')
 (out/'data-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(sample_n=len(sampled),regions=len(regions),all_nine_category_combinations_allowed=True,complete_embedding_regions=sum(x.get('aef',{}).get('status')=='present' and x.get('tessera',{}).get('status')=='present' for x in regions))))
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--pattern',default='R??');a=p.parse_args();audit(a.root,a.out,a.pattern)
