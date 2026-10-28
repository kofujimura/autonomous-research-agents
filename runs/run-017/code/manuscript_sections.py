"""Manuscript prose whose empirical numbers are rendered from analysis outputs."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

def sections(root,analysis,scores,summary,values,number,markdown,region_labels,
             tables_out=None,alignment=None,threshold_directory=None):
    def emit(name,text):
        if tables_out is not None:(tables_out/name).write_text(text+'\n')
    def pct(x):return number(x,scale=100)
    def interval(row):
        if row.get('status')!='complete':return 'incomplete'
        return '['+', '.join(pct(x) for x in row['conditional_block_bootstrap_95_percent_interval'])+']'
    def contrast(name,collection=None):
        row=(collection or summary['primary_contrasts']).get(name,{})
        return (pct(row['estimate'])+' pp; conditional 95% interval '+interval(row)+' pp') if row.get('status')=='complete' else 'not yet complete'
    selected=scores[(scores.version=='raw')&(scores.boundary_tolerance_m==0)]
    standard=selected[selected.condition=='standardized_0.05']
    primary=standard[(standard.scope=='within')&(standard.decoder=='rf')&(standard.budget==2000)]
    def mean(rep,policy,column='small_macro_recovery_50',frame=primary):
        part=frame[(frame.representation==rep)&(frame.policy==policy)]
        return part[column].mean() if len(part)==5 else np.nan
    audit=json.loads((analysis/'comparison-audit.json').read_text())
    allocation=pd.read_csv(analysis/'allocation-audit.csv')
    main_alloc=allocation[(allocation.scope=='within')&(allocation.budget==2000)]
    pair_alloc=main_alloc[main_alloc.policy=='object']
    secondary=summary['secondary_condition_contrasts']
    boundary=[]
    for row in secondary:
        if row['scope']=='within' and row['decoder'] in ['rf','logit']:
            boundary.append([row['decoder'],row['budget'],contrast('H1_interaction',row['contrasts'])])
    boundary_table=markdown(['Decoder','Fitting positions','Representation × allocation interaction'],boundary)
    transfer=[]
    for row in secondary:
        if row['scope'].startswith('leave_'):
            transfer.append([region_labels[row['scope'][6:]],contrast('aef_oracle_gain',row['contrasts']),
                contrast('optical_oracle_gain',row['contrasts']),contrast('H1_interaction',row['contrasts'])])
    transfer_table=markdown(['Held-out reference project','Embedding oracle gain','Optical oracle gain','Interaction'],transfer)
    smoothing=selected[(selected.scope=='within')&(selected.decoder=='rf')&(selected.budget==2000)&
        (selected.representation=='optical')&(selected.condition=='standardized_0.05')&
        selected.policy.isin(['area','object'])]
    smooth_rows=[]
    for (policy,version),part in scores[(scores.scope=='within')&(scores.decoder=='rf')&(scores.budget==2000)&
        (scores.representation=='optical')&(scores.condition=='standardized_0.05')&
        (scores.boundary_tolerance_m==0)&scores.policy.isin(['area','object'])].groupby(['policy','version'],sort=True):
        smooth_rows.append([policy,version,pct(part.small_macro_recovery_50.mean()),pct(part.producer_accuracy.mean()),pct(part.edge_disagreement_fraction.mean())])
    smooth_table=markdown(['Optical allocation','Map version','Small-patch recovery (%)','Pixel producer accuracy (%)','Adjacent-edge disagreement (%)'],smooth_rows)
    replay=selected[(selected.scope=='within')&(selected.decoder=='rf')&(selected.budget==2000)&(selected.condition=='validation_0.05')]
    budget_table=markdown(['Budget','Embedding area (%)','Embedding oracle (%)','Optical area (%)','Optical oracle (%)'],
        [[budget,*[pct(mean(rep,policy,frame=standard[(standard.scope=='within')&(standard.decoder=='rf')&(standard.budget==budget)]))
            for rep,policy in [('aef','area'),('aef','object'),('optical','area'),('optical','object')]]] for budget in [500,2000,8000]])
    primary_text=f'''### 4.1. Reference population and original comparisons

The frozen dataset has {values['small_test_count']} eligible small test patches. Of these, {values['test_small_no_interior']} have no 20 m interior. This is an eligibility consequence of patch geometry, not a discovery about a model. No selected core was replaced. One training core has an empty reference-scoring domain because other aquatic systems are excluded; it is retained. The original analysis contains {values['primary_fit_count']} fitted models. No primary map is an all-positive or all-negative prediction in the {audit['primary_fit_core_cases']} fit–test-core cases. The primary macro recovery reaches neither zero nor one in any fitted arm. Coincident probability maps and decisions are counted in the comparison audit; none occurred in the evaluated primary pairs.

**Table 2. Original small-patch recovery at a pooled reference-upland FPR of 5%.** Values are means of five seeds after equal weighting of the four regions. Context denotes added optical neighborhood means.

{{{{TABLE_PRIMARY}}}}

Oracle allocation changed embedding recovery from {pct(mean('aef','area'))}% to {pct(mean('aef','object'))}%, and optical recovery from {pct(mean('optical','area'))}% to {pct(mean('optical','object'))}%. The primary interaction was {contrast('H1_interaction')}. The exact threshold-reselection bootstrap, which includes operating-threshold variability from the resampled cores, is reported separately below. The primary fixed-threshold interval conditions on the original evaluated thresholds.

**Table 3. Planned original contrasts.** Differences are percentage points; intervals are paired conditional block-bootstrap summaries, not population-wide guarantees.

{{{{TABLE_CONTRASTS}}}}

The original optical-derived proposals gave an embedding change of {contrast('aef_proposal_gain')}; the optical change was {contrast('optical_proposal_gain')}. Thus this specific practical rule did not recover the observed embedding oracle gain. This is not an equivalence test, and it does not establish that a method without object identities cannot improve. Uncertainty allocation also remained close to the embedding area baseline. Both methods use the same counted initialization; their final class composition is different from balanced area allocation. Additional class-matched controls appear below.

The oracle and area allocations deliberately share all negative positions. Across seeds they share {int(pair_alloc.shared_with_area.min())}–{int(pair_alloc.shared_with_area.max())} of the unique fitting positions. They are neither independent training datasets nor identical inputs. All representation comparisons within an allocation use identical fitting positions. The allocation audit reports positive class counts, sub-minimum-unit positions, spatial allocation, patch representation and fallbacks rather than treating the nominal fitting budget as an annotation-cost measurement.

![Original recovery comparison](figures/primary-recovery.svg)

### 4.2. Regional error distribution and threshold replay

**Table 4. Original regional results, in fixed project order.** The projects differ in habitats, mapping procedures and source timing. These are case descriptions, not a ranking of regional inventory quality.

{{{{TABLE_REGIONS}}}}

A single pooled threshold does not impose equal error rates within regions. The corresponding reference-upland FPRs are:

{{{{TABLE_REGIONAL_FPR}}}}

When separate test-region thresholds impose the regional operating point, the interaction is {contrast('H1_interaction',summary['region_standardized_contrasts'])}. This reduces the original estimate but does not eliminate its direction in the sampled cases. The original result therefore includes a redistribution-of-error component as well as a remaining within-region ranking component.

**Table 5. Validation-selected threshold replay.** The threshold targets 5% reference-upland FPR in validation geography and is frozen before applying it to the test scores. Actual test FPR is reported alongside recovery.

{{{{TABLE_DEPLOYMENT}}}}

For embedding area allocation, replay yields {pct(mean('aef','area',frame=replay))}% recovery at {pct(mean('aef','area','upland_fpr',replay))}% test FPR; oracle allocation yields {pct(mean('aef','object',frame=replay))}% at {pct(mean('aef','object','upland_fpr',replay))}%. These outcomes do not establish a deployed 5% FPR. The greater replay recovery is partly associated with a less restrictive test operating point. Threshold transport is a separate practical problem from the standardized score comparison.

![Operating threshold transfer](figures/threshold-transfer.svg)

### 4.3. Planned capacity, budget and geographic boundaries

{budget_table}

{boundary_table}

The budget and decoder checks retain the sign of the original interaction under their tested settings. The hybrid predictor's observed recovery is {pct(mean('hybrid','area'))}% with area allocation and {pct(mean('hybrid','object'))}% with oracle allocation. A richer predictor does not remove the allocation question, but these comparisons do not identify the causal role of any input sensor or pretraining target.

The geographic-transfer fits omit all training and validation cores in the target reference project, then predict all sixteen cores in that project. Their test cohort is larger than the original four-core cohort. At held-region standardized 5% FPR, their interactions are small and their intervals include zero in every case:

{transfer_table}

This is a material boundary on generalization. The within-region interaction is not established for entire-region transfer. The original transfer validation replay uses only thresholds from the other regions; the standardized transfer thresholds in this table use held-region labels for evaluation, as in the main operating-point comparison. The held-region table is therefore not a deployment estimate. Exploratory matched-cohort and split-rotation checks are distinguished below.

### 4.4. Pre-performance secondary controls

{{{{TABLE_EXTRA}}}}

The equal-region allocation interaction is {contrast('regional_allocation_interaction')}. Restricting the oracle frame to the evaluation minimum mapping unit changes embedding recovery by {contrast('aef_mmu_frame_change')}; the optical change is {contrast('optical_mmu_frame_change')}. The original oracle's allocation to sub-minimum-unit components therefore is not an innocuous implementation detail. These amendments were fixed before performance, while their extended interval summaries were added after the first primary result.

### 4.5. Exploratory checks added after the primary outcome

{{{{EXPLORATORY_RESULTS}}}}
'''
    pixel_text=(f"The pooled pixel metrics change much less for embeddings: producer's accuracy is "
        f"{number(mean('aef','area','producer_accuracy'),digits=2,scale=100)}% with area allocation and "
        f"{number(mean('aef','object','producer_accuracy'),digits=2,scale=100)}% with oracle allocation; IoU is "
        f"{number(mean('aef','area','iou'),digits=2,scale=100)}% and {number(mean('aef','object','iou'),digits=2,scale=100)}%, respectively. "
        f"Optical producer's accuracy is {number(mean('optical','area','producer_accuracy'),digits=2,scale=100)}% and "
        f"{number(mean('optical','object','producer_accuracy'),digits=2,scale=100)}%, with IoU "
        f"{number(mean('optical','area','iou'),digits=2,scale=100)}% and {number(mean('optical','object','iou'),digits=2,scale=100)}%. "
        "These are observed means, not tests of equivalence. Pooled pixel metrics weight area, whereas the primary patch measure first weights regions equally. The embedding small-patch change is therefore not apparent from the near-constant pooled area metrics alone. ")
    primary_text=primary_text.replace('The primary interaction was ',pixel_text+'The primary interaction was ',1)
    threshold_path=(threshold_directory or root/'data/threshold-bootstrap')/'summary.json'
    threshold_text='The planned threshold-reselection check is not complete.'
    if threshold_path.exists():
        t=json.loads(threshold_path.read_text())
        # Its point estimates equal the observed original estimates; intervals are resampled.
        rows=[]
        for key,label in [('H1_interaction','Interaction'),('aef_oracle_gain','Embedding oracle gain'),('optical_oracle_gain','Optical oracle gain')]:
            row=t['contrasts'][key]
            bounds=row['reselected_threshold_block_bootstrap_95_percent_interval']
            rows.append([label,'['+', '.join(pct(x) for x in bounds)+']',row['undefined_replicates']])
        threshold_text='The exact threshold-reselection bootstrap retains the fitted models and reference maps while recalculating thresholds from each resampled test-core distribution. It changes the uncertainty calculation, not the original point estimates.\n\n'+markdown(['Comparison','Reselected-threshold 95% interval (pp)','Undefined replicates'],rows)
        emit('threshold-bootstrap.md',markdown(['Comparison','Reselected-threshold 95% interval (pp)','Undefined replicates'],rows))
    abstract=f'''Across {values['core_count']} geographically separated cores in four US inventory projects, the planned primary test used {values['small_test_count']} complete mapped patches of 0.2–1 ha, five training seeds and 2,000 fitting positions. At a test-standardized 5% reference-upland false-positive area rate, oracle object allocation raised annual-embedding patch recovery from {pct(mean('aef','area'))}% to {pct(mean('aef','object'))}%, compared with {pct(mean('optical','area'))}% to {pct(mean('optical','object'))}% for seasonal optical predictors. The interaction was {contrast('H1_interaction')}. The planned optical-derived proposal rule did not recover this embedding gain. The interaction remained positive with the tested linear decoder and alternative fitting budgets, but was small and uncertain in all entire-region transfer cases. In the original split, validation-selected thresholds exceeded their nominal test FPR, so these standardized results are not a demonstrated deployment guarantee. {values['test_small_no_interior']}/{values['small_test_count']} small test patches had no 20 m interior grid centers, a geometry restriction relevant to homogeneous sampling. {{{{EXPLORATORY_ABSTRACT}}}}'''
    discussion='''For an analyst subsampling an existing wetland reference, allocation can materially change the apparent benefit of a reusable representation. The observed embedding improvement under object allocation is larger than the corresponding optical improvement within the original regions. Choosing a representation using one homogeneous or area-weighted training design can therefore obscure a useful conditional mapping behavior. This evidence supports checking allocation and patch-level outcomes together; it does not justify assuming that embeddings automatically preserve small wetlands.

The oracle comparison is a diagnostic with privileged information. The full inventory already contains class boundaries and connected components, so object geometry is not established to be independently unavailable or costly. The result is about which fitting positions a classifier receives from that resource. It is not a claim that collecting the same number of isolated labels in an unmapped landscape gives the same result. Image-derived sampling is accordingly evaluated as a specific algorithmic alternative, with a separate uniform-initialization simulation, rather than a proof of the necessity of mapped objects.

Geographic transfer and calibration limit the practical inference. An allocation rule helpful for interpolation across separated cores within the same reference projects need not recover the same gain in a completely unrepresented region. Likewise, a standardized reference-upland FPR is an evaluation condition whose threshold uses held-out labels; a practitioner must validate threshold transport using available local reference information. Neither the inventory comparison nor visual map coherence measures ecological wetland completeness.

The intervention an inventory-owning mapping team can consider is modest: include an object-allocation baseline and report recovery of small mapped patches alongside area metrics before settling a fitting design. Whether this improves conservation decisions, annotation effort, ecological discovery or later-year updates requires different evidence. The exploratory controls below are mechanism and scope checks, not confirmations of those unmeasured outcomes.'''
    appendix=f'''### A. Appearance controls and non-identical sensitivity cohorts

{smooth_table}

Gaussian smoothing changes both edge density and recovery. Its edge-disagreement number describes visual coherence, not correctness. The primary comparison already uses common valid pixels. All original small test patches meet the ≥90% valid-pixel sensitivity, so that filter reproduces the same cohort and is not additional independent robustness evidence. Any-overlap, 75% coverage, boundary tolerance, isolation and habitat-code strata are available in the regenerated `scores.csv`, `regional-scores.csv` and `strata-scores.csv`; empty strata remain undefined.

### B. Threshold uncertainty

{threshold_text}

### C. Completion and interpretation

The analysis snapshot includes {summary['fit_count']} final fitted models. `completed-cells.csv` lists the exact observed representation, allocation, decoder, budget, geography and seed combinations. The original grid was prioritized to the main area–oracle contrast for decoder, budget, hybrid and transfer checks; it did not execute every possible cross-product of all five policies and all sensitivity settings. Missing cells are not scored as failures or successes. Exploratory v7–v9 additions are separately labelled and retain all outcomes. No human user experiment was performed.

Failed source-orientation and partial-retrieval batches remain in the experiment records. The first full analysis attempt failed at a missing table handoff after preserving its metrics; the corrected snapshot did not substitute different scientific data. `protocol/deviations.jsonl` and `protocol/implementation-clarifications.md` document changes, including scene-selection tile preferences and the E03 code-provenance correction. Hashes and Git records are inspection aids, not an immutable external audit.
'''
    exploratory_text='Exploratory experiments are not complete in this snapshot.'
    exploratory_abstract=''
    nb_rows=[r for r in secondary if r['scope']=='within' and r['decoder']=='rf_noboot' and r['budget']==2000]
    robustness_path=analysis/'robustness/summary.json'
    if nb_rows and robustness_path.exists():
        nb_contrasts=nb_rows[0]['contrasts']
        nb=standard[(standard.scope=='within')&(standard.decoder=='rf_noboot')&(standard.budget==2000)]
        fit_data=pd.read_csv(analysis/'fits.csv')
        weight_rows=[]
        weight_labels={'area':'Area (no bootstrap)','object':'Oracle objects (no bootstrap)',
            'weighted_area':'Same area positions, inverse-size weights',
            'weighted_area_cap10':'Same area positions, truncated weights'}
        for policy,label in weight_labels.items():
            row=[label,pct(mean('aef',policy,frame=nb)),pct(mean('optical',policy,frame=nb))]
            part=fit_data[(fit_data.decoder=='rf_noboot')&(fit_data.policy==policy)]
            if policy.startswith('weighted'):
                ess=part.weight_positive_effective_sample_size
                row.append(number(ess.min())+'–'+number(ess.max()))
            else:row.append('unweighted')
            weight_rows.append(row)
        weight_table=markdown(['No-bootstrap fitting condition','Embedding recovery (%)','Optical recovery (%)','Positive-weight effective sample size'],weight_rows)
        proposal_policies=[('area','Balanced area'),('proposal','Original optical proposals'),('uncertainty','Original optical uncertainty'),
            ('proposal_aef','Embedding proposals'),('uncertainty_aef','Embedding uncertainty'),
            ('proposal_aef_classmatched','Area matching embedding-proposal counts'),
            ('uncertainty_aef_classmatched','Area matching embedding-uncertainty counts')]
        proposal_table=markdown(['Balanced initialization / final allocation','Embedding recovery (%)','Optical recovery (%)'],
            [[label,pct(mean('aef',policy)),pct(mean('optical',policy))] for policy,label in proposal_policies])
        uniform_table=markdown(['Uniform initialization condition','Embedding recovery (%)','Optical recovery (%)'],
            [[label,pct(mean('aef',policy)),pct(mean('optical',policy))] for policy,label in
                [('natural_area','Uniform area, all positions'),('proposal_uniform_aef','Embedding proposals after uniform initialization'),
                 ('uncertainty_uniform_aef','Embedding uncertainty after uniform initialization')]])
        quota_table=markdown(['Positive allocation with original oracle negatives','Embedding recovery (%)','Optical recovery (%)'],
            [[label,pct(mean('aef',policy)),pct(mean('optical',policy))] for policy,label in
                [('area','Original balanced area'),('area_regionmatched','Area matching oracle regional counts'),
                 ('area_corematched','Area matching oracle core counts'),('object','Original oracle objects')]])
        rotation_rows=[]
        original_row=summary['primary_contrasts']['H1_interaction']
        for scope,label,collection in [('within','Original split (primary)',summary['primary_contrasts']),
            *[(r['scope'],r['scope']+' (exploratory)',r['contrasts']) for r in secondary if r['scope'].startswith('rotation')]]:
            part=standard[(standard.scope==scope)&(standard.decoder=='rf')&(standard.budget==2000)&
                (standard.policy=='area')&(standard.representation=='aef')]
            n=int(part.small_patch_count.iloc[0])
            rotation_rows.append([label,n,contrast('H1_interaction',collection),collection['H1_interaction']['undefined_replicates']])
        rotation_table=markdown(['Held-out split','Small patches','Interaction','Undefined bootstrap replicates'],rotation_rows)
        families=json.loads(robustness_path.read_text())['families']
        rotated=families['rotations_all']['conditional_contrasts']['standardized_0.05']
        transferred=families['geographic_all']['conditional_contrasts']['standardized_0.05']
        matched=families['geographic_original_test']['conditional_contrasts']['standardized_0.05']
        cohort_means=pd.read_csv(analysis/'robustness/arm-means.csv')
        cohort_rows=[]
        labels={'rotations_all':'All split rotations','geographic_all':'Entire-region transfer, all cores',
            'geographic_original_test':'Transfer, original test-core subgroup'}
        for family,label in labels.items():
            for condition in ['standardized_0.05','validation_0.05']:
                part=cohort_means[(cohort_means.scope==family)&(cohort_means.condition==condition)]
                row=[label,'test-standardized' if condition.startswith('standardized') else 'validation replay',int(part.patches_per_seed.iloc[0])]
                for rep,policy in [('aef','area'),('aef','object'),('optical','area'),('optical','object')]:
                    cell=part[(part.representation==rep)&(part.policy==policy)].iloc[0]
                    row.append(pct(cell.estimate)+' ('+pct(cell.mean_achieved_upland_fpr)+')')
                cohort_rows.append(row)
        cohort_table=markdown(['Cohort','Threshold','Patches','Embedding area','Embedding oracle','Optical area','Optical oracle'],cohort_rows)
        weighted=fit_data[fit_data.policy=='weighted_area'];capped=fit_data[fit_data.policy=='weighted_area_cap10']
        minimum=lambda part:number(part.weight_minimum_positive_weight.min(),digits=4)+'–'+number(part.weight_minimum_positive_weight.max(),digits=4)
        maximum=lambda part:number(part.weight_maximum_positive_weight.min())+'–'+number(part.weight_maximum_positive_weight.max())
        exploratory_text=f'''**Fixed-position weighting controls.** With bootstrap disabled in every comparator, inverse-size weighting improves embedding recovery by {contrast('aef_weighted_area_gain',nb_contrasts)}; the truncated variant changes it by {contrast('aef_weighted_area_cap10_gain',nb_contrasts)}. The same fitting positions and labels are used, so this improvement does not require newly represented training patches. The weighted models' means remain below the matched oracle mean, with weighted-minus-oracle contrasts {contrast('aef_weighted_area_vs_oracle',nb_contrasts)} and {contrast('aef_weighted_area_cap10_vs_oracle',nb_contrasts)}. This does not decompose the original bootstrapped-forest gain or prove the cause of its remaining gap.

{weight_table}

Across seeds, minimum positive weights are {minimum(weighted)} and maximum weights {maximum(weighted)} without truncation; corresponding ranges after truncation and normalization are {minimum(capped)} and {maximum(capped)}. The post-normalization maxima exceed ten, as specified. Full weight vectors, class totals and effective sample sizes remain in the fit records. The control changes the RF bootstrap setting, with matched controls in that setting; its effect cannot simply be assigned to the primary decoder.

**Stronger image-derived allocation.** Replacing only the proposal predictor with embeddings does not give a clear component-proposal gain, but embedding-guided uncertainty improves the final embedding classifier by {contrast('aef_uncertainty_aef_gain')}. Its comparison with the class-count-matched area control is {contrast('aef_uncertainty_aef_vs_classmatched')}. The mean remains below the original oracle mean; equivalence was not tested. The original optical-teacher negative result therefore should not be generalized to every method that does not select by object identity.

{proposal_table}

With uniform initialization, embedding proposals change embedding recovery relative to uniform area by {contrast('aef_proposal_uniform_aef_vs_natural')}, and embedding uncertainty changes it by {contrast('aef_uncertainty_uniform_aef_vs_natural')}. These simulated-query results still assume the supplied reference-derived land domain. They measure neither human annotation cost nor discovery of omitted ecological wetlands.

{uniform_table}

**Geographical-mixture controls.** Matching the original oracle's positive counts by core improves the embedding area control by {contrast('aef_area_corematched_gain')}. The oracle-minus-core-matched interaction is {contrast('oracle_vs_area_corematched_interaction')}. Between-core allocation can therefore account for part of the observed contrast in this control, while its residual remains. The geographical and weighting controls are not an orthogonal factorial decomposition and their gains must not be added.

{quota_table}

**Split dependence and transfer cohorts.** The original interaction is larger than each new split's estimate. Two new splits have some undefined core-bootstrap replicates because a resampled region can contain no eligible small patch; the table reports these rather than silently counting all replicates as defined.

{rotation_table}

Pooling all four held-out rotations within each region gives {contrast('H1_interaction',rotated)} across all {int(cohort_means[cohort_means.scope=='rotations_all'].patches_per_seed.iloc[0])} eligible small patches. This attenuated estimate materially changes interpretation of the original split's magnitude. It is a conditional cross-validation summary from overlapping training sets, not independent ecological replication.

The equal-region pooled entire-transfer interaction is {contrast('H1_interaction',transferred)}. Restricting those transfer scores to the original test-core subgroup gives {contrast('H1_interaction',matched)}, but its achieved FPR differs from the nominal operating point because thresholds were retained from the wider cohort. These subgroup numbers do not establish a matched-FPR improvement. The appendix reports recovery and actual FPR together.

**Reference alignment.** {{{{ALIGNMENT_RESULTS}}}}'''
        exploratory_abstract=f"Exploratory split rotations over {int(cohort_means[cohort_means.scope=='rotations_all'].patches_per_seed.iloc[0])} eligible small patches reduced the interaction to {contrast('H1_interaction',rotated)}. Exploratory fixed-position loss weighting and embedding-guided uncertainty recovered part of the allocation benefit, leaving its mechanism and the necessity of an oracle frame unestablished."
        discussion+='''\n\nThe exploratory controls change the interpretation in two ways. The original split gives a larger estimate than the pooled rotations, and a benefit can arise from reweighting existing fitting positions or stronger image-guided selection. An explanation based only on exposing additional mapped patches is therefore insufficient for the broader set of tested classifiers and allocations. Neither weighting nor geographical matching identifies a complete causal decomposition of the original effect. Their information requirements also remain explicit: inverse-size weights use the object frame, and matched quotas are derived from the oracle sample.'''
        appendix+='\n### D. Cohort and threshold details\n\nCells give recovery percent followed by achieved reference-upland FPR in parentheses. The transfer subgroup retains wider-cohort thresholds.\n\n'+cohort_table+'\n\nFor an entire-held-region fit there is only one test region, so its pooled and region-specific test thresholds coincide by construction. These duplicate conditions are not counted as independent robustness evidence.\n'
        for name,table in [('weight-controls.md',weight_table),('embedding-proposals.md',proposal_table),
            ('uniform-initialization.md',uniform_table),('geographical-quotas.md',quota_table),
            ('split-rotations.md',rotation_table),('cohort-thresholds.md',cohort_table)]:emit(name,table)
    alignment_text='Alignment stress analysis is not complete in this snapshot.'
    alignment_path=(alignment or root/'data/alignment-stress')/'summary.json'
    if alignment_path.exists():
        align=json.loads(alignment_path.read_text());alignment_rows=[]
        for direction,collection in align['contrasts'].items():
            alignment_rows.append([direction,align['common_cohort_patches'],contrast('H1_interaction',collection)])
        alignment_table=markdown(['Synthetic reference offset','Common-cohort patches','Interaction'],alignment_rows)
        alignment_text=f"The shared cohort contains {align['common_cohort_patches']} of {align['original_patches']} original small patches. The interaction remains positive under every cardinal one-cell shift in this restricted cohort. The excluded {align['original_patches']-align['common_cohort_patches']} patches are outside that robustness claim; this is not an empirical error distribution.\n\n"+alignment_table
        emit('alignment-stress.md',alignment_table)
    cases=standard.copy()
    def case_family(row):
        if row.scope.startswith('leave_'):return 'Entire-region transfer'
        if row.scope.startswith('rotation'):return 'Added split rotations'
        if row.decoder=='rf_noboot':return 'Weighting and bagging controls'
        if row.policy in ['area_corematched','area_regionmatched']:return 'Oracle-quota controls'
        if row.policy in ['proposal_aef','uncertainty_aef','proposal_aef_classmatched','uncertainty_aef_classmatched','proposal_uniform_aef','uncertainty_uniform_aef']:return 'Embedding-guided allocation'
        if row.decoder=='rf' and row.budget==2000 and row.policy in ['area','object','interior','proposal','uncertainty'] and row.representation in ['aef','optical','optical_context']:return 'Original primary'
        return 'Other planned controls'
    cases['comparison_family']=cases.apply(case_family,axis=1)
    case_rows=[]
    for label,part in cases.groupby('comparison_family',sort=True):
        case_rows.append([label,len(part),int(part.core_count.sum()),int(part.empty_scoring_cores.sum()),
            int(part.all_positive_cores.sum()),int(part.all_negative_cores.sum()),
            int((part.small_macro_recovery_50==0).sum()),int((part.small_macro_recovery_50==1).sum())])
    cases_table=markdown(['Comparison family','Fits','Fit–test-core cases','Empty scoring cases','All-positive cases','All-negative cases','Macro floor fits','Macro ceiling fits'],case_rows)
    emit('comparison-cases.md',cases_table)
    exploratory_text+='\n\n**Constant and empty cases across comparisons.** Counts concern raw maps at the standardized 5% FPR, with zero boundary tolerance. Empty scoring domains are retained separately from constant predictions. Macro floor/ceiling counts concern small-patch recovery.\n\n'+cases_table+'\n'
    original_cases=cases[cases.comparison_family=='Original primary']
    rotated_cases=cases[cases.comparison_family=='Added split rotations']
    transfer_cases=cases[cases.comparison_family=='Entire-region transfer']
    if exploratory_abstract:
        n_constant=lambda part:int(part.all_positive_cores.sum()+part.all_negative_cores.sum())
        exploratory_abstract+=f" Constant predictions occurred in {n_constant(original_cases)}/{int(original_cases.core_count.sum())} primary fit–core cases, {n_constant(rotated_cases)}/{int(rotated_cases.core_count.sum())} added-rotation cases and {n_constant(transfer_cases)}/{int(transfer_cases.core_count.sum())} transfer cases."
    discussion+='\n\nEqual weighting of mapped patches and a reference-upland false-positive area constraint are evaluation choices. They do not imply that all wetlands have the same ecological value or regulatory priority. The appropriate balance between area and patch objectives depends on the application; that value judgment was not measured here.'
    for name,table in [('budget.md',budget_table),('secondary-contrasts.md',boundary_table),
                       ('geographic-transfer.md',transfer_table),('smoothing.md',smooth_table)]:emit(name,table)
    fields=dict(ABSTRACT_RESULTS=abstract,RESULTS=primary_text,DISCUSSION=discussion,APPENDIX=appendix,
        RESULT_LIMITATIONS='The primary benefit is conditional on within-region training and the tested reference agreement task. It is not retained at the same magnitude under entire-region exclusion. Sparse forested/uncertain wetlands omitted from the inventory cannot enter the patch-recovery denominator. Differences between representation inputs, native resolutions and pretraining prevent a causal attribution to spatial context.',
        PROTOCOL_CHRONOLOGY='Exploratory v7–v10 followed the primary outcome: inverse-size loss weights and stronger proposals; fixed split rotations and matched transfer summaries; oracle geographical-quota controls; and deterministic reference-alignment stress. These additions do not redefine the primary estimand. Plans, exact timestamps, input hashes and commits accompany every batch.',
        DEVIATIONS='See the versioned protocol and deviations record.',
        VERIFICATION_RESULT=(f"The session's clean-copy offline numerical run passed in {json.loads((root/'review/offline-verification.json').read_text())['verification']['elapsed_seconds']:.3f} seconds, using shared saved-probability inputs; see `review/offline-verification.json` and `review/self-check.md` for the exact committed revision and scope." if (root/'review/offline-verification.json').exists() else 'The clean-copy verification has not yet completed; no success is claimed.'),
        EXPLORATORY_RESULTS=exploratory_text,EXPLORATORY_ABSTRACT=exploratory_abstract,
        ALIGNMENT_RESULTS=alignment_text)

    from review_manuscript import revise
    return revise(fields,root,analysis,scores,summary,number,tables_out)
