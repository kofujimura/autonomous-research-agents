"""Execute one prespecified classifier robustness condition, preserving all fits."""
import argparse,json
from records import ROOT,now,digest
from fit_models import fit
from audit_inference import run
from summarize_inference import build

p=argparse.ArgumentParser();p.add_argument('--representation',required=True,choices=['tessera','alphaearth'])
p.add_argument('--refreshed',action='store_true');a=p.parse_args()
kind='logistic' if a.refreshed else 'forest'
name=f"{kind}-broad-{'refreshed-' if a.refreshed else ''}{a.representation}"
model=f'results/models/{name}';analysis=f'results/inference/{name}'
manifest='data/population-refreshed-v1.json' if a.refreshed else 'data/population-main-v1.json'
if a.refreshed:
    main=json.loads((ROOT/'data/population-main-v1.json').read_text())
    fresh=json.loads((ROOT/manifest).read_text())
    original={r['landscape_id']:r for r in main['landscapes']}
    assert set(original)==set(r['landscape_id'] for r in fresh['landscapes'])
    for record in fresh['landscapes']:
        old=original[record['landscape_id']]
        assert record['status']==old['status'] and record['valid_indices']==old['valid_indices']
        assert record['path']==old['path'] and record['sha256']==old['sha256']
        for feature in record['feature_inputs']:
            assert digest(ROOT/feature['path'])==feature['sha256']
fit(manifest,a.representation,'broad',kind,model,a.refreshed,10000)
run(model,'data/audit-draws-main/manifest.json',analysis)
build([analysis],f'results/tables/{name}')
print(json.dumps(dict(completed_at_utc=now(),condition=name,status='completed')))
