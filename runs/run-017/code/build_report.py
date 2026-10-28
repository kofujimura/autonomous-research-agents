"""Compile observable resource/intervention tallies; do not invent hidden usage."""
import json
from collections import Counter
from pathlib import Path
from records import ROOT,now

def lines(path):return [json.loads(x) for x in path.read_text().splitlines() if x] if path.exists() else []

def main():
    manifest=json.loads((ROOT/'manifest.json').read_text())
    interventions=lines(ROOT/'interventions.jsonl');api=lines(ROOT/'api_calls.jsonl')
    calls={}
    for row in api:calls[row['call_id']]=row
    runs=[json.loads(x.read_text()) for x in sorted((ROOT/'experiments').glob('*/run.json'))]
    completed=[x for x in runs if 'ended_at_utc' in x]
    failed=[x for x in completed if x['exit_code']!=0]
    active=[x['experiment_id'] for x in runs if 'ended_at_utc' not in x]
    models=Counter((x['model_returned'] or x['model_requested'],x['purpose']) for x in calls.values())
    usage=Counter()
    for row in calls.values():
        for name in ['input_tokens','output_tokens']:
            usage[name]+=row.get('usage',{}).get(name,0)
    storage=sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file() and not p.is_symlink())
    cost=json.loads((ROOT/'api/cost-recomputed.json').read_text())
    summary=dict(generated_at_utc=now(),experiment_process_runs=len(runs),completed_runs=len(completed),
        failed_runs=len(failed),failure_ids=[x['experiment_id'] for x in failed],active_runs=active,
        intervention_tally=dict(Counter(x['type'] for x in interventions)),intervention_rows=len(interventions),
        distinct_ai_api_calls=len(calls),api_calls_by_model_purpose=[dict(model=m,purpose=p,calls=n) for (m,p),n in models.items()],
        api_tokens=dict(usage),api_cost_recomputed=cost,storage_bytes=storage,
        session_usage='Not exposed; search/session-model token usage and charges unknown',
        session_ids=manifest.get('session_ids',manifest.get('session_id')))
    (ROOT/'analysis').mkdir(exist_ok=True)
    (ROOT/'analysis/resource-tally.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
