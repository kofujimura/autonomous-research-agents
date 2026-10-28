"""Generate the pointwise review response and its observable tally."""
import json
from collections import Counter
from records import ROOT,now

def main():
    s=json.loads((ROOT/'analysis/review-response/summary.json').read_text())
    def item(family,condition='standardized_0.05',coverage='50'):
        return next(x for x in s['sensitivities'] if (x['family'],x['condition'],x['coverage'])==(family,condition,coverage))
    def effect(row,key):
        r=row['contrasts'][key];v=f"{r['estimate']*100:.1f} pp"
        ci=r.get('conditional_block_bootstrap_95_percent_interval')
        return v+(' ['+', '.join(f'{x*100:.1f}' for x in ci)+']' if ci else ' (point only)')
    pooled=item('four_splits');original=item('original');replay=item('original','validation_0.05');transfer=s['transfer_replay'][-1]
    points=[
        dict(point_id='R1-1',decision='adopted',reason='The largest original-split interaction was numerically correct but its prominence understated split dependence and optical gains. The bootstrap conditions on fitted training sets, thresholds and maps; it does not resample split selection.',
             changes='paper.md Abstract, §§3.4,4.1,4.5,5; claims C01 implication and C06 text/implication; code/review_manuscript.py and code/write_claims.py.',
             evidence=f"All-split embedding gain {effect(pooled,'aef_oracle_gain')}; optical gain {effect(pooled,'optical_oracle_gain')}; interaction {effect(pooled,'H1_interaction')}. Original interaction {effect(original,'H1_interaction')} retained as planned, not substituted. Text explicitly says optical gained in every new split and two of three new interaction estimates fall below the original lower interval endpoint. Four test-core clusters per region and fixed training cores are explicit.",
             experiments_added=['E68'],commit_ids=['36bc480627ec5dd0455fd08b4eaa4e86a71c94b7']),
        dict(point_id='R1-2',decision='adopted',reason='Preplanned conditions were computed but inadequately reported. Complete reporting changes the reader’s interpretation, particularly coverage and validation replay. Expanded tables/intervals are labelled review-prompted while the underlying preplanned definitions retain that status.',
             changes='paper.md §4.2, Discussion, Appendices E–G; analysis/review-response/summary.json; five new generated tables; claims C11; code/review_sensitivities.py and VERIFY.md.',
             evidence=f"All16 fixed rows are shown (original/four-split × six >=50%-coverage operating conditions plus any/75%). Existing >=50% blocks supply conditional intervals; any/75% are point estimates explicitly. Original pooled validation replay interaction {effect(replay,'H1_interaction')}. Without-Vermont interaction {effect(s['additional']['without_vermont'],'H1_interaction')}. All rotation replays, medium/large patch counts/results, balanced accuracy, per-fit pooled AP averaged across seeds and the size/isolation figure are now reported. Optical any-overlap exceeds embedding any-overlap in pooled arms; >=50% ordering reverses. We do not infer a smoothness cause or ecological completeness. No requested condition was omitted.",
             experiments_added=['E68'],commit_ids=['9509e2e690025eab85e7df7f7d0e2fe31b726c28','36bc480627ec5dd0455fd08b4eaa4e86a71c94b7']),
        dict(point_id='R1-3',decision='adopted',reason='The planned other-project-threshold transfer is more decision relevant than held-project test-standardized thresholds alone. Negative recovery differences accompany FPR differences, so they cannot be interpreted as matched-error causal effects.',
             changes='paper.md Abstract, §4.3 and Discussion; analysis/tables/review-transfer-replay.md; C04 text, scope, implication and expected fields.',
             evidence=f"Planned pooled transfer embedding gain {effect(transfer,'aef_oracle_gain')}, optical gain {effect(transfer,'optical_oracle_gain')}, interaction {effect(transfer,'H1_interaction')}. All four regional rows and achieved FPRs appear next to the standardized-transfer table. Regional five-seed mean FPR range "+'–'.join(f'{x*100:.1f}%' for x in s['transfer_regional_mean_fpr_range'])+' is distinguished from the individual-seed range. The former broad “small and uncertain” characterization is restricted to held-project-standardized interactions.',
             experiments_added=['E68'],commit_ids=['36bc480627ec5dd0455fd08b4eaa4e86a71c94b7']),
        dict(point_id='R1-4',decision='adopted',reason='The first abstract was too dense for practitioners and did not explain the stable decision or its practical limits.',
             changes='paper.md Abstract (about200words), Introduction, §§3.3–3.6 and Discussion; paper-template.md and code/review_manuscript.py.',
             evidence='The revised abstract explains patch-first allocation and the fraction of reference-upland area predicted positive, identifies16primary test cores and2,000positions, reports both predictor gains and the planned test, labels pooling exploratory, and states transfer/calibration limits and a practical recommendation. Geometry, constant-map and mechanism-control counts remain in Results rather than the abstract; no entire primary comparison is a floor, ceiling or identical-map case. Oracle is glossed as privileged access to inventory boundaries/identities. Duplicate3.5 is corrected to3.6 and the deviations section now summarizes actual changes.',
             experiments_added=[],commit_ids=['36bc480627ec5dd0455fd08b4eaa4e86a71c94b7']),
        dict(point_id='R1-5',decision='adopted',reason='Classic training-allocation and point/object studies are close precedents. The sampling principle was expected; the contribution is the quantified held-out representation × allocation comparison.',
             changes='paper.md §2 and References; sources S046/S047 and supplemented S039; data/literature/*-2015-review-notes.md.',
             evidence='Checked relevant full-text methods/results/discussion and CC BY4footers in primary publisher-provided public copies for Millard & Richardson, Colditz and Corcoran after direct publisher429 responses were stopped. Colditz’s heterogeneous-pixel precedent is related to the interior arm without asserting identical mechanisms; between-class area objectives differ from equal-patch recovery. Corcoran’s forested-site benefit and coarser agricultural-site tie are qualified by its changed predictor aggregation/output unit. Relevant passage ranges and public URLs are recorded; original PDF/HTML bytes are not bundled and notes are not presented as source transcriptions.',
             experiments_added=[],commit_ids=['36bc480627ec5dd0455fd08b4eaa4e86a71c94b7']),
        dict(point_id='R1-6',decision='adopted',reason='The v9 launch pointer and identical source IDs were imprecise descriptions of cumulative coverage and evidence roles, despite not changing numbers.',
             changes='protocol/implementation-clarifications.md review-017-1 subsection; every claim source_ids_role; VERIFY.md revision subsection.',
             evidence='Original E61–E67 run.json files remain unchanged. The clarification says those runs cover cumulative v1–v10, including v10 alignment; final v11 verification includes all of them plus review summaries. source_ids explicitly denote data-provenance/access documents only, whereas evidence_paths and experiment_ids support numerical findings.',
             experiments_added=[],commit_ids=['9517bf40fa7c930405c310aea1ed12a408ccf00d','36bc480627ec5dd0455fd08b4eaa4e86a71c94b7'])]
    old={r['claim_id']:r for r in map(json.loads,(ROOT/'review/submission-1/claims.jsonl').read_text().splitlines())}
    new={r['claim_id']:r for r in map(json.loads,(ROOT/'claims.jsonl').read_text().splitlines())}
    scientific_keys=['text','status','scope','reader_implication','expected']
    changed=[cid for cid in old if any(old[cid].get(k)!=new[cid].get(k) for k in scientific_keys)]
    status_changed=[cid for cid in old if old[cid]['status']!=new[cid]['status']]
    tally=dict(generated_at_utc=now(),review_id='review-017-1',points=len(points),
        decisions=dict(Counter(p['decision'] for p in points)),existing_claims_revised=changed,
        claim_statuses_changed=status_changed,claims_withdrawn=[],claims_added=sorted(set(new)-set(old)),
        analysis_batches_added=['E68'],verification_batches_added=['E69','E70'],new_model_fits=0,new_ai_calls=0)
    tally['new_analysis_process_runs']=len(tally['analysis_batches_added'])
    tally['new_verification_process_runs']=len(tally['verification_batches_added'])
    tally['new_experiment_process_runs']=tally['new_analysis_process_runs']+tally['new_verification_process_runs']
    (ROOT/'review/response-points.json').write_text(json.dumps(points,indent=2)+'\n')
    (ROOT/'review/response-tally.json').write_text(json.dumps(tally,indent=2)+'\n')
    text='# Response to review-017-1\n\n'+f"Written {now()}. Original review: `review/review-1.md`; target `submission-1` (`8ff25a6335b4ec3aee0b998032633a6948f840b9`). All six findings are adopted with evidence-specific qualifications below. No result, fit, failure or first-draft snapshot was deleted. Review-prompted analysis plan v11 was committed before E68. No new model fitting or AI API call was used.\n\n"
    for p in points:
        text+='## '+p['point_id']+' — '+p['decision']+'\n\n'
        text+='Reason: '+p['reason']+'\n\nChanges: '+p['changes']+'\n\nEvidence and limits: '+p['evidence']+'\n\n'
        text+='Change commits: '+', '.join('`'+x+'`' for x in p['commit_ids'])+'. Added scientific analyses: '+(', '.join(p['experiments_added']) or 'none')+'.\n\n'
    text+='## Verification and tally\n\n```json\n'+json.dumps(tally,indent=2)+'\n```\n\n'
    verification=ROOT/'review/offline-verification.json'
    if verification.exists():
        v=json.loads(verification.read_text())
        text+=f"Latest full self-rerun: **{v['verification']['status']}**, revision `{v['prepared_revision']}`, {v['verification']['elapsed_seconds']:.3f}s. See `review/offline-verification.json` for exact scope/time and `VERIFY.md` for the single entry point. This same-session numerical rerun shares the saved probability bytes; it is not independent reproduction.\n"
    text+='\nThe human reports that the AI-agent reviewer also reran saved-prediction verification on the same machine. That report is preserved, not independently inspected or described as human peer review/independent reproduction. Reviewer model/runtime labels are human-reported, not directly observable by this session. Final amendments and the completed verification receipt appear in the final tagged tree.\n'
    (ROOT/'review/response-1.md').write_text(text)
    print(json.dumps(tally,indent=2))

if __name__=='__main__':main()
