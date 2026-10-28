"""Diagnose the first preserved label-decoding failure from cached bytes."""
import json
import numpy as np
from numcodecs import get_codec
from records import ROOT,now
from public_ranges import swiss_range

order=json.loads((ROOT/'data/selection-order.json').read_text())['candidates'][0]
name=order['tiles']['2021'][0]
refs=json.loads((ROOT/'data/catalogues/labels_2021.tar.json').read_text())['refs']
meta=json.loads(swiss_range(refs[name+'/.zmetadata'],2021))['metadata']
spec=meta['lnf_code/.zarray'];codec=get_codec(spec['compressor'])
result=[]
band_spec=meta['band/.zarray']
band_codec=get_codec(band_spec['compressor'])
bands=np.frombuffer(band_codec.decode(swiss_range(refs[name+'/band/0'],2021)),dtype=band_spec['dtype'])
for key,ref in refs.items():
    if not key.startswith(name+'/lnf_code/') or '/.' in key:continue
    v=np.frombuffer(codec.decode(swiss_range(ref,2021)),dtype=spec['dtype'])
    bi=int(key.split('/')[-1].split('.')[0])*spec['chunks'][0]
    vv=v.reshape(spec['chunks'])
    anomalies=[dict(original_code=int(bands[bi+i]),minimum=float(np.nanmin(b)),maximum=float(np.nanmax(b)),
                    negative_pixels=int((b< -1e-6).sum()),above_one_pixels=int((b>1+1e-6).sum()))
               for i,b in enumerate(vv) if np.nanmin(b)< -1e-6 or np.nanmax(b)>1+1e-6]
    result.append(dict(key=key,min=float(np.nanmin(v)),max=float(np.nanmax(v)),
                       negative_count=int((v<0).sum()),anomalies_by_original_code=anomalies,
                       nonfinite=int((~np.isfinite(v)).sum())))
out=dict(observed_at_utc=now(),landscape_id=order['landscape_id'],tile=name,metadata=meta,chunk_diagnostics=result)
(ROOT/'data/fraction-diagnostic-by-code.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(result,indent=2))
