"""The only permitted AI API path. Topic critique only unless a later plan authorizes measurement.

No API credential is written, logged, or passed on a command line. SDK retries are
disabled; at most two critic creations are permitted by the selection skill.
"""
from pathlib import Path
from decimal import Decimal
import argparse
import json
import os
from openai import OpenAI
from records import ROOT, append, event, now

PRICES = {'input_per_million':Decimal('10'), 'cached_input_per_million':Decimal('1'),
          'output_per_million':Decimal('50'), 'web_search_per_call':Decimal('0.01')}
BUDGET=Decimal('20')

def previous():
    return [json.loads(x) for x in (ROOT/'api_calls.jsonl').read_text().splitlines() if x]

def client():
    return OpenAI(api_key=os.environ['FREE_RESEARCH_OPENAI_API_KEY'],max_retries=0,timeout=90.0)

def safe_error(exc):
    text=str(exc)
    value=os.environ.get('FREE_RESEARCH_OPENAI_API_KEY')
    return text.replace(value,'[REDACTED]') if value else text

def create():
    rows=previous()
    pending=list((ROOT/'api').glob('state-*.json'))
    if any(json.loads(p.read_text()).get('status') in ['queued','in_progress','submitting'] for p in pending):
        raise RuntimeError('An API creation is already pending; retrieve it instead')
    if len(rows)>=2:raise RuntimeError('Critic creation limit reached')
    if any(r.get('cost_usd') is None for r in rows):
        raise RuntimeError('Unresolved previous-call cost prevents another request')
    total=sum((Decimal(str(r['cost_usd'])) for r in rows),Decimal('0'))
    if total>=BUDGET:raise RuntimeError('Budget exhausted')
    prompt=(ROOT/'api/critic-prompt.txt').read_text()
    request=dict(model='gpt-6-astra',reasoning={'effort':'xhigh'},
                 tools=[{'type':'web_search'}],include=['web_search_call.action.sources'],
                 background=True,input=prompt)
    call_id=f'API{len(rows)+1:03d}'
    request_path=f'api/requests/{call_id}.json'
    response_path=f'api/responses/{call_id}.json'
    (ROOT/request_path).write_text(json.dumps(request,indent=2)+'\n')
    state=dict(call_id=call_id,experiment_id='topic-selection-step6',purpose='topic_candidate_critique',
        requested_at_utc=now(),provider='OpenAI',model_requested='gpt-6-astra',model_returned=None,
        parameters={k:v for k,v in request.items() if k!='input'},request_path=request_path,
        response_path=response_path,usage=None,cost_usd=None,cumulative_cost_usd=float(total),
        status='submitting',error=None,
        pre_call_check={'cumulative_actual_cost_usd':float(total),'budget_usd':float(BUDGET),
                       'maximum_cost_check_exception':'research-question skill step 6: no output limit and actual cost only',
                       'max_create_attempts':2,'sdk_max_retries':0},
        price_source='data/literature/openai-pricing.md',price_checked_date='2026-10-27')
    state_path=ROOT/f'api/state-{call_id}.json'
    state_path.write_text(json.dumps(state,indent=2)+'\n')
    event('api_request','Sent one permitted candidate critique request',[request_path,'protocol/critic-plan.md'],call_id=call_id)
    try:
        response=client().responses.create(**request)
    except Exception as exc:
        state.update(status='request_failed',error={'type':type(exc).__name__,'message':safe_error(exc)},
                     cost_usd=None,cost_note='Unknown: no usage response. No automatic retry permitted.')
        (ROOT/response_path).write_text(json.dumps(state['error'],indent=2)+'\n')
        state_path.write_text(json.dumps(state,indent=2)+'\n');append('api_calls.jsonl',state)
        raise RuntimeError('API request failed; inspect saved sanitized error; no retry performed') from None
    save(response,state,state_path,rows)

def save(response,state,state_path,rows):
    raw=response.model_dump(mode='json')
    (ROOT/state['response_path']).write_text(json.dumps(raw,indent=2,ensure_ascii=False)+'\n')
    state.update(response_id=response.id,status=response.status,model_returned=response.model,
                 usage=raw.get('usage'),last_retrieved_at_utc=now())
    if response.status not in ['queued','in_progress']:
        usage=raw.get('usage')
        if usage is not None:
            cached=(usage.get('input_tokens_details') or {}).get('cached_tokens',0)
            inp=usage['input_tokens'];out=usage['output_tokens']
            searches=sum(x.get('type')=='web_search_call' for x in raw.get('output',[]))
            cost=(Decimal(inp-cached)*PRICES['input_per_million']+
                  Decimal(cached)*PRICES['cached_input_per_million']+
                  Decimal(out)*PRICES['output_per_million'])/Decimal(1000000)
            cost+=Decimal(searches)*PRICES['web_search_per_call']
            total=sum((Decimal(str(r['cost_usd'])) for r in rows),Decimal('0'))+cost
            state.update(cost_usd=float(cost),cumulative_cost_usd=float(total),web_search_calls=searches,
                         cost_calculation={'prices_usd':{k:str(v) for k,v in PRICES.items()},
                             'input_tokens':inp,'cached_input_tokens':cached,'output_tokens':out,
                             'reasoning_tokens_included_in_output':True,'web_search_call_items':searches},
                         service_tier=raw.get('service_tier'))
        else: state['cost_note']='Unknown: terminal response contained no usage'
        state['error']=raw.get('error')
        append('api_calls.jsonl',state)
        if response.status=='completed':
            (ROOT/f'api/responses/{state["call_id"]}-text.txt').write_text(response.output_text+'\n')
        event('api_complete',f'Critic request reached {response.status}',[state['response_path']],
              call_id=state['call_id'],cost_usd=state['cost_usd'])
    state_path.write_text(json.dumps(state,indent=2)+'\n')
    print(json.dumps({k:state.get(k) for k in ['call_id','response_id','status','model_returned','cost_usd','cumulative_cost_usd']}))

def retrieve(call_id,cancel=False):
    state_path=ROOT/f'api/state-{call_id}.json'
    state=json.loads(state_path.read_text())
    if state['status'] not in ['queued','in_progress']:print('Already terminal; reuse saved response');return
    response=(client().responses.cancel(state['response_id']) if cancel
              else client().responses.retrieve(state['response_id']))
    save(response,state,state_path,previous())

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['create','retrieve','cancel']);p.add_argument('call_id',nargs='?')
    a=p.parse_args()
    if a.action=='create':create()
    else:retrieve(a.call_id,cancel=a.action=='cancel')
