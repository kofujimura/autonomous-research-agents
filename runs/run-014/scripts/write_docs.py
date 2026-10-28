"""Author-written first-draft documentation with tool-derived tallies and runtimes."""
import collections,datetime as dt,json,subprocess
from pathlib import Path
from record import ROOT,now
from report import record_summary,latest_self_rerun,rerun_covers_current

def stamp_parse(s):return dt.datetime.fromisoformat(s.replace('Z','+00:00'))

def update_verify(claims,path,result,covered):
    stages={x['stage']:x['elapsed_seconds'] for x in result.get('stage_timings',[])} if result else {}
    stage_map={
        'C001':['main_v1'],'C002':['main_v1'],'C003':['main_v1'],'C004':['prepare_lcmap'],
        'C005':['endpoint_v13'],'C006':['reference_completeness_v14'],
        'C007':['robustness_aef_v12','cohort_history_feasibility'],
        'C008':['secondary_v2','robustness_paired_v12'],
        'C009':['initial_lcmap_v17','initial_nlcd_v17'],'C010':['geography_lcmap_v18'],
        'C011':['class_lcmap_v19'],'C012':['nlcd_v4'],'C013':['native_v5'],
        'C014':['reference_access_lcmap_v20','reference_access_nlcd_v20'],
        'C015':['unfinished_native_pairs_v21'],'C016':['native_single_date_v22','native_identity_v22'],
        'C017':['direct_inputs_lcmap_v23','direct_inputs_nlcd_v23'],'C018':['partition_sensitivity_v24'],'C019':['review_diagnostics_r1'],'C020':['review_diagnostics_r1']}
    e=lambda cid:claims[cid]['expected']
    mag=[x for x in e('C003') if x['task']=='gain'];stable=e('C005')['magnitude_rows'][0]
    rate=next(x for x in e('C011')['class_rate'] if x['task']=='gain')
    f=e('C012');late=next(x for x in f['magnitude'] if 'beyond' in x['availability_mode'] and x['model']=='tessera' and x['task']=='gain')
    native=e('C013');pair=e('C015');ident=e('C016')['summary']
    di=[x for x in e('C017')['lcmap_contrasts']+e('C017')['forest_contrasts'] if x['method']=='direct_difference' and x['baseline_method']=='direct_gradient_boosting']
    gain=[x for x in di if x['task']=='gain'];loss=[x for x in di if x['task']=='loss']
    expected={
        'C001':f"{len(e('C001'))} contrasts, mixed point directions; every changed-flag count and interval matches expected.",
        'C002':f"Higher direct J point estimates in {sum(x['delta_J']>0 for x in e('C002'))}/{len(e('C002'))} original conditions, unequal label resources.",
        'C003':f"Magnitude flags {mag[0]['true_positive']}/{mag[0]['n_positive']} gains in all {len(mag)} product/support rows; retain loss counts.",
        'C004':'All supplied initial classes and counts match; read task definitions and official metadata; no ecological outcome measured.',
        'C005':f"Stable-negative condition: {stable['n_positive']} gain positives/{stable['n_negative']} negatives, magnitude TP={stable['true_positive']}; raw scalar reconstruction matches.",
        'C006':f"Changed test scores={e('C006')['changed_test_scores']}; TESSERA gain contrast {e('C006')['original_delta_J']:+.6f} to {e('C006')['intersection_delta_J']:+.6f} via calibration.",
        'C007':f"{e('C007')['later_labels']}/{e('C007')['cohort']} later labels, {e('C007')['known_later_binary_disagreements']} known disagreements; saved-history route matches={e('C007')['saved_forest_history_route']['cohort_plots_with_match']}.",
        'C008':f"All {len(e('C008'))} added-readout rows and fixed calibration conditions match; no winning rule selected.",
        'C009':f"Input-period rows match separately by endpoint; permutation leaves {e('C009')['permutation_check']['scored_rows']} initial-only rows unchanged.",
        'C010':f"All {len(e('C010'))} LCMAP geographic readout/task rows match; one baseline without embedding values.",
        'C011':f"Class-rate gain TP={rate['true_positive']}/{rate['n_positive']}, FP={rate['false_positive']}/{rate['n_negative']}; initial-class strata retained; constant loss condition is predictable.",
        'C012':f"{f['unchanged_original_thresholds']} original thresholds match; direct J higher in {sum(x['delta_J']>0 for x in f['direct_contrasts'])}/{len(f['direct_contrasts'])}; later TESSERA magnitude TP={late['true_positive']}/{late['n_positive']}.",
        'C013':f"Native {native['native_present']}/{native['planned_point_years']} slots, {native['valid_centres']} valid centres, {native['raw_centres_equal']} raw centre matches; all summary quantiles match.",
        'C014':f"Eighth-reference median {e('C014')['original_reference_eighth_median_m']/1000:.3f} to {e('C014')['all_region_reference_eighth_median_m']/1000:.3f} km; all contrasts and supervised invariance match.",
        'C015':f"{pair['status']}: {pair['present_point_years']}/{pair['planned_point_years']} point-years, {pair['complete_native_file_pairs']}/{pair['planned_pairs']} complete pairs. Empty counts are not stability evidence.",
        'C016':f"{ident['pairs']} single-date cases, {ident['changed_pairs']} pairs with any flag change; all input/score identity and method-case counts match.",
        'C017':f"Difference-only minus both-date point J negative in {sum(x['delta_J']<0 for x in gain)}/{len(gain)} gain and positive in {sum(x['delta_J']>0 for x in loss)}/{len(loss)} loss conditions; all inputs/intervals retained, exploratory reused data.",
        'C018':f"All {e('C018')['summary']['completed_partitions']} fixed partition assignments, reconstruction/invariance and {len(e('C018')['primary_ranges'])} primary range rows match; retain availability counts.",
        'C019':f"All {len(e('C019')['pooled_similarity'])} primary score correlations and exact fold/year drift/count rows match; multi-year summaries are reference-only.",
        'C020':f"All {len(e('C020')['sample_support'])} support rows and {len(e('C020')['magnitude_ranking'])} magnitude-ranking rows match, including unchanged-only negatives.",
        'P001':f"Peak {e('P001')['recorded_peak']} rather than permitted {e('P001')['permitted']} for {e('P001')['registered_overlap_seconds']:g} seconds; later guard recorded.",
        'P002':f"{e('P002')['recorded_failed_attempts']} recorded errors/{e('P002')['distinct_task_ids']} task IDs; original arrays lost and repair used."}
    rows=[]
    for cid in sorted(claims):
        names=stage_map.get(cid,[])
        timing=(f"{sum(stages[n] for n in names):.3f}s: "+', '.join(names)) if names and all(n in stages for n in names) else ('Expanded rerun pending' if names else 'Read-only manual log/definition inspection; time not measured')
        evidence=claims[cid]['evidence_paths'][0]
        rows.append(f'| {cid} | {evidence} | {expected[cid]} | {timing} |')
    main='''## Main claims and expected checks

Exact unrounded expected values, scope and verification paths are in claims.jsonl. Regenerated folders have the same names under new-results. The observed stage durations below are measured on the author's machine **after shared prerequisites**, not independent per-claim runtimes or promises for other hardware. Rows share stages and their times must not be added. The single full run remains the complete procedure. Manual reading times were not measured.

| Claim | First evidence file | Expected result and check | Observed stage time(s) |
| --- | --- | --- | --- |
'''+ '\n'.join(rows)+'\n\n'
    verify=(ROOT/'VERIFY.md').read_text();start=verify.index('## Main claims and expected checks');end=verify.index('## Integrity and chronology')
    verify=verify[:start]+main+verify[end:]
    if '## Measured self-rerun' in verify:start=verify.index('## Measured self-rerun')
    else:start=verify.index('The measured end-to-end self-rerun outcome')
    end=verify.index('## Quick saved-evidence check')
    if result:
        status=f'''## Measured self-rerun

Latest record: {path.relative_to(ROOT)}. Candidate {result['candidate_commit']} returned {result['status']} with {result['check_count']} checks and {result['stage_count']} timed stages in {result['elapsed_seconds']:.3f} seconds (wrapper elapsed {result['wrapper_elapsed_seconds']:.3f} seconds). Its {result['source_files_before']} source working files were unchanged: {result['source_unchanged']}. Current numerical code covered by that candidate: **{covered}**. This is an author self-rerun, not independent reproduction. If coverage is False, later scientific additions still require an expanded run. Environment installation is not included in these durations. The author used an external 1800-second experiment timeout for this run; the direct entry point does not impose a timeout itself.

'''
    else:status='## Measured self-rerun\n\nNot yet executed; no success asserted.\n\n'
    verify=verify[:start]+status+verify[end:]
    start=verify.index('## Quick saved-evidence check');end=verify.index('## Main claims and expected checks')
    auditfile=ROOT/'review'/('saved-flag-audit-'+path.stem.rsplit('-',1)[1]+'.json') if path else None
    audit=json.loads(auditfile.read_text()) if auditfile and auditfile.exists() else None
    measured=f"The saved check in that candidate took {audit['elapsed_seconds']:.6f} seconds for {len(audit['checks'])} result sets." if audit else 'A recorded duration is not yet available.'
    quick='''## Quick saved-evidence check

```
/path/to/verification-venv/bin/python -B /path/to/source-copy/scripts/audit_saved.py
```

This separate counter checks saved prediction/flag counts and operating points, including strict-threshold flags and native case summaries. It does not reconstruct raw vectors or fit models, and is not a substitute for the full entry point. It prints PASS or raises an error and writes no source files. '''+measured+'\n\n'
    verify=verify[:start]+quick+verify[end:];(ROOT/'VERIFY.md').write_text(verify)

def write_docs():
    c={r['claim_id']:r for r in map(json.loads,(ROOT/'claims.jsonl').read_text().splitlines())}
    m=json.loads((ROOT/'manifest.json').read_text());r=record_summary();path,v=latest_self_rerun()
    covered=rerun_covers_current(v);ready=bool(v and v['status']=='PASS' and v['source_unchanged'] and covered)
    review_mode=bool(m.get('review_received_at_utc'))
    title=(ROOT/'paper-methods.md').read_text().splitlines()[0].lstrip('# ')
    report_heading='Final research report' if review_mode else 'First-draft research report'
    phase=('Revised package after review by an AI agent; full verification complete.' if ready else 'Review revision in progress; expanded numerical verification pending.') if review_mode else ('Prepared first-draft package; review has not been received.' if ready else 'Working package; expanded numerical verification is still pending.')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    r['snapshot_commit']=head;(ROOT/'review/record-summary.json').write_text(json.dumps(r,indent=2)+'\n')
    claims_status=dict(collections.Counter(x['status'] for x in c.values()))
    api=r['api_latest_records'];uses=collections.Counter((x['model_returned'],x['purpose']) for x in api)
    input_tokens=sum(x['usage']['input_tokens'] for x in api);output_tokens=sum(x['usage']['output_tokens'] for x in api)
    reasoning=sum(x['usage'].get('output_tokens_details',{}).get('reasoning_tokens',0) for x in api)
    cached=sum(x['usage'].get('input_tokens_details',{}).get('cached_tokens',0) for x in api)
    writes=sum(x['usage'].get('input_tokens_details',{}).get('cache_write_tokens',0) for x in api)
    total_cost=sum(x['cost_usd'] for x in api);searches=sum(x.get('web_search_calls',0) for x in api)
    api_table='\n'.join(f'| {model} | {purpose} | {n} |' for (model,purpose),n in uses.items())
    interventions=[json.loads(x) for x in (ROOT/'interventions.jsonl').read_text().splitlines()]
    intervention_table='\n'.join(f'| {x["intervention_id"]} | {x["type"]} | {x["observed_at_utc"]} | {x["decision"]} |' for x in interventions)
    stop_seconds=sum(x.get('excluded_seconds',0) for x in m['deadline_changes'])
    research_end=m.get('first_draft',{}).get('submitted_at_utc',r['observed_at_utc'])
    active_seconds=(stamp_parse(research_end)-stamp_parse(m['start_time_utc'])).total_seconds()-stop_seconds
    science=sum(x['claim_id'].startswith('C') for x in c.values())
    native=c['C013']['expected'];empty=c['C015']['expected'];ident=c['C016']['expected']['summary']
    primary=c['C001']['expected'];direct=c['C002']['expected'];ext=c['C012']['expected'];hist=c['C007']['expected']['saved_forest_history_route']
    verification=(f'{v["status"]}; {v["check_count"]} checks, {v["stage_count"]} measured stages, {v["elapsed_seconds"]:.3f} seconds; source working files unchanged={v["source_unchanged"]}; current numerical code covered={covered}. Candidate {v["candidate_commit"]}. Record: {path.relative_to(ROOT)}.' if v else 'Not yet executed.')
    report=f'''# {report_heading} — {m['trial_id']}

{phase}

## Study and supported scope

**{title}.** The question is whether year-matched references or separate control-plot mean changes improve classification of these CONUS one-year cover transitions over a fixed start-year reference and supervised classifiers. It is a retrospective public-data measurement study. All initial classes are supplied. The original LCMAP dominant-Trees endpoint and the separate Annual NLCD Forest endpoint remain distinct; neither measures ecological restoration success or benefits to users.

## Results and unresolved tests

- All {len(primary)} original primary correction contrasts and their changed-case counts are retained. Directions vary; gain uncertainty does not establish equivalence or a population zero effect. The original direct classifier has higher J point estimates in {sum(x['delta_J']>0 for x in direct)}/{len(direct)} main conditions, with different earlier-label resources.
- Scalar magnitude flags no observed original gains under the original fixed partition. The separate Forest sample has a later TESSERA exception. Original Forest threshold comparisons match in {ext['unchanged_original_thresholds']} rows; the direct classifier has higher J point estimates in {sum(x['delta_J']>0 for x in ext['direct_contrasts'])}/{len(ext['direct_contrasts'])} original Forest conditions. Complete counts and intervals are in claims.jsonl and the paper tables.
- Exploratory initial-only, matched direct-input, coordinate, initial-class and fitting/calibration-partition comparisons identify different associations and input dependencies. They do not establish forecasting, static-context causation, encoder drift, leakage or annotation efficiency. Matched direct-input Forest results reuse already-inspected outcomes; all four input choices remain reported. All original correction contrasts span both signs across the ten fixed earlier-partition assignments, and the original direct TESSERA loss advantage does not hold in every split. AlphaEarth centre-magnitude gain detections also have an isolated nonzero partition, retained in the paper rather than hidden by the original zero count.
- Native co-location reached {native['native_present']}/{native['planned_point_years']} selected point-years, with {native['raw_centres_equal']} raw centre matches among {native['valid_centres']} valid centres. The fixed paired-native check remains **{c['C015']['status']}**: {empty['present_point_years']}/{empty['planned_point_years']} point-years, {empty['complete_native_file_pairs']}/{empty['planned_pairs']} complete pairs. Its empty counts are not stability evidence.
- The saved-data single-date alternative has {ident['pairs']} availability-selected pairs and {ident['changed_pairs']} pairs with any flag change across methods/supports. It retains the other date, fitting, references and calibration as mosaics. Identity counts and the very small gain sample prevent a general robustness conclusion. A saved-history feasibility check found {hist['cohort_plots_with_match']}/{hist['cohort_plots']} co-located cohort plots under its fixed matching rule; complete cohort histories remain unverified.

There are {science} scientific claim entries plus process entries; current claim statuses are {json.dumps(claims_status,sort_keys=True)}. These statuses concern the stated observed scopes. No ecological field outcome, independent future-year variance, current-best-encoder comparison, full native refit or human decision outcome was measured.

## Verification

{verification}

The entry point is scripts/reproduce.py; VERIFY.md gives setup, the single numerical command, per-claim expected checks, measured stage durations, network/API separation and timeline inspection. The quick scripts/audit_saved.py counter checks saved evidence without fitting and is a different check from raw-data recomputation. All selected raw measurements, invalid values, original failures, plans and API-response records are bundled. The source copy and generated outputs under verification-work are excluded from Git and the SHA-256 list, count toward storage, and are not independent reproduction. A separate sealed-submission integrity check uses scripts/hash_outputs.py --check.

## Failures and procedural departures

The process peak was {r['maximum_registered_concurrency']} registered experiments, above the permitted {m['resource_limits']['concurrent_experiment_processes']}; the recorded overlap and later launch guard are in manifest.json/protocol/deviations.md. Earlier library HTTP concurrency was not measured. The old additional-control path error lost returned arrays; error rows and the later fixed-sample repair remain. Gateway reporting failures and offline recovery remain. Native paired acquisition was never launched before the fixed acquisition cutoff passed during a confirmed usage stop. No later acquisition replaced missing slots. These are not represented as full resource compliance or recovered old data.

At the record snapshot, {r['registered_experiment_count']} experiment processes have run records, with statuses {json.dumps(r['run_status_counts'],sort_keys=True)}. A completed software process can represent an unfinished scientific test, as in the paired-native availability analysis. The maximum recorded elapsed experiment duration is {r['maximum_completed_duration_seconds']:.6f} seconds, including timeout/termination overhead. Every run records its configured limit and exit code. Main scientific results do not use the lost failed arrays.

## Conditions, timing and storage

Start: {m['start_time_utc']} (UTC). Current first-draft deadline: {m['first_draft_deadline_utc']} (UTC). Confirmed usage-limit exclusions total {stop_seconds} seconds. Active research-period elapsed time through {research_end} is {active_seconds:.0f} seconds; other waits remain included. The unspecified resumption adds no exclusion. The embedding/native acquisition cutoff stayed fixed at 17:00 UTC; ordinary scholarly prior-work consultation continued for the required self-check.

Allocated directory size at this snapshot: {r['allocated_storage_bytes']} bytes; logical file size: {r['logical_storage_bytes']} bytes; storage cap: {m['resource_limits']['storage_bytes']} bytes. Excluded environments/caches/working copies still count. Git contained {r['git_commit_count']} commits through snapshot {head}; final documentation/sealing commits follow. This is a dated tally, not a claim to include its own future sealing commit.

Root deployment ID, root reasoning settings, session token use, runtime version, normal-tool billing and persistent-memory existence are not directly observable. The conversation presents the authoring session as Codex based on GPT-6/OpenAI; this is distinguished from a confirmed deployment ID. No profile or past sessions were searched for the topic. Session/continuation IDs remain unexposed; preserve this conversation and this directory.

## AI API usage

| Returned model | Purpose | Generation calls |
| --- | --- | --- |
{api_table}

Returned input tokens: {input_tokens}; cached-input tokens: {cached}; cache-write tokens: {writes}; returned output tokens: {output_tokens}, including {reasoning} reasoning tokens. Search-call items: {searches}. Generation failures in the latest deduplicated ledger: {sum(x['status']!='completed' for x in api)}. Polling/accounting rows are not additional generations. No other model was called by the author to write code, summarize literature, draft the paper or review it. The human separately supplied the planned review by an AI agent. No author-invoked subagents were used.

Computed actual cost from returned usage and saved official rates: **USD{total_cost:.5f}**, out of the combined research/review budget USD{m['api']['budget_usd']:.2f}. This is not invoice-verified. The response's legacy cache-retention field lacks a write-lifetime token breakdown; the documented default30-minute write accounting is used, with the caveat retained in manifest.json and api_calls.jsonl. Reasoning output is included once in output-token cost. Price source: {m['api']['price_confirmation']['source']}, checked {m['api']['price_confirmation']['checked_at_utc']}, snapshot sources/openai-pricing.md. The sole critic used the copied skill's explicit no-output-limit/pre-call-maximum exception. No further paid AI calls were made. The saved response is sufficient to recompute accounting without an API call.

## Human interventions

After the initial instructions, the recorded intervention count is {r['intervention_count']}, by type {json.dumps(r['intervention_counts'],sort_keys=True)}. Permission requests: {r['intervention_counts'].get('permission_request',0)}; scientific feedback: {r['intervention_counts'].get('scientific_feedback',0)}; paper-review results received: {r['intervention_counts'].get('peer_review',0)}.

| ID | Type | Recorded UTC time | Decision |
| --- | --- | --- | --- |
{intervention_table}

The one other-model topic critique is an authorized planned instrument of topic selection, not human feedback or the later paper review. No external publication, posting or contact was made.

## End state and main outputs

The reason for ending is completion of the primary/Forest analyses and the relevant alternative-explanation and boundary checks, followed by the required self-check and full verification. Data acquisition is closed; the unsuccessful paired-native check remains referable. Saved measurements were checked for alternative recovery routes and used for the limited single-date analysis, without treating it as completed paired validation. The paired-native test is retained unfinished. The first-draft snapshot and submission-1 tag are preserved. The planned review and response are recorded separately; the final tag identifies the revised package after sealing.

- paper.md, claims.jsonl and figures/: scientific report, evidence mapping and generated visuals.
- VERIFY.md, scripts/reproduce.py, requirements-analysis.txt: offline numerical procedure.
- review/self-check.md and review/self-rerun-*.json: author assessment and actual self-rerun records.
- protocol/, experiments/, data/, sources.jsonl, manifest.json, events.jsonl and interventions.jsonl: fixed plans, provenance, raw/results/failure records and interventions.
- SHA256SUMS.txt with HASH_SCOPE.md: final integrity inventory, generated at sealing. review/submission-1/ contains the required first-draft snapshots after sealing.
'''
    (ROOT/'final_report.md').write_text(report)
    readme=f'''# Free Research014 — tree-cover transition screening

{phase}

Read [paper.md](paper.md), [claims.jsonl](claims.jsonl), [final_report.md](final_report.md) and [VERIFY.md](VERIFY.md). This study compares change scores and classifiers for retrospective one-year tree-cover transitions in CONUS. LCMAP dominant Trees and Annual NLCD Forest are different endpoints. Initial classes are supplied; ecological restoration success and user effects are unmeasured.

The full offline entry point is `python -B /path/to/source-copy/scripts/reproduce.py --output /path/outside/source`. Install requirements-analysis.txt in a dedicated environment outside the source. No live data download or AI call is needed after setup. VERIFY.md gives exact steps, expected checks, stage durations, source-integrity checking and the local Git timeline. The latest self-rerun record is {str(path.relative_to(ROOT)) if path else 'pending'}; current numerical coverage verified={ready}.

## Outputs

- analysis/main-v1: paired primary results, model-specific availability, fixed reference/support sensitivities, thresholds, predictions and contrasts.
- analysis/secondary-v2: preplanned additional controls/calendar anchors.
- analysis/robustness-*-v12, endpoint-v13, reference-completeness-v14, initial-vector-v17, geography-v18, initial-class-v19, reference-access-v20: explicitly exploratory checks.
- analysis/nlcd-*: separate Forest/horizon/label-agreement results; matched direct-input additions are exploratory on already-inspected data.
- analysis/partition-sensitivity-v24: ten fixed earlier fitting/calibration assignments; all results and missing conditions retained.
- analysis/direct-inputs-v23 and nlcd-direct-inputs-v23: matched learner/target, four fixed inputs, all results and reconstruction/calibration checks.
- analysis/native-v5: {native['native_present']}/{native['planned_point_years']} point-year input comparisons. analysis/native-pairs-v21: unfinished paired check, {empty['complete_native_file_pairs']} complete pairs. analysis/native-single-date-v22: availability-selected single-date substitutions with identity counts, not a native refit.
- figures/, tables/: generated paper visuals/tables. data/: public labels/raw selected measurements. experiments/: actual commands, commits, times, logs, raw/results and retained failures.
- input_prompt.md and input_skills/: finalized original instruction transcription and unchanged copied topic-selection skill. protocol/: original/amended plans and deviations. sources/ and sources.jsonl: bibliographic/access/licence records and checked passages.
- review/: author self-check, candidate self-reruns and first-draft snapshot; human-provided AI-agent review and point-by-point response are preserved.

## Attribution and limits

Analysed LCMAP/NLCD reference labels are public domain; the archive contains unused components with separate terms. TESSERA v1 data are CC0. AlphaEarth V1 data are CC BY4.0: **The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind.** The primary AlphaEarth source is an unofficial geographic mosaic. Native-grid input processing differs; full paired/native performance is unverified.

The records retain a brief experiment-concurrency breach, unknown earlier library request concurrency, lost arrays from a failed acquisition, reporting errors and incomplete native acquisition. No external publication/contact or subagents occurred. The sole API generation was a topic critique, not paper review. Hashes/Git/local logs do not prove independence or untampered chronology. The submission-1 snapshot remains unchanged; final identifies the revised package after review.
'''
    (ROOT/'README.md').write_text(readme)
    update_verify(c,path,v,covered)
    print(json.dumps(dict(final_report_words=len(report.split()),readme_words=len(readme.split()),current_numerical_coverage=ready,record_snapshot_utc=r['observed_at_utc'],claims=len(c))))

if __name__=='__main__':write_docs()
