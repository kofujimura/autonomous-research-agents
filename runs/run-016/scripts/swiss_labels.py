"""Decode public SwissCrop25 fractional labels and select fixed landscapes."""
import argparse,hashlib,json,time
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from numcodecs import get_codec
from records import ROOT,now,digest,append
from public_ranges import swiss_range,read_range

YEARS=list(range(2021,2026)); SEED=16016
QUOTAS={'train':20,'calibration':10,'test':30}
CAT=ROOT/'data/catalogues'
OUT=ROOT/'data/landscapes';OUT.mkdir(parents=True,exist_ok=True)

def stable_seed(text):
    return int.from_bytes(hashlib.sha256(str(text).encode()).digest()[:8],'little')

def mapping():
    d=pd.read_csv(CAT/'metadata_crop_classes.csv')
    d=d.dropna(subset=['LNF_code','Crop_Label_lv1','Crop_Label_lv2','Crop_Label_lv3'])
    fine=sorted(d.Crop_Label_lv1.unique());broad=sorted(d.Crop_Label_lv2.unique())
    parents={};ag={};codes={}
    for row in d.itertuples(index=False):
        f=fine.index(row.Crop_Label_lv1);b=broad.index(row.Crop_Label_lv2)
        if f in parents:assert parents[f]==b
        parents[f]=b
        ag[f]=row.Crop_Label_lv3 in ['Arable Land','Grassland','Permanent']
        code=int(row.LNF_code)
        if code in codes:assert codes[code]==f
        codes[code]=f
    obj=dict(fine=fine,broad=broad,fine_to_broad=[parents[i] for i in range(len(fine))],
             fine_is_agricultural=[ag[i] for i in range(len(fine))],
             original_code_to_fine={str(k):v for k,v in codes.items()},
             source_sha256=digest(CAT/'metadata_crop_classes.csv'))
    p=ROOT/'data/taxonomy.json'
    if p.exists():assert json.loads(p.read_text())==obj
    else:p.write_text(json.dumps(obj,indent=2)+'\n')
    return obj

class LabelReader:
    def __init__(self):
        self.indices={}
        m=json.loads((ROOT/'data/catalogue-manifest.json').read_text())
        self.base=m['swiss_resolve_base']
        self.lookup=mapping()
        self.decoder_checked=False
    def refs(self,year):
        if year not in self.indices:
            flat=json.loads((CAT/f'labels_{year}.tar.json').read_text())['refs']
            groups={}
            for key,value in flat.items():
                if '/' not in key:continue  # Root .zgroup/.zattrs are not tile members.
                name,sub=key.split('/',1)
                groups.setdefault(name,{})[sys.intern(sub)]=value
            self.indices[year]=groups
        return self.indices[year]
    def tile(self,year,name):
        refs=self.refs(year)
        # A tile's tar members are contiguous. Fetch their full span once.
        selected=refs[name]
        ranges=[v for v in selected.values() if isinstance(v,list)]
        lo=min(int(v[1]) for v in ranges);hi=max(int(v[1])+int(v[2]) for v in ranges)
        raw=read_range(self.base+f'labels/{year}.tar',lo,hi-lo)
        def member(key):
            v=selected[key]
            if isinstance(v,list):return raw[int(v[1])-lo:int(v[1])+int(v[2])-lo]
            if v.startswith('base64:'):
                import base64
                return base64.b64decode(v[7:])
            return v.encode()
        meta=json.loads(member('.zmetadata'))['metadata']
        def array(name):
            spec=meta[name+'/.zarray'];shape=tuple(spec['shape']);chunks=tuple(spec['chunks'])
            result=np.full(shape,np.nan if np.dtype(spec['dtype']).kind=='f' else 0,dtype=spec['dtype'])
            codec=get_codec(spec['compressor']) if spec.get('compressor') else None
            grid=tuple((s+c-1)//c for s,c in zip(shape,chunks))
            for index in np.ndindex(*grid):
                key=name+'/'+'.'.join(map(str,index))
                if key not in selected:continue
                body=member(key);body=codec.decode(body) if codec else body
                block=np.frombuffer(body,dtype=spec['dtype']).reshape(chunks,order=spec.get('order','C'))
                sl=tuple(slice(i*c,min((i+1)*c,s)) for i,c,s in zip(index,chunks,shape))
                result[sl]=block[tuple(slice(0,x.stop-x.start) for x in sl)]
            return result
        bands=array('band');xs=array('lon');ys=array('lat');values=array('lnf_code')
        assert values.shape==(len(bands),128,128)
        assert np.isfinite(xs).all() and np.isfinite(ys).all()
        # Labels are spatially north-up after sorting coordinate arrays.
        ix=np.argsort(xs);iy=np.argsort(ys)[::-1]
        values=values[:,iy][:,:,ix];xs=xs[ix];ys=ys[iy]
        assert np.allclose(np.diff(xs),10) and np.allclose(np.diff(ys),-10)
        if not self.decoder_checked:
            # A second library path checks manual chunk layout/codec handling.
            import zarr
            from zarr.storage import MemoryStore
            from zarr.core.buffer.cpu import Buffer
            store=MemoryStore(store_dict={k:Buffer.from_bytes(member(k)) for k in selected})
            group=zarr.open_group(store=store,mode='r')
            oracle=np.asarray(group['lnf_code'][:])[:,iy][:,:,ix]
            assert np.array_equal(values,oracle,equal_nan=True)
            check=dict(observed_at_utc=now(),year=year,tile=name,manual_equals_zarr=True,
                       raw_array_sha256=hashlib.sha256(values.tobytes()).hexdigest(),
                       x_first=float(xs[0]),y_first=float(ys[0]),bands=bands.tolist(),
                       sum_all_bands_min=float(np.nanmin(values.sum(axis=0))),
                       sum_all_bands_max=float(np.nanmax(values.sum(axis=0))),
                       note='Second software decoding path run by the same session; not independent reproduction')
            dest=ROOT/'data/decoder-crosschecks.jsonl';append(str(dest.relative_to(ROOT)),check)
            self.decoder_checked=True
        # Original code 0 is an unmapped residual/background band and can
        # be negative when source coverage overlaps. It is never a crop.
        # Do not apply a sign assertion to an unused background band.
        grouped=np.zeros((len(self.lookup['fine']),128,128),np.float32)
        unknown=np.zeros((128,128),np.float32)
        unmapped=[]
        for code,band in zip(bands,values):
            f=self.lookup['original_code_to_fine'].get(str(int(code)))
            if f is None:
                if np.nansum(band)>0:unmapped.append(int(code))
                unknown+=np.nan_to_num(band,nan=0.)
                continue
            assert np.nanmin(band)>=-1e-6, 'Negative mapped crop/land-cover fraction'
            grouped[f]+=np.nan_to_num(band,nan=0.)
        mass=grouped.sum(axis=0)
        largest=grouped.max(axis=0)
        fine=grouped.argmax(axis=0).astype(np.uint8)
        fine[(mass<=0)|(unknown>largest)]=255
        broad=np.full((128,128),255,np.uint8)
        valid=fine!=255
        broad[valid]=np.array(self.lookup['fine_to_broad'],np.uint8)[fine[valid]]
        isag=np.zeros((128,128),bool)
        isag[valid]=np.array(self.lookup['fine_is_agricultural'])[fine[valid]]
        return dict(fine=fine,broad=broad,isag=isag,xs=xs,ys=ys,
                    diagnostics=dict(unmapped_codes=unmapped,coverage_min=float(mass.min()),
                                     coverage_max=float(mass.max()),range_bytes=len(raw),
                                     raw_negative_values=int((values < -1e-6).sum()),
                                     raw_above_one_values=int((values > 1+1e-6).sum())))

def candidates():
    p=ROOT/'data/selection-order.json'
    if p.exists():return json.loads(p.read_text())
    tiles=pd.read_parquet(CAT/'metadata_tiles.parquet').drop(columns='geometry')
    d=tiles[(tiles.year.isin(YEARS))&tiles.labels_tile.notna()].copy()
    d['r']=d.row_index.astype(int);d['c']=d.col_index.astype(int)
    x0=np.unique(d.left-d.c*1280);y0=np.unique(d.top+d.r*1280)
    assert len(x0)==len(y0)==1
    x0=int(x0[0]);y0=int(y0[0])
    table={(int(r.year),r.r,r.c):str(r.labels_tile) for r in d.itertuples()}
    possible=[]
    for r0 in range(0,int(d.r.max())+1,5):
        for c0 in range(0,int(d.c.max())+1,5):
            if not all((y,r,c) in table for y in YEARS for r in range(r0,r0+4) for c in range(c0,c0+4)):continue
            left=x0+c0*1280;top=y0-r0*1280
            group=f'{left//25600},{top//25600}'
            k=stable_seed(f'{SEED}/split/{group}')%6
            split='train' if k<2 else 'calibration' if k==2 else 'test'
            possible.append(dict(landscape_id=f'L{r0:03d}_{c0:03d}',r0=r0,c0=c0,left=left,top=top,
                                 split=split,supercell=group,
                                 tiles={str(y):[table[y,r,c] for r in range(r0,r0+4) for c in range(c0,c0+4)] for y in YEARS}))
    rng=np.random.default_rng(SEED);rng.shuffle(possible)
    obj=dict(seed=SEED,created_at_utc=now(),grid_origin_left=x0,grid_origin_top=y0,
             metadata_sha256=digest(CAT/'metadata_tiles.parquet'),quotas=QUOTAS,candidates=possible)
    p.write_text(json.dumps(obj,indent=2)+'\n')
    return obj

def collect(batch,retry_failed=False,max_seconds=1650,ledger_path='data/selection-results.jsonl',
            output_path='data/landscapes',order_items=None,quotas=None,distinct_supercells=False,should_stop=None):
    begin=time.monotonic()
    order=candidates()['candidates'] if order_items is None else order_items;reader=LabelReader()
    ledger=ROOT/ledger_path;output=ROOT/output_path;output.mkdir(parents=True,exist_ok=True)
    limits=QUOTAS if quotas is None else quotas
    records=[json.loads(x) for x in ledger.read_text().splitlines()] if ledger.exists() else []
    latest={r['landscape_id']:r for r in records}
    attempted=set(latest)
    completed={lid for lid,r in latest.items() if not (retry_failed and r['status']=='failed')}
    counts={s:sum(r['status']=='accepted' and r['split']==s for r in latest.values()) for s in limits}
    accepted_cells={r['supercell'] for r in latest.values() if r['status']=='accepted'}
    done=0
    for item in order:
        if should_stop is not None and should_stop():break
        lid=item['landscape_id'];split=item['split']
        if lid in completed or counts[split]>=limits[split]:continue
        if distinct_supercells and item['supercell'] in accepted_cells:continue
        if len(attempted)>=200 or done>=batch or time.monotonic()-begin>max_seconds-180:break
        start=now();print('START',lid,split,start,flush=True)
        rec=dict(landscape_id=lid,split=split,started_at_utc=start,supercell=item['supercell'])
        try:
            rasters=[];diagnostics=[]
            for year in YEARS:
                fine=np.full((512,512),255,np.uint8);broad=fine.copy();ag=np.zeros_like(fine,bool)
                for k,name in enumerate(item['tiles'][str(year)]):
                    v=reader.tile(year,name);r=k//4;c=k%4
                    sl=np.s_[r*128:(r+1)*128,c*128:(c+1)*128]
                    fine[sl]=v['fine'];broad[sl]=v['broad'];ag[sl]=v['isag']
                    # Source pixel centres must agree with metadata within floating error.
                    # Public vectors contain upper-left coordinates, not centres.
                    # The sample coordinates below use the centre of each 10m cell.
                    assert np.allclose(v['xs'],item['left']+c*1280+np.arange(128)*10,atol=.01)
                    assert np.allclose(v['ys'],item['top']-r*1280-np.arange(128)*10,atol=.01)
                    diagnostics.append(dict(year=year,tile=name,**v['diagnostics']))
                rasters.append((fine,broad,ag))
                if year==2021 and ag.mean()<.1:break
            ag0=rasters[0][2];rec['baseline_agricultural_pixels']=int(ag0.sum())
            if len(rasters)!=5:rec.update(status='ineligible',reason='2021 agricultural fraction below 10%')
            else:
                support=np.logical_and.reduce([r[2] for r in rasters]);n=int(support.sum())
                rec.update(stable_agricultural_pixels=n,stable_fraction=float(support.mean()))
                if support.mean()<.1 or n<4096:
                    rec.update(status='ineligible',reason='Five-year stable support below preplanned eligibility')
                else:
                    rng=np.random.default_rng(stable_seed(f'{SEED}/population/{lid}'))
                    points=rng.choice(np.flatnonzero(support.ravel()),4096,replace=False)
                    fine=np.stack([r[0] for r in rasters]);broad=np.stack([r[1] for r in rasters])
                    rows,cols=np.unravel_index(points,support.shape)
                    xs=item['left']+5+cols*10;ys=item['top']-5-rows*10
                    dest=output/(lid+'.npz')
                    temp=dest.with_name(dest.name+'.tmp.npz')
                    np.savez_compressed(temp,years=YEARS,point_indices=points,point_x=xs,point_y=ys,
                                        fine=fine[:,rows,cols],broad=broad[:,rows,cols],
                                        fine_raster=fine,broad_raster=broad,support=support,baseline_agricultural=ag0,
                                        fine_census=np.stack([np.bincount(f[support],minlength=len(reader.lookup['fine'])) for f in fine]),
                                        broad_census=np.stack([np.bincount(b[support],minlength=len(reader.lookup['broad'])) for b in broad]))
                    if dest.exists():dest.rename(dest.with_name(dest.name+'.orphan-'+now().replace(':','-')))
                    temp.replace(dest)
                    rec.update(status='accepted',path=str(dest.relative_to(ROOT)),sha256=digest(dest),
                               point_count=4096,left=item['left'],top=item['top'])
                    counts[split]+=1
                    accepted_cells.add(item['supercell'])
            rec['diagnostics']=diagnostics
        except Exception as e:
            rec.update(status='failed',reason=repr(e))
            import traceback
            traceback.print_exc()
        rec['ended_at_utc']=now();append(ledger_path,rec)
        attempted.add(lid);done+=1
        print('END',lid,rec['status'],counts,flush=True)
    print(json.dumps(dict(completed_at_utc=now(),accepted=counts,attempted=len(attempted),batch_attempts=done)),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--batch',type=int,default=12)
    p.add_argument('--retry-failed',action='store_true');p.add_argument('--max-seconds',type=int,default=1650)
    a=p.parse_args();collect(a.batch,a.retry_failed,a.max_seconds)
