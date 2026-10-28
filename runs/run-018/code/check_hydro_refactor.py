"""Required exact archive check for the new optional point sampler."""
from pathlib import Path
import json,numpy as np
from derive_features import hydro
from records import ROOT,now
original=np.load(ROOT/'analysis/features/features-2024.npz');names=original['hydro_names'].tolist();rows=json.loads((ROOT/'analysis/features/rows-2024.json').read_text());index={v['objectid']:i for i,v in enumerate(rows)};checks=[]
for folder in sorted((ROOT/'data/main').glob('R??')):
 fs=json.loads((folder/'selected.geojson').read_text())['features'];nn,h=hydro(folder);ix=[index[f['properties']['objectid']] for f in fs];expected=original['hydro'][ix];same=nn==names and np.array_equal(h,expected,equal_nan=True);checks.append(dict(region=folder.name,rows=len(h),values=int(h.size),exact_equal=same));assert same,folder
out=ROOT/'analysis/hydro-refactor-check';out.mkdir(exist_ok=False);(out/'result.json').write_text(json.dumps(dict(checked_at_utc=now(),checks=checks,exact_equal=True,total_values=sum(v['values'] for v in checks)),indent=2)+'\n');print(json.dumps(checks))
