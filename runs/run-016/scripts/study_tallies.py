"""Count observable resources and interventions without calling any API."""
import json
from collections import Counter
from records import ROOT,now

def read_lines(name):
    p=ROOT/name
    return [json.loads(s) for s in p.read_text().splitlines() if s] if p.exists() else []

def tally():
    calls={r['call_id']:r for r in read_lines('api_calls.jsonl')}
    api=[]
    for r in calls.values():
        u=r.get('usage') or {};inp=u.get('input_tokens',0);out=u.get('output_tokens',0)
        details=u.get('input_tokens_details') or {};cached=details.get('cached_tokens',0);writes=details.get('cache_write_tokens',0)
        reasoning=(u.get('output_tokens_details') or {}).get('reasoning_tokens',0)
        response=json.loads((ROOT/r['response_path']).read_text()) if r.get('response_path') else {}
        web=sum(c.get('type')=='web_search_call' for c in response.get('output',[]))
        price=r.get('price_table') or {};i=price.get('input_per_million');o=price.get('output_per_million');c=price.get('cached_input_per_million')
        cost=((inp-cached-writes)*i+cached*c+writes*i*1.25+out*o)/1e6+web*price['web_search_call'] if all(v is not None for v in [i,o,c]) else None
        if cost is not None:assert abs(cost-r['cost_usd'])<1e-10
        api.append(dict(call_id=r['call_id'],model=r.get('model_returned'),purpose=r['purpose'],status=r['status'],
                        input_tokens=inp,cached_input_tokens=cached,cache_write_30m_tokens=writes,
                        output_tokens_including_reasoning=out,reasoning_tokens=reasoning,web_search_calls=web,
                        recomputed_cost_usd=cost,recorded_cost_usd=r.get('cost_usd'),price_source=price.get('source')))
    runs=[]
    for p in sorted((ROOT/'experiments').glob('*/run.json')):
        r=json.loads(p.read_text());runs.append(dict(experiment_id=r['experiment_id'],status=r['status'],
                                elapsed_seconds=r.get('elapsed_seconds'),exit_code=r.get('exit_code')))
    label_attempts=read_lines('data/selection-results.jsonl')
    labels={r['landscape_id']:r for r in label_attempts}
    feature_attempts=read_lines('data/feature-results.jsonl')
    features={(r['landscape_id'],r['year'],r['representation']):r for r in feature_attempts}
    train_ids=[r['landscape_id'] for r in labels.values() if r['status']=='accepted' and r['split']=='train']
    future_keys=[(lid,year,rep) for lid in train_ids for year in range(2022,2026) for rep in ['tessera','alphaearth']]
    future_done=[key for key in future_keys if features.get(key,{}).get('status')=='completed']
    interventions=read_lines('interventions.jsonl');events=read_lines('events.jsonl')
    event_ids=Counter(r['event_id'] for r in events)
    paths=[p for p in ROOT.rglob('*') if p.is_file() and not p.is_symlink()]
    size=sum(p.stat().st_size for p in paths)
    unique={}
    for p in paths:
        st=p.stat();unique[(st.st_dev,st.st_ino)]=st.st_size
    unwrapped=[str(p.relative_to(ROOT)) for p in (ROOT/'experiments').glob('*/retrospective-record.json')]
    return dict(observed_at_utc=now(),api=api,unique_api_generations=len(api),api_cost_usd=sum(r['recorded_cost_usd'] or 0 for r in api),
                api_status_counts=dict(Counter(r['status'] for r in api)),
                api_record_lines=len(read_lines('api_calls.jsonl')),api_note='Ledger updates and offline cost correction are not additional generations; reasoning tokens are a subset of output tokens.',
                intervention_types=dict(Counter(r['type'] for r in interventions)),intervention_records=len(interventions),
                experiment_status_counts=dict(Counter(r['status'] for r in runs)),experiment_runs=runs,
                latest_landscape_status_counts=dict(Counter(r['status'] for r in labels.values())),
                label_attempt_status_counts=dict(Counter(r['status'] for r in label_attempts)),
                feature_attempt_status_counts=dict(Counter(r['status'] for r in feature_attempts)),
                future_training_feature_progress=dict(required=len(future_keys),recorded_completed=len(future_done),
                    remaining=len(future_keys)-len(future_done),note='Bookkeeping count from ledger; loader verifies file hashes before use'),
                accepted_landscape_splits=dict(Counter(r['split'] for r in labels.values() if r['status']=='accepted')),
                event_records=len(events),duplicate_event_ids={k:v for k,v in event_ids.items() if v>1},
                storage_logical_path_bytes_including_environment_cache_git_and_verification=size,
                storage_unique_inode_bytes=sum(unique.values()),unwrapped_retrospective_experiments=unwrapped,
                session_model_usage=None,tool_prices_beyond_API=None,
                unknowns=['Session sampling-token usage and billing are not exposed.','Session and continuation identifiers are unknown.','No independent reproduction or human-participant outcomes were measured.'])

if __name__=='__main__':
    print(json.dumps(tally(),indent=2))
