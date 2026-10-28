"""Deterministic, label-only sample preparation under protocol/plan-v1.md."""
import argparse, hashlib, io, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Geod, Transformer
from sklearn.cluster import KMeans
from record import ROOT, now

SEED = 14014
CLASSES = ['Trees', 'Grass/forb/herb', 'Shrubs']

def digest(*parts):
    return hashlib.sha256('|'.join(map(str, parts)).encode()).hexdigest()

def prepare(dest):
    dest.mkdir(parents=True,exist_ok=False)
    with zipfile.ZipFile(ROOT/'data/aef-evaluation.zip') as z:
        df=pd.read_csv(io.BytesIO(z.read('evaluation/lcmap/lcmap_lcc/lcmap_lcc.csv')))
    df['before_year']=pd.to_datetime(df.valid_time_start_before_ms,unit='ms',utc=True).dt.year
    df['after_year']=pd.to_datetime(df.valid_time_start_after_ms,unit='ms',utc=True).dt.year
    df['point_id']=[digest(f'{x:.12f}',f'{y:.12f}')[:20] for x,y in zip(df.x,df.y)]
    assert df.point_id.is_unique, 'Published paired rows should have unique plot locations'
    _,_,distance=Geod(ellps='WGS84').inv(np.full(len(df),-119.6),np.full(len(df),37.7),df.x,df.y)
    eligible=(df.label_name_before.isin(CLASSES)&df.label_name_after.isin(CLASSES)
              &df.before_year.between(2017,2020)&(df.after_year==df.before_year+1)&(distance>10000))
    df['pilot_distance_m']=distance
    base=df[eligible].copy()
    refs=base[(base.before_year==2017)&(base.label_name_before=='Trees')&(base.label_name_after=='Trees')].copy()
    base=base[~base.point_id.isin(refs.point_id)].copy()
    base['sample_hash']=[digest(SEED,p,y) for p,y in zip(base.point_id,base.before_year)]
    selected=[]
    for year,g in base.groupby('before_year'):
        for (before,after),s in g.groupby(['label_name_before','label_name_after']):
            cap=None if 'Trees' in (before,after) else (16 if before==after else 8)
            selected.append(s.sort_values('sample_hash').head(cap) if cap else s.sort_values('sample_hash'))
    targets=pd.concat(selected,ignore_index=True).sort_values('sample_hash').reset_index(drop=True)
    tx=Transformer.from_crs('EPSG:4326','EPSG:5070',always_xy=True)
    xx,yy=tx.transform(targets.x.to_numpy(),targets.y.to_numpy())
    km=KMeans(n_clusters=5,n_init=20,random_state=SEED).fit(np.column_stack([xx,yy]))
    # Lexicographic relabeling makes region numbers purely geographic and stable.
    order=np.lexsort((km.cluster_centers_[:,1],km.cluster_centers_[:,0])); remap=np.argsort(order)
    targets['region']=remap[km.labels_]
    rx,ry=tx.transform(refs.x.to_numpy(),refs.y.to_numpy())
    refs['region']=remap[km.predict(np.column_stack([rx,ry]))]
    def cell(x,y):return f'{int(np.floor((x+180)/5))}_{int(np.floor((y+90)/5))}'
    targets['block']=[cell(x,y) for x,y in zip(targets.x,targets.y)]
    targets['calibration_cell']=[int(digest(SEED,'calibration',b)[:16],16)/16**16<.3 for b in targets.block]
    targets['gain_task']=targets.label_name_before!='Trees'
    targets['loss_task']=targets.label_name_before=='Trees'
    targets['gain_positive']=targets.label_name_after=='Trees'
    targets['loss_positive']=targets.label_name_after!='Trees'
    refs['reference_hash']=[digest(SEED,'reference',p) for p in refs.point_id]
    refs=refs.sort_values('reference_hash').reset_index(drop=True)
    refs['role']=np.where(np.arange(len(refs))<len(refs)//2,'R','C')
    targets.to_csv(dest/'targets.csv',index=False); refs.to_csv(dest/'references.csv',index=False)
    tasks=[]
    for role,group in [('target',targets),('reference_pool',refs)]:
        for row in group.itertuples():
            years=range(2017,2022) if role=='reference_pool' else [row.before_year,row.after_year]
            for year in years:
                task_id=f'{row.point_id}-{year}'
                tasks.append(dict(task_id=task_id,point_id=row.point_id,x=row.x,y=row.y,year=year,role=role,
                                  order_hash=digest(SEED,'retrieval',task_id)))
    tasks=pd.DataFrame(tasks).drop_duplicates('task_id').sort_values('order_hash').reset_index(drop=True)
    tasks['batch']=np.arange(len(tasks))//64
    tasks.to_csv(dest/'tasks.csv',index=False)
    counts=targets.groupby(['before_year','label_name_before','label_name_after']).size().rename('n').reset_index()
    counts.to_csv(dest/'sample_counts.csv',index=False)
    summary=dict(created_at_utc=now(),seed=SEED,eligible_before_sampling=len(df[eligible]),
                 pilot_excluded_in_class_range=int(((distance<=10000)&df.label_name_before.isin(CLASSES)&df.label_name_after.isin(CLASSES)).sum()),
                 targets=len(targets),reference_pool=len(refs),point_year_tasks=len(tasks),batches=int(tasks.batch.max()+1),
                 region_centres_epsg5070=km.cluster_centers_[order].tolist(),
                 targets_by_region=targets.region.value_counts().sort_index().to_dict(),
                 reference_by_region=refs.region.value_counts().sort_index().to_dict(),
                 original_split_counts=targets.split.value_counts().to_dict())
    (dest/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2));print(counts.to_string(index=False))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'data/prepared')
    prepare(ap.parse_args().output)
