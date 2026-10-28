"""Generate the required trial report from scientific outputs and record tallies."""
import json
from pathlib import Path
import pandas as pd
import build_report
from records import ROOT,now

def main():
    build_report.main()
    tally=json.loads((ROOT/'analysis/resource-tally.json').read_text())
    m=json.loads((ROOT/'manifest.json').read_text());s=json.loads((ROOT/'analysis/summary.json').read_text())
    r=json.loads((ROOT/'analysis/robustness/summary.json').read_text())['families']
    scores=pd.read_csv(ROOT/'analysis/scores.csv')
    selected=scores[(scores.scope=='within')&(scores.decoder=='rf')&(scores.budget==2000)&
        (scores.version=='raw')&(scores.condition=='standardized_0.05')&(scores.boundary_tolerance_m==0)]
    mean=lambda rep,policy:float(selected[(selected.representation==rep)&(selected.policy==policy)].small_macro_recovery_50.mean())
    def contrast(row):
        lo,hi=row['conditional_block_bootstrap_95_percent_interval']
        return f"{row['estimate']*100:.1f} pp [{lo*100:.1f}, {hi*100:.1f}]"
    primary=s['primary_contrasts'];cost=tally['api_cost_recomputed']
    inv=pd.read_csv(ROOT/'analysis/inventory-summary.csv')
    ncores=int(inv.cores.sum());ntest=int(inv[inv.split=='test'].eligible_small_patches.sum());nall=int(inv.eligible_small_patches.sum())
    fits=pd.read_csv(ROOT/'analysis/fits.csv')
    rotation_fits=int(fits.scope.str.startswith('rotation').sum())
    quota_fits=int(fits.policy.isin(['area_corematched','area_regionmatched']).sum())
    v7_fits=int(((fits.decoder=='rf_noboot')|fits.policy.isin(['proposal_aef','uncertainty_aef','proposal_aef_classmatched','uncertainty_aef_classmatched','proposal_uniform_aef','uncertainty_uniform_aef'])).sum())
    priority_fits=len(fits)-rotation_fits-quota_fits-v7_fits
    align=json.loads((ROOT/'data/alignment-stress/summary.json').read_text())

    verification_path=ROOT/'review/offline-verification.json'
    verification=json.loads(verification_path.read_text()) if verification_path.exists() else None
    if verification:
        v=verification['verification'];verification_text=(f"The clean selected-copy offline run reports **{v['status']}**, in {v['elapsed_seconds']:.3f} seconds, "
            f"using committed revision `{verification['prepared_revision']}`. It checks {v['committed_input_files_checked_unchanged']} copied committed files unchanged, "
            "recomputes all final-fit measurements/intervals and checks the frozen numeric table hashes. The probability bytes and dedicated environment are shared with the original bundle; this is a self-rerun, not independent reproduction.")
    else:verification_text='The clean-copy offline procedure is running; success is not yet claimed. See experiments/E66 and verification-work/run-1.'
    intervention_rows=[json.loads(x) for x in (ROOT/'interventions.jsonl').read_text().splitlines() if x]
    interventions='\n'.join(f"- {x['intervention_id']}: {x['type']} at {x['observed_at_utc']}; {x.get('decision')}." for x in intervention_rows)
    api_models='; '.join(f"{x['calls']} call to {x['model']} for {x['purpose']}" for x in tally['api_calls_by_model_purpose'])
    prices=[json.loads(x) for x in (ROOT/'sources.jsonl').read_text().splitlines() if x]
    price_url=next((x['url'] for x in prices if x.get('path')=='data/literature/openai-pricing.md'),'See saved pricing source')
    text=f'''# First-draft research report: free-research-017

Report generated at {now()}. This is the research-period report; the planned review by an AI agent has not yet been received. No external publication, upload or contact occurred.

## Scope and question

**Training Point Allocation and Recovery of Small Wetland Patches from Satellite Embeddings.** How does allocation interact with annual embeddings versus seasonal optical predictors at a common reference-upland false-positive area rate, and can image-derived allocation recover an oracle object-frame benefit?

The study selected one topic through the supplied research-question skill, bounded prior-work searches, pilots, recorded scoring and one permitted model critique. Main data contain {ncores} separated cores in four convenience NWI projects. Original test data have {ntest} eligible mapped palustrine patches of 0.2–1 ha; all fixed split rotations together have {nall}. These counts describe the retained inventory, not true ecological completeness or a national probability sample.

The completed analysis includes **{s['fit_count']} final local classifier fits**, with all five fixed seeds in every reported fitted cell. It contains the {priority_fits}-fit priority grid plus {v7_fits} exploratory weighting/proposal/query fits, {rotation_fits} added split fits and {quota_fits} geographical-quota fits. `analysis/completed-cells.csv` records the exact conditions. The original protocol's entire possible cross-product was not run: decoder, alternative-budget, hybrid and transfer sensitivities were prioritized to the main area–oracle contrast. Missing cells are not presented as completed experiments.

## Findings

- The original planned interaction is **{contrast(primary['H1_interaction'])}**. Embedding recovery changes from {mean('aef','area')*100:.1f}% to {mean('aef','object')*100:.1f}%; optical recovery from {mean('optical','area')*100:.1f}% to {mean('optical','object')*100:.1f}%. The original optical-derived proposal rule does not reproduce the embedding oracle gain. This is a result about fitting allocation from an existing reference resource.
- The planned budget and linear-decoder checks retain the interaction's direction. Entire-held-region cases have small, uncertain interactions; their equal-region pooled exploratory summary is {contrast(r['geographic_all']['conditional_contrasts']['standardized_0.05']['H1_interaction'])}. Threshold replay exposes calibration transport rather than establishing a deployed 5% FPR guarantee.
- Exploratory pooled split rotations attenuate the interaction to **{contrast(r['rotations_all']['conditional_contrasts']['standardized_0.05']['H1_interaction'])}**. New split intervals, undefined bootstrap replicates and constant/empty cases remain visible. Overlapping training sets do not provide independent replication.
- Exploratory same-position inverse-size loss weights, stronger embedding-guided uncertainty and oracle-core-quota controls recover part of the benefit. They do not establish that additional patch coverage alone causes it, or that an oracle frame is necessary. The weighted decoder disables bootstrap in matched controls; effects are not a causal decomposition of the primary forest.
- The deterministic reference-shift stress test retains {align["common_cohort_patches"]} of {align["original_patches"]} original small patches in a shared cohort and gives positive conditional interactions for all cardinal shifts. Its {align["original_patches"]-align["common_cohort_patches"]} excluded patches are outside that robustness claim. It is not an estimated inventory-error distribution.

All original and exploratory results, including weaker transfer and split results, remain in the paper and machine-readable outputs. Interval estimates condition on the fixed fitted models and reference maps; secondary/exploratory intervals do not correct for multiple comparisons.

## Limitations and unverified matters

The reference is NWI agreement, with omissions, boundary uncertainty, differing project procedures and nominal source-year matching. Public project reports document older/ancillary inputs as well as 2020 imagery. AEF production v2.1 inputs and global pretraining differ from the fixed seasonal optical summary; architecture or spatial context is not isolated. No independence from related pretraining products is guaranteed. No human annotation labour, ecological completeness, later-year updating, legal wetland determination or conservation outcome was measured.

The dense labelled pool already contains information from which geometry can be reconstructed; sampler restrictions are algorithmic restrictions, not proof that object information is independently unavailable or costly. Uniform-initialization query simulations still receive an inventory-derived land domain. We did not compare every modern segmentation model or input stack. The field-reference alternatives checked (WetSAM point annotations, NWCA site/assessment-area schemas and the new area-weighted-loss paper's request-only data statement) did not supply a verified dense independent patch reference in the searched range. This is not proof none exists. No request/contact was made.

The final literature repeat found direct prior size-aware loss weighting (full relevant method checked) and a recent small-pond embedding search hit (secondary abstract only). No new weighting principle, first small-feature embedding study or absence of close prior work is claimed. All literature used as supporting evidence was checked at the relevant full-text passage; abstract-only hits are marked and not used for findings.

## Failures and recording limitations

There are {tally['failed_runs']} failed experiment-process runs among {tally['completed_runs']} completed runs at this report time: {', '.join(tally['failure_ids'])}. E02/E03 encountered source orientation/construction problems; E07 retained a partial input batch after HTTP503; E38 retained measured outputs before an analysis-table handoff failure; E62 had a syntax error before analysis. Corrected runs and original logs are kept. No failed study was replaced by a different successful topic.

An empty initialization helper file was accidentally created in the parent directory and immediately removed (E0004); the recorded correction states no user file was read or changed.

E03 and E62 also have explicit code-provenance timing corrections: execution began while a code commit was pending. A later matching snapshot is not claimed to precede the run. E62 did no scientific computation and its compiled retry passed. E64 also has a presentation-helper addendum: a lazy import loaded prose/table-generation code edited during the running job, so its entrypoint commit alone does not describe that helper. No import-time hash is claimed. E65 verified all numeric rows/intervals, E66 recomputed all numeric tables from immutable committed code, and E67 checked the final manuscript on those fresh outputs. All main classifier batches link to their fixed dataset, plan/code commits and input hashes. Git dates are self-reported; records/hashes do not prove absence of tampering. Session identifier, exact runtime session model/build/settings and session-wide token charges are not exposed.

## Verification and outputs

{verification_text}

Main files: `paper.md`, `claims.jsonl`, `VERIFY.md`, `analysis/`, `figures/`, `review/self-check.md`, `review/offline-verification.json`, `README.md`, the output SHA-256 list and `HASH_SCOPE.md`. Raw prediction arrays outside Git remain bundled with per-fit hashes. Verification working copies and environments count toward storage; working-copy inputs/caches are excluded from output hashes, while regenerated verification measurements/logs are included. See `VERIFY.md` for a single offline entry point, optional rebuilding/refitting and timeline checks.

## Interventions, usage and end state

{interventions}

Tally by type: `{json.dumps(tally['intervention_tally'],sort_keys=True)}`. No permission request, unplanned scientific advice or peer review was received during this research period. The candidate critique is a separate pre-authorized model use. The review round remains pending.

AI API: **{tally['distinct_ai_api_calls']} distinct call** ({api_models}). Observed usage is {cost['input_tokens']} input tokens, including {cost['cache_write_tokens']} cache-write tokens and {cost['cached_input_tokens']} cache-read tokens; {cost['output_tokens']} output tokens include {cost['reasoning_tokens']} reasoning tokens. The saved response has {cost['web_search_call_items']} search-call items, while provider tool usage reports {cost['provider_tool_usage_web_requests']} web requests. No retries or failed AI API calls occurred. A cost-correction row is not a second call.

Exact invoice-priced cost is **unknown** because the returned cache-write lifetime breakdown is missing and a legacy 24h retention label does not match current documented tiers. The recomputed charge range, using the prescribed search-item count and confirmed current write tiers, is ${cost['cost_usd_lower_bound']:.7f}–${cost['cost_usd_upper_bound']:.7f}; original under-accounting was corrected append-only. Budget is ${m['ai_api']['budget_usd']}. Pricing source: [official price list]({price_url}), checked {m['ai_api']['price_checked_at_utc']}, preserved in `data/literature/openai-pricing.md` and `data/literature/prompt-caching.md`. No further API calls are planned. Session/search-tool allowance use and charges remain unknown; no new paid billing route was added.

Research began {m['start_time_utc']}; original first-draft deadline 2026-10-27T16:34:15Z; extended deadline {m['first_draft_deadline_utc']}. Two human-confirmed usage-limit stops are documented in manifest/events/interventions, including processes that completed during the first stop. Latest measured directory size is {tally['storage_bytes']} bytes (including dependencies/history and working copies); limit is {m['limits']['storage_bytes']} bytes. Active experiment runs at the tally time: `{json.dumps(tally['active_runs'])}`.

The original grid was deepened after completion with mechanism controls, more realistic initialization, all-core rotations, geographical mixture checks and reference stress tests. The experimental phase ends with those checks complete and storage approaching its ceiling; remaining space is reserved for verification and retained artifacts. The first draft will be frozen under tag `submission-1`, then no research work will occur until human-supplied `REVIEW-1`. SessionID to preserve: unknown; preserve this directory and local Git history. This report will be updated after review response.
'''
    response_path=ROOT/'review/response-tally.json'
    if response_path.exists():
        response=json.loads(response_path.read_text())
        reviewed=json.loads((ROOT/'analysis/review-response/summary.json').read_text())
        pooled=next(x for x in reviewed['sensitivities'] if x['family']=='four_splits' and x['condition']=='standardized_0.05' and x['coverage']=='50')
        transfer=reviewed['transfer_replay'][-1]
        text=text.replace('# First-draft research report:','# Final research report:')
        text=text.replace('This is the research-period report; the planned review by an AI agent has not yet been received.',
            'This updates the research-period report after the single planned review by an AI agent, review-017-1.')
        marker='## Findings\n\n'
        text=text.replace(marker,marker+
            f"The more comprehensive exploratory fixed-split summary gives gains for both predictors: embeddings **{contrast(pooled['contrasts']['aef_oracle_gain'])}**, optical **{contrast(pooled['contrasts']['optical_oracle_gain'])}**, interaction **{contrast(pooled['contrasts']['H1_interaction'])}**. Optical gains in all new rotations. The original planned interaction below is the largest of the four splits and does not include split-selection uncertainty.\n\n")
        text=text.replace('Entire-held-region cases have small, uncertain interactions;',
            'Entire-held-region cases at held-project-standardized thresholds have small, uncertain interactions;')
        marker='## Limitations and unverified matters'
        text=text.replace(marker,
            f"Review-prompted complete reporting of planned sensitivities materially qualifies the interpretation. Optical has higher any-overlap recovery across the four splits, while embeddings have higher ≥50% recovery. The planned other-project-threshold transfer gives a pooled embedding gain of **{contrast(transfer['contrasts']['aef_oracle_gain'])}** and interaction **{contrast(transfer['contrasts']['H1_interaction'])}**, with regional mean achieved FPR spanning "+'–'.join(f'{x*100:.1f}%' for x in reviewed['transfer_regional_mean_fpr_range'])+". These replay differences are not constant-FPR effects. All16fixed sensitivity rows, four split replays, transfer project rows, size bins and secondary pixel metrics are retained.\n\n"+marker)
        text=text.replace('Corcoran2015 and Liu2026 small-pond embedding hits remain abstract/bibliographic-only in the checked range and supply no claimed findings.',
            'Corcoran2015 was checked at relevant full-text passages after review, alongside Millard/Richardson2015 and Colditz2015; Liu2026 remains an abstract/bibliographic-only small-pond embedding hit and supplies no claimed finding.')
        text=text.replace('No permission request, unplanned scientific advice or peer review was received during this research period. The candidate critique is a separate pre-authorized model use. The review round remains pending.',
            'No permission request or unplanned scientific advice was received. One planned review by an AI agent was supplied by the human after the research period; the original text is retained, and the reviewer identity/execution details are human-reported rather than directly observable. The candidate critique is a separate pre-authorized model use.')
        a=text.index('The original grid was deepened after completion')
        text=text[:a]+f'''The original grid was deepened with mechanism controls, uniform initialization, all-core rotations, geographical mixture and reference stress checks. After review, v11 added saved-score analyses, with **{response['new_model_fits']} new model fits** and **{response['new_ai_calls']} new AI calls**. First-draft submission time was 2026-10-27T12:00:03.445631Z under `submission-1` (`8ff25a6335b4ec3aee0b998032633a6948f840b9`); no directory changes occurred while awaiting review. Review-response first tool time {m['review_response']['received_first_tool_time_utc']}; deadline {m['review_response']['deadline_utc']}. No review-period usage-limit stop has been reported or excluded.

## Review response and final state

Review findings: **{response['points']}**; decisions: `{json.dumps(response['decisions'],sort_keys=True)}`. Existing scientific claim records revised: `{json.dumps(response['existing_claims_revised'])}` ({len(response['existing_claims_revised'])}); status changes: {len(response['claim_statuses_changed'])}; withdrawn: {len(response['claims_withdrawn'])}; added: `{json.dumps(response['claims_added'])}` ({len(response['claims_added'])}). Every claim now states that source_ids are data-provenance references. New analysis batch: `{json.dumps(response['analysis_batches_added'])}`; full revised verification batch: `{json.dumps(response['verification_batches_added'])}`. Counts are generated by `code/write_review_response.py`, not inferred from prose. Original review, pointwise response and tallies are in `review/review-1.md`, `review/response-1.md`, `review/response-points.json` and `review/response-tally.json`.

The reviewer reports a same-machine rerun from saved probability arrays, not refitting or independent reproduction. This session's final full numerical self-rerun and manuscript/claim check are separately recorded. Original raw outputs, failed runs and first-draft snapshot remain; all reported empirical numbers are generated from retained outputs. Numerical scope is unchanged at465fits; the revised paper has25numeric tables and11claims. Main limitations remain the fixed inventory, four convenience projects, representation/pretraining differences, conditional uncertainty, and unmeasured ecological completeness/labour/outcomes.

End reason: all six review findings addressed within the review-response period; no further scientific work is required for this study's stated scope. Finalize with a credential-value scan, regenerated output hashes, local commit and tag `final`; post-commit receipts record the actual commit/time without claiming to be bytes inside their own earlier snapshot. No external publication or contact. Session ID and continuation IDs to preserve are **unknown**; preserve this conversation, the research directory, large non-Git raw arrays and complete local Git history.
'''
    (ROOT/'final_report.md').write_text(text)

if __name__=='__main__':main()
