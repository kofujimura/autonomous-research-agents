"""Execute the four fixed source logistic fits without looking at test outcomes."""
import argparse,json
from records import ROOT
from fit_models import fit

p=argparse.ArgumentParser();p.add_argument('--manifest',required=True)
p.add_argument('--max-iter',type=int,default=1000);p.add_argument('--destination-root',default='results/source-models');a=p.parse_args()
m=json.loads((ROOT/a.manifest).read_text())
assert m['source_only'] and m['counts']=={'train':20,'calibration':10,'test':0}
assert not m['status_counts'].get('incomplete',0)
for taxonomy in ['broad','fine']:
    for representation in ['tessera','alphaearth']:
        fit(a.manifest,representation,taxonomy,'logistic',f'{a.destination_root}/logistic-{taxonomy}-{representation}',max_iter=a.max_iter)
