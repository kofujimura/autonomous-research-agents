import argparse,json
from records import ROOT,now,digest

p=argparse.ArgumentParser();p.add_argument('--source-manifest',required=True);p.add_argument('--destination',required=True);a=p.parse_args()
source=json.loads((ROOT/a.source_manifest).read_text());assert source['source_only']
cases=json.loads((ROOT/'data/census-cases.json').read_text())
rows=list(source['landscapes'])
for r in cases['selected']:
    path=ROOT/'data/census'/r['landscape_id']/'case-result.json'
    result=json.loads(path.read_text());rows.append(result)
out=dict(source);out.update(created_at_utc=now(),plan_path='protocol/plan-v3-census-check.md',source_only=False,
                           source_manifest_path=a.source_manifest,source_manifest_sha256=digest(ROOT/a.source_manifest),
                           native_census=True,landscapes=rows,
                           counts={s:sum(r['status']=='included' and r['split']==s for r in rows) for s in ['train','calibration','test']},
                           status_counts={s:sum(r['status']==s for r in rows) for s in sorted(set(r['status'] for r in rows))})
path=ROOT/a.destination
if path.exists():raise FileExistsError('Preserve census population manifests')
path.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out['counts']))
