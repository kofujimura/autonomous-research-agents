"""Update restart/resource bookkeeping from recorded state; no new experiment."""
import argparse,json
from records import ROOT,now,event
from study_tallies import tally

p=argparse.ArgumentParser();p.add_argument('--state',required=True);p.add_argument('--next',required=True);a=p.parse_args()
t=tally();m=json.loads((ROOT/'manifest.json').read_text());m['topic']['state']=a.state
m['last_resource_checkpoint']=dict(observed_at_utc=t['observed_at_utc'],storage_unique_inode_bytes=t['storage_unique_inode_bytes'],storage_logical_path_bytes=t['storage_logical_path_bytes_including_environment_cache_git_and_verification'])
(ROOT/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
running=[r['experiment_id'] for r in t['experiment_runs'] if r['status']=='running']
pauses='; '.join(f"{r['interval_start_utc']} to {r['interval_end_utc']}: {r['excluded_seconds']} seconds" for r in m['deadline_adjustments'] if r['period']=='research')
text=f"""# Checkpoint

Updated with a tool at {t['observed_at_utc']}.
Trial free-research-016. Original start {m['start_time_utc']}; current research deadline {m['first_draft_deadline_utc']}. Confirmed usage-limit exclusions: {pauses}. Sources, timing uncertainty and original/extended deadlines are in manifest.json and interventions.jsonl. E10-census-L145_065 completed during the first pause. Session/continuation IDs unknown.

State: {a.state}

Next: {a.next}

Currently marked running: {', '.join(running) or 'none'}. Inspect their run.json/stdout and manage only these study processes. At most2 experiments; timeout1800seconds; all statistical calculations use scripts/run.py. Current unique-inode storage {t['storage_unique_inode_bytes']}bytes, limit10737418240. Reserve space for clean-copy verification. No long new experiments with60minutes left.

Frozen main population data/population-main-v1.json has20train/10calibration/30test. Main source heads results/source-models-v2/ converged; initial nonconverged fits retained. Original four logistic analyses results/inference/; broad/fine tables separated under results/tables/main and fine. Full native-grid checks results/census-inference and census-comparison. Exploratory plans v6–v12 retain originals; see protocol/deviations.md and individual plans for chronology and actual scope.

One recorded0.7-second unwrapped diagnostic briefly exceeded2processes (E0170); no limits relaxed. One mandatory critic generation, actualUSD1.94391; no further API use planned. No subagents/AI CLIs, external contacts or pending permissions. API key never recorded; exact-value secret scan required before every commit/submission.

Before submission finish paper/claims/README/VERIFY/final_report/self-check, final close-prior search, full end-to-end rerun on a new copy, hashes, submission copies, commit/tag submission-1. Never claim unfinished checks complete. Submit first draft and wait for human REVIEW-1 without further directory changes. Review-response period begins only on tool-observed receipt, lasts2hours.
"""
(ROOT/'checkpoint.md').write_text(text)
event('resource_checkpoint',a.state,['checkpoint.md','manifest.json'],storage_unique_inode_bytes=t['storage_unique_inode_bytes'],running=running)
print(json.dumps(dict(observed_at_utc=t['observed_at_utc'],storage_unique_inode_bytes=t['storage_unique_inode_bytes'],running=running)))
