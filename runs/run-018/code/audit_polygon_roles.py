"""Count shared sampled embedding pixels across polygons and retained spatial roles."""
from pathlib import Path
import argparse,json
import numpy as np,pandas as pd
from scipy.spatial import cKDTree
from records import ROOT,now
p=argparse.ArgumentParser();p.add_argument('--rows',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);rows=pd.DataFrame(json.loads(a.rows.read_text()));counts=[];details=[]
for rid,g in rows.groupby('region',sort=True):
 points=np.load(ROOT/f'data/polygon/{rid}/points.npz');ids=points['objectid'];owners=points['owners'];keep=np.isin(ids[owners],g.objectid.to_numpy());xy=points['xy'][keep];oid=ids[owners[keep]];df=pd.DataFrame(dict(x=xy[:,0],y=xy[:,1],objectid=oid));dd=df[df.duplicated(['x','y'],keep=False)];shared=[(xx,yy,sorted(set(v.objectid))) for (xx,yy),v in dd.groupby(['x','y'],sort=True)]
 local=g.reset_index(drop=True);coords=local[['x','y']].to_numpy();fold=local.fold.to_numpy();objectids=local.objectid.to_numpy()
 for r in range(4):
  query=np.flatnonzero(fold==r);refs=np.flatnonzero(fold==(r+1)%4);nominal=np.flatnonzero((fold!=r)&(fold!=(r+1)%4));held=np.concatenate([query,refs]);train=nominal[cKDTree(coords[held]).query(coords[nominal])[0]>=1000] if len(nominal) and len(held) else nominal
  role={int(objectids[i]):name for name,ix in [('query',query),('reference',refs),('training',train)] for i in ix};totals={'query_reference':0,'training_query':0,'training_reference':0};cross=0
  for xx,yy,oids in shared:
   present=set(role.get(int(v),'excluded') for v in oids);present.discard('excluded');cross+=int(len(present)>1)
   for name,rr in [('query_reference',{'query','reference'}),('training_query',{'training','query'}),('training_reference',{'training','reference'})]:totals[name]+=int(rr<=present)
   if len(present)>1:details.append(dict(region=rid,rotation=r,x=xx,y=yy,objectids=oids,roles=sorted(present)))
  counts.append(dict(region=rid,rotation=r,polygon_n=len(g),sampled_point_assignments=len(df),shared_sampled_pixels_between_polygons=len(shared),cross_role_shared_pixels=cross,**totals))
pd.DataFrame(counts).to_csv(a.out/'counts.csv',index=False);(a.out/'details.json').write_text(json.dumps(details,indent=2)+'\n');(a.out/'record.json').write_text(json.dumps(dict(audited_at_utc=now(),rows=str(a.rows),scope='Sampled embedding pixel overlap only; not all polygon pixels or shared physical-neighbourhood inputs',cross_role_pixel_rotation_count=sum(v['cross_role_shared_pixels'] for v in counts)),indent=2)+'\n');print(json.dumps(dict(cross_role_pixel_rotation_count=sum(v['cross_role_shared_pixels'] for v in counts),windows=int(rows.region.nunique()))))
