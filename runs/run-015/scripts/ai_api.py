"""Only route for AI API calls in this study; designated critique only."""
import argparse
import datetime as dt
from decimal import Decimal
import json
import os
from pathlib import Path
import sys
from openai import OpenAI
from record import ROOT, append, event, now, secret_check

BUDGET=Decimal('20')
DIRECTORY=ROOT/'experiments/topic-critique'

def latest_calls():
    records={}
    for line in (ROOT/'api_calls.jsonl').read_text().splitlines():
        item=json.loads(line);records[item['call_id']]=item
    return records

def total_cost(records):
    return sum((Decimal(str(x['cost_usd'])) for x in records.values() if x.get('cost_usd') is not None),Decimal(0))

def cost_of(response):
    usage=response.get('usage')
    if not usage:return None
    detail=usage.get('input_tokens_details') or {}
    total=usage['input_tokens'];cached=detail.get('cached_tokens',0);writes=detail.get('cache_write_tokens',0)
    wd=detail.get('cache_write_tokens_details') or {'ttl_30m_tokens':writes,'ttl_12h_tokens':0}
    short_writes=wd.get('ttl_30m_tokens',0);long_writes=wd.get('ttl_12h_tokens',0)
    if short_writes+long_writes!=writes or cached+writes>total:return None
    # Cumulative reported input is used for the documented long-context switch;
    # all raw fields remain saved for a reviewer to inspect or recalculate.
    factor=Decimal(2) if total>272000 else Decimal(1)
    ordinary=Decimal(total-cached-writes)*Decimal(10)*factor
    read=Decimal(cached)*Decimal(1)*factor
    write=Decimal(short_writes)*Decimal('12.5')*factor+Decimal(long_writes)*Decimal(25)*factor
    output=Decimal(usage['output_tokens'])*(Decimal(75) if total>272000 else Decimal(50))
    searches=sum(x.get('type')=='web_search_call' for x in response.get('output',[]))
    result=(ordinary+read+write+output)/Decimal(1000000)+Decimal(searches)*Decimal('.01')
    return {'cost_usd':float(result),'cost_decimal_usd':str(result),'web_search_calls':searches,'pricing_source':'literature/openai-pricing.md','cache_pricing_source':'literature/openai-prompt-caching.md','context_rate_switch':'long' if total>272000 else 'short'}

def save_response(response,record):
    raw=response.model_dump(mode='json')
    snapshots=DIRECTORY/'snapshots';snapshots.mkdir(exist_ok=True)
    snapshot=snapshots/f'{record["call_id"]}-{len(list(snapshots.glob(record["call_id"]+"-*.json"))):03d}.json'
    snapshot.write_text(json.dumps(raw,indent=2,ensure_ascii=False)+'\n')
    path=DIRECTORY/f'{record["call_id"]}-response.json'
    path.write_text(json.dumps(raw,indent=2,ensure_ascii=False)+'\n')
    record.update(model_returned=raw.get('model'),response_path=str(path.relative_to(ROOT)),response_snapshot_path=str(snapshot.relative_to(ROOT)),usage=raw.get('usage'),status=raw.get('status'),response_id=raw.get('id'),error=raw.get('error'))
    if raw.get('status') not in ['queued','in_progress']:
        cost=cost_of(raw)
        record['cost_usd']=None if cost is None else cost['cost_usd'];record['cost_calculation']=cost
        prior=latest_calls();prior.pop(record['call_id'],None)
        record['cumulative_cost_usd']=float(total_cost(prior)+(Decimal(str(record['cost_usd'])) if record['cost_usd'] is not None else Decimal(0)))
        record['cumulative_cost_complete']=all(x.get('cost_usd') is not None for x in prior.values()) and cost is not None
        extracted='\n\n'.join(c.get('text','') for item in raw.get('output',[]) if item.get('type')=='message' for c in item.get('content',[]) if c.get('type')=='output_text')
        (DIRECTORY/f'{record["call_id"]}-text.md').write_text(extracted+'\n')
    record['recorded_at_utc']=now();append('api_calls.jsonl',record)
    (DIRECTORY/'state.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:record.get(k) for k in ['call_id','status','model_returned','cost_usd','cumulative_cost_usd','response_path','recorded_at_utc']}))

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['start','poll','cancel','recompute-cost']);p.add_argument('--without-web',action='store_true');a=p.parse_args()
    DIRECTORY.mkdir(exist_ok=True,parents=True)
    if a.action=='recompute-cost':
        for path in DIRECTORY.glob('*-response.json'):print(json.dumps({'path':str(path.relative_to(ROOT)),'calculation':cost_of(json.loads(path.read_text()))}))
        return
    key=os.environ.get('FREE_RESEARCH_OPENAI_API_KEY')
    if not key:raise SystemExit('Designated API key not set; no call made')
    client=OpenAI(api_key=key,max_retries=0,timeout=60.0)
    if a.action=='start':
        records=latest_calls()
        if len(records)>=2:raise SystemExit('Two-attempt cap reached')
        if any(x.get('cost_usd') is None for x in records.values()):raise SystemExit('Earlier call unresolved or cost unknown; no resend permitted')
        if any(x.get('status')=='completed' for x in records.values()):raise SystemExit('Completed critique already exists; reuse it')
        current=total_cost(records)
        if current>=BUDGET:raise SystemExit('Budget exhausted')
        call_id=f'topic-critique-{len(records)+1}'
        prompt=(ROOT/'protocol/critique-prompt.txt').read_text()
        request=dict(model='gpt-6-astra',reasoning={'effort':'xhigh'},input=prompt,background=True,service_tier='default')
        if not a.without_web:request.update(tools=[{'type':'web_search'}],include=['web_search_call.action.sources'])
        path=DIRECTORY/f'{call_id}-request.json';path.write_text(json.dumps(request,indent=2,ensure_ascii=False)+'\n')
        record=dict(call_id=call_id,experiment_id='topic-critique',purpose='research-question skill step 6 candidate critique',requested_at_utc=now(),provider='OpenAI',model_requested='gpt-6-astra',model_returned=None,parameters={k:v for k,v in request.items() if k!='input'},request_path=str(path.relative_to(ROOT)),response_path=None,usage=None,cost_usd=None,cumulative_cost_usd=float(current),status='requested',error=None,budget_check={'budget_usd':20,'cumulative_known_cost_usd':float(current),'maximum_next_cost_usd':None,'exception':'Explicit skill step 6 exception: no output limit/pre-call maximum-cost check; record actual cost'},sdk_max_retries=0)
        append('api_calls.jsonl',record);(DIRECTORY/'state.json').write_text(json.dumps(record,indent=2)+'\n')
        event('api_call_start','Start designated candidate critique; no maximum-output parameter set',[record['request_path'],'protocol/api-critique-plan.md'],call_id=call_id)
        try:save_response(client.responses.create(**request),record)
        except Exception as error:
            # Error messages may echo credentials; only non-secret type/status/code
            # are saved. No automatic resend after an ambiguous transport error.
            record.update(status='failed',error={'exception_type':type(error).__name__,'http_status':getattr(error,'status_code',None),'code':getattr(error,'code',None),'message':'Not retained: may echo credentials'},recorded_at_utc=now())
            append('api_calls.jsonl',record);(DIRECTORY/'state.json').write_text(json.dumps(record,indent=2)+'\n')
            print(json.dumps({'call_id':call_id,'status':'failed','error':record['error']}));raise SystemExit(1)
    else:
        record=json.loads((DIRECTORY/'state.json').read_text());rid=record.get('response_id')
        if not rid:raise SystemExit('No response ID saved; no generation call will be repeated')
        if record['status'] not in ['queued','in_progress']:
            print(json.dumps({'status':record['status'],'message':'Terminal response already saved'}));return
        age=(dt.datetime.now(dt.timezone.utc)-dt.datetime.fromisoformat(record['requested_at_utc'].replace('Z','+00:00'))).total_seconds()
        if a.action=='cancel' or age>1500:response=client.responses.cancel(rid)
        else:response=client.responses.retrieve(rid)
        save_response(response,record)

if __name__=='__main__':main()
