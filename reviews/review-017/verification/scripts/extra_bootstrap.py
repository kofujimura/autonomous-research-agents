"""Reviewer check: conditional block-bootstrap intervals for planned-but-unreported operating points,
using the research side's own primary_bootstrap (imported read-only from the clone) on regenerated bootstrap-blocks.csv.
usage: extra_bootstrap.py <clone_code_dir> <bootstrap-blocks.csv> <out.json>"""
import sys, json
sys.path.insert(0, sys.argv[1])
import pandas as pd
from summarize import primary_bootstrap
blocks = pd.read_csv(sys.argv[2])
res = {}
for scope in ['within']:
    for cond in ['standardized_0.05', 'standardized_0.01', 'standardized_0.1', 'regional_0.05', 'validation_0.05', 'regional_validation_0.05']:
        r = primary_bootstrap(blocks, condition=cond, scope=scope)
        res[f'{scope}|{cond}'] = {k: r[k] for k in ['H1_interaction', 'aef_oracle_gain', 'optical_oracle_gain']}
        print(scope, cond, {k: (round(v['estimate'] * 100, 1), [round(x * 100, 1) for x in v['conditional_block_bootstrap_95_percent_interval']]) if v.get('status') == 'complete' else v for k, v in res[f'{scope}|{cond}'].items()}, flush=True)
json.dump(res, open(sys.argv[3], 'w'), indent=1)
