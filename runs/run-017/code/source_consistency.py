"""Check repeated inventory-source identities across bundled raw core responses."""
import hashlib
import json
from pathlib import Path
from records import ROOT,now

def main():
    seen={};conflicts=[];appearances=0
    for directory in sorted((ROOT/'data/main/cores').iterdir()):
        if not (directory/'complete.json').exists():continue
        for path in sorted(directory.glob('nwi-batch-*.geojson')):
            for f in json.loads(path.read_text())['features']:
                sid=int(f['properties']['OBJECTID']);appearances+=1
                value=dict(geometry=f['geometry'],properties=f['properties'])
                digest=hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
                if sid in seen and seen[sid]['sha256']!=digest:
                    conflicts.append(dict(source_id=sid,first=seen[sid],later=dict(core_id=directory.name,sha256=digest)))
                else:seen[sid]=dict(core_id=directory.name,sha256=digest)
    out=ROOT/'analysis';out.mkdir(exist_ok=True)
    result=dict(checked_at_utc=now(),source_feature_appearances=appearances,distinct_source_ids=len(seen),
        repeated_appearances=appearances-len(seen),inconsistent_repeated_ids=conflicts,
        meaning='Exact returned geometry and retained attributes checked; no field validation or claim of inventory completeness')
    (out/'source-consistency.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='inconsistent_repeated_ids'},indent=2))
    print('Inconsistent repeated IDs:',len(conflicts))
    if conflicts:raise RuntimeError('Live-source version/geometry inconsistency; preserve and investigate before object merging')

if __name__=='__main__':main()
