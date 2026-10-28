from pathlib import Path
import json,sys,zipfile,io,time,shutil
import numpy as np
import requests,torch
from chronos import ChronosPipeline
from records import ROOT,now,digest,append
from fetch import fetch

d=ROOT/'experiments'/('P03b-ts' if len(sys.argv)>1 else 'P03-ts');d.mkdir(parents=True,exist_ok=True)
start=now();torch.set_num_threads(4);torch.manual_seed(16003)
url='https://zenodo.org/records/4656021/files/car_parts_dataset_without_missing_values.zip?download=1'
if d.name=='P03b-ts':shutil.copyfile(ROOT/'experiments/P03-ts/car-parts.zip',d/'car-parts.zip')
else:fetch(url,'experiments/P03-ts/car-parts.zip','CC BY 4.0 per Zenodo API metadata checked; research purpose. Missing values replaced by zero in source, not true demand.','Feasibility pilot only')
z=zipfile.ZipFile(d/'car-parts.zip');text=z.read(z.namelist()[0]).decode('utf-8')
(d/'car-parts.tsf').write_text(text)
rows=[]
for line in text.splitlines():
    if not line or line.startswith(('#','@')):continue
    try:y=np.array([float(x) for x in line.split(':')[-1].split(',')],dtype=np.float32)
    except ValueError:continue
    if len(y)>=36 and np.isfinite(y).all() and y[:36].sum()>0:rows.append(y)
    if len(rows)==4:break
pipe=ChronosPipeline.from_pretrained('amazon/chronos-t5-tiny',device_map='cpu',dtype=torch.float32,
                                     token=False,cache_dir=str(ROOT/'.cache/huggingface'))
y=np.stack(rows);ctx=torch.from_numpy(y[:,:36])
t=time.monotonic();pred=pipe.predict(ctx,prediction_length=6,num_samples=20).numpy();elapsed=time.monotonic()-t
np.savez_compressed(d/'forecasts.npz',context=ctx.numpy(),forecast=pred,observed=y[:,36:42])
stats=dict(pilot_id='P03',started_at_utc=start,ended_at_utc=now(),seed=16003,
           model_requested='amazon/chronos-t5-tiny',local=True,shape=list(pred.shape),
           finite_fraction=float(np.isfinite(pred).mean()),prediction_seconds=elapsed,
           lead_sum_sd=np.std(pred.sum(-1),axis=1).tolist(),source_limitation='Missing values replaced by zeros; training-corpus overlap; not main-test evidence',
           input_sha256=digest(d/'car-parts.zip'),output_sha256=digest(d/'forecasts.npz'))
(d/'result.json').write_text(json.dumps(stats,indent=2)+'\n');print(json.dumps(stats),flush=True)
