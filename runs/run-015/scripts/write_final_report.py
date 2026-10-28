"""Generate factual resource/intervention tallies and the submission report."""
import argparse
from collections import Counter
import datetime as dt
import json
from pathlib import Path
import subprocess

import pandas as pd

from record import ROOT,now
from summarize import clean,markdown_table

def lines(path):return [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []

def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['working','first-draft','final'],default='working')
    p.add_argument('--reason',required=True);p.add_argument('--output',default=str(ROOT/'final_report.md'));a=p.parse_args()
    stamp=now();manifest=json.loads((ROOT/'manifest.json').read_text());interventions=lines(ROOT/'interventions.jsonl')
    counts=Counter(x['type'] for x in interventions);runs=[]
    for path in sorted((ROOT/'experiments').glob('*/record.json')):
        item=json.loads(path.read_text());runs.append(item)
    run_counts=Counter(x.get('status','unknown') for x in runs)
    latest={x['call_id']:x for x in lines(ROOT/'api_calls.jsonl')};api=list(latest.values())
    api_rows=[]
    for item in api:
        u=item.get('usage') or {};api_rows.append({'model':item.get('model_returned') or item.get('model_requested'),
            'purpose':item['purpose'],'calls':1,'status':item['status'],'input_tokens':u.get('input_tokens'),
            'cache_write_input_tokens':u.get('input_tokens_details',{}).get('cache_write_tokens'),
            'cached_input_tokens':u.get('input_tokens_details',{}).get('cached_tokens'),
            'output_tokens':u.get('output_tokens'),'reasoning_output_tokens':u.get('output_tokens_details',{}).get('reasoning_tokens'),
            'cost_usd':item.get('cost_usd'),'web_search_calls':item.get('cost_calculation',{}).get('web_search_calls'),
            'pricing_source':item.get('cost_calculation',{}).get('pricing_source')})
    cost=sum(x['cost_usd'] for x in api_rows if x['cost_usd'] is not None)
    raw={}
    for phase in ['weather','weather-v4']:
        base=ROOT/'data'/phase;complete=list(base.glob('*/*/*/complete.json')) if base.exists() else []
        attempts=list(base.glob('*/*/*/unit-attempts.jsonl')) if base.exists() else []
        raw[phase]={'complete_forecast_units':len(complete),'incomplete_attempted_units':sum(not (path.parent/'complete.json').exists() for path in attempts),
                    'acquisition_invocations':sum(len(path.read_text().splitlines()) for path in attempts)}
    allocated_kib=int(subprocess.check_output(['du','-sk',str(ROOT)],text=True).split()[0])
    tally={'generated_at_utc':stamp,'stage':a.stage,'experiment_status_counts':dict(run_counts),'experiment_runs':len(runs),
           'summed_recorded_worker_seconds':sum(r.get('elapsed_seconds',0) for r in runs),
           'intervention_type_counts':dict(counts),'intervention_count':len(interventions),'api_generations':len(api_rows),
           'api_by_model_and_purpose':api_rows,'api_usage_computed_actual_cost_usd':cost,
           'api_remaining_budget_usd':manifest['ai_api']['budget_usd']-cost,'raw_units':raw,
           'directory_allocated_kib_at_check':allocated_kib,'directory_limit_bytes':manifest['limits']['storage_bytes'],
           'confirmed_excluded_usage_stop_seconds':sum(x.get('excluded_stop_seconds',0) for x in manifest['deadline_history']),
           'unquantified_stop_count':sum(x.get('duration_status') is not None for x in manifest['deadline_history']),
           'session_id':manifest['session_id'],'continuation_session_ids':manifest['continuation_session_ids']}
    primary=ROOT/'results/primary/summary.json';primary_summary=json.loads(primary.read_text()) if primary.exists() else None
    text='# Research report — free-research-015\n\nGenerated '+stamp+'. Stage: **'+a.stage+'**. Ending reason: '+a.reason+'\n\n'
    text+='## Topic and measured scope\n\nThe study audits partial identification of spatial temperature-exceedance count-tail probabilities from individual, aggregate-second-moment and pairwise releases of operational ensemble data. The target is the retained empirical forecast law. Observed weather skill, public-health benefit, real service demand, human usability, adoption, actual traffic and realized economic value were not measured. No novelty of the probability LP, dependence loss, count sufficiency or exact mask is asserted.\n\n'
    text+='This document is based on data and products of the European Centre for Medium-Range Weather Forecasts (ECMWF). © 2026 ECMWF. Data are used under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) and the recorded general terms. Location extraction, thresholding and analysis are modifications by this study; ECMWF has not endorsed them.\n\n'
    if primary_summary:
        w=pd.read_csv(ROOT/'results/primary/width-summary.csv');part=w[(w['n_sites']==12)&(w['model']=='all')&(w['lead']=='all')&(w['geometry']=='all')]
        text+=f"Primary coverage: {primary_summary['complete_forecast_units']} complete units of {primary_summary['scheduled_forecast_units']} scheduled, {primary_summary['matched_dates']} fully matched dates, status `{primary_summary['status']}`.\n\n"
        text+=markdown_table(part.to_dict('records'),[('stratum','Stratum'),('cases','Queries'),('q_zero','q=0'),('q_one','q=1'),('at_most_two_uncertain','≤2 uncertain'),('marginal_width','Marginal width'),('aggregate_width','Aggregate width'),('pair_width','Pair width'),('pair_exact_count','Pair identified')])+'\n\n'
    else:text+='Final primary results are not assembled. No final scientific finding is claimed.\n\n'
    city=ROOT/'results/city-time/summary.json'
    if city.exists():
        s=json.loads(city.read_text())
        text+=f"The exploratory city/time schedule contains {s['scheduled_dates']} dates and {4*s['scheduled_dates']} product/horizon combinations. It has {s['matched_dates']} fully matched dates, {s['complete_horizons']} complete combinations and {s['complete_raw_forecast_units']} complete raw fields; status `{s['status']}`. An adequate-date status does not mean every scheduled acquisition finished. Remaining combinations are listed in results/city-time/availability.json; all partial data and bounded failures are retained.\n\n"
    text+='Primary results, prespecified sensitivities and exploratory subset/city/coverage/identification comparisons retain separate labels. Additional midpoint, common-query member and controlled-precision comparisons are exploratory. The English manuscript is generated from analysis outputs; `claims.jsonl` maps statements to evidence and expected checks. Consult their stated denominators and scope rather than treating every query as independent.\n\n'
    text+='## Failures, incomplete matters and limitations\n\nThe original AIFS20260709/84h unit exhausted the fixed two-invocation cap, retaining 41 complete member vectors and remaining incomplete. Later overlapping coordinate extraction does not restore it to the primary sample. Technical transfer failures and all recoveries remain in per-unit logs. G002 optional IFS mask extraction failed on a relative-path log error after one HTTP request; its response outcome was lost, recorded as unknown and counted as a used attempt. G003 recovered without resetting the cap. The initially proposed city source was not downloaded after robots disallowed retrieval; Natural Earth was substituted and fixed before city data/weather extraction.\n\n'
    text+='The selected question had two relevant closest full texts checked; a second full-text check for one unselected topic candidate remained inaccessible. This is an incomplete topic-selection check, not evidence that the missing literature does not exist. Selection took less than the skill’s 60-minute guide, with the reason recorded at selection. Public author/affiliation/contact metadata occur incidentally in archived scholarly sources and are not individual-level analytical variables or contact targets.\n\n'
    text+='D002 completed a prefix of identification-diagnostic units before a numerical SVD failure. Its run command also named a nonexistent abbreviated plan path; an append-only correction identifies the actual previously committed v6 plan. D003 refused an attempted overwrite from a stale resume index. D004 resumed at the checked incomplete prefix with a documented gesvd fallback and unchanged scientific tolerances; all completed outputs and failures remain.\n\n'
    text+='A later manual audit found that the exploratory paired all-land city rows reused the broader common-informative mask. The old table, summary and source are preserved in review/corrections/city-paired-land-before. The named conditional mask was repaired under protocol/analysis-correction-v1.md, and a separate audit now checks counts and mean differences directly from saved cases and the bundled land table. Main LP endpoints and the ordinary paired comparison were unaffected. Earlier code-consistency replays did not establish correctness of that filter.\n\n'
    text+='The sampled calendar, locations, thresholds and exact finite ensembles limit generalization. LP extremal laws impose the released binary information, not an atmospheric dynamical model. Exact zero cells can strongly constrain compatibility. Resampling intervals describe a convenience calendar; sensitivity neighborhoods are not statistical confidence sets. City points are coarse snapped cartographic samples; the four-time maximum is not a continuous daily maximum or simultaneous peak load. No product/region ranking of observed forecast quality is established.\n\n'
    for name in ['sensitivity','subsets','city-time','coverage','identification','midpoints','common-members','controlled-moments','overlap-recovery','repeated-members','integer-precision']:
        path=ROOT/'results'/name/('recovery.json' if name=='overlap-recovery' else 'summary.json')
        if path.exists():
            item=json.loads(path.read_text());status=item.get('status','completed report; inspect denominators')
            text+='- `results/'+name+'/`: '+str(status)+'.\n'
        else:text+='- `results/'+name+'/`: not yet completed.\n'
    ip=ROOT/'results/integer-precision/summary.json'
    if ip.exists():
        s=json.loads(ip.read_text())
        text+=f"\nThe exploratory known-size precision check recorded {s['recorded_cases']} queries: {s['optimal_cases']} with both endpoints optimal and {s['unresolved_cases']} unresolved. At radius 0.005 all {s['epsilon005_lattice_equivalent_cases']} retain exactly the original integer moment counts. At radius 0.02 the mean width over all cases is bounded by [{s['epsilon02_mean_width_lower_bound']:.4f}, {s['epsilon02_mean_width_upper_bound']:.4f}]. These optimization bounds are not confidence limits or a measured rounding process.\n\n"
    repeated=ROOT/'results/repeated-members/summary.json'
    if repeated.exists():
        s=json.loads(repeated.read_text())
        text+=f"The repeated-member check completed {s['completed_draws']} of {s['planned_draws']} fixed draws, status `{s['status']}`. It conditions on the same retained fifty-member forecasts and frozen sensitivity queries; draws do not add independent weather cases.\n\n"
    text+='\n## Verification and records\n\n'
    verification=ROOT/'review/verification-summary.json'
    if verification.exists():
        item=json.loads(verification.read_text());text+=f"The author ran `{item['mode']}` verification with status `{item['status']}` in a fresh copy in {item['elapsed_seconds']:.1f} seconds. It is an author re-run, not independent reproduction. The report and VERIFY.md distinguish all recomputed aggregates from the reduced subset and repeated-member LP re-solves; submitted integer witnesses, solver bounds and tiny exact fixtures are checked without claiming every large MILP was solved anew.\n\n"
    else:text+='The final-state end-to-end verification has not yet been completed. Intermediate author replays are retained separately; this stage is not submission-ready.\n\n'
    text+='An earlier integrated replay (V012) failed on absolute source-path strings after its numerical solve phases. A root-relative report-reference repair was planned and recorded; the old source/output and failure remain. V013 passed an intermediate replay after the repair, and a separate final-state replay is required for submission. Source-file hashes are checked before and after each completed replay.\n\n'
    text+='Plans, commit links, input hashes, raw selected vectors, stdout/stderr, failed/partial runs, source passages, deviations and the original API response are retained. Git times are self-reported; hashes support consistency rather than tamper-proofness or independence. SHA256SUMS and hash-scope.json state the finalized exclusions; the auxiliary review/verification-work-SHA256SUMS covers retained verification copies and raw replay outputs. Package environments/caches and author verification working copies count toward the storage limit even when excluded from Git.\n\n'
    text+='## Interventions and observed usage\n\n'
    text+=markdown_table([{'type':key,'count':value} for key,value in sorted(counts.items())],[('type','Intervention type'),('count','Count')])+'\n\n'
    text+=f"Total intervention records (including author record corrections): {len(interventions)}. Permission requests/decisions: {counts['permission_request']}/{counts['permission_decision']}; unplanned scientific feedback: {counts['scientific_feedback']}; peer review received: {counts['peer_review']}. There are {counts['runtime_resume']} human resume confirmations; record corrections are administrative entries, not additional human messages. Exact human messages and observability limits are in interventions.jsonl. Confirmed excluded stop time totals {tally['confirmed_excluded_usage_stop_seconds']:.0f} seconds; {tally['unquantified_stop_count']} confirmed stops lack an exact prior tool clock reading and received no estimated extension. Current research deadline: {manifest['first_draft_deadline_utc']}.\n\n"
    text+=markdown_table(api_rows,[('model','Returned model'),('purpose','Purpose'),('calls','Generations'),('input_tokens','Input'),('cache_write_input_tokens','Cache-write input'),('output_tokens','Output'),('reasoning_output_tokens','Reasoning within output'),('web_search_calls','Web searches'),('cost_usd','Actual usage cost USD')])+'\n\n'
    text+=f"Usage-computed actual API cost: **${cost:.5f}**, remaining combined-period budget **${tally['api_remaining_budget_usd']:.5f}**. Cache-write tokens are part of input, reasoning tokens part of output; do not add them twice. Costs use the archived official price and caching pages, checked 25 October 2026 UTC, including web-search charges. No provider invoice was visible. Status checks of one response are not new generations. The copied skill explicitly exempts its one critique call from the pre-call maximum-cost check/output cap; actual cost is included. No other AI API generation or sub-agent was used for research work.\n\n"
    text+=f"Recorded experiment runs: {len(runs)}; statuses `{dict(run_counts)}`. Sum of recorded worker elapsed times is {tally['summed_recorded_worker_seconds']:.1f} seconds, not CPU time or wall-clock research duration. The main experiment runner enforces at most two workers and 1800 seconds per run. Directory allocated size at the tool check: {allocated_kib}KiB; limit 10 GiB. Source and extension raw-unit counts: `{raw}`. No new paid service/cloud route was added.\n\n"
    text+='Session-model token usage/cost, exact runtime model/provider identifier, runtime build and marginal prices of existing session tools were not observable. The presented session model is GPT-6/Codex with provider OpenAI; the critic response identifier is separately confirmed from API output. Persistent-memory/profile existence is unknown and none was sought or used for topic selection. No private user files outside the authorized scope were investigated.\n\n'
    text+='## Review response and end state\n\n'
    review=ROOT/'review/decisions.json'
    if review.exists():
        decisions=json.loads(review.read_text());by_decision=Counter(x['decision'] for x in decisions)
        original={x['claim_id']:x for x in lines(ROOT/'review/submission-1/claims.jsonl')}
        revised={x['claim_id']:x for x in lines(ROOT/'claims.jsonl')}
        fields=['text','status','scope','expected','exploratory','reader_implication']
        changed=[cid for cid in original if cid in revised and any(original[cid].get(k)!=revised[cid].get(k) for k in fields)]
        status_changed=[cid for cid in original if cid in revised and original[cid]['status']!=revised[cid]['status']]
        withdrawn=[cid for cid in status_changed if revised[cid]['status'] in ['unsupported','withdrawn']]
        added=[cid for cid in revised if cid not in original]
        start=manifest.get('review_response',{}).get('started_at_utc') or json.loads((ROOT/'review/response-clock.json').read_text())['review_received_first_tool_time_utc']
        response_runs=[r['experiment_id'] for r in runs if r['started_at_utc']>=start]
        analysis_runs=[rid for rid in response_runs if not rid.startswith('V')]
        verification_runs=[rid for rid in response_runs if rid.startswith('V')]
        tally['review_response']={'points':len(decisions),'by_decision':dict(by_decision),
            'changed_claim_ids':changed,'changed_claim_count':len(changed),'claim_status_changes':status_changed,
            'withdrawn_claim_ids':withdrawn,'new_claim_ids':added,'new_claim_count':len(added),
            'analysis_runs_added':analysis_runs,'analysis_run_count':len(analysis_runs),
            'verification_runs_added':verification_runs,'verification_run_count':len(verification_runs)}
        text+=f"Review points: {len(decisions)}; decisions `{dict(by_decision)}`. Existing claim text/scope/expected values changed in {len(changed)} records ({', '.join(changed)}), including wording/spacing changes; {len(status_changed)} statuses changed and {len(withdrawn)} claims were withdrawn. Added {len(added)} exploratory claim ({', '.join(added)}). Added {len(analysis_runs)} saved-data analysis run and {len(verification_runs)} author verification run: `{response_runs}`. These counts are computed from records, not manually assigned. See review/response-1.md for reasons, changes and added analyses.\n\n"
        text+='The review is by an AI agent, supplied by the human. Its reported model and same-machine verification (including a separate LP implementation) were not directly observed by the author and are not called independent reproduction. The review also reports a brief three-process reviewer deviation; this is retained as supplied, separate from the author’s enforced two-worker workflow. No reviewer contact, sibling review-file access or extra AI/API call occurred. The review-response deadline and any confirmed stop treatment are recorded separately from the completed research period.\n\n'
    else:text+='No planned review has yet been received. The first draft must be frozen after its submission until the human supplies REVIEW-1; this report is not a substitute review.\n\n'
    text+='Main files: paper.md, claims.jsonl, VERIFY.md, README.md, final_report.md, protocol/, results/, review/, manifest.json, events.jsonl, interventions.jsonl, sources.jsonl, api_calls.jsonl, checkpoint.md, SHA256SUMS. Files absent at this stage remain incomplete. No external publication/contact has occurred.\n\n'
    text+='Conversation session ID: '+str(manifest['session_id'])+'; continuation IDs: '+json.dumps(manifest['continuation_session_ids'])+'. These are unknown/empty when not exposed; process/PTY session IDs are not substituted for conversation IDs. Preserve this conversation and the submitted Git tag/commit.\n'
    Path(a.output).write_text(text);(ROOT/'usage-tally.json').write_text(json.dumps(clean(tally),indent=2,allow_nan=False)+'\n')
    print(json.dumps({'generated_at_utc':stamp,'stage':a.stage,'experiment_runs':len(runs),'api_cost_usd':cost,'interventions':len(interventions)}))

if __name__=='__main__':main()
