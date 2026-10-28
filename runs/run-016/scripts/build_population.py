"""Freeze the common valid finite populations after planned data collection."""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from records import ROOT,now,digest

def build(destination,source_only=False):
    taxonomy=json.loads((ROOT/'data/taxonomy.json').read_text())
    fine_ids=np.flatnonzero(taxonomy['fine_is_agricultural']).tolist()
    broad_ids=sorted(set(taxonomy['fine_to_broad'][i] for i in fine_ids))
    csv=ROOT/'sources/swisscrop25-crop-classes.csv'
    assert digest(csv)==taxonomy['source_sha256']
    parent=dict(pd.read_csv(csv).dropna(subset=['Crop_Label_lv1','Crop_Label_lv3'])[['Crop_Label_lv1','Crop_Label_lv3']].values)
    levels=np.array([parent.get(name,'Undefined') for name in taxonomy['fine']])
    labels={}
    for line in (ROOT/'data/selection-results.jsonl').read_text().splitlines():
        r=json.loads(line);labels[r['landscape_id']]=r
    feature_records={}
    for line in (ROOT/'data/feature-results.jsonl').read_text().splitlines():
        r=json.loads(line);feature_records[r['landscape_id'],r['year'],r['representation']]=r
    rows=[]
    for lid,r in labels.items():
        if r['status']!='accepted':continue
        if source_only and r['split']=='test':continue
        rec={k:r.get(k) for k in ['landscape_id','split','path','sha256','left','top','supercell',
                                  'baseline_agricultural_pixels','stable_agricultural_pixels']}
        valid=np.ones(4096,bool);inputs=[];missing=[]
        required_years=list(range(2021,2026)) if r['split']=='test' else [2021]
        rec['required_feature_years']=required_years
        for y in range(2021,2026):
            if source_only and y!=2021:continue
            for rep in ['tessera','alphaearth']:
                fr=feature_records.get((lid,y,rep))
                if not fr or fr['status']!='completed':
                    if y in required_years:missing.append([y,rep])
                    continue
                p=ROOT/fr['path'];assert digest(p)==fr['sha256']
                with np.load(p) as z:
                    v=np.isfinite(z['values']).all(axis=1) if rep=='tessera' else (z['raw_values']!=-128).all(axis=1)
                    assert v.shape==(4096,)
                    if y in required_years:valid &= v
                inputs.append(dict(path=fr['path'],sha256=fr['sha256'],year=y,representation=rep))
        if missing:rec.update(status='incomplete',missing=missing)
        elif valid.sum()<2048:rec.update(status='excluded_embedding_missingness',valid_points=int(valid.sum()),feature_inputs=inputs)
        else:rec.update(status='included',valid_indices=np.flatnonzero(valid).tolist(),valid_points=int(valid.sum()),
                        feature_inputs=inputs,missing_points=int((~valid).sum()))
        if rec['status']=='included':
            with np.load(ROOT/rec['path']) as z:baseline=levels[z['fine_raster'][0][z['baseline_agricultural']]]
            rec.update(baseline_arable_fraction=float((baseline=='Arable Land').mean()),
                       baseline_grassland_fraction=float((baseline=='Grassland').mean()))
        rows.append(rec)
    obj=dict(created_at_utc=now(),plan_path='protocol/plan-v2.md',seed=16016,years=list(range(2021,2026)),
             source_only=source_only,
             taxonomy_path='data/taxonomy.json',taxonomy_sha256=digest(ROOT/'data/taxonomy.json'),
             fine_ids=fine_ids,broad_ids=broad_ids,
             fine_names=[taxonomy['fine'][i] for i in fine_ids],broad_names=[taxonomy['broad'][i] for i in broad_ids],
             landscapes=rows,counts={s:sum(r['status']=='included' and r['split']==s for r in rows)
                                    for s in ['train','calibration','test']},
             status_counts={s:sum(r['status']==s for r in rows) for s in sorted(set(r['status'] for r in rows))})
    p=ROOT/destination
    if p.exists():raise FileExistsError('Keep prior manifests; specify a new destination')
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps({k:obj[k] for k in ['created_at_utc','counts','status_counts']}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('destination');p.add_argument('--source-only',action='store_true')
    a=p.parse_args();build(a.destination,a.source_only)
