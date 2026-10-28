"""Small preselection feasibility check; no main inference."""
import json, hashlib
from pathlib import Path
import numpy as np
import rasterio
from rasterio.warp import transform
from rasterio.windows import Window
import certifi
from records import ROOT, now, event

def main():
    start=now()
    tile=json.loads((ROOT/'data/pilot/aef-matching-tiles.json').read_text())[0]
    url=tile['path'].replace('s3://us-west-2.opendata.source.coop/','https://data.source.coop/').replace('.tiff','.vrt')
    info={'start_utc':start,'url':url,'label_probe_path':'data/pilot/nwi-sample.geojson'}
    # The published VRT refers to the anonymous S3 location. Redirect only its
    # SourceDataset to the provider's documented public HTTPS mirror, preserving
    # its vertical-flip warp. This does not change pixels or geographic metadata.
    vrt=(ROOT/'data/pilot/aef-source.vrt').read_text().replace(
        '/vsis3/us-west-2.opendata.source.coop/',
        '/vsicurl/https://data.source.coop/')
    local=ROOT/'data/pilot/aef-https.vrt';local.write_text(vrt)
    info['adaptation']='SourceDataset transport only: anonymous S3 to public HTTPS; warp preserved'
    with rasterio.Env(GDAL_HTTP_TIMEOUT='60',GDAL_HTTP_MAX_RETRY='1',
                      CURL_CA_BUNDLE=certifi.where(),GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR'):
        with rasterio.open(local) as src:
            info.update(crs=str(src.crs),shape=src.shape,bands=src.count,
                        transform=list(src.transform),blocks=src.block_shapes[:2],dtypes=src.dtypes[:2])
            x,y=transform('EPSG:4326',src.crs,[-99.05],[46.95])
            row,col=src.index(x[0],y[0]);info.update(row=row,col=col)
            raw=src.read(window=Window(col-16,row-16,32,32))
    np.savez_compressed(ROOT/'data/pilot/aef-window.npz',raw=raw)
    vec=np.sign(raw.astype('float32'))*(raw.astype('float32')/127.5)**2
    valid=(raw!=-128).all(axis=0)
    info.update(valid_pixels=int(valid.sum()),pixels=int(valid.size),shape_read=list(raw.shape),
                norm_mean=float(np.linalg.norm(vec[:,valid],axis=0).mean()),
                raw_sha256=hashlib.sha256(raw.tobytes()).hexdigest(),end_utc=now())
    (ROOT/'data/pilot/wetland-pilot-result.json').write_text(json.dumps(info,indent=2)+'\n')
    print(json.dumps(info))
    event('pilot_complete','C01 public wetland labels and a small correctly oriented embedding window obtained.',['data/pilot/wetland-pilot-result.json'])

if __name__=='__main__':main()
