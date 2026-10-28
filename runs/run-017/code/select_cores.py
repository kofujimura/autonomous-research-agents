"""Outcome-blind geometry selection fixed by protocol v1."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Transformer
from shapely.geometry import shape, box, Point
from shapely.ops import transform as geom_transform
from records import ROOT, now

def main():
    projects=json.loads((ROOT/'data/pilot/2020-project-geometries.geojson').read_text())['features']
    cols=['path','year','crs','utm_west','utm_south','utm_east','utm_north',
          'wgs84_west','wgs84_south','wgs84_east','wgs84_north']
    index=pd.read_parquet(ROOT/'data/pilot/aef_index.parquet',columns=cols)
    index=index[index.year==2020]
    regions=[]
    for project in sorted(projects,key=lambda f:f['properties']['OBJECTID']):
        props=project['properties'];g=shape(project['geometry'])
        candidates=[]
        west,south,east,north=g.bounds
        for lon in np.arange(np.ceil(west/.06)*.06,east,.06):
            for lat in np.arange(np.ceil(south/.06)*.06,north,.06):
                if not g.contains(Point(lon,lat)):continue
                tiles=index[(index.wgs84_west<lon)&(index.wgs84_east>lon)&
                            (index.wgs84_south<lat)&(index.wgs84_north>lat)]
                for _,tile in tiles.sort_values('path').iterrows():
                    crs=tile.crs
                    forward=Transformer.from_crs(4326,crs,always_xy=True)
                    inverse=Transformer.from_crs(crs,4326,always_xy=True)
                    x,y=forward.transform(float(lon),float(lat));x=round(x/10)*10;y=round(y/10)*10
                    # Core is 256 pixels; 16-pixel retrieval buffer on each side.
                    bounds=[x-1440,y-1440,x+1440,y+1440]
                    if not box(tile.utm_west,tile.utm_south,tile.utm_east,tile.utm_north).contains(box(*bounds)):continue
                    footprint=geom_transform(inverse.transform,box(*bounds))
                    if not g.contains(footprint):continue
                    candidates.append(dict(lon=float(lon),lat=float(lat),x=x,y=y,crs=crs,
                        core_bounds=[x-1280,y-1280,x+1280,y+1280],buffer_bounds=bounds,
                        aef_url=tile.path.replace('gs://','https://storage.googleapis.com/',1),
                        wgs84_bounds=list(footprint.bounds)))
                    break
        rng=np.random.default_rng(1729+int(props['OBJECTID']))
        order=rng.permutation(len(candidates))
        chosen=[]
        for i in order:
            c=candidates[int(i)]
            if any(np.hypot((c['lon']-o['lon'])*111000*np.cos(np.deg2rad(c['lat'])),
                            (c['lat']-o['lat'])*111000)<5000 for o in chosen):continue
            chosen.append(c)
            if len(chosen)==32:break
        if len(chosen)<16:raise RuntimeError(f'Not enough geometry-eligible cores: {props["PROJECT_NAME"]}')
        rid=f'R{len(regions)+1:02d}'
        role_order=np.random.default_rng(2718+int(props['OBJECTID'])).permutation(16)
        roles={int(i):('train' if k<8 else 'validation' if k<12 else 'test') for k,i in enumerate(role_order)}
        for k,c in enumerate(chosen):
            c.update(core_id=f'{rid}C{k:02d}',region_id=rid,ordinal=k,reserve=k>=16,
                     split=roles[k] if k<16 else None)
        regions.append(dict(region_id=rid,project=props,candidate_count=len(candidates),cores=chosen))
    output=dict(created_at_utc=now(),year=2020,selection_seed=1729,split_seed=2718,
                seed_derivation='base seed plus USFWS project object ID',regions=regions)
    out=ROOT/'data/main';out.mkdir(exist_ok=True)
    (out/'core-selection.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({r['region_id']:{'project':r['project']['PROJECT_NAME'],
        'candidates':r['candidate_count'],'selected':sum(not c['reserve'] for c in r['cores']),
        'reserves':sum(c['reserve'] for c in r['cores'])} for r in regions},indent=2))

if __name__=='__main__':main()
