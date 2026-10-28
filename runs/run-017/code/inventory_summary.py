"""Describe the reference population without making model-based exclusions."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from records import ROOT,now

def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',default='data/derived/dataset-manifest.json')
    p.add_argument('--out',default='analysis');a=p.parse_args()
    manifest=json.loads((ROOT/a.manifest).read_text());cores=[];objects=[];sources={}
    for e in sorted(manifest['cores'],key=lambda x:x['core_id']):
        m=json.loads((ROOT/e['metadata_path']).read_text())
        with np.load(ROOT/e['reference_path']) as f:
            valid=f['valid'].astype(bool);y=f['y'].astype(bool)
            row=dict(core_id=e['core_id'],region_id=e['region_id'],split=e['split'],
                valid_pixels=int(valid.sum()),positive_pixels=int(np.sum(y&valid)),negative_pixels=int(np.sum(~y&valid)),
                reference_scoring_empty=bool(not np.any(valid)),
                empty_positive=not np.any(y&valid),**m['reference_diagnostics'])
        row.update(technical_common_valid_fraction=m['quality']['common_valid_fraction'],
            minimum_season_clear_fraction=min(m['quality']['seasonal_clear_fractions']))
        cores.append(row)
        for o in m['objects']:
            objects.append(dict(**o,split=e['split']))
            for sid in o['source_ids']:sources.setdefault(sid,set()).add(e['split'])
    c=pd.DataFrame(cores);o=pd.DataFrame(objects);out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
    c.to_csv(out/'inventory-cores.csv',index=False,float_format='%.17g')
    counts=[]
    for (region,split),part in c.groupby(['region_id','split'],sort=True):
        patches=o[(o.region_id==region)&(o.split==split)]
        eligible=patches[patches.main_eligible]
        row=dict(region_id=region,split=split,cores=len(part),valid_pixels=int(part.valid_pixels.sum()),
            positive_pixels=int(part.positive_pixels.sum()),empty_positive_cores=int(part.empty_positive.sum()),
            empty_scoring_cores=int(part.reference_scoring_empty.sum()),
            eligible_patches=len(eligible),eligible_small_patches=int(np.sum(eligible.size_bin=='small')),
            contained_sub_mmu=int(np.sum(patches.wholly_in_core&(patches.vector_area_m2<2000))),
            boundary_crossing=int(np.sum(~patches.wholly_in_core)),
            zero_raster_pixels=int(np.sum(patches.wholly_in_core&(patches.raster_pixels==0))),
            zero_valid_pixels=int(np.sum(patches.wholly_in_core&(patches.valid_pixels==0))),
            vector_small_zero_centers=int(np.sum(patches.wholly_in_core&(patches.vector_area_m2>=2000)&
                (patches.vector_area_m2<10000)&(patches.raster_pixels==0))),
            vector_small_zero_valid=int(np.sum(patches.wholly_in_core&(patches.vector_area_m2>=2000)&
                (patches.vector_area_m2<10000)&(patches.valid_pixels==0))),
            eligible_small_no_20m_interior=int(np.sum((eligible.size_bin=='small')&(eligible.interior_pixels==0))),
            eligible_small_90_percent_valid=int(np.sum((eligible.size_bin=='small')&(eligible.valid_fraction>=.9))))
        counts.append(row)
    pd.DataFrame(counts).to_csv(out/'inventory-summary.csv',index=False)
    shared_train_test=sum('train' in roles and 'test' in roles for roles in sources.values())
    summary=dict(generated_at_utc=now(),cores=len(c),eligible_small_patches=int(np.sum(o.main_eligible&(o.size_bin=='small'))),
        source_polygons_appearing_in_train_and_test_buffers=shared_train_test,
        source_polygons_appearing_in_multiple_roles=sum(len(roles)>1 for roles in sources.values()),
        explanation='Buffer-source overlap is not pixel overlap; complete test objects are checked separately below.')
    train_ids={sid for sid,roles in sources.items() if 'train' in roles}
    summary['eligible_test_patches_sharing_any_training_buffer_source']=sum(
        row['split']=='test' and row['main_eligible'] and bool(set(row['source_ids'])&train_ids) for row in objects)
    (out/'inventory-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
