"""Select the prospectively specified native-grid checks without change outcomes."""
import json
import numpy as np,pandas as pd
from pyproj import Transformer
from records import ROOT,now,digest

def choose():
    path=ROOT/'data/census-cases.json'
    if path.exists():raise FileExistsError('Keep the frozen case selection')
    latest={}
    for line in (ROOT/'data/selection-results.jsonl').read_text().splitlines():
        r=json.loads(line);latest[r['landscape_id']]=r
    counts={s:sum(r['status']=='accepted' and r['split']==s for r in latest.values()) for s in ['train','calibration','test']}
    assert counts=={'train':20,'calibration':10,'test':30},'Wait for planned landscape selection'
    taxonomy=json.loads((ROOT/'data/taxonomy.json').read_text())
    frame=pd.read_csv(ROOT/'sources/swisscrop25-crop-classes.csv').dropna(subset=['Crop_Label_lv1','Crop_Label_lv3'])
    parents=dict(frame[['Crop_Label_lv1','Crop_Label_lv3']].values);level=np.array([parents.get(s,'Undefined') for s in taxonomy['fine']])
    index=pd.read_csv(ROOT/'data/aef-swiss-index.csv');to_ll=Transformer.from_crs(32632,4326,always_xy=True)
    eligible=[]
    order=json.loads((ROOT/'data/selection-order.json').read_text())['candidates']
    for item in order:
        lid=item['landscape_id'];r=latest.get(lid)
        if not r or r['status']!='accepted' or r['split']!='test':continue
        left=r['left'];top=r['top'];right=left+5120;bottom=top-5120
        lons,_=to_ll.transform([left,left,right,right],[top,bottom,top,bottom])
        if min(lons)<6 or max(lons)>=12:continue
        files={}
        for year in range(2021,2026):
            match=index[(index.year==year)&(index.utm_zone=='32N')&(index.utm_west<=left)&
                        (index.utm_east>=right)&(index.utm_south<=bottom)&(index.utm_north>=top)]
            if match.empty:break
            files[str(year)]=match.sort_values('path').iloc[0].to_dict()
        if len(files)!=5:continue
        with np.load(ROOT/r['path']) as z:
            baseline=level[z['fine_raster'][0][z['baseline_agricultural']]]
        eligible.append(dict(landscape_id=lid,left=left,top=top,point_label_path=r['path'],point_label_sha256=digest(ROOT/r['path']),
                             baseline_arable_fraction=float((baseline=='Arable Land').mean()),
                             baseline_grassland_fraction=float((baseline=='Grassland').mean()),aef_files=files))
    selected=[];missing=[]
    for stratum in ['arable_dominated','grassland_dominated','remaining']:
        found=next((r for r in eligible if r['landscape_id'] not in [v['landscape_id'] for v in selected]
                    and (stratum=='remaining' or r['baseline_arable_fraction' if stratum=='arable_dominated' else 'baseline_grassland_fraction']>.5)),None)
        if found is None:missing.append(stratum)
        else:selected.append(dict(found,stratum=stratum))
    result=dict(selected_at_utc=now(),plan_path='protocol/plan-v3-census-check.md',counts=counts,
                selection_order_sha256=digest(ROOT/'data/selection-order.json'),eligible_case_ids=[r['landscape_id'] for r in eligible],
                selected=selected,unavailable_strata=missing,
                selection_uses='2021 reference agricultural category shares and static source geometry; no diversity change or classifier output')
    path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':choose()
