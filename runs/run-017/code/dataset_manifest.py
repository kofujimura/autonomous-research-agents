"""Fix the complete, outcome-blind data set before classifier comparisons."""
import hashlib
import json
from pathlib import Path
from records import ROOT, now

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    selection=ROOT/'data/main/core-selection.json'
    regions=json.loads(selection.read_text())['regions']
    entries=[];missing=[];counts=[]
    for region in regions:
        for core in region['cores']:
            if core['reserve']:continue
            cid=core['core_id'];raw=ROOT/'data/main/cores'/cid
            meta_path=ROOT/'data/derived/features'/(cid+'.json')
            feature_path=meta_path.with_suffix('.npz')
            if not meta_path.exists() or not feature_path.exists():missing.append(cid);continue
            m=json.loads(meta_path.read_text())
            if m.get('status')!='complete' or not m['quality']['technical_coverage_pass']:
                missing.append(cid);continue
            current_sha=sha(feature_path)
            if current_sha!=m['feature_file_sha256']:raise RuntimeError('Feature hash mismatch: '+cid)
            entry=dict(core_id=cid,region_id=core['region_id'],split=core['split'],
                feature_path=str(feature_path.relative_to(ROOT)),feature_sha256=current_sha,
                metadata_path=str(meta_path.relative_to(ROOT)),metadata_sha256=sha(meta_path),
                reference_path=m['reference_path'],reference_sha256=m['reference_file_sha256'],
                raw_complete_path=str((raw/'complete.json').relative_to(ROOT)),
                raw_complete_sha256=sha(raw/'complete.json'),source_project=region['project'])
            entries.append(entry)
            objects=m['objects']
            counts.append(dict(core_id=cid,region_id=core['region_id'],split=core['split'],
                eligible_small=sum(o['main_eligible'] and o['size_bin']=='small' for o in objects),
                eligible_objects=sum(o['main_eligible'] for o in objects),
                sub_mmu=m['reference_diagnostics']['sub_mmu_objects'],
                boundary_objects=sum(not o['wholly_in_core'] for o in objects),
                zero_pixel=m['reference_diagnostics']['zero_pixel_objects']))
    out=dict(created_at_utc=now(),selection_path=str(selection.relative_to(ROOT)),selection_sha256=sha(selection),
             core_count=len(entries),missing_cores=missing,cores=entries,input_object_counts=counts,
             population='four convenience reference projects; complete selected cores; no map outcome used in inclusion')
    path=ROOT/'data/derived/dataset-manifest.json';path.parent.mkdir(parents=True,exist_ok=True)
    if missing:
        (path.parent/'dataset-incomplete.json').write_text(json.dumps(out,indent=2)+'\n')
        raise RuntimeError('Dataset incomplete; missing/failed cores: '+', '.join(missing))
    if len(entries)!=64:raise RuntimeError('Expected 64 cores under unchanged primary selection')
    if sum(x['eligible_small'] for x in counts)<200:raise RuntimeError('Fewer than 200 eligible small mapped patches')
    path.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(core_count=len(entries),small_patches=sum(x['eligible_small'] for x in counts),
        object_count=sum(x['eligible_objects'] for x in counts),manifest_sha256=sha(path)),indent=2))

if __name__=='__main__':main()
