"""Self-check of a saved-data route to cohort histories; no cohort filtering."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import CRS,Transformer,Geod
from record import ROOT

def feasibility(output):
    output.mkdir(parents=True,exist_ok=False)
    paths=['data/prepared/references.csv','data/controls/controls.csv','data/nlcd/Plot_Coordinates_List_Simple_and_Stratified.csv','data/nlcd/lcnext_8360_final.prj']
    r=pd.read_csv(ROOT/paths[0]);r['cohort']='baseline_trees'
    c=pd.read_csv(ROOT/paths[1]);c['cohort']='baseline_non_tree';cohorts=pd.concat([r,c],ignore_index=True)
    n=pd.read_csv(ROOT/paths[2]);crs=CRS.from_wkt((ROOT/paths[3]).read_text())
    lon,lat=Transformer.from_crs(crs,'EPSG:4326',always_xy=True).transform(n.x,n.y)
    rows=[];geod=Geod(ellps='WGS84')
    for q in cohorts.itertuples():
        d=geod.inv(np.full(len(n),q.x),np.full(len(n),q.y),lon,lat)[2]
        rows.append(dict(point_id=q.point_id,cohort=q.cohort,minimum_distance_m=float(np.min(d)),
            matches_within_1m=int((d<=1).sum()),nearest_nlcd_plotid=int(n.iloc[int(np.argmin(d))].plotid)))
    table=pd.DataFrame(rows);table.to_csv(output/'coordinate-matches.csv',index=False)
    summary=dict(cohort_plots=len(table),nlcd_source_plots=len(n),matching_radius_m=1,
        cohort_plots_with_match=int((table.matches_within_1m>0).sum()),
        cohort_plots_with_unique_match=int((table.matches_within_1m==1).sum()),
        minimum_cross_source_distance_m=float(table.minimum_distance_m.min()),
        scope='Coordinate feasibility only. NLCD Forest differs from LCMAP Trees; no annual label or primary cohort is changed. No new retrieval.')
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (output/'input-sha256.json').write_text(json.dumps({p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();feasibility(a.output)
