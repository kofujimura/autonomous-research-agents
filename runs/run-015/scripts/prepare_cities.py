"""Freeze geography-only city portfolios before new weather acquisition."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import zipfile

import geopandas as gpd
import numpy as np

from acquire import points_for
from fetch import fetch
from record import ROOT,now

COUNTRY3={'ESP':'ES','PRT':'PT','FRA':'FR','DEU':'DE','AUT':'AT','CZE':'CZ','ROU':'RO','BGR':'BG','SRB':'RS','IND':'IN','BFA':'BF','MLI':'ML','NER':'NE'}

def angular(lat,lon,lat2,lon2):
    lat=np.radians(lat);lon=np.radians(lon);lat2=np.radians(lat2);lon2=np.radians(lon2)
    a=np.sin((lat-lat2)/2)**2+np.cos(lat)*np.cos(lat2)*np.sin((lon-lon2)/2)**2
    return 2*np.arcsin(np.sqrt(np.clip(a,0,1)))

def write_csv(path,rows):
    if not rows:return
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--offline',action='store_true');a=p.parse_args()
    out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
    params=json.loads((ROOT/'protocol/city-time-parameters-v4.1.json').read_text())
    archive=ROOT/'data/cities/naturalearth-populated-places.zip'
    if not archive.exists():
        if a.offline:raise RuntimeError('Bundled gazetteer archive missing; offline mode will not retrieve it')
        if fetch(params['source_url'],str(archive.relative_to(ROOT)),'naturalearth-populated-places',licence=params['source_licence']) is False:raise RuntimeError('Gazetteer download failed')
    archive_sha=hashlib.sha256(archive.read_bytes()).hexdigest()
    data=gpd.read_file(archive)
    if data.crs is None or data.crs.to_epsg()!=4326:raise ValueError('Expected WGS84 point data; refuse an unrecorded coordinate assumption')
    names={c.upper():c for c in data.columns};assert 'POP_MAX' in names
    eligible=[]
    for source_row,(_,row) in enumerate(data.iterrows()):
        point=row[data.geometry.name]
        if point is None or point.geom_type!='Point':continue
        population=float(row[names['POP_MAX']])
        if not np.isfinite(population) or population<params['minimum_population']:continue
        iso=str(row[names['ISO_A2']]) if 'ISO_A2' in names else ''
        if iso not in set(COUNTRY3.values()):
            iso=COUNTRY3.get(str(row[names['ADM0_A3']]),'') if 'ADM0_A3' in names else ''
        lat,lon=float(point.y),float(point.x)
        if not np.isfinite([lat,lon]).all():continue
        grid_lat=float(np.floor(4*lat+.5)/4);grid_lon=float(np.floor(4*lon+.5)/4)
        eligible.append(dict(source_row=source_row,name=str(row[names['NAME']]),country=iso,
                             population_eligibility_value=population,latitude=lat,longitude=lon,
                             grid_latitude=grid_lat,grid_longitude=grid_lon))
    original=json.loads((ROOT/'protocol/design-v1.json').read_text());old_ports,old_points=points_for(original)
    portfolios=[{**port,'portfolio_type':'regular','points':old_points[i*12:(i+1)*12].tolist()} for i,port in enumerate(old_ports)]
    candidates=[];selected=[];diagnostics=[]
    for group in params['groups']:
        rows=[r for r in eligible if r['country'] in group['countries']]
        if 'bounds' in group:
            box=group['bounds'];rows=[r for r in rows if box['lat'][0]<=r['latitude']<=box['lat'][1] and box['lon'][0]<=r['longitude']<=box['lon'][1]]
        rows=sorted(rows,key=lambda r:r['source_row'])
        candidates.extend({**r,'group':group['name']} for r in rows)
        cells={(r['grid_latitude'],r['grid_longitude']) for r in rows}
        info={'group':group['name'],'eligible_records':len(rows),'unique_grid_cells':len(cells)}
        if len(cells)<12:
            info.update(status='omitted_city_portfolios',reason='Fewer than twelve eligible distinct cells; no cutoff/country relaxation')
            diagnostics.append(info);continue
        lat0,lon0=group['center']
        order=sorted(range(len(rows)),key=lambda i:(float(angular(rows[i]['grid_latitude'],rows[i]['grid_longitude'],lat0,lon0)),rows[i]['source_row']))
        nearby=[];used=set()
        for i in order:
            cell=(rows[i]['grid_latitude'],rows[i]['grid_longitude'])
            if cell in used:continue
            used.add(cell);nearby.append(i)
            if len(nearby)==12:break
        dispersed=[nearby[0]];used={(rows[nearby[0]]['grid_latitude'],rows[nearby[0]]['grid_longitude'])}
        while len(dispersed)<12:
            remaining=[i for i in range(len(rows)) if (rows[i]['grid_latitude'],rows[i]['grid_longitude']) not in used]
            def score(i):
                distance=min(float(angular(rows[i]['grid_latitude'],rows[i]['grid_longitude'],rows[j]['grid_latitude'],rows[j]['grid_longitude'])) for j in dispersed)
                return (-distance,rows[i]['source_row'])
            i=min(remaining,key=score);dispersed.append(i);used.add((rows[i]['grid_latitude'],rows[i]['grid_longitude']))
        for rule,indices in [('nearby',nearby),('dispersed',dispersed)]:
            chosen=[rows[i] for i in indices]
            assert len({(r['grid_latitude'],r['grid_longitude']) for r in chosen})==12
            points=[[r['grid_latitude'],r['grid_longitude']] for r in chosen]
            portfolios.append({'center':group['name'],'geometry':rule,'portfolio_type':'city','points':points,
                               'source_rows':[r['source_row'] for r in chosen]})
            selected.extend({**r,'group':group['name'],'selection_rule':rule,'order':i} for i,r in enumerate(chosen))
        info['status']='two_city_portfolios_selected';diagnostics.append(info)
    versions=[]
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            if 'VERSION' in name.upper() and z.getinfo(name).file_size<10000:versions.append({'path':name,'text':z.read(name).decode(errors='replace').strip()})
    design={**params,'created_at_utc':now(),'gazetteer_sha256':archive_sha,'gazetteer_archive_versions':versions,
            'portfolios':portfolios,'source_columns':list(data.columns),'selection_diagnostics':diagnostics,
            'data_root':'data/weather-v4'}
    write_csv(out/'candidates.csv',candidates);write_csv(out/'selected.csv',selected)
    (out/'design-v4.json').write_text(json.dumps(design,indent=2)+'\n')
    report={'completed_at_utc':now(),'gazetteer_sha256':archive_sha,'source_records':len(data),
            'portfolio_count':len(portfolios),'city_portfolio_count':sum(x['portfolio_type']=='city' for x in portfolios),
            'diagnostics':diagnostics,'archive_versions':versions,'offline':a.offline}
    (out/'preparation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
