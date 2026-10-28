"""Describe all shared-pixel differences without dropping measurement records."""
from pathlib import Path
import argparse,json
import numpy as np,pandas as pd
from records import ROOT,now
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);counts=[];examples=[]
for folder in sorted((ROOT/'data/polygon').glob('R??')):
 rid=folder.name;x=np.load(folder/'points.npz');xy=x['xy'];offsets=x['offsets'];owners=x['owners'];ids=x['objectid'];na=np.load(folder/'aef-2024.npz')['raw'];ntfile=np.load(folder/'tessera-2024.npz');nt=ntfile['raw'];ns=ntfile['scales'];pa=np.load(ROOT/f'data/main/{rid}/aef-2024.npz');pt=np.load(ROOT/f'data/main/{rid}/tessera-2024.npz');oa=pa['raw'];ot=pt['raw'];os=pt['scales'];op=pa['xy'];inside=pa['inside'];c=dict(region=rid,shared=0,aef_both_valid_equal=0,aef_both_valid_different=0,aef_old_missing_new_valid=0,aef_old_valid_new_missing=0,aef_both_missing=0,tessera_raw_or_scale_different=0)
 for k,oid in enumerate(ids):
  lo,hi=offsets[k:k+2];lookup={tuple(point):j for j,point in enumerate(xy[lo:hi],start=int(lo))}
  for j in np.flatnonzero(inside[k]):
   i=lookup.get(tuple(op[k,j]))
   if i is None:continue
   c['shared']+=1;old_valid=bool((oa[k,j]!=-128).all());new_valid=bool((na[i]!=-128).all());equal=bool(np.array_equal(oa[k,j],na[i]))
   tag='aef_both_valid_equal' if old_valid and new_valid and equal else 'aef_both_valid_different' if old_valid and new_valid else 'aef_old_missing_new_valid' if not old_valid and new_valid else 'aef_old_valid_new_missing' if old_valid and not new_valid else 'aef_both_missing';c[tag]+=1
   td=not(np.array_equal(ot[k,j],nt[i]) and np.array_equal(np.asarray(os[k,j]),np.asarray(ns[i]),equal_nan=True));c['tessera_raw_or_scale_different']+=int(td)
   if (not equal or td) and len(examples)<100:examples.append(dict(region=rid,objectid=int(oid),xy=op[k,j].tolist(),primary_patch_index=int(j),polygon_point_index=int(i),aef_tag=tag,aef_different_components=int((oa[k,j]!=na[i]).sum()),old_raw=oa[k,j].tolist(),new_raw=na[i].tolist(),tessera_different=td))
 counts.append(c)
pd.DataFrame(counts).to_csv(a.out/'counts.csv',index=False);(a.out/'examples.json').write_text(json.dumps(examples,indent=2)+'\n');(a.out/'record.json').write_text(json.dumps(dict(checked_at_utc=now(),scope='Diagnostic after failed strict shared-pixel assertion; all original/new raw measurements retained'),indent=2)+'\n');print(pd.DataFrame(counts).to_string(index=False))
