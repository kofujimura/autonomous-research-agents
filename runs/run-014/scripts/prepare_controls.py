"""Additional baseline non-tree control cohort specified before score analysis."""
import io,json,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Geod,Transformer
from prepare import digest
from record import ROOT,now

def prepare_controls(output):
    output.mkdir(parents=True,exist_ok=False)
    with zipfile.ZipFile(ROOT/'data/aef-evaluation.zip') as z:
        df=pd.read_csv(io.BytesIO(z.read('evaluation/lcmap/lcmap_lcc/lcmap_lcc.csv')))
    df['before_year']=pd.to_datetime(df.valid_time_start_before_ms,unit='ms',utc=True).dt.year
    df['after_year']=pd.to_datetime(df.valid_time_start_after_ms,unit='ms',utc=True).dt.year
    df['point_id']=[digest(f'{x:.12f}',f'{y:.12f}')[:20] for x,y in zip(df.x,df.y)]
    used=set(pd.read_csv(ROOT/'data/prepared/targets.csv').point_id)|set(pd.read_csv(ROOT/'data/prepared/references.csv').point_id)
    _,_,d=Geod(ellps='WGS84').inv(np.full(len(df),-119.6),np.full(len(df),37.7),df.x,df.y)
    df=df[(df.before_year==2017)&(df.after_year==2018)&(df.label_name_before==df.label_name_after)
          &df.label_name_before.isin(['Grass/forb/herb','Shrubs'])&~df.point_id.isin(used)&(d>10000)].copy()
    df['selection_hash']=[digest(14014,'extra_control',p) for p in df.point_id]
    df=df.sort_values('selection_hash').groupby('label_name_before').head(32).copy().reset_index(drop=True)
    centres=np.array(json.loads((ROOT/'data/prepared/summary.json').read_text())['region_centres_epsg5070'])
    xx,yy=Transformer.from_crs('EPSG:4326','EPSG:5070',always_xy=True).transform(df.x,df.y)
    df['region']=np.argmin(((np.column_stack([xx,yy])[:,None,:]-centres[None,:,:])**2).sum(2),axis=1)
    df.to_csv(output/'controls.csv',index=False)
    tasks=[]
    for r in df.itertuples():
        for year in range(2017,2022):
            tid=f'{r.point_id}-{year}'
            tasks.append(dict(task_id=tid,point_id=r.point_id,x=r.x,y=r.y,year=year,
                              role='extra_non_tree_control',order_hash=digest(14014,'retrieval',tid)))
    tasks=pd.DataFrame(tasks).sort_values('order_hash').reset_index(drop=True);tasks['batch']=np.arange(len(tasks))//64
    tasks.to_csv(output/'tasks.csv',index=False)
    summary=dict(created_at_utc=now(),seed=14014,controls=len(df),point_year_tasks=len(tasks),
                 by_initial_class=df.label_name_before.value_counts().to_dict(),
                 by_region=df.region.value_counts().sort_index().to_dict(),batches=int(tasks.batch.max()+1))
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':prepare_controls(ROOT/'data/controls')
