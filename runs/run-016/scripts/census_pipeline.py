"""Execute the previously selected full native-grid sensitivity check."""
import subprocess,sys,json
from records import ROOT,now
from predict_fixed import predict
from draw_audits import make
from audit_inference import run
from summarize_inference import build
from compare_census import compare

manifest='data/population-census-v1.json'
subprocess.run([sys.executable,str(ROOT/'scripts/build_census_manifest.py'),
               '--source-manifest','data/population-source-v1.json','--destination',manifest],check=True)
make(manifest,'data/audit-draws-census')
analyses=[];points=[]
for rep in ['tessera','alphaearth']:
    name=f'logistic-broad-{rep}'
    model=f'results/census-models/{name}'
    analysis=f'results/census-inference/{name}'
    predict(f'results/source-models-v2/{name}',manifest,model)
    run(model,'data/audit-draws-census/manifest.json',analysis)
    analyses.append(analysis);points.append(f'results/inference/{name}')
build(analyses,'results/tables/census')
compare(points,analyses,'results/census-comparison')
print(json.dumps(dict(completed_at_utc=now(),status='completed')))
