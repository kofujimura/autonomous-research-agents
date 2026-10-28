"""Integrate complete review-response summaries into the generated manuscript."""
import json
import numpy as np

def revise(fields,root,analysis,scores,summary,number,tables_out):
    extra=json.loads((analysis/'review-response/summary.json').read_text())
    def pct(v):return number(v,scale=100)
    def row(family,condition='standardized_0.05',coverage='50'):
        return next(x for x in extra['sensitivities'] if x['family']==family and x['condition']==condition and x['coverage']==coverage)
    def est(item,key):return pct(item['contrasts'][key]['estimate'])
    def ci(item,key):return '['+', '.join(pct(v) for v in item['contrasts'][key]['conditional_block_bootstrap_95_percent_interval'])+']'
    def rec(item,arm):return pct(item['arms'][arm]['recovery'])
    original=row('original');pooled=row('four_splits');any_pooled=row('four_splits',coverage='any')
    replay=row('original','validation_0.05');transfer=extra['transfer_replay'][-1]
    fpr_low,fpr_high=map(pct,extra['transfer_regional_mean_fpr_range'])
    original_h=summary['primary_contrasts']['H1_interaction']
    rotations=[x for x in summary['secondary_condition_contrasts'] if x['scope'].startswith('rotation')]
    n_below=sum(x['contrasts']['H1_interaction']['estimate']<original_h['conditional_block_bootstrap_95_percent_interval'][0] for x in rotations)
    def table_file(name):
        value=(analysis/'review-response'/name).read_text().rstrip()
        if tables_out is not None:(tables_out/('review-'+name)).write_text(value+'\n')
        return value
    tables={name:table_file(name) for name in ['definition-sensitivity.md','transfer-replay.md','rotation-replay.md','patch-size.md','pixel-secondary.md']}
    # Planned result first, followed immediately by the more comprehensive exploratory estimate.
    fields['ABSTRACT_RESULTS']=f'''Wetland inventories guide conservation planning, but area accuracy can conceal missed small patches. We compared annual satellite embeddings with seasonal optical imagery in four US inventory projects, using 2,000 training positions and five seeds; the planned split had 16 test cores. Patch-first allocation selects a mapped patch, then a pixel, using existing inventory boundaries. Recovery required at least half a patch’s valid reference pixels. At thresholds set to target 5% of reference-upland area predicted as wetland, its planned embedding-minus-optical gain difference was {est(original,'H1_interaction')} percentage points (conditional 95% interval {ci(original,'H1_interaction')}). Exploratory pooling of four fixed splits gave gains of {est(pooled,'aef_oracle_gain')} points for embeddings and {est(pooled,'optical_oracle_gain')} for optical predictors, a difference of {est(pooled,'H1_interaction')} {ci(pooled,'H1_interaction')}; optical gained in every new split. These intervals exclude split-selection uncertainty. Planned coverage sensitivities change the interpretation: optical maps touched more patches, while embeddings covered more patches by at least half. Benefits did not transport reliably between projects: thresholds transferred from other projects gave a negative embedding gain, with regional false-positive rates spanning {fpr_low}–{fpr_high}%. The planned optical-guided proposals did not reproduce the embedding gain; exploratory embedding-guided uncertainty recovered part. Inventory-owning teams should compare patch-first sampling and patch recovery beside pixel metrics, and validate threshold transport locally. These results concern mapped inventory agreement, not ecological completeness or annotation-cost savings.'''
    # The first-draft results remain visible, but their interpretation is conditional.
    text=fields['RESULTS']
    marker='**Table 3. Planned original contrasts.**'
    text=text.replace(marker,
        f"The original split has the largest interaction of the four fixed splits. The exploratory all-split summary gains {est(pooled,'aef_oracle_gain')} pp for embeddings and {est(pooled,'optical_oracle_gain')} pp for optical predictors, with an interaction of {est(pooled,'H1_interaction')} pp {ci(pooled,'H1_interaction')}; both predictors benefit in that pooled comparison. The larger original estimate should be read with the split variation below.\n\n"+marker)
    marker='![Operating threshold transfer](figures/threshold-transfer.svg)'
    text=text.replace(marker,
        f"Under this planned validation replay, the embedding gain is {est(replay,'aef_oracle_gain')} pp {ci(replay,'aef_oracle_gain')}, but the interaction is {est(replay,'H1_interaction')} pp {ci(replay,'H1_interaction')}. Its interval includes zero. Appendix E reports every planned FPR target and coverage definition, including regional validation replay, rather than selecting the original operating point alone.\n\n"+marker)
    marker='This is a material boundary on generalization.'
    text=text.replace(marker,f'''**Planned transfer with thresholds chosen in other projects.** Each threshold is fixed using only the remaining projects' validation cores. Cells give recovery (%) and achieved FPR (%) in parentheses; contrast intervals are conditional on these transferred thresholds. They are not matched-FPR effects.

{tables['transfer-replay.md']}

Pooling the four held-out projects gives an embedding gain of {est(transfer,'aef_oracle_gain')} pp {ci(transfer,'aef_oracle_gain')}, an optical gain of {est(transfer,'optical_oracle_gain')} pp {ci(transfer,'optical_oracle_gain')}, and an interaction of {est(transfer,'H1_interaction')} pp {ci(transfer,'H1_interaction')}. The embedding recovery gain is negative in each held-out project. The regional five-seed mean FPRs range from {fpr_low}% to {fpr_high}%; this is a range over project/representation/allocation means, not individual seeds. Across individual seeds the range is {pct(extra['transfer_seed_fpr_range'][0])}–{pct(extra['transfer_seed_fpr_range'][1])}%. Lower embedding FPR under oracle allocation contributes to its lower recovery, so the replay does not isolate an allocation effect at constant error rate. It directly shows poor threshold transport under the planned transfer protocol.

'''+marker)
    fields['RESULTS']=text
    text=fields['EXPLORATORY_RESULTS']
    marker='**Split dependence and transfer cohorts.**'
    text=text.replace(marker,
        marker+f" Optical oracle-minus-area gains are positive in every new rotation, and the embedding-specific excess is split dependent. {n_below} of {len(rotations)} new-split interaction estimates fall below the lower endpoint of the original conditional interval. With only four resampled test cores per region and fixed training cores, that interval omits the observed split-to-split variability; it must not be interpreted as uncertainty over alternative splits.")
    marker='This attenuated estimate materially changes interpretation of the original split\'s magnitude.'
    text=text.replace(marker,
        f"The component gains are {est(pooled,'aef_oracle_gain')} pp {ci(pooled,'aef_oracle_gain')} for embeddings and {est(pooled,'optical_oracle_gain')} pp {ci(pooled,'optical_oracle_gain')} for optical predictors. "+marker)
    fields['EXPLORATORY_RESULTS']=text
    discussion=fields['DISCUSSION']
    a=discussion.index('For an analyst');b=discussion.index('\n\nThe oracle comparison',a)
    discussion=discussion[:a]+f'''Patch-first allocation improved small-patch recovery for both predictors within these inventory projects. In the exploratory pooled four-split summary, gains are {est(pooled,'aef_oracle_gain')} pp for embeddings and {est(pooled,'optical_oracle_gain')} pp for optical predictors; their {est(pooled,'H1_interaction')} pp difference is smaller than the planned original-split interaction of {est(original,'H1_interaction')} pp. Optical gained in all new rotations. The embedding-specific excess is a few points in the pooled comparison and varies with the training/test split and coverage definition. The original conditional interval measures neither split selection nor national uncertainty. This quantification for fixed representations and held-out mapped patches, rather than patch-first upweighting itself, is the contribution.

The planned coverage sensitivities distinguish touching a patch from covering it substantially. Across all four splits, optical any-overlap recovery is {rec(any_pooled,'optical_area')}→{rec(any_pooled,'optical_object')}%, exceeding embeddings' {rec(any_pooled,'aef_area')}→{rec(any_pooled,'aef_object')}%. At ≥50% coverage the ordering reverses: embeddings {rec(pooled,'aef_area')}→{rec(pooled,'aef_object')}%, optical {rec(pooled,'optical_area')}→{rec(pooled,'optical_object')}%. These aggregate outcomes are consistent with optical maps touching more patches and embedding maps covering more patches substantially; they do not establish a cause such as smoothness, nor greater ecological completeness. A practitioner interested in locating any trace of a patch can reach a different judgment from one requiring recovery of most of its extent.'''+discussion[b:]
    a=discussion.index('Geographic transfer and calibration');b=discussion.index('\n\nThe intervention',a)
    discussion=discussion[:a]+f'''Geographic transfer and threshold transport are major practical limits. At held-project standardized thresholds the allocation interactions are uncertain; the planned thresholds transferred from other projects instead give a pooled embedding gain of {est(transfer,'aef_oracle_gain')} pp {ci(transfer,'aef_oracle_gain')} and regional achieved FPRs of {fpr_low}–{fpr_high}%. Because FPR changes between allocations, the negative replay gain is not a constant-error causal effect. It does show that a within-project sampling benefit and a test-label-standardized score comparison do not provide a usable threshold for a new project. Even the original within-project validation replay has an interaction interval spanning zero. Suitable local reference data and explicit reporting of achieved error rates remain necessary.'''+discussion[b:]
    fields['DISCUSSION']=discussion
    without=extra['additional']['without_vermont'];new=extra['additional']['three_new_splits']
    appendix=f'''### E. Complete planned operating-point and coverage sensitivities

The underlying operating points and coverage definitions were fixed in v1/v6 before performance; v4 promised the without-Vermont description. Their complete tabulation and the additional condition-specific intervals below were added after review under v11. The original split is the planned comparison; four-split pooling is exploratory. Recovery and component gains use equal regional weights, then average five seeds. Each row uses the indicated thresholds from its original fitted scope. Intervals resample paired cores and seeds while keeping those models, thresholds and maps fixed; they are not adjusted for multiple comparisons. Any-overlap and ≥75% results are point estimates only because the saved bootstrap blocks encode ≥50% coverage. All fixed conditions are shown.

{tables['definition-sensitivity.md']}

The planned original interaction is smaller at the 1% and 10% FPR targets and in validation replay than at the primary 5% target, while ≥75% coverage makes it larger. The original any-overlap interaction is also smaller. Thus the numerical magnitude is definition dependent. Pooled results show benefits to both predictors at ≥50% coverage, including validation replay, but remain conditional on fixed models and this inventory. No equivalence or multiplicity-adjusted significance claim follows.

The descriptive interaction after excluding Vermont is {est(without,'H1_interaction')} pp, with embedding gain {est(without,'aef_oracle_gain')} pp and optical gain {est(without,'optical_oracle_gain')} pp (point estimates only). This excludes a region from the descriptive evaluation, not from model training. Pooling only the three added split rotations gives gains of {est(new,'aef_oracle_gain')} pp and {est(new,'optical_oracle_gain')} pp, interaction {est(new,'H1_interaction')} pp (review-prompted point estimates only).

### F. Every split under validation-threshold replay

Cells show recovery (%) with achieved reference-upland FPR (%) in parentheses. These are the v8 replay conditions, fully tabulated after review. Each interval conditions on the saved validation threshold and its split's fitted models. Training sets overlap; this is not independent replication.

{tables['rotation-replay.md']}

### G. Patch size, isolation and secondary pixel measures

At pooled 5% FPR and ≥50% coverage, recovery by the planned vector-area bins is below. Small is 0.2–1 ha, medium 1–10 ha and large ≥10 ha. Values are point estimates; large-patch counts are sparse and do not support a general conclusion. The plotted [coverage-by-size figure](figures/coverage-by-size.svg) shows each complete mapped patch's mean coverage over seeds, vector area and the preplanned ≥50 m isolation stratum. The isolation designation concerns mapped component proximity, not hydrological function.

{tables['patch-size.md']}

The original area/oracle arms also have the following planned secondary pixel summaries. Balanced accuracy uses the same standardized 5% FPR threshold. Average precision is computed on pooled test pixels before choosing a threshold for each model, then averaged across the five seeds; it uses area weighting and is not the region-macro patch metric. These are descriptive point estimates. The embedding oracle arm's average precision is lower even though small-patch recovery at the specified operating point is higher, so the patch improvement is not a uniform gain in every accuracy measure. We do not report a pooled-rotation AP obtained by averaging split APs, because it would not be AP on pooled predictions.

{tables['pixel-secondary.md']}
'''
    fields['APPENDIX'] += '\n'+appendix
    fields['DEVIATIONS']='''The initial source-orientation and retrieval failures were corrected before fitting; their original logs remain. Before performance, implementations clarified south-up embedding grids, optical radiometric harmonization, source-ID grouping, and finite sampling pools; scene availability sometimes required adjacent optical tiles despite the preferred same-tile selection. After the primary result, v7–v10 added explicitly exploratory mechanism, split and alignment checks. Review-prompted v11 exposes omitted planned sensitivities and adds their conditional summaries without changing fits, input data or the primary estimand. The complete ordered record, including E03/E62 commit-timing corrections and E64's late-loaded presentation helper, remains in `protocol/deviations.jsonl` and `protocol/implementation-clarifications.md`.'''
    fields['PROTOCOL_CHRONOLOGY']+=' Review-prompted v11 subsequently added complete saved-score reporting of preplanned definitions and threshold transport; no model was refit.'
    fields['RESULT_LIMITATIONS']='The original-split interaction overstates the pooled fixed-split magnitude. Both predictors benefit from patch-first allocation within these projects, while the embedding-specific excess is split and definition dependent. The original conditional interval resamples only four test cores per region with fitted training sets fixed. Whole-project transfer and threshold transport do not retain the within-project finding. Reference omissions and the different representation inputs/pretraining remain unverified; no ecological completeness, causal architecture or annotation-cost claim is supported.'
    return fields
