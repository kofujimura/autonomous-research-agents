# Transcription of the original unwrapped inline command; do not execute while
# both experiment slots are occupied. This file was saved retrospectively.
import json,numpy as np
from scipy.stats import hypergeom
from pathlib import Path
u=[json.loads(s) for s in Path('results/pipeline-check/inference/units.jsonl').read_text().splitlines()]
m=json.load(open('results/pipeline-check/audit-draws/manifest.json'))
p=json.load(open('results/pipeline-check/model-tessera-broad/fit.json'))
f=next(r['path'] for r in p['prediction_files'] if r['landscape_id']==u[0]['landscape_id'])
with np.load(f) as z:y=z['labels']
for r in u:
 a=r['year_a']-2021;b=r['year_b']-2021;changed=y[a]!=y[b];N=len(changed);M=int(changed.sum())
 unit=next(x for x in m['draws'] if x['landscape_id']==r['landscape_id'] and x['year_a']==r['year_a'] and x['year_b']==r['year_b'])
 with np.load(unit['path']) as z:ix=z['a'][:,:128]
 print(dict(unit=r['unit_id'],N=N,changed=M,changed_fraction=M/N,prob_no_change_n128=float(hypergeom.pmf(0,N,M,128)),empirical_no_change=float((changed[ix].sum(axis=1)==0).mean())))
