"""Outcome-blind common cohort for the fixed alternate-year comparison."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
from derive_features import derive
from analysis_paths import paths
from records import ROOT,now

def prepare(root,out):
 root=Path(root).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False);years=[2024,2023,2021];inputs={};rows={};arrays={};hashes={}
 for year in years:
  if year==2024:folder=root/paths(root)['primary_features']
  else:
   folder=out/'raw-derived'/str(year);derive(root,folder,year=year,aef_overrides=root/'data/corrections')
   assert not json.loads((folder/f'missing-{year}.json').read_text()),'Incomplete annual inputs; preserve and report'
  inputs[year]=folder;rows[year]=json.loads((folder/f'rows-{year}.json').read_text());arrays[year]=np.load(folder/f'features-{year}.npz')
  for p in [folder/f'rows-{year}.json',folder/f'features-{year}.npz']:hashes[str(p.relative_to(root)) if p.is_relative_to(root) else str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
 original=rows[2024];n=len(original);keep=np.ones(n,bool);quality={};ids=[r['objectid'] for r in original]
 for year in years:
  assert [r['objectid'] for r in rows[year]]==ids,'Annual rows/windows differ before common-cohort filtering'
  for key in ['vegetation','regime','x','y','fold','region','interior_margin_m','image_year']:
   assert [r[key] for r in rows[year]]==[r[key] for r in original],(year,key)
  a=arrays[year];assert np.array_equal(a['hydro'],arrays[2024]['hydro'],equal_nan=True);assert np.array_equal(a['hydro_names'],arrays[2024]['hydro_names']);names=a['hydro_names'].tolist()
  valid=np.isfinite(a['aef']).all(axis=1)&np.isfinite(a['tessera']).all(axis=1)&np.isfinite(a['hydro'][:,names.index('elevation_mean90')])&np.asarray([r['interior_margin_m']>=15 for r in rows[year]])
  quality[year]=dict(eligible_n=int(valid.sum()),excluded_ids=[int(ids[i]) for i in np.flatnonzero(~valid)]);keep&=valid
 assert keep.any(),'No common cohort'
 output_hashes={}
 for year in years:
  folder=out/str(year);folder.mkdir();a=arrays[year];np.savez_compressed(folder/f'features-{year}.npz',**{k:a[k][keep] for k in ['hydro','aef','tessera','aef_norm','tessera_norm']},hydro_names=a['hydro_names']);(folder/f'rows-{year}.json').write_text(json.dumps([r for r,k in zip(rows[year],keep) if k],indent=2)+'\n')
  for p in folder.iterdir():output_hashes[str(p.relative_to(out))]=hashlib.sha256(p.read_bytes()).hexdigest()
 raw_hashes={}
 for year in years:
  for rid in sorted(set(r['region'] for r in original)):
   for product in ['aef','tessera']:
    p=root/f'data/corrections/{rid}/{product}-{year}.npz'
    if not p.exists():p=root/f'data/main/{rid}/{product}-{year}.npz'
    assert p.exists();raw_hashes[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
 record=dict(prepared_at_utc=now(),years=years,original_n=n,common_n=int(keep.sum()),excluded_n=int((~keep).sum()),common_ids=[int(v) for v,k in zip(ids,keep) if k],reuse_original_2024_fits=bool(keep.all()),year_quality=quality,physical_arrays_identical=True,region_counts={rid:sum(r['region']==rid and bool(k) for r,k in zip(original,keep)) for rid in sorted(set(r['region'] for r in original))},input_feature_sha256=hashes,raw_input_sha256=raw_hashes,output_sha256=output_hashes,scope='Fixed inventory labels and2024physical covariates; embedding-year agreement diagnostic only')
 (out/'manifest.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items() if k not in ['common_ids','input_feature_sha256','raw_input_sha256','output_sha256']}));return record

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--out',type=Path,required=True);a=p.parse_args();prepare(a.root,a.out)
