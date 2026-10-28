"""Compare an orientation-aware raw COG read with a saved source-VRT read."""
import argparse,json,time,requests
import certifi,numpy as np,rasterio
from rasterio.windows import Window
from records import ROOT,now,digest

lid='L065_150';year=2021
with np.load(ROOT/f'data/landscapes/{lid}.npz') as z:xs=z['point_x'];ys=z['point_y']
with np.load(ROOT/f'data/features/{lid}-{year}-alphaearth.npz') as z:
    expected=z['raw_values'];vrt_rows=z['native_row'];vrt_cols=z['native_col']
record=next(json.loads(x) for x in (ROOT/'data/embedding_reads.jsonl').read_text().splitlines() if json.loads(x)['year']==year)
p=argparse.ArgumentParser();p.add_argument('--s3',action='store_true');args=p.parse_args()
url=record['raw_cog_url'];start=now();begin=time.monotonic();headers={}
if args.s3:
    original=url
    url='https://s3.us-west-2.amazonaws.com/us-west-2.opendata.source.coop/'+url.split('data.source.coop/',1)[1]
    session=requests.Session();session.trust_env=False
    for label,target in [('published_gateway',original),('published_s3_bucket',url)]:
        r=session.head(target,timeout=(20,30));headers[label]=dict(status=r.status_code,
                       content_length=r.headers.get('Content-Length'),etag=r.headers.get('ETag'),
                       request_charged=r.headers.get('x-amz-request-charged'))
        (ROOT/'data/aef-s3-endpoint-headers.json').write_text(json.dumps(dict(observed_at_utc=now(),headers=headers),indent=2)+'\n')
        r.raise_for_status()
    assert headers['published_gateway']['etag']==headers['published_s3_bucket']['etag']
    assert headers['published_gateway']['content_length']==headers['published_s3_bucket']['content_length']
with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',GDAL_NUM_THREADS='1',AWS_NO_SIGN_REQUEST='YES',
                  AWS_EC2_METADATA_DISABLED='TRUE',GDAL_HTTP_MAX_RETRY=2,GDAL_HTTP_TIMEOUT=90,
                  GDAL_HTTP_CONNECTTIMEOUT=20,GDAL_HTTP_RETRY_DELAY=1,CPL_VSIL_CURL_CHUNK_SIZE=524288,
                  CPL_VSIL_CURL_CACHE_SIZE=256*1024**2,
                  GDAL_HTTP_CA_BUNDLE=certifi.where(),GDAL_CACHEMAX=512*1024**2):
    with rasterio.open(url) as src:
        print('OPENED',str(src.crs),src.transform,list(set(src.block_shapes)),flush=True)
        rr,cc=rasterio.transform.rowcol(src.transform,xs,ys);rr=np.asarray(rr,int);cc=np.asarray(cc,int)
        assert np.array_equal(cc,vrt_cols)
        assert np.array_equal(rr,src.height-1-vrt_rows)
        r0=int(rr.min());c0=int(cc.min());h=int(rr.max())-r0+1;w=int(cc.max())-c0+1
        block=src.read(window=Window(c0,r0,w,h),out_dtype='int8',masked=False)
        got=block[:,rr-r0,cc-c0].T
        out=dict(started_at_utc=start,ended_at_utc=now(),elapsed_seconds=time.monotonic()-begin,
                 url=url,transform=list(src.transform),block_shapes=src.block_shapes,
                 exact_match=bool(np.array_equal(got,expected)),different_values=int((got!=expected).sum()),
                 compared_values=int(got.size),point_count=len(xs),row_reversal_identity=True,
                 endpoint_headers=headers,
                 saved_vrt_extract_sha256=digest(ROOT/f'data/features/{lid}-{year}-alphaearth.npz'))
(ROOT/('data/aef-s3-read-validation.json' if args.s3 else 'data/aef-direct-read-validation.json')).write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out),flush=True)
assert out['exact_match']
