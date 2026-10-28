"""Apply prospectively frozen heads and execute the original audit comparison."""
from records import ROOT,now
from predict_fixed import predict
from draw_audits import make
from audit_inference import run
from summarize_inference import build
import json

manifest='data/population-main-v1.json'
m=json.loads((ROOT/manifest).read_text())
assert not m['source_only'] and not m['status_counts'].get('incomplete',0)
make(manifest,'data/audit-draws-main')
for taxonomy in ['broad','fine']:
    analyses=[]
    for representation in ['tessera','alphaearth']:
        name=f'logistic-{taxonomy}-{representation}'
        model=f'results/models/{name}'
        analysis=f'results/inference/{name}'
        predict(f'results/source-models-v2/{name}',manifest,model)
        run(model,'data/audit-draws-main/manifest.json',analysis)
        analyses.append(analysis)
    build(analyses,f"results/tables/{'main' if taxonomy=='broad' else 'fine'}")
print(json.dumps(dict(completed_at_utc=now(),status='completed')))
