"""Save common random simple-random-sample draws for all planned comparisons."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from records import ROOT,now,digest

PAIRS=[(2022,2023),(2023,2024),(2024,2025),(2021,2022),(2022,2025)]
def make(manifest_path,destination):
    m=json.loads((ROOT/manifest_path).read_text());out=ROOT/destination
    if out.exists():raise FileExistsError('Preserve prior audit draws')
    out.mkdir(parents=True);rows=[]
    for r in m['landscapes']:
        if r['status']!='included' or r['split']!='test':continue
        lid=r['landscape_id'];N=r['valid_points']
        for a,b in PAIRS:
            seed=int.from_bytes(hashlib.sha256(f'16016/audit/{lid}/{a}/{b}'.encode()).digest()[:8],'little')
            rng=np.random.default_rng(seed)
            dtype=np.uint16 if N<=65535 else np.uint32
            ia=np.stack([rng.choice(N,512,replace=False).astype(dtype) for _ in range(500)])
            ib=np.stack([rng.choice(N,512,replace=False).astype(dtype) for _ in range(500)])
            path=out/f'{lid}-{a}-{b}.npz';np.savez_compressed(path,a=ia,b=ib,N=N,seed=seed)
            rows.append(dict(landscape_id=lid,year_a=a,year_b=b,primary=(a,b) in PAIRS[:3],
                             N=N,replications=500,budgets=[32,64,128,256,512],seed=seed,
                             path=str(path.relative_to(ROOT)),sha256=digest(path)))
    obj=dict(created_at_utc=now(),manifest_path=manifest_path,manifest_sha256=digest(ROOT/manifest_path),
             sampling='Independent uniform ordered samples without replacement; prefixes give each budget; use same a indices in both years for paired design',
             draws=rows)
    (out/'manifest.json').write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps(dict(completed_at_utc=now(),units=len(rows),destination=destination)))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--destination',required=True)
    a=p.parse_args();make(a.manifest,a.destination)
