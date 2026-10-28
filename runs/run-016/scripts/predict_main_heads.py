"""Apply the four already fixed source heads to a completed main manifest."""
import argparse,json
from records import ROOT
from predict_fixed import predict

p=argparse.ArgumentParser();p.add_argument('--manifest',required=True)
p.add_argument('--source-root',default='results/source-models-v2');a=p.parse_args()
m=json.loads((ROOT/a.manifest).read_text())
assert not m['source_only'] and not m['status_counts'].get('incomplete',0)
for taxonomy in ['broad','fine']:
    for representation in ['tessera','alphaearth']:
        predict(f'{a.source_root}/logistic-{taxonomy}-{representation}',a.manifest,
                f'results/models/logistic-{taxonomy}-{representation}')
