"""Prepare and finalize review-response documents from actual records."""
import argparse,json,subprocess
from collections import Counter
from records import ROOT,now,event

def run(verified=False):
    observed=now();head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    old={r['claim_id']:r for r in map(json.loads,(ROOT/'review/submission-1/claims.jsonl').read_text().splitlines())}
    current={r['claim_id']:r for r in map(json.loads,(ROOT/'claims.jsonl').read_text().splitlines())}
    changed=[cid for cid in old if any(old[cid].get(k)!=current[cid].get(k) for k in ['text','scope','status','expected','reader_implication'])]
    statuses=[cid for cid in old if old[cid]['status']!=current[cid]['status']]
    decisions={f'R1-{n}':('partly adopted' if n in [4,5,6,7] else 'adopted') for n in range(1,10)}
    summary=dict(observed_at_utc=observed,review_id='review-016-1',points=len(decisions),decisions=decisions,
        decision_counts=dict(Counter(decisions.values())),claims_changed=changed,claim_status_changes=statuses,
        claims_withdrawn=[cid for cid in old if current[cid]['status']=='unsupported' and old[cid]['status']!='unsupported'],
        claims_added=[cid for cid in current if cid not in old],analyses_added=['E56-review-label-error','E57-review-summaries'],
        new_statistical_analyses=2,revision_code_commit=head,review_directly_observed=False,
        review_observability='Human supplied AI-agent review; reviewer model/runtime and reviewer calculations are not directly observed by this research session.')
    if verified:
        v=json.loads((ROOT/'review/verification-final.json').read_text());assert v['status']=='passed' and v['valid_as_final_submission_check']
        snap=json.loads((ROOT/'review/snapshot-final.json').read_text());summary.update(verification_status='passed',verified_source_commit=snap['source_commit'],verification_elapsed_seconds=v['elapsed_seconds'])
    else:summary['verification_status']='pending final full self-rerun'
    (ROOT/'review/response-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    entries=[
      ('R1-1','“Add a sensitivity analysis of independent (and ... partly correlated) annual labelling error.”',
       'Added all planned error probabilities and three annual coupling settings using saved draws. Zero-error estimates, standard errors and directions match the originals bitwise. Independent errors largely remove the aggregate coverage deficit while increasing absolute point error; shared errors can preserve it. These are synthetic scenarios, not measured field rates, and retaining the original FPC is explicitly not a newly justified measurement-error interval.',
       'paper.md Abstract, §3.4, §4.8 Table8, §5–6; claims C01,C02,C06,C12; scripts/review_label_error.py; results/review-label-error/','E56-review-label-error'),
      ('R1-2','“Revise the title ... Put the model-assisted point-accuracy result in the abstract.”',
       'Revised the title to Swiss declared crop groups and a resampling benchmark. The abstract and §4.2 state that the direct gain uses no satellite input, frozen logistic assistance gives no revisited point-accuracy gain at128, and forests improve it modestly. Standard post-stratification is identified as an untested comparator. The reviewer’s post-stratified computations are not presented as this study’s experiments.',
       'paper.md title, Abstract, §4.2, §5; scripts/review_revision.py; original frozen logistic/forest tables','No additional fitting or estimator experiment'),
      ('R1-3','“Report the prespecified grassland/arable ratios ... Add a landscape-level resampling interval.”',
       'Table2 now includes all budgets for the preplanned grassland/arable subsets. Added whole-landscape resampling of the original cohort and the higher-replication additional arable cohort. §4.8 reports ratio and coverage ranges, explicitly as within-cohort composition sensitivity, not national uncertainty. Both broad and fine additional-arable ratio ranges include1; C10 is now an observed ratio with unresolved landscape variation.',
       'paper.md Abstract, §4.2 Table2, §4.8; claims C10,C13; results/review-summaries/landscape-resampling.csv; scripts/review_summaries.py','E57-review-summaries'),
      ('R1-4','“Add the conditional wrong-direction share ... state that no tested budget ... reached the no-change RMSE.”',
       'Added actual wrong/report counts, tiny/non-tiny strata, coverage minimum/percentiles/countbelow90%, and per-unit baseline comparisons early in §4.1. Added the longer2022→2025 direct contrast against its own no-change baseline. The no-change statement is restricted to direct sampling: the reviewer’s broader wording would be false because both revisited frozen forests beat no change at512labels/year. The exceptions are explicitly reported from the original outputs; no original numeric claim was contradicted.',
       'paper.md Abstract, §4.1, AppendixE TableE1; results/review-summaries/decision-context.csv, all-budget-point-baselines.csv, long-contrast.csv','E57-review-summaries'),
      ('R1-5','“The preplanned interval rule ... omitted the derivative ... with the derivative ... behave like the direct ones.”',
       'Adopted the omitted-derivative diagnosis and plainly qualified C04 as a property of the original interval calculation. The original preplanned result and corrected exploratory calculation remain. Did not equate the corrected intervals with revisited direct coverage: corrected assisted coverage is close to independent direct coverage, whereas revisited direct coverage is substantially lower. Approximate local derivatives still do not prove coverage at changing support.',
       'paper.md Abstract, §3.3, §4.6, §5; claims C04,C11; original projection-derivative outputs','No new experiment; interpretation of retained original/exploratory outputs'),
      ('R1-6','“Add these works ... classic successive-occasion theory ... current practice.”',
       'Added checked full-passage context for Jessen, Brown–Cai–DasGupta’s author preprint, operational LUCAS/NASS/ALL-EMA, Lu et al.version7 and van der Velde et al. The latter’s relevant full article sections were available in the indexed publisher body; direct DOI access was blocked and was not bypassed. The expected direction is explicitly attributed to classic sampling. Patterson, Basharin, Hutcheson and Cochran are retained as bibliographic leads only because relevant full text was not obtained; original instruction§8 prohibits using such leads as supporting evidence. Publisher/metadata searches and access limitations are saved, rather than implying those works were read.',
       'paper.md §1–2 and References; sources.jsonl; sources/review-prior-access-*.json and checked PDFs','Literature check only; no scientific experiment'),
      ('R1-7','“Restructure the abstract ... move the case counts ... give ... percentage change in effective number.”',
       'Reworked the abstract around the preplanned design, accuracy and reporting outcomes with subsequent exploratory qualifications. Added actual RMS percentage error of the estimated effective-number ratio from every saved trial, rather than exponentiating entropy RMSE and calling it percentage RMSE. This new descriptive transformation is explicitly exploratory. Kept a compact tiny/zero/unchanged case count in the abstract because the original trial instruction§10 requires trivial-case counts there; other case details remain in results. Readers’ monitoring decision is stated near the beginning.',
       'paper.md Abstract, §1, §3.4, §4.1; results/review-summaries/effective-group-errors.csv; scripts/review_revision.py','E57-review-summaries'),
      ('R1-8','“Add one paragraph naming the intended operational settings ... corresponding unit of a reference label.”',
       'Added map-based monitoring without complete declarations and independent photo/field checks as possible applications. Defined a label as one point-year classification in that setting, and distinguished the actual10m database reading and supplied finite frame from parcels, visits, clustering, real interpretation errors and frame/travel costs. Complete trustworthy declarations need no sample to calculate this target.',
       'paper.md §1, §3.1, §5–6; manuscript/template.md','No new experiment'),
      ('R1-9','“Correct the tag name in VERIFY.md.”',
       'VERIFY.md now gives explicit submission-1 and final checkout instructions. Original first-draft hash/event receipts remain preserved; the reviewed-final inventory is regenerated separately. Terminal commit/submission events use the documented prefix rule, not an implied self-referential whole-file hash.',
       'VERIFY.md; README.md; SHA256SUMS.json; final tag and terminal receipt in events.jsonl','Final full offline self-rerun')]
    text=f'# Response to review-016-1\n\nPrepared from the human-supplied REVIEW-1, observed {observed}. This was a review by an AI agent, not human peer review or independent reproduction. The original review is unchanged in review/review-1.md; the first draft is tag submission-1 (faf7dce40c1a27313b4ae7fb51554fa5d061393b).\n\n'
    text+=f'Revision code/document anchor commit: {head}. Added-analysis plan/code commits and execution times are in experiments/E56-review-label-error/run.json and experiments/E57-review-summaries/run.json; their completed results were preserved in0f1fb39c263ef2915254cc9ebcb707d1be047d98. Planv15 was committed before either analysis. Final verification state: {summary["verification_status"]}.\n\n'
    for cid,quote,reason,files,exp in entries:
        text+=f'## {cid}: {decisions[cid]}\n\nPoint: {quote}\n\nDecision and reason: {reason}\n\nChanges: {files}. Revision anchor: {head}.\n\nAdded experiments: {exp}.\n\n'
    text+='## Tally\n\n```json\n'+json.dumps(summary,indent=2)+'\n```\n'
    (ROOT/'review/response-1.md').write_text(text)
    p=ROOT/'VERIFY.md';s=p.read_text();a=s.index('Run on a copy');b=s.index('\n\n## Environment',a)
    state='The first-draft full self-rerun passed; its preserved report is review/verification-submission-1.json. The reviewed-final full rerun is pending.'
    if verified:
        counts=dict(main_csv=len(v['table_checks']),supplemental_csv=sum(len(t['csv_checks']) for t in v['supplemental_checks']),main_raw=len(v['raw_array_checks']),supplemental_raw=sum(len(t.get('raw_array_checks',[])) for t in v['supplemental_checks']))
        state=f"The reviewed-final full self-rerun passed in {v['elapsed_seconds']:.3f}s: {counts['main_csv']} main and {counts['supplemental_csv']} supplemental CSV files, {counts['main_raw']} main and {counts['supplemental_raw']} supplemental raw-array files, and exact paper.md/claims.jsonl matches. Source commit {snap['source_commit']}; original result review/verification-final.json; snapshot review/snapshot-final.json. This is a rerun by this session, not independent reproduction. The first-draft verification remains unchanged in review/verification-submission-1.json."
    s=s[:a]+'Run on a copy of the submitted commit, with a fresh output directory outside the copy. Numerical verification writes no source files, uses no network and calls no AI API. '+state+s[b:]
    s=s.replace('Use tag `final` for the reviewed version.', 'For the original first draft, use `git checkout submission-1`. For this reviewed final version, replace that checkout command with `git checkout final`. The tags identify different preserved submissions.')
    s=s.replace('projection derivatives and cohort context.', 'projection derivatives, synthetic annual label-error scenarios, whole-landscape resampling, decision summaries and cohort context.')
    s=s.replace('A fresh minimal package installation was not separately tested.', 'This session did not separately test a fresh minimal installation. The supplied AI-agent review reports that a fresh requirements-verify.txt environment passed the complete first-draft check; that is the reviewer’s report, not an action directly observed by this session.')
    marker='## Claim checks and observed contributing computation times'
    if marker in s:s=s[:s.index(marker)]
    s+='## Claim checks and chronology after review\n\nFor each claim, inspect the listed evidence paths and exact expected values in claims.jsonl; the entry point recomputes all numerical sources and regenerates the entire claim document. C01–C11 retain the original analyses; C01,C02,C06 explicitly condition on perfectly repeatable labels, C04 diagnoses the original interval rule, and C10 reports unresolved composition variation. C12 adds label-error sensitivity and C13 adds within-cohort resampling. The new error sensitivity originally took17.723seconds and the summary analysis4.228seconds (observed run records, not time guarantees). Together with the full rerun, verification stays under the trial’s30-minute per-process limit in the observed environment; slower machines can use the clearly reduced --quick mode.\n\nThe pre-review anchors remain above. Planv15 was fixed after receipt of REVIEW-1 and before E56/E57; inspect their plan_commit_id, code_commit_id, input hashes, start/end times and the response letter. All added analyses are exploratory. protocol/deviations.md lists the review additions and preserves earlier changes. No reviewer-only script/output was used as this study’s experimental evidence.\n'
    p.write_text(s)
    p=ROOT/'README.md';s=p.read_text();a=s.index('Current state:');b=s.index('\n\n## Read',a)
    s=s[:a]+('Current state: reviewed final revision prepared. One AI-agent review was received; all nine points have a recorded disposition in review/response-1.md. Original first draft: tag submission-1. Reviewed version: tag final. '+state)+s[b:]
    if 'results/review-label-error/' not in s:s+='\nPost-review additions: results/review-label-error/ (synthetic sampled-label scenarios), results/review-summaries/ (landscape composition ranges, conditional direction errors, effective-number errors and longer contrast), protocol/plan-v15-review-response.md, review/review-1.md, review/response-1.md and review/response-summary.json. All are included in offline verification.\n'
    p.write_text(s)
    p=ROOT/'review/self-check.md';s=p.read_text();marker='## Review-response self-check'
    if marker in s:s=s[:s.index(marker)]
    s+=f'''## Review-response self-check

Observed {observed}. This is self-assessment; the AI-agent review is a separate planned intervention.

- Close sources: checked historical Jessen and Wald-interval context, current crop-diversity/PPI work and operational panel examples. Inaccessible classics are explicitly bibliographic-only. The renderer enforces full-passage status for every supporting reference; no new novelty assertion.
- Readability and scope: title states Swiss declared groups and resampling; an operational point-year label is distinguished from a parcel or visit. The abstract separates planned results from exploratory transformations/sensitivity and retains the required trivial-case counts.
- Alternative explanations: tested independent and coupled label errors on unchanged draws, and resampled whole landscapes rather than conflating Monte Carlo SE with geographic uncertainty. Original ratios and intervals retained. Field error rates are unknown, not inferred from improved synthetic coverage.
- Stronger baseline check: reviewer’s all-budget no-change assertion corrected for the two frozen forest exceptions; direct-only statement verified at every tested budget. Longer contrast uses its own baseline.
- Reporting: conditional wrong/report counts and per-unit coverage quantiles/counts are now early in results. The effective-number scale uses actual transformed trial errors, not exp(RMSE)-1.
- Interval interpretation: original assisted rule omitted the projection derivative. C04 is qualified; corrected assisted coverage is not equated with revisited-direct coverage. Additional-arable broad and fine resampling ranges both include1; claims stay descriptive.
- Numbers: generated from saved original/new CSVs and raw outcomes. Verification state: {summary['verification_status']}. No original scientific output or first-draft submission file was overwritten.
- Remaining limits: convenience geography, error-free declaration target, fixed retrospective frame, unmeasured field costs and real error processes remain. Classic full-text access gaps and untested post-stratification are disclosed. No independent reproduction, new model/AI call, participant experiment or external contact occurred in this response.
'''
    p.write_text(s)
    event('review_response_documents_updated','Update point-by-point decisions, tag-specific verification and final self-check',['review/response-1.md','review/response-summary.json','review/self-check.md','README.md','VERIFY.md'],verification_state=summary['verification_status'])
    print(json.dumps(summary))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--verified',action='store_true');a=p.parse_args();run(a.verified)
