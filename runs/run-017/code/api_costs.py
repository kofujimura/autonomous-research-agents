"""Recompute API cost components without making an API call."""
from decimal import Decimal as D
import json
from pathlib import Path

def compute(root):
    raw=json.loads((root/'api/responses/API001.json').read_text())
    u=raw['usage'];d=u.get('input_tokens_details',{})
    writes=d.get('cache_write_tokens',0);cached=d.get('cached_tokens',0)
    ordinary=u['input_tokens']-writes-cached
    search_items=sum(x.get('type')=='web_search_call' for x in raw['output'])
    fixed=(D(ordinary)*D('10')+D(cached)*D('1')+D(u['output_tokens'])*D('50'))/D(1000000)+D(search_items)*D('.01')
    costs=[fixed+D(writes)*rate/D(1000000) for rate in [D('12.5'),D('25')]]
    return dict(call_id='API001',model=raw['model'],input_tokens=u['input_tokens'],
        ordinary_input_tokens=ordinary,cached_input_tokens=cached,cache_write_tokens=writes,
        output_tokens=u['output_tokens'],reasoning_tokens=u['output_tokens_details'].get('reasoning_tokens'),
        web_search_call_items=search_items,provider_tool_usage_web_requests=(raw.get('tool_usage',{}).get('web_search',{}).get('num_requests')),
        requested_cache_options=None,returned_prompt_cache_retention=raw.get('prompt_cache_retention'),
        returned_write_lifetime_breakdown=d.get('cache_write_tokens_details'),
        cost_usd=None,cost_usd_lower_bound=float(costs[0]),cost_usd_upper_bound=float(costs[1]),
        reason='Returned write-token count lacks the current 30m/12h lifetime breakdown and legacy retention is 24h. Prices for both current lifetimes are confirmed, but exact invoice-priced write charge is not observable. Do not invent a lifetime. Search item count follows skill step 6, which differs from provider tool_usage request count.',
        price_source='data/literature/openai-pricing.md',cache_documentation='data/literature/prompt-caching.md')

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    print(json.dumps(compute(root),indent=2))
