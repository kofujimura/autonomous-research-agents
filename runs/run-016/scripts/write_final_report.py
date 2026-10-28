"""Generate resource/process tallies and a bounded research report from records."""
import argparse,datetime,json,subprocess
from collections import Counter
from records import ROOT,now
from study_tallies import tally,read_lines

def run(phase):
    observed=now();m=json.loads((ROOT/'manifest.json').read_text());t=tally()
    events=read_lines('events.jsonl');interventions=read_lines('interventions.jsonl')
    claims={r['claim_id']:r for r in read_lines('claims.jsonl')}
    submission=next((r for r in events if r['type']=='first_draft_submission'),None)
    end=(submission or {}).get('observed_at_utc',observed)
    dt=lambda x:datetime.datetime.fromisoformat(x.replace('Z','+00:00'))
    excluded=sum(r['excluded_seconds'] for r in m['deadline_adjustments'] if r['period']=='research')
    elapsed=(dt(end)-dt(m['start_time_utc'])).total_seconds()-excluded
    refreshed=all((ROOT/f'results/inference/logistic-broad-refreshed-{rep}/analysis.json').exists() for rep in ['tessera','alphaearth'])
    extra=(ROOT/'results/additional-geography/analysis.json').exists()
    verification=[]
    for path in sorted((ROOT/'review').glob('verification-*.json')):
        r=json.loads(path.read_text())
        if 'status' not in r:continue
        verification.append(dict(path=str(path.relative_to(ROOT)),status=r['status'],elapsed_seconds=r['elapsed_seconds'],
            main_csv_checks=len(r['table_checks']),supplemental_csv_checks=sum(len(s['csv_checks']) for s in r.get('supplemental_checks',[])),
            main_raw_files=len(r.get('raw_array_checks',[])),supplemental_raw_files=sum(len(s.get('raw_array_checks',[])) for s in r.get('supplemental_checks',[])),
            valid_as_final_submission_check=r.get('valid_as_final_submission_check',True),document_checks=r.get('document_checks',[])))
    initial_fits=[json.loads(p.read_text()) for p in (ROOT/'results/source-models').glob('*/fit.json')]
    warnings=sum(bool(r['fit_records'][0]['convergence_warnings']) for r in initial_fits)
    download_status=dict(Counter(r.get('status') for r in read_lines('data/downloads.jsonl')))
    runs=t['experiment_runs'];failed=[r for r in runs if r['status'] not in ['completed','running']]
    review_received=(ROOT/'review/review-1.md').exists()
    state={'working':'Working paper; experiments/verification still being finalized.',
           'submission-1':'First-draft snapshot prepared for the planned review by an AI agent; no review result has been received.',
           'final':'Final revised submission; see review/response-1.md or the recorded no-review decision.'}[phase]
    result=dict(observed_at_utc=observed,phase=phase,state=state,trial_id=m['trial_id'],start_time_utc=m['start_time_utc'],
        first_draft_deadline_utc=m['first_draft_deadline_utc'],research_elapsed_seconds_as_of_report=elapsed,
        confirmed_usage_limit_excluded_seconds=excluded,research_end_from_submission_receipt=submission is not None,
        refreshed_comparison_complete=refreshed,additional_geography_complete=extra,review_received=review_received,
        observable_tallies=t,verification=verification,initial_source_fits=len(initial_fits),initial_nonconverged_fits=warnings,
        public_download_attempt_status_counts=download_status,failed_bounded_runs=failed,
        current_claim_status_counts=dict(Counter(r['status'] for r in claims.values())),
        storage_peak_observability='Automatic Git packing occurred between checkpoints. Temporary peak unknown; possible transient ceiling breach cannot be ruled out. Current counts do not establish continuous compliance.',
        session_ids=dict(session_id=m['session_id'],continuation_session_ids=m['continuation_session_ids']))
    if (ROOT/'review/response-summary.json').exists():result['review_response']=json.loads((ROOT/'review/response-summary.json').read_text())
    (ROOT/'results/study-tallies.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Research report',f"Observed at {observed}. {state}",
      '## Study and attained scope',
      'Title: '+(ROOT/'paper.md').read_text().splitlines()[0].lstrip('# ')+'.',
      'Question: At a fixed annual reference-label budget, how reliably do estimates using frozen annual-embedding classifiers identify changes in declared crop-group diversity, and does revisiting improve inference relative to independent samples?',
      'The original cohort contains 20 training, 10 calibration and 30 test landscapes; three target-year transitions and 500 Monte Carlo trials per condition. Main results concern 17 published agricultural groups; 54 groups are a prespecified check. Methods, source input sizes and label burden are in paper.md and its generated tables. Labels measure declared intent rather than independently observed harvest.',
      f"Prespecified finer taxonomy, forest, secondary years, native-grid and reference-error checks are complete. Refreshed-head comparison complete: {refreshed}. Added geographical reference-only comparison complete: {extra}. Exploratory strata, weighting, jackknife, entropy envelopes, gradient floors and coherent panels retain all original results.",
      '## Confirmed numerical results']
    for cid in sorted(claims):
        if cid in claims:
            r=claims[cid];lines += [f"- {cid}: {r['text']} Expected values: `{json.dumps(r['expected'],ensure_ascii=False)}`. Scope and reproduction: claims.jsonl."]
    lines += ['Magnitude coverage and wrong-direction reporting are different outcomes. In the original n128 direct comparison, revisiting gives more reports and fewer wrong directions in aggregate despite lower magnitude-interval coverage. A no-change point baseline is not evidence that an individual landscape did not change.',
      '## Limits, failures and unfinished work',
      'No representative national estimate, field-visit cost, user outcome, policy effect, ecological effect or independent harvest validation was measured. Source training/calibration and five-year eligibility information are outside audit-label counts. Reference frames, model releases, taxonomy, numerical gradient, conditional fitted maps and the selected period bound every claim.',
      f"Initial source fits reaching their iteration limit: {warnings}/{len(initial_fits)}; all revised source heads were fixed before target outcomes. Failed bounded run count: {len(failed)}. Label-attempt statuses: `{json.dumps(t['label_attempt_status_counts'])}`. Feature-attempt statuses: `{json.dumps(t['feature_attempt_status_counts'])}`. Per-case and pilot failure records remain in their ledgers/directories; batch exit0 is not universal candidate success.",
      'One recorded short unwrapped diagnostic briefly exceeded the two-experiment limit and lacked a configured runner timeout; it exited normally and its record is retained. One paper-formatting run recorded a stale code commit because the commit was still finishing; the correction identifies its actual later code snapshot and a committed-code rerun. The runner now checks committed scripts/plans and stores script hashes.',
      result['storage_peak_observability']+' See review/git-packing-storage-observation.json. Subsequent study commits disable automatic maintenance with per-command options, without global configuration changes or history rewriting.',
      ('The refreshed diagnostic is complete; its extra training labels are explicitly not budget-matched to small audits.' if refreshed else 'Refreshed-head acquisition/fitting is unfinished in this report; no refreshed result is asserted.'),
      ('Additional-geography results are retained separately and exploratory.' if extra else 'The separately fixed additional-geography extension is not yet complete; its absent results are not presented as evidence.'),
      '## Verification']
    for r in verification:lines.append(f"- {r['path']}: {r['status']}; {r['elapsed_seconds']:.3f}s; CSV checks {r['main_csv_checks']}+{r['supplemental_csv_checks']}; raw-array files {r['main_raw_files']}+{r['supplemental_raw_files']}; valid as final submission check: {r['valid_as_final_submission_check']}.")
    lines += ['These are reruns by this same session. Immutable input sharing and post-comparison exact-array sharing preserve all scientific arrays while reducing duplicate storage; neither constitutes independent reproduction. VERIFY.md is the single procedure. A full final check must reject still-running experiments.',
      '## Interventions and observable usage',f"Human intervention records by type: `{json.dumps(t['intervention_types'])}`. No unplanned human research advice is inferred. Planned AI-agent review received: {review_received}."]
    for r in interventions:lines.append(f"- {r['intervention_id']}: {r['type']}, observed {r['observed_at_utc']}; decision `{r['decision']}`; effect `{r['effect']}`. Message identifiers/approver details are not invented when unobservable.")
    lines += [f"Unique AI API generations: {t['unique_api_generations']}. Tariff-derived actual cost: USD {t['api_cost_usd']:.6f} of the USD 20 total budget. Status retrievals and ledger corrections are not additional generations. No other AI performed research work. No numerical verification step calls an API."]
    api_table=['| Model returned | Purpose | Input tokens | Cached read | Cache write | Output incl. reasoning | Reasoning subset | Web calls | Actual USD |',
      '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in t['api']:
        api_table.append(f"| {r['model']} | {r['purpose']} | {r['input_tokens']} | {r['cached_input_tokens']} | {r['cache_write_30m_tokens']} | {r['output_tokens_including_reasoning']} | {r['reasoning_tokens']} | {r['web_search_calls']} | {r['recorded_cost_usd']:.6f} |")
    lines.append('\n'.join(api_table))
    lines += ['Prices and check dates are in api_calls.jsonl, sources/openai-pricing.md and the prompt-caching documentation. The actual tally includes the cache-write premium and web searches; the original estimate/correction is retained. Reasoning tokens are a subset of billed output. Provider invoices and this session model\'s own token usage/billing are not exposed. No figures are guessed for them.',
      f"Confirmed usage-limit exclusion: {excluded} seconds. The second exclusion has a documented endpoint uncertainty; see manifest.json. Research elapsed time as of this report: {elapsed:.3f} seconds; the pre-review waiting interval is excluded once submission/receipt events exist. Current deadline: {m['first_draft_deadline_utc']}. Session identifier: {m['session_id']}; continuation IDs: `{m['continuation_session_ids']}`.",
      f"Storage at tally time: {t['storage_unique_inode_bytes']} unique-inode payload bytes; {t['storage_logical_path_bytes_including_environment_cache_git_and_verification']} logical path bytes including hardlink aliases. All unique payload is inside the research directory; dependencies/caches/Git are included. This is a point observation, not a measured high-water mark.",
      '## Outputs and ending state',
      'Main files: paper.md, claims.jsonl, VERIFY.md, README.md, DATA_LICENSES.md, manifest.json, protocol/, experiments/, results/, sources.jsonl, review/self-check.md, review/ verification records and the submission SHA-256 manifest. Initial instructions/skill copies are unchanged. Each completed stage and failed attempt remains referable; missing future-stage files are not marked complete.',
      state+' The submitted commit/tag and terminal submission time are recorded in events.jsonl and reported to the conversation. No external publication or contact was made. Tallies are as of the report timestamp; subsequent terminal commit receipts are append-only bookkeeping.']
    if 'review_response' in result:
        lines += ['## Review response',json.dumps(result['review_response'],indent=2), 'One review by an AI agent was supplied by the human. The review reports a clean fresh-environment rerun; this is recorded as the reviewer’s report, not a verification directly observed by this session. Additional exploratory label-error and within-cohort resampling analyses used no other AI and no new API calls. Review-response start and deadline: '+m['review_response_start_utc']+'; '+m['review_response_deadline_utc']+'.']
    (ROOT/'final_report.md').write_text('\n\n'.join(lines)+'\n')
    print(json.dumps(dict(observed_at_utc=observed,phase=phase,api_cost_usd=t['api_cost_usd'],refreshed_complete=refreshed,additional_geography_complete=extra,storage_unique_inode_bytes=t['storage_unique_inode_bytes'])))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=['working','submission-1','final'],default='working');a=p.parse_args();run(a.phase)
