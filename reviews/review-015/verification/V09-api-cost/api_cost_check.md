# API cost recomputation (reviewer, by hand from saved records; no API call)
Source: run-015 api_calls.jsonl last record for call_id topic-critique-1 (usage), literature/openai-pricing.md line 38 (gpt-6-astra short-context Standard: input $10/M, output $50/M, 30m cache write $12.50/M), lines 468 (web search $10 / 1k calls), literature/openai-prompt-caching.md line 17 (cache-write tokens billed at the write rate instead of the uncached rate).
- uncached input: 116195 - 6424 = 109771 tokens x $10/M = $1.09771
- cache write: 6424 x $12.50/M = $0.08030
- output (incl. 9849 reasoning): 14327 x $50/M = $0.71635
- web search: 13 calls x $0.01 = $0.13000
- total = $2.02436 (matches recorded cost_usd 2.02436; budget $20). Short-context rate applies (116k input, below the long-context threshold shown for other models as 272K; threshold for gpt-6-astra itself not stated on the archived page row).
