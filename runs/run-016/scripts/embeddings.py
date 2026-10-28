"""Collect exact numerical embedding extracts at preselected public label points."""
import argparse,json,traceback,time,hashlib
from pathlib import Path
import certifi
import numpy as np
import pandas as pd
from pyproj import Transformer
import rasterio
from rasterio.windows import Window
from geotessera import GeoTesseraZarr
from records import ROOT,now,digest,append

OUT=ROOT/'data/features';OUT.mkdir(parents=True,exist_ok=True)
TO_LL=Transformer.from_crs(32632,4326,always_xy=True)
GT=None

def source_index():
    dest=ROOT/'data/aef-swiss-index.csv'
    if dest.exists():return pd.read_csv(dest)
    cols=['path','crs','year','utm_zone','utm_west','utm_south','utm_east','utm_north',
          'wgs84_west','wgs84_south','wgs84_east','wgs84_north']
    d=pd.read_parquet(ROOT/'data/catalogues/aef_index.parquet',columns=cols)
    d=d[(d.year.between(2021,2025))&(d.wgs84_west<=11)&(d.wgs84_east>=5.5)&
        (d.wgs84_south<=48)&(d.wgs84_north>=45.5)&d.utm_zone.isin(['31N','32N'])]
    d=d.sort_values(['year','path']).reset_index(drop=True);d.to_csv(dest,index=False)
    return d

def tessera(xs,ys,year):
    global GT
    if GT is None:GT=GeoTesseraZarr(cache_dir=ROOT/'.cache/tessera',cache_max_size=256*1024**2)
    lons,lats=TO_LL.transform(xs,ys)
    coords=list(zip(lons.tolist(),lats.tolist()))
    values=GT.sample_points(coords,year=year,cross_zone=False,search_px=0)
    zones=np.floor((lons+180)/6).astype(int)+1
    rows=np.full(len(xs),-1,np.int32);cols=rows.copy();dist=np.full(len(xs),np.nan,np.float32)
    metadata=[]
    for zone in np.unique(zones):
        ds=GT.open_zone(zone=int(zone));crs=ds.tessera.crs
        affine=ds.attrs['spatial:transform']
        assert affine[0]==10 and affine[4]==-10 and affine[1]==affine[3]==0
        sub=zones==zone
        tr=Transformer.from_crs(4326,crs,always_xy=True)
        ex,ny=tr.transform(lons[sub],lats[sub])
        cc=np.floor((ex-affine[2])/10).astype(int)
        rr=np.floor((affine[5]-ny)/10).astype(int)
        cols[sub]=cc;rows[sub]=rr
        dist[sub]=np.hypot(ex-(affine[2]+(cc+.5)*10),ny-(affine[5]-(rr+.5)*10))
        assert dist[sub].max()<7.072
        p=ROOT/f'data/tessera-zone-{zone}-metadata.json'
        if not p.exists():
            p.write_text(json.dumps(dict(obtained_at_utc=now(),url=GT.url,dataset=str(GT.dataset),
                  model_version=GT.model_version,zone=int(zone),attrs=ds.attrs),indent=2)+'\n')
        metadata.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p)))
    assert values.shape==(len(xs),128)
    return dict(values=values,native_row=rows,native_col=cols,native_zone=zones,pixel_distance_m=dist),\
           dict(url=GT.url,dataset=str(GT.dataset),model_version=GT.model_version,metadata=metadata,
                nearby_valid_search=False,cross_zone_repair=False)

def alphaearth(xs,ys,year,index):
    lons,lats=TO_LL.transform(xs,ys);zones=np.floor((lons+180)/6).astype(int)+1
    values=np.full((len(xs),64),-128,np.int8)
    rows=np.full(len(xs),-1,np.int32);cols=rows.copy();file_ids=np.full(len(xs),-1,np.int32)
    distance=np.full(len(xs),np.nan,np.float32);sources=[]
    for zone in np.unique(zones):
        mask=zones==zone;ids=np.flatnonzero(mask)
        tr=Transformer.from_crs(32632,32600+int(zone),always_xy=True)
        ex,ny=tr.transform(xs[mask],ys[mask])
        candidates=index[(index.year==year)&(index.utm_zone==f'{zone}N')]
        for fid,row in candidates.iterrows():
            take=(ex>=row.utm_west)&(ex<row.utm_east)&(ny>=row.utm_south)&(ny<row.utm_north)
            take &= file_ids[ids]<0
            if not take.any():continue
            selected=ids[take];xx=ex[take];yy=ny[take]
            path=row.path
            assert '/tge-labs/aef/' in path
            relative=path.split('/tge-labs/aef/',1)[1]
            vrt='https://data.source.coop/tge-labs/aef/'+relative.rsplit('.',1)[0]+'.vrt'
            started=now()
            with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',GDAL_NUM_THREADS='1',
                              AWS_NO_SIGN_REQUEST='YES',AWS_EC2_METADATA_DISABLED='TRUE',
                              GDAL_HTTP_MAX_RETRY=2,GDAL_HTTP_RETRY_DELAY=1,
                              GDAL_HTTP_TIMEOUT=90,GDAL_HTTP_CONNECTTIMEOUT=20,
                              GDAL_HTTP_USERAGENT='FreeResearch016/1.0 public dataset research',
                              CURL_CA_BUNDLE=certifi.where(),GDAL_HTTP_CA_BUNDLE=certifi.where(),
                              GDAL_CACHEMAX=128*1024**2):
                with rasterio.open(vrt) as src:
                    assert src.count==64 and src.transform.a==10 and src.transform.e==-10
                    rr,cc=rasterio.transform.rowcol(src.transform,xx,yy)
                    rr=np.asarray(rr,dtype=int);cc=np.asarray(cc,dtype=int)
                    assert rr.min()>=0 and cc.min()>=0 and rr.max()<src.height and cc.max()<src.width
                    r0=int(rr.min());c0=int(cc.min());h=int(rr.max())-r0+1;w=int(cc.max())-c0+1
                    assert h*w<=1024**2,'Unexpectedly large window; do not fetch full COG'
                    # No resampling or overview: exact native-resolution window.
                    block=src.read(window=Window(c0,r0,w,h),out_dtype='int8',masked=False)
                    v=block[:,rr-r0,cc-c0].T
                    values[selected]=v;rows[selected]=rr;cols[selected]=cc;file_ids[selected]=int(fid)
                    cx,cy=rasterio.transform.xy(src.transform,rr,cc,offset='center')
                    distance[selected]=np.hypot(xx-np.asarray(cx),yy-np.asarray(cy))
                    assert distance[selected].max()<7.072
                    rec=dict(requested_at_utc=started,completed_at_utc=now(),url=vrt,
                             raw_cog_url=vrt.rsplit('.',1)[0]+'.tiff',year=year,
                             crs=str(src.crs),transform=list(src.transform),width=src.width,height=src.height,
                             block_shapes=src.block_shapes,window=[c0,r0,w,h],point_count=len(selected),
                             raw_vector_sha256=__import__('hashlib').sha256(v.tobytes()).hexdigest(),
                             file_id=int(fid),full_source_object_sha256=None,
                             hash_scope='Exact downloaded int8 numerical point extract; entire COG not downloaded',
                             bottom_up_corrected_by_source_vrt=True)
                    sources.append(rec);append('data/embedding_reads.jsonl',rec)
    return dict(raw_values=values,native_row=rows,native_col=cols,native_zone=zones,
                source_file_id=file_ids,pixel_distance_m=distance),dict(sources=sources,
                index_path='data/aef-swiss-index.csv',index_sha256=digest(ROOT/'data/aef-swiss-index.csv'),
                decode='sign(q)*(q/127.5)^2; q=-128 is missing')

def collect(batch,all_training_years=False,max_seconds=1650,shard=0,shards=1):
    begin=time.monotonic()
    latest={}
    for line in (ROOT/'data/selection-results.jsonl').read_text().splitlines():
        r=json.loads(line);latest[r['landscape_id']]=r
    index=source_index();done=0;failures=0
    completed={}
    fp=ROOT/'data/feature-results.jsonl'
    if fp.exists():
        for line in fp.read_text().splitlines():
            fr=json.loads(line);completed[fr['landscape_id'],fr['year'],fr['representation']]=fr
    # Source data can fix the frozen head while target reads continue.
    # This changes retrieval order only; candidate selection is unchanged.
    queue=sorted(latest.items(),key=lambda item:item[1].get('split')=='test')
    for lid,rec in queue:
        if rec['status']!='accepted':continue
        if int.from_bytes(hashlib.sha256(lid.encode()).digest()[:4],'little')%shards!=shard:continue
        labelpath=ROOT/rec['path']
        with np.load(labelpath) as labels:
            xs=labels['point_x'];ys=labels['point_y']
        required_years=list(range(2021,2026)) if rec['split']=='test' or (all_training_years and rec['split']=='train') else [2021]
        pending=[(y,rep) for y in required_years for rep in ['tessera','alphaearth']
                 if not ((fr:=completed.get((lid,y,rep))) and fr['status']=='completed' and
                         (OUT/f'{lid}-{y}-{rep}.npz').exists() and digest(OUT/f'{lid}-{y}-{rep}.npz')==fr['sha256'])]
        if not pending:continue
        if done>=batch:break
        for year,rep in pending:
            if time.monotonic()-begin>max_seconds-300:
                print('BOUNDED BATCH END: reserve time before next read',flush=True)
                print(json.dumps(dict(completed_at_utc=now(),landscapes_attempted=done,failures=failures)),flush=True)
                if failures:raise SystemExit(1)
                return
            started=now();p=OUT/f'{lid}-{year}-{rep}.npz'
            print('START',lid,year,rep,started,flush=True)
            entry=dict(landscape_id=lid,year=year,representation=rep,started_at_utc=started,
                       input_label_path=rec['path'],input_label_sha256=digest(labelpath))
            try:
                arrays,provenance=tessera(xs,ys,year) if rep=='tessera' else alphaearth(xs,ys,year,index)
                temp=p.with_name(p.name+'.tmp.npz');np.savez_compressed(temp,**arrays)
                if p.exists():p.rename(p.with_name(p.name+'.orphan-'+now().replace(':','-')))
                temp.replace(p)
                finite=np.isfinite(arrays['values']).all(axis=1) if rep=='tessera' else (arrays['raw_values']!=-128).all(axis=1)
                entry.update(status='completed',path=str(p.relative_to(ROOT)),sha256=digest(p),
                             finite_points=int(finite.sum()),total_points=len(xs),provenance=provenance)
                print('END',lid,year,rep,'finite',int(finite.sum()),flush=True)
            except Exception as e:
                entry.update(status='failed',error=repr(e));traceback.print_exc();failures+=1
            entry['ended_at_utc']=now();append('data/feature-results.jsonl',entry)
        done+=1
    print(json.dumps(dict(completed_at_utc=now(),landscapes_attempted=done,failures=failures)),flush=True)
    if failures:raise SystemExit(1)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--batch',type=int,default=2)
    p.add_argument('--all-training-years',action='store_true');p.add_argument('--max-seconds',type=int,default=1650)
    p.add_argument('--shard',type=int,default=0);p.add_argument('--shards',type=int,default=1)
    a=p.parse_args();assert 0<=a.shard<a.shards
    collect(a.batch,a.all_training_years,a.max_seconds,a.shard,a.shards)
