"""Only authorized external-model instrument: the one topic-candidate critique.

No automatic retries. Background polling never initiates a new generation.
The API key is read directly from its authorized environment variable.
"""
import argparse, json, os
from pathlib import Path
from records import ROOT, now, append, event

STATE = ROOT / 'experiments' / 'topic-critique'
BUDGET = 20.0
PRICES = {'input':10.0,'cached':1.0,'output':50.0,'web_search':0.01}

def client():
    from openai import OpenAI
    return OpenAI(api_key=os.environ['FREE_RESEARCH_OPENAI_API_KEY'],
                  max_retries=0, timeout=90.0)

def cumulative_cost():
    latest={}
    for line in (ROOT/'api_calls.jsonl').read_text().splitlines():
        row=json.loads(line);latest[row['call_id']]=row
    unknown=[x for x in latest.values() if x['status'] not in ['queued','in_progress'] and x['cost_usd'] is None]
    if unknown:
        raise RuntimeError('Unresolved prior API costs; further generation prohibited')
    return sum(x['cost_usd'] or 0.0 for x in latest.values())

def record(data, state, error=None):
    usage=data.get('usage')
    cost=None
    searches=sum(item.get('type')=='web_search_call' for item in data.get('output',[]))
    if usage:
        inp=usage['input_tokens'];out=usage['output_tokens']
        detail=usage.get('input_tokens_details') or {}
        cached=detail.get('cached_tokens',0)
        if inp>272000:
            raise RuntimeError('Unexpected long-context use: pricing must be reconciled before proceeding')
        # Cache-write fields, if present, require explicit accounting rather than omission.
        writes30=detail.get('cache_write_tokens',detail.get('cache_creation_tokens',0))
        writes12=detail.get('cache_write_12h_tokens',0)
        cost=((inp-cached-writes30-writes12)*PRICES['input']+cached*PRICES['cached']
              +writes30*12.5+writes12*25.0+out*PRICES['output'])/1e6+searches*PRICES['web_search']
    if data.get('status') in ['queued','in_progress']:
        cost=0.0 # No settled usage yet: this is a progress record, not a final bill.
    total=state['cumulative_before_usd']+(cost or 0.0)
    row=dict(call_id=state['call_id'],experiment_id='topic-selection',purpose='candidate critique: research-question step 6 exception',
             requested_at_utc=state['requested_at_utc'],recorded_at_utc=now(),provider='OpenAI',
             model_requested='gpt-6-astra',model_returned=data.get('model'),parameters=state['parameters'],
             request_path=state['request_path'],response_path=state['response_path'],usage=usage,
             web_search_call_count=searches,prices=PRICES,cost_usd=cost,cumulative_cost_usd=total,
             cumulative_cost_is_settled=cost is not None and data.get('status') not in ['queued','in_progress'],
             status=data.get('status','request_failed'),error=error or data.get('error'),
             pre_call_check='Skill-mandated exception: no output cap and exempt from pre-call maximum-cost check; actual cost counted',
             budget_usd=BUDGET)
    append('api_calls.jsonl',row)
    if cost is not None and total>BUDGET:
        event('api_budget_exceeded','Critique actual cost exceeded total budget; no more API calls authorized.',['api_calls.jsonl'])
    return row

def start(prompt_path, without_search=False):
    STATE.mkdir(parents=True,exist_ok=True)
    prior=list(STATE.glob('request-*.json'))
    if len(prior)>=2:raise RuntimeError('Maximum two critique requests reached')
    if prior and not without_search:raise RuntimeError('Only a documented unsupported-web-search failure permits the second request')
    if prior and without_search:
        old=json.loads((STATE/'response-1.json').read_text())
        if 'web' not in json.dumps(old.get('error','')).lower():
            raise RuntimeError('Second request requires documented web-search support failure')
    before=cumulative_cost()
    if before>=BUDGET:raise RuntimeError('Budget exhausted')
    n=len(prior)+1
    parameters=dict(model='gpt-6-astra',reasoning={'effort':'xhigh'},background=True,store=True)
    if not without_search:
        parameters.update(tools=[{'type':'web_search'}],include=['web_search_call.action.sources'])
    request=dict(parameters,input=(ROOT/prompt_path).read_text())
    req_path=f'experiments/topic-critique/request-{n}.json'
    res_path=f'experiments/topic-critique/response-{n}.json'
    state=dict(call_id=f'critic-{n}',requested_at_utc=now(),parameters=parameters,
               request_path=req_path,response_path=res_path,cumulative_before_usd=before)
    (ROOT/req_path).write_text(json.dumps(request,indent=2)+'\n')
    (STATE/'state.json').write_text(json.dumps(state,indent=2)+'\n')
    event('api_request','One authorized candidate critique requested.',['protocol/critique-plan.md',req_path])
    try:
        response=client().responses.create(**request)
        data=response.model_dump(mode='json')
    except Exception as exc:
        safe_error=str(exc).replace(os.environ['FREE_RESEARCH_OPENAI_API_KEY'],'[REDACTED]')
        data=dict(status='request_failed',error={'type':type(exc).__name__,'message':safe_error})
        (ROOT/res_path).write_text(json.dumps(data,indent=2)+'\n')
        record(data,state)
        raise RuntimeError(safe_error) from None
    (ROOT/res_path).write_text(json.dumps(data,indent=2)+'\n')
    state['response_id']=data['id'];(STATE/'state.json').write_text(json.dumps(state,indent=2)+'\n')
    row=record(data,state)
    print(json.dumps({k:row[k] for k in ['call_id','status','cost_usd','cumulative_cost_usd']}))

def poll(cancel=False):
    state=json.loads((STATE/'state.json').read_text())
    response=client().responses.cancel(state['response_id']) if cancel else client().responses.retrieve(state['response_id'])
    data=response.model_dump(mode='json')
    (ROOT/state['response_path']).write_text(json.dumps(data,indent=2)+'\n')
    row=record(data,state)
    if data.get('status')=='completed':
        text='\n'.join(c.get('text','') for o in data.get('output',[]) if o.get('type')=='message'
                       for c in o.get('content',[]) if c.get('type')=='output_text')
        (STATE/'critique.md').write_text(text+'\n')
    print(json.dumps({k:row[k] for k in ['call_id','status','cost_usd','cumulative_cost_usd','web_search_call_count']}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['start','poll','cancel'])
    p.add_argument('--prompt',default='protocol/critique-prompt.txt');p.add_argument('--without-search',action='store_true')
    a=p.parse_args()
    if a.action=='start':start(a.prompt,a.without_search)
    else:poll(a.action=='cancel')
