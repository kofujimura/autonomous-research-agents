import json
from records import ROOT
from study_tallies import tally
from reference_frame_analysis import run
assert tally()['storage_unique_inode_bytes']+256*1024**2<=10*1024**3,'Keep prespecified storage reserve'
cohort=json.loads((ROOT/'data/validation-cohort-v1.json').read_text())
run('data/population-source-v1.json','results/additional-arable-high-replication',arable_only=True,
    selection_ledger='data/validation-selection-results.jsonl',expected_landscapes=cohort['accepted_landscapes'],
    plan_path='protocol/plan-v13b-monte-carlo-precision.md',replications=5000,keep_draws=False)
