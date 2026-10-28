"""Pre-score secondary sample through 2023, keeping its different label ontology."""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import CRS,Geod,Transformer
from prepare import digest
from record import ROOT,now

CROSSWALK={'Forest':'Trees','Herbaceous':'Grass/forb/herb','Shrubland':'Shrubs'}

def prepare_nlcd(output):
    output.mkdir(parents=True,exist_ok=False)
    use=['plotid','image_year','primary_cover','alternate_cover','primary_cover_subclass']
    annual=pd.read_csv(ROOT/'data/nlcd/NLCD2023_Full8360_AnnualAttributes.csv',usecols=use)
    assert not annual.duplicated(['plotid','image_year']).any()
    coords=pd.read_csv(ROOT/'data/nlcd/Plot_Coordinates_List_Simple_and_Stratified.csv')
    crs=CRS.from_wkt((ROOT/'data/nlcd/lcnext_8360_final.prj').read_text())
    coords['x_source']=coords.x;coords['y_source']=coords.y
    lon,lat=Transformer.from_crs(crs,'EPSG:4326',always_xy=True).transform(coords.x,coords.y)
    coords['x']=lon;coords['y']=lat
    existing=pd.concat([pd.read_csv(ROOT/p)[['x','y']] for p in ['data/prepared/targets.csv','data/prepared/references.csv','data/controls/controls.csv']],ignore_index=True).drop_duplicates()
    geod=Geod(ellps='WGS84');mind=[]
    ex=existing.x.to_numpy();ey=existing.y.to_numpy()
    for start in range(0,len(coords),128):
        q=coords.iloc[start:start+128];shape=(len(q),len(existing))
        qx=np.broadcast_to(q.x.to_numpy()[:,None],shape);qy=np.broadcast_to(q.y.to_numpy()[:,None],shape)
        xx=np.broadcast_to(ex[None,:],shape);yy=np.broadcast_to(ey[None,:],shape)
        distances=geod.inv(qx.ravel(),qy.ravel(),xx.ravel(),yy.ravel())[2].reshape(shape)
        mind.extend(distances.min(axis=1).tolist())
    coords['distance_to_v1_v2_m']=mind
    _,_,pilot=geod.inv(np.full(len(coords),-119.6),np.full(len(coords),37.7),coords.x,coords.y)
    coords['distance_to_pilot_m']=pilot
    allowed=coords[(coords.distance_to_v1_v2_m>1280)&(coords.distance_to_pilot_m>10000)].copy()
    before=annual[annual.image_year.between(2019,2022)].rename(columns={'image_year':'before_year',
        'primary_cover':'original_before','alternate_cover':'alternate_before','primary_cover_subclass':'subclass_before'})
    after=annual[annual.image_year.between(2020,2023)].rename(columns={'image_year':'after_year',
        'primary_cover':'original_after','alternate_cover':'alternate_after','primary_cover_subclass':'subclass_after'})
    after['before_year']=after.after_year-1
    pairs=before.merge(after,on=['plotid','before_year'],validate='one_to_one').merge(allowed,on='plotid',validate='many_to_one')
    pairs=pairs[pairs.original_before.isin(CROSSWALK)&pairs.original_after.isin(CROSSWALK)].copy()
    pairs['label_name_before']=pairs.original_before.map(CROSSWALK);pairs['label_name_after']=pairs.original_after.map(CROSSWALK)
    pairs['sample_hash']=[digest(14014,'nlcd_sample',p,y) for p,y in zip(pairs.plotid,pairs.before_year)]
    chosen=[]
    for (year,b,a),g in pairs.groupby(['before_year','label_name_before','label_name_after']):
        cap=None if (b!=a and 'Trees' in [a,b]) else (50 if b==a=='Trees' else (25 if b==a else 8))
        chosen.append(g.sort_values('sample_hash').head(cap) if cap else g.sort_values('sample_hash'))
    t=pd.concat(chosen,ignore_index=True).sort_values('sample_hash').reset_index(drop=True)
    t['feature_point_id']='nlcd-'+t.plotid.astype(str)
    t['point_id']=t.feature_point_id+'-pair'+t.before_year.astype(str)
    assert t.point_id.is_unique
    centres=np.array(json.loads((ROOT/'data/prepared/summary.json').read_text())['region_centres_epsg5070'])
    xx,yy=Transformer.from_crs('EPSG:4326','EPSG:5070',always_xy=True).transform(t.x,t.y)
    t['region']=np.argmin(((np.column_stack([xx,yy])[:,None,:]-centres[None,:,:])**2).sum(2),axis=1)
    t['block']=[f'{int(np.floor((x+180)/5))}_{int(np.floor((y+90)/5))}' for x,y in zip(t.x,t.y)]
    t['calibration_cell']=False
    t['gain_task']=t.label_name_before!='Trees';t['loss_task']=t.label_name_before=='Trees'
    t['gain_positive']=t.label_name_after=='Trees';t['loss_positive']=t.label_name_after!='Trees'
    t['unambiguous']=(t.original_before==t.alternate_before)&(t.original_after==t.alternate_after)
    t['horizon']=np.where(t.before_year>=2021,'beyond_2021','overlapping_2019_2021')
    t.to_csv(output/'targets.csv',index=False)
    tasks=[]
    for r in t.itertuples():
        for year in [r.before_year,r.after_year]:
            tid=f'{r.feature_point_id}-{year}'
            tasks.append(dict(task_id=tid,point_id=r.feature_point_id,x=r.x,y=r.y,year=year,
                              role='nlcd_target',order_hash=digest(14014,'retrieval',tid)))
    for path,role in [('data/prepared/references.csv','reference_pool_future'),('data/controls/controls.csv','extra_non_tree_control_future')]:
        for r in pd.read_csv(ROOT/path).itertuples():
            for year in [2022,2023]:
                tid=f'{r.point_id}-{year}'
                tasks.append(dict(task_id=tid,point_id=r.point_id,x=r.x,y=r.y,year=year,role=role,
                                  order_hash=digest(14014,'retrieval',tid)))
    tasks=pd.DataFrame(tasks).drop_duplicates('task_id').sort_values('order_hash').reset_index(drop=True)
    tasks['batch']=np.arange(len(tasks))//64;tasks.to_csv(output/'tasks.csv',index=False)
    summary=dict(created_at_utc=now(),seed=14014,pairs=len(t),unique_plots=t.plotid.nunique(),
                 point_year_tasks=len(tasks),batches=int(tasks.batch.max()+1),
                 source_plots=len(coords),excluded_near_v1_v2=int((coords.distance_to_v1_v2_m<=1280).sum()),
                 excluded_pilot=int((coords.distance_to_pilot_m<=10000).sum()),
                 unambiguous_pairs=int(t.unambiguous.sum()),by_horizon=t.horizon.value_counts().to_dict(),
                 min_distance_selected_m=float(t.distance_to_v1_v2_m.min()),
                 endpoint='NLCD Forest class, not LCMAP dominant Trees',coordinate_crs=crs.to_wkt())
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    t.groupby(['before_year','original_before','original_after']).size().rename('n').reset_index().to_csv(output/'sample-counts.csv',index=False)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'data/nlcd/prepared')
    prepare_nlcd(p.parse_args().output)
