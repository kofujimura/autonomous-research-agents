"""Acquire lossless native-grid inputs for one preselected census case."""
import argparse,json,time
from pathlib import Path
import numpy as np,rasterio,certifi
from rasterio.windows import Window
from geotessera import GeoTesseraZarr
from geotessera.store import _time_index
from records import ROOT,now,digest,append

def save(path,**arrays):
    temporary=path.with_name(path.name+'.tmp.npz');np.savez_compressed(temporary,**arrays)
    temporary.replace(path)

def acquire(lid):
    selection=json.loads((ROOT/'data/census-cases.json').read_text())
    case=next(r for r in selection['selected'] if r['landscape_id']==lid)
    out=ROOT/'data/census'/lid;out.mkdir(parents=True,exist_ok=True)
    if (out/'case-result.json').exists():raise FileExistsError('Census case already completed')
    with np.load(ROOT/case['point_label_path']) as z:
        point_indices=z['point_indices'];support=z['support'];fine=z['fine_raster'];broad=z['broad_raster']
    for year in range(2021,2026):
        for rep in ['tessera','alphaearth']:
            assert (ROOT/f'data/features/{lid}-{year}-{rep}.npz').exists(),'Wait for matching primary point extracts'
    gt=GeoTesseraZarr(cache_dir=ROOT/'.cache/tessera-census',cache_max_size=256*1024**2)
    ds=gt.open_zone(zone=32);group=gt._zone_arrays(32);a=ds.attrs['spatial:transform']
    assert a[0]==10 and a[4]==-10 and str(ds.tessera.crs)=='EPSG:32632'
    c0=int(round((case['left']-a[2])/10));r0=int(round((a[5]-case['top'])/10))
    assert abs(a[2]+10*c0-case['left'])<1e-6 and abs(a[5]-10*r0-case['top'])<1e-6
    assert c0>=0 and r0>=0
    common=np.ones(512*512,bool);entries=[];checks=[]
    for year in range(2021,2026):
        size=sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file() and not p.is_symlink())
        if size+512*1024**2>10*1024**3:raise RuntimeError('Insufficient storage headroom before next census year')
        for rep in ['tessera','alphaearth']:
            path=out/f'{year}-{rep}.npz';started=now();print('CENSUS',lid,year,rep,started,flush=True)
            if not path.exists():
                if rep=='tessera':
                    ti=_time_index(ds,year)
                    quant=np.asarray(group['embeddings'][ti,:,r0:r0+512,c0:c0+512])
                    scale=np.asarray(group['scales'][ti,r0:r0+512,c0:c0+512])
                    assert quant.shape==(128,512,512) and quant.dtype==np.int8 and scale.shape==(512,512)
                    raw=np.moveaxis(quant,0,-1).reshape(-1,128)
                    save(path,raw_values=raw,scales=scale.ravel())
                    provenance=dict(url=gt.url,dataset=str(gt.dataset),model_version=gt.model_version,
                                    year=year,global_window=[c0,r0,512,512],global_transform=a,
                                    native_quantization='int8 * float32 scale; nonfinite scales yield missing')
                else:
                    row=case['aef_files'][str(year)]
                    relative=row['path'].split('/tge-labs/aef/',1)[1]
                    vrt='https://data.source.coop/tge-labs/aef/'+relative.rsplit('.',1)[0]+'.vrt'
                    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',GDAL_NUM_THREADS='1',AWS_NO_SIGN_REQUEST='YES',
                                      AWS_EC2_METADATA_DISABLED='TRUE',GDAL_HTTP_MAX_RETRY=2,GDAL_HTTP_TIMEOUT=90,
                                      GDAL_HTTP_CONNECTTIMEOUT=20,GDAL_HTTP_RETRY_DELAY=1,
                                      GDAL_HTTP_CA_BUNDLE=certifi.where(),GDAL_CACHEMAX=128*1024**2):
                        with rasterio.open(vrt) as src:
                            assert str(src.crs)=='EPSG:32632' and src.transform.a==10 and src.transform.e==-10
                            cc=(case['left']-src.transform.c)/10;rr=(src.transform.f-case['top'])/10
                            assert abs(cc-round(cc))<1e-6 and abs(rr-round(rr))<1e-6
                            block=src.read(window=Window(int(round(cc)),int(round(rr)),512,512),out_dtype='int8',masked=False)
                            assert block.shape==(64,512,512)
                            raw=np.moveaxis(block,0,-1).reshape(-1,64);save(path,raw_values=raw)
                            provenance=dict(url=vrt,raw_cog_url=vrt.rsplit('.',1)[0]+'.tiff',year=year,
                                            transform=list(src.transform),window=[int(round(cc)),int(round(rr)),512,512],
                                            hash_scope='Lossless native int8 numerical grid extract; full COG not downloaded')
                entry=dict(landscape_id=lid,year=year,representation=rep,started_at_utc=started,ended_at_utc=now(),
                           path=str(path.relative_to(ROOT)),sha256=digest(path),provenance=provenance)
                append('data/census-reads.jsonl',entry)
                path.with_suffix('.json').write_text(json.dumps(entry,indent=2)+'\n')
            entry=json.loads(path.with_suffix('.json').read_text());assert digest(path)==entry['sha256'];entries.append(entry)
            with np.load(path) as grid,np.load(ROOT/f'data/features/{lid}-{year}-{rep}.npz') as points:
                if rep=='tessera':
                    raw=grid['raw_values'];scale=grid['scales'];valid=np.isfinite(scale)
                    selected=raw[point_indices].astype(np.float32)*np.where(np.isfinite(scale[point_indices]),scale[point_indices],np.nan)[:,None]
                    expected=points['values']
                else:
                    raw=grid['raw_values'];valid=(raw!=-128).all(axis=1)
                    selected=raw[point_indices];expected=points['raw_values']
                assert np.array_equal(selected,expected,equal_nan=True),'Native grid and primary point values differ'
                common &= valid
                checks.append(dict(year=year,representation=rep,compared_points=len(point_indices),bitwise_equal=True))
            print('VALIDATED',lid,year,rep,flush=True)
    mask=support.ravel()&common;N=int(mask.sum());assert N>=2048
    label_path=out/'labels.npz';save(label_path,years=np.arange(2021,2026),fine=fine.reshape(5,-1),broad=broad.reshape(5,-1),
                                   original_support=support,common_support=mask.reshape(512,512),point_indices=point_indices)
    result=dict(landscape_id=lid,stratum=case['stratum'],completed_at_utc=now(),
                plan_path='protocol/plan-v3-census-check.md',case_selection_sha256=digest(ROOT/'data/census-cases.json'),
                point_label_path=case['point_label_path'],point_label_sha256=case['point_label_sha256'],
                path=str(label_path.relative_to(ROOT)),sha256=digest(label_path),split='test',left=case['left'],top=case['top'],
                valid_points=N,valid_indices=np.flatnonzero(mask).tolist(),
                stable_agricultural_pixels=int(support.sum()),excluded_for_features=int(support.sum()-mask.sum()),
                baseline_arable_fraction=case['baseline_arable_fraction'],baseline_grassland_fraction=case['baseline_grassland_fraction'],
                feature_inputs=[{k:e[k] for k in ['path','sha256','year','representation']} for e in entries],
                point_grid_crosschecks=checks,status='included')
    (out/'case-result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(completed_at_utc=now(),landscape_id=lid,native_population=N,crosschecks=len(checks))),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('landscape_id');a=p.parse_args();acquire(a.landscape_id)
