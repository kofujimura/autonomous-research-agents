"""Feasibility probes only; no main-study outcome comparisons."""
import argparse
from pathlib import Path
import json
import urllib.parse
import urllib.request
import hashlib
import numpy as np
from records import ROOT, now, append
from web_record import fetch

def wetland():
    import pandas as pd
    import rasterio
    from rasterio.windows import Window
    base='https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer/0'
    fetch(base+'?f=pjson','data/pilot/fws-layer.json','D002-meta',
          'US federal public data; source limitations apply','Pilot layer schema')
    schema=json.loads((ROOT/'data/pilot/fws-layer.json').read_text())
    print('schema',schema.get('name'),[x['name'] for x in schema.get('fields',[])],flush=True)
    params=dict(f='geojson',where='1=1',geometry='-95.07,45.96,-94.95,46.04',
                geometryType='esriGeometryEnvelope',inSR=4326,outSR=4326,
                spatialRel='esriSpatialRelIntersects',outFields='*',returnGeometry='true',
                resultRecordCount=500)
    url=base+'/query?'+urllib.parse.urlencode(params)
    fetch(url,'data/pilot/wetlands.geojson','D002',
          'USFWS public-domain federal wetland inventory; planning data, not legal delineation',
          'Pilot count and geometry access')
    data=json.loads((ROOT/'data/pilot/wetlands.geojson').read_text())
    print('wetland_features',len(data.get('features',[])),'exceeded',data.get('exceededTransferLimit'),flush=True)
    if data.get('error'):print('query_error',data['error'],flush=True)
    tile=json.loads((ROOT/'data/pilot/aef_pilot_tile.json').read_text())[0]
    url=tile['path'].replace('gs://','https://storage.googleapis.com/',1)
    with rasterio.open(url) as src:
        from rasterio.warp import transform
        x,y=transform('EPSG:4326',src.crs,[-95],[46])
        row,col=src.index(x[0],y[0])
        window=Window(col-64,row-64,128,128)
        values=src.read(window=window)
        profile=src.profile.copy()
        profile.update(width=128,height=128,transform=src.window_transform(window))
        with rasterio.open(ROOT/'data/pilot/embedding-window.tif','w',**profile) as dst:dst.write(values)
    valid=np.all(values!=-128,axis=0)
    decoded=np.sign(values.astype(float))*(values.astype(float)/127.5)**2
    norm=np.sqrt((decoded**2).sum(axis=0))
    result=dict(observed_at_utc=now(),wetland_features=len(data.get('features',[])),
        reference_truncated=data.get('exceededTransferLimit',False),shape=list(values.shape),
        valid_pixels=int(valid.sum()),median_decoded_norm=float(np.median(norm[valid])),
        aef_source_url=url,main_outcomes_compared=False)
    path='data/pilot/embedding-window.tif'
    append('sources.jsonl',dict(source_id='D003',url=url,obtained_at_utc=now(),
        path=path,sha256=hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),
        license='CC BY 4.0; AlphaEarth Foundations Satellite Embedding dataset produced by Google and Google DeepMind',
        retrieval='rasterio ordinary HTTPS range read; 128x128 window at -95,46; no authentication or billing',bundled=True))
    (ROOT/'data/pilot/P01-result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

def weather():
    result=dict(observed_at_utc=now(),sources=[],usable_unauthenticated_archive=False)
    url='https://developers.google.com/weathernext/guides/models-wn-gen'
    r=fetch(url,'data/pilot/weathernext-gen.html','D004',
            'Official data access documentation','P02 archive feasibility')
    from bs4 import BeautifulSoup
    text=BeautifulSoup((ROOT/r['path']).read_text(),'html.parser').get_text(' ',strip=True)
    for word in ['deprecated','July 29, 2026','Cloud Storage','access','Earth Engine']:
        i=text.find(word)
        print(word,text[max(0,i-80):i+500])
    result['sources'].append(r['path'])
    result['note']='Official documented Earth Engine/BigQuery routes checked; no usable unauthenticated trajectory archive established in pilot. Full-model inference is not a fallback.'
    (ROOT/'data/pilot/P02-result.json').write_text(json.dumps(result,indent=2)+'\n')

def load():
    url='https://data.open-power-system-data.org/time_series/2020-10-06/datapackage.json'
    r=fetch(url,'data/pilot/opsd-datapackage.json','D005','Licence in data package','P03 licence and availability')
    package=json.loads((ROOT/r['path']).read_text())
    print('licences',package.get('licenses'))
    print('resources',[(x.get('name'),x.get('path')) for x in package.get('resources',[])])
    m='https://huggingface.co/amazon/chronos-t5-tiny/raw/main/config.json'
    fetch(m,'data/pilot/chronos-tiny-config.json','D006','Apache 2.0 model card to check','P03 small model availability')
    print('model_config',json.loads((ROOT/'data/pilot/chronos-tiny-config.json').read_text()))
    result=dict(observed_at_utc=now(),data_package_obtained=True,small_model_config_obtained=True,
        inference_run=False,note='Access-only feasibility; generic temporal aggregation has close prior work, so no large model dependency added at selection stage.')
    (ROOT/'data/pilot/P03-result.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('pilot',choices=['wetland','weather','load']);a=p.parse_args()
    {'wetland':wetland,'weather':weather,'load':load}[a.pilot]()
