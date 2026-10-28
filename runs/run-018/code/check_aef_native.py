"""Check direct source-TIFF coordinates against an archived main-study VRT patch."""
import json,time,hashlib
import numpy as np,rasterio
from rasterio.windows import Window
from collect_embeddings import GDAL
from records import ROOT,now

def main():
 folder=ROOT/'data/main/R01';saved=np.load(folder/'aef-2024.npz');meta=json.loads((folder/'aef-2024-record.json').read_text());url=meta['reads'][0]['url'];xy=saved['xy'][0];expected=saved['raw'][0]
 t0=time.monotonic();stamp=now()
 with rasterio.Env(**GDAL):
  with rasterio.open('/vsicurl/'+url) as src:
   rc=np.array([src.index(*p) for p in xy]);r0=int(rc[:,0].min());c0=int(rc[:,1].min());r1=int(rc[:,0].max())+1;c1=int(rc[:,1].max())+1
   arr=src.read(window=Window(c0,r0,c1-c0,r1-r0));actual=np.array([arr[:,r-r0,c-c0] for r,c in rc]);same=np.array_equal(expected,actual)
   result=dict(start_time_utc=stamp,end_time_utc=now(),elapsed_seconds=time.monotonic()-t0,url=url,transform=list(src.transform),shape=list(src.shape),blocks=src.block_shapes[:1],interleave=src.profile.get('interleave'),compression=str(src.compression),all64bands_and9pixels_identical=bool(same),different_values=int((actual!=expected).sum()),source_window=[c0,r0,c1-c0,r1-r0],scope='Instrument coordinate/transport check on one archived primary patch, not a matching-effect experiment')
 out=ROOT/'analysis/native-source-check';out.mkdir(exist_ok=True)
 np.savez_compressed(out/'raw.npz',actual=actual,expected=expected,xy=xy,native_window=arr)
 (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
 assert same
if __name__=='__main__':main()
