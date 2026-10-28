"""Small public-access pilots. They do not estimate the main recovery effect."""
import argparse,json,sys,os
from pathlib import Path
import numpy as np
from fetch import fetch
from record import ROOT,now

def c1():
    record={'candidate':'C1','checked_at_utc':now(),
      'full_text_sources':['sources/gencast.html','sources/joint-weather.html'],
      'historical_access':'FGN Section 3.2 links 2022/2023 GenCast to Earth Engine and BigQuery',
      'public_bucket':'dm_graphcast contains weights, stats and example input batches, not a located full historical ensemble archive',
      'decision':'No paid BigQuery or new account access attempted. Local full-scale generation infeasible. No adequate output archive obtained.',
      'effect_test_run':False,'feasible_without_new_permission':False}
    (ROOT/'experiments/pilot-c1/result.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record))

def c3():
    import certifi
    os.environ['SSL_CERT_FILE']=certifi.where()
    import zarr
    from affine import Affine
    dest=ROOT/'experiments'/os.environ.get('PILOT_EXPERIMENT_ID','pilot-c3')
    root_url='https://data.source.coop/tge-labs/aef-mosaic/'
    fetch(root_url+'zarr.json',str(dest.relative_to(ROOT)/'aef-root.json'),'CC BY 4.0; Google/DeepMind attribution')
    fetch(root_url+'embeddings/zarr.json',str(dest.relative_to(ROOT)/'aef-embeddings.json'),'CC BY 4.0; Google/DeepMind attribution')
    meta=json.loads((dest/'aef-root.json').read_text())
    transform=Affine(*meta['attributes']['spatial:transform'])
    # Public forest landscape near a well-known national park, no household data.
    lon,lat=-119.6,37.7
    col,row=map(int,(~transform)*(lon,lat))
    zarr.config.set({'async.concurrency':2})
    arr=zarr.open_group(root_url,mode='r',use_consolidated=False)['embeddings']
    raw=np.stack([arr[y,:,row:row+16,col:col+16] for y in [0,7]])
    np.savez_compressed(dest/'aef-raw.npz',values=raw,years=np.array([2017,2024]),lon=lon,lat=lat,row=row,col=col)
    valid=(raw!=-128).all(axis=1)
    dq=np.sign(raw.astype(float))*(raw.astype(float)/127.5)**2
    norms=np.sqrt((dq**2).sum(axis=1))
    result={'candidate':'C3','checked_at_utc':now(),'coordinate':[lon,lat],
            'shape':list(raw.shape),'valid_pixels_by_year':valid.sum(axis=(1,2)).tolist(),
            'dequantized_norm_range':[float(norms[valid].min()),float(norms[valid].max())],
            'zarr_version':zarr.__version__,'data_source':root_url,
            'licence':'CC BY 4.0','note':'Pilot location to be excluded from main sampling; no recovery effect estimated.'}
    (dest/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))

def c11():
    url='https://data.usbr.gov/rise/api/result?itemId=6123&dateTime%5Bafter%5D=2020-01-01&dateTime%5Bbefore%5D=2020-12-31&itemsPerPage=400'
    fetch(url,'experiments/pilot-c11/series.json','US government open data; provisional; agency disclaimer applies')
    result={'candidate':'C11','checked_at_utc':now(),'url':url,'note':'Access/schema pilot only; no main warning score.'}
    dat=json.loads((ROOT/'experiments/pilot-c11/series.json').read_text())
    result['top_level_keys']=list(dat.keys())
    result['rows_returned']=len(dat.get('data',[]))
    (ROOT/'experiments/pilot-c11/result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('candidate',choices=['c1','c3','c11']);a=p.parse_args()
    globals()[a.candidate]()
