"""Final self-assessment; retain the original first-draft self-check as history."""
import json
from records import ROOT,now

def main():
    verification=json.loads((ROOT/'review/offline-verification.json').read_text())
    manuscript=ROOT/'review/final-manuscript-check/comparison.json'
    check=json.loads(manuscript.read_text()) if manuscript.exists() else None
    extra=json.loads((ROOT/'analysis/review-response/summary.json').read_text())
    response=json.loads((ROOT/'review/response-tally.json').read_text())
    v=verification['verification']
    text=f'''# Final self-check after review-017-1

Observed {now()}. This is the author's self-assessment, not a replacement for the single planned review by an AI agent. The original first-draft self-check remains unchanged under `review/submission-1/self-check.md`; a historical copy is appended below and does not describe the revised state.

## Claims, numbers and execution

Latest full offline numerical self-rerun: **{v['status']}**, {v['elapsed_seconds']:.3f}s, committed input revision `{verification['prepared_revision']}`; {v['committed_input_files_checked_unchanged']} copied committed files remained unchanged. Scope includes all465fits and the v11 saved-score reporting additions. Shared prediction bytes and the same environment mean this is not independent reproduction. Original E66/run-1 outputs remain. The current manuscript/claim check is **{check['status'] if check else 'pending'}**; report `review/final-manuscript-check/comparison.json`. The final procedure requires25numeric table hashes and11claims. Success is not inferred from an unfinished job.

All six review findings were adopted. Existing scientific interpretations C01/C04/C06 were revised; no existing claim status was changed and no claim was withdrawn. C11 exposes omitted sensitivities. `source_ids_role` states the common source IDs denote data provenance only. Original fitting inputs, seeds, probabilities, exclusions and main estimand were not changed. E68 is a new saved-score reporting analysis; E69 is the final full verification. No new model fits or AI API calls were added.

## Strength and alternative explanations

The abstract now gives both pooled component gains and the smaller embedding-specific excess beside the original planned test. It states that optical gains in every new split, identifies16primary test cores, and excludes split-selection uncertainty from the conditional intervals. Methods and Results specify four resampled test cores per region, fixed training sets, and two new estimates below the original interval's lower endpoint. No frequentist coverage claim over split selection is made.

The16fixed original/four-split sensitivity rows show1%/5%/10%pooled FPR, regional5%, pooled/regional validation replay and any/50%/75%coverage. Underlying definitions precede performance; complete tabulation/extra intervals are explicitly review prompted. Any/75%, size bins, without-Vermont and three-new-split aggregates are point estimates only. Optical touches more patches whereas embeddings recover more by at least half across the four splits; the paper does not infer a smoothness mechanism or ecological completeness. Medium/large outcomes and sparse large-patch counts are shown; the size/isolation figure is referenced. Balanced accuracy and pooled per-fit AP averaged across seeds are reported without pretending average split AP is AP on pooled predictions.

Planned transfer thresholds come only from other projects. Their negative pooled embedding gain is now prominent beside the test-label-standardized result, with regional achieved FPRs and the distinct individual-seed range. The replay's allocations have different achieved FPRs, so no constant-error causal allocation effect is claimed. Every within-project split replay is reported. Generality remains limited to the four convenience projects, fixed maps, tested representations and period.

No complete primary comparison is an identical-map, all-positive/negative or macro floor/ceiling comparison. The full comparison-case table retains0/1200constant primary fit–core cases,19/960added-rotation cases and17/1280transfer cases, and separate empty-domain counts. Geometry/interior restrictions and the identical90%-valid cohort remain described as design consequences, not novel empirical findings. These counts stay in Results; the abstract focuses on the nontrivial primary comparison and material scope changes.

## Literature, readability and reproducibility

All supporting citations have checked relevant full-text passages. The review repeat added primary publisher-provided public full text for Millard/Richardson2015, Colditz2015 and Corcoran2015, with section/page ranges, access route and CC BY4footers in S046/S047/supplementedS039 and retained notes. Direct publisher429 routes were stopped; public publisher copies were read ordinarily without credentials. Notes are not represented as original PDF/HTML bytes. Liu2026 remains abstract/bibliographic-only and supports no reported finding; no absence or first-study claim is asserted. Classic allocation principles and the expected interior restriction are explicitly acknowledged.

The introduction still explains inventory planning uses and reference limitations before technical content. Oracle is glossed as privileged access to existing mapped boundaries/identities; the sampler is described as patch then pixel. FPR is distinct from commission error and defined in area terms. The abstract is approximately200words, planned result precedes clearly labelled exploratory pooling, mechanism counts remain in Results, and a practical recommendation is explicit. Methods numbering is unique3.1–3.6, and deviations have a substantive summary.

E61–E67 originally point to v9; an append-only clarification identifies cumulative v1–v10 coverage including alignment stress, without rewriting run.json. V11 was fixed before added analysis. The final fresh input copy is immutable to the verification program while later root report/prose files are edited; this avoids treating a later prose edit as code loaded by the running copy. E03/E62/E64 historical exceptions remain disclosed. Time, storage, interventions, costs and unknown session identifiers are retained; no fabricated exact API invoice charge is supplied.

Remaining weaknesses cannot be resolved by these saved-score summaries: field-reference completeness, pretraining independence, causal representation mechanisms, representative site selection and human outcomes. The paper narrows its claims accordingly. The response does not promise that an untested model or more data must remove them. No external contact, new data request or participant work was used.

## Historical first-draft self-assessment

The following text was written before the review; its pending-review state,20tables/10claims and Corcoran abstract-only status are historical and superseded above.

'''
    text+=(ROOT/'review/submission-1/self-check.md').read_text()
    (ROOT/'review/self-check.md').write_text(text)
    print(json.dumps({'numerical_status':v['status'],'manuscript_status':check['status'] if check else 'pending','review_points':response['points']}))

if __name__=='__main__':main()
