"""The only AI API entry point for this study: required topic critique only."""
import argparse,json,os,sys
from pathlib import Path
from openai import OpenAI
from records import ROOT,now,append,event,digest

DIR=ROOT/'experiments/topic-critic';DIR.mkdir(parents=True,exist_ok=True)
PRICE={'input_per_million':10.,'cached_input_per_million':1.,'output_per_million':50.,
       'web_search_call':.01,'long_input_per_million':20.,'long_cached_input_per_million':2.,
       'long_output_per_million':75.,'source':'https://developers.openai.com/api/docs/pricing',
       'checked_date':'2026-10-26','saved_path':'sources/openai-pricing.md'}

def client():
    return OpenAI(api_key=os.environ['FREE_RESEARCH_OPENAI_API_KEY'],
                  base_url='https://api.openai.com/v1',max_retries=0,timeout=60.)

def latest_calls():
    result={}
    for line in (ROOT/'api_calls.jsonl').read_text().splitlines():
        obj=json.loads(line);result[obj['call_id']]=obj
    return result

def total():return sum(x.get('cost_usd') or 0 for x in latest_calls().values())

def save_response(call_id,response):
    obj=response.model_dump(mode='json')
    path=DIR/(call_id+'_'+now().replace(':','-')+'.json')
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
    return obj,str(path.relative_to(ROOT))

def account(rec,obj,path):
    rec.update(model_returned=obj.get('model'),status=obj.get('status'),response_path=path,
               usage=obj.get('usage'),error=obj.get('error'),updated_at_utc=now())
    if obj.get('status') not in ['queued','in_progress']:
        use=obj.get('usage')
        if use:
            inp=use['input_tokens'];out=use['output_tokens']
            details=use.get('input_tokens_details') or {}
            cached=details.get('cached_tokens',0)
            writes=details.get('cache_write_tokens',0)
            ttl=details.get('cache_write_tokens_details') or {}
            # No TTL was specified in A001: official documented default is 30m.
            w12=ttl.get('ttl_12h_tokens',0)
            w30=ttl.get('ttl_30m_tokens',writes-w12)
            ordinary=inp-cached-writes
            assert ordinary>=0 and w30+w12==writes
            web=sum(x.get('type')=='web_search_call' for x in obj.get('output',[]))
            long=inp>272000
            i,c,o=(20.,2.,75.) if long else (10.,1.,50.)
            cost=(ordinary*i+cached*c+w30*i*1.25+w12*i*2.5+out*o)/1e6+web*PRICE['web_search_call']
            rec.update(cost_usd=cost,web_search_calls=web,price_table=PRICE,
                       cache_write_price_source='sources/openai-prompt-caching.md',
                       cost_components_usd={'uncached_input':ordinary*i/1e6,'cached_input':cached*c/1e6,
                                            'cache_write_30m':w30*i*1.25/1e6,'cache_write_12h':w12*i*2.5/1e6,
                                            'output_including_reasoning':out*o/1e6,'web_search':web*.01})
        else:rec.update(cost_usd=None,charge_observability='No usage returned; charges unknown')
    calls=latest_calls();calls[rec['call_id']]=rec
    rec['cumulative_cost_usd']=sum(x.get('cost_usd') or 0 for x in calls.values())
    rec['cumulative_cost_incomplete']=any(x.get('cost_usd') is None and x['status'] not in ['queued','in_progress'] for x in calls.values())
    append('api_calls.jsonl',rec)
    if obj.get('status') not in ['queued','in_progress']:
        texts=[c.get('text','') for x in obj.get('output',[]) if x.get('type')=='message'
               for c in x.get('content',[]) if c.get('type')=='output_text']
        (DIR/(rec['call_id']+'-output.txt')).write_text('\n'.join(texts)+'\n')
        m=json.loads((ROOT/'manifest.json').read_text());m['api']['actual_cost_usd']=rec['cumulative_cost_usd']
        m['api']['price_source']=PRICE;m['api']['cost_incomplete']=rec['cumulative_cost_incomplete']
        (ROOT/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
        event('critic_api_terminal','Required topic critique '+str(obj.get('status')),
              [path,'api_calls.jsonl'],[rec['call_id']],cost_usd=rec.get('cost_usd'))
    print(json.dumps({k:rec.get(k) for k in ['call_id','status','response_path','model_returned','cost_usd','cumulative_cost_usd']}))

def start(prompt_path,no_web=False):
    calls=latest_calls()
    if len(calls)>=2:raise SystemExit('Critic maximum of two generation attempts reached')
    if any(x['status'] in ['queued','in_progress'] for x in calls.values()):raise SystemExit('A critique is already running')
    if total()>=20:raise SystemExit('Budget exhausted')
    if calls and any(x['status']=='completed' for x in calls.values()):raise SystemExit('Completed critique already exists; reuse it')
    call_id='A%03d'%(len(calls)+1);prompt=(ROOT/prompt_path).read_text()
    req=dict(model='gpt-6-astra',reasoning={'effort':'xhigh'},background=True,
             input=prompt)
    if not no_web:req.update(tools=[{'type':'web_search'}],include=['web_search_call.action.sources'])
    rp=DIR/(call_id+'-request.json');rp.write_text(json.dumps(req,indent=2,ensure_ascii=False)+'\n')
    rec=dict(call_id=call_id,experiment_id='topic-selection',purpose='Required candidate critique, skill step 6',
             requested_at_utc=now(),provider='OpenAI',model_requested=req['model'],model_returned=None,
             parameters={k:v for k,v in req.items() if k!='input'},request_path=str(rp.relative_to(ROOT)),
             response_path=None,usage=None,cost_usd=None,cumulative_cost_usd=total(),status='requesting',error=None,
             budget_check={'budget_usd':20,'cumulative_known_actual_before_call':total(),
                           'maximum_next_cost':None,'exemption':'research-question step 6 explicitly exempts uncapped mandatory critique',
                           'price_confirmed':True},prompt_source=prompt_path,prompt_sha256=digest(ROOT/prompt_path))
    append('api_calls.jsonl',rec)
    event('critic_api_start','Required one-time candidate critique; no scores sent',[str(rp.relative_to(ROOT)),prompt_path],[call_id])
    try:
        resp=client().responses.create(**req)
        obj,path=save_response(call_id,resp)
        (DIR/(call_id+'-id.txt')).write_text(resp.id+'\n');account(rec,obj,path)
    except Exception as e:
        err=str(e).replace(os.environ['FREE_RESEARCH_OPENAI_API_KEY'],'[REDACTED]')
        rec.update(status='failed',error={'type':type(e).__name__,'message':err},updated_at_utc=now(),
                   charge_observability='Usage unavailable; failure charges unknown')
        append('api_calls.jsonl',rec);print(json.dumps({'call_id':call_id,'status':'failed','error_type':type(e).__name__}))
        raise SystemExit(1)

def status(call_id,cancel=False):
    rec=latest_calls()[call_id]
    ident=(DIR/(call_id+'-id.txt')).read_text().strip()
    resp=client().responses.cancel(ident) if cancel else client().responses.retrieve(ident)
    obj,path=save_response(call_id,resp);account(rec,obj,path)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['start','status','cancel']);p.add_argument('value')
    p.add_argument('--no-web',action='store_true');a=p.parse_args()
    if a.action=='start':start(a.value,a.no_web)
    else:status(a.value,a.action=='cancel')
