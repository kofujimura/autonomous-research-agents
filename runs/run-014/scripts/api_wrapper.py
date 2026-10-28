"""Sole AI API gateway for this trial. Authorized purpose: one topic critique.

No research agents, literature summaries, code assistance or drafting calls.
The critique uses the explicit skill exception to the pre-call maximum-cost check.
No automatic retries. A second create is allowed only after a recorded failure.
"""
import argparse,json,os
from pathlib import Path
from record import ROOT,now,append,event

API=ROOT/'experiments/topic-critique'
RATES={'input_per_million':10.0,'cached_input_per_million':1.0,'cache_write_30m_per_million':12.5,'cache_write_12h_per_million':25.0,'output_per_million':50.0,'web_search_per_call':0.01}
BUDGET=20.0

def save(path,obj):
    text=json.dumps(obj,indent=2,ensure_ascii=False)+'\n'
    key=os.environ.get('FREE_RESEARCH_OPENAI_API_KEY','')
    if key and key in text:
        raise RuntimeError('STOP: secret detected in proposed API artifact; artifact was not written')
    path.write_text(text)

def latest():
    rows={}
    for line in (ROOT/'api_calls.jsonl').read_text().splitlines():
        row=json.loads(line);rows[row['call_id']]=row
    return rows

def cost(response):
    u=response.get('usage')
    if u is None:return None
    inp=u['input_tokens'];out=u['output_tokens']
    details=u.get('input_tokens_details') or {}
    cached=details.get('cached_tokens',0)
    written=details.get('cache_write_tokens',0)
    lifetimes=details.get('cache_write_tokens_details')
    # No explicit cache TTL was requested: current GPT-6 documentation specifies
    # 30m as the default. The response's legacy prompt_cache_retention field is
    # retained verbatim but is not used as a write-lifetime token breakdown.
    w30=written if not lifetimes else lifetimes.get('ttl_30m_tokens',0)
    w12=0 if not lifetimes else lifetimes.get('ttl_12h_tokens',0)
    assert w30+w12==written
    # Long-context rates are applied to all tokens
    # when the official 272K threshold is exceeded.
    i_rate,c_rate,o_rate=10.0,1.0,50.0
    if inp>272000:i_rate,c_rate,o_rate=20.0,2.0,75.0
    searches=sum(x.get('type')=='web_search_call' for x in response.get('output',[]))
    return ((inp-cached-written)*i_rate+cached*c_rate+w30*i_rate*1.25+w12*i_rate*2.5+out*o_rate)/1e6+searches*0.01

def log_response(row,response):
    serial=len(list(API.glob(row['call_id']+'-response-*.json')))
    path=API/(row['call_id']+f'-response-{serial:03d}.json')
    save(path,response)
    calculated=cost(response)
    previous=latest()
    other=[r['cost_usd'] for cid,r in previous.items() if cid!=row['call_id']]
    cumulative=None if calculated is None or any(c is None for c in other) else sum(other)+calculated
    row.update(model_returned=response.get('model'),response_path=str(path.relative_to(ROOT)),
               usage=response.get('usage'),cost_usd=calculated,cumulative_cost_usd=cumulative,
               status=response['status'],error=response.get('error'),updated_at_utc=now(),
               web_search_calls=sum(x.get('type')=='web_search_call' for x in response.get('output',[])))
    append('api_calls.jsonl',row)
    text='\n'.join(part.get('text','') for item in response.get('output',[]) if item.get('type')=='message'
                   for part in item.get('content',[]) if part.get('type')=='output_text')
    if text:
        key=os.environ.get('FREE_RESEARCH_OPENAI_API_KEY','')
        if key and key in text:raise RuntimeError('STOP: secret detected in proposed output; not written')
        (API/(row['call_id']+'-output.md')).write_text(text+'\n')
    save(API/'state.json',{'response_id':response['id'],'call_id':row['call_id'],'status':response['status']})
    print(json.dumps({'call_id':row['call_id'],'status':response['status'],'model_returned':row['model_returned'],
                      'usage':row['usage'],'cost_usd':calculated,'cumulative_cost_usd':cumulative,'web_search_calls':row['web_search_calls']}))
    if cumulative is not None and cumulative>BUDGET:
        event('api_budget_exceeded','Critique exception actual cost exceeds budget; no further API calls permitted',['api_calls.jsonl'])
        raise SystemExit(21)

def main():
    from openai import OpenAI
    p=argparse.ArgumentParser();p.add_argument('action',choices=['start','poll','cancel','reaccount']);p.add_argument('--without-web',action='store_true');a=p.parse_args()
    if a.action=='reaccount':
        state=json.loads((API/'state.json').read_text());row=latest()[state['call_id']]
        response=json.loads((ROOT/row['response_path']).read_text())
        row['accounting_note']='Locally recomputed from saved response; no new API request. Includes cache-write tokens at published default 30m rate. Legacy retention field and absent lifetime detail retained as a reporting caveat.'
        log_response(row,response)
        return
    if not os.environ.get('FREE_RESEARCH_OPENAI_API_KEY'):raise RuntimeError('Authorized key unavailable')
    client=OpenAI(api_key=os.environ['FREE_RESEARCH_OPENAI_API_KEY'],base_url='https://api.openai.com/v1',max_retries=0,timeout=60)
    rows=latest();API.mkdir(exist_ok=True)
    if a.action=='start':
        if len(rows)>=2:raise RuntimeError('Critique maximum two create requests reached')
        if rows and list(rows.values())[-1]['status'] not in ['failed','incomplete','cancelled','error']:
            raise RuntimeError('No resend permitted after successful or pending critique')
        known=[r['cost_usd'] for r in rows.values()]
        if any(c is None for c in known):raise RuntimeError('Unknown billed cost; cannot authorize another create')
        cumulative=sum(known)
        if cumulative>=BUDGET:raise RuntimeError('Budget exhausted')
        prompt=(ROOT/'protocol/critique-prompt.txt').read_text()
        params={'model':'gpt-6-astra','reasoning':{'effort':'xhigh'},'input':prompt,'background':True,'store':True,
                'service_tier':'default','tools':[] if a.without_web else [{'type':'web_search'}],
                'include':[] if a.without_web else ['web_search_call.action.sources']}
        cid=f'API{len(rows)+1:03d}';request=API/(cid+'-request.json');save(request,params)
        row=dict(call_id=cid,experiment_id='topic-selection-step-6',purpose='candidate critique (explicit sole research-decision exception)',
            requested_at_utc=now(),provider='OpenAI',model_requested='gpt-6-astra',model_returned=None,
            parameters={k:v for k,v in params.items() if k!='input'},request_path=str(request.relative_to(ROOT)),
            response_path=None,usage=None,cost_usd=None,cumulative_cost_usd=cumulative,status='requested',error=None,
            budget_check={'actual_before_usd':cumulative,'maximum_next_usd':None,'maximum_check_exception':'research-question skill step 6; no max_output_tokens',
              'budget_usd':BUDGET,'price_source':'sources/openai-pricing.md','rates_standard_short_context':RATES},
            retry_limit=0,attempt=len(rows)+1)
        append('api_calls.jsonl',row)
        event('api_call_start','Sent authorized candidate critique through sole wrapper',['protocol/critique-prompt.txt',str(request.relative_to(ROOT))],call_id=cid)
        try:r=client.responses.create(**params)
        except Exception as e:
            # Error strings can echo credentials: retain only safe structured metadata.
            err={'type':type(e).__name__,'http_status':getattr(e,'status_code',None)}
            save(API/(cid+'-error.json'),err)
            row.update(status='error',error=err,cost_usd=None,cumulative_cost_usd=None)
            append('api_calls.jsonl',row);print(json.dumps(err));raise SystemExit(1)
        log_response(row,r.model_dump(mode='json'))
    else:
        state=json.loads((API/'state.json').read_text());row=rows[state['call_id']]
        r=client.responses.cancel(state['response_id']) if a.action=='cancel' else client.responses.retrieve(state['response_id'])
        log_response(row,r.model_dump(mode='json'))

if __name__=='__main__':main()
