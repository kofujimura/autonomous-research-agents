"""Create claim-to-evidence records from the completed numeric analysis."""
import argparse
import json
import pandas as pd
from records import ROOT

def main():
    p=argparse.ArgumentParser();p.add_argument('--analysis',default='analysis');p.add_argument('--out',default='claims.jsonl')
    p.add_argument('--alignment',default='data/alignment-stress');a=p.parse_args()
    analysis=ROOT/a.analysis;s=json.loads((analysis/'summary.json').read_text())
    scores=pd.read_csv(analysis/'scores.csv');claims=[]
    def add(cid,text,evidence,expected,experiments,exploratory,implication,scope=None,status='supported',sources=None):
        claims.append(dict(claim_id=cid,text=text,status=status,evidence_paths=evidence,
            source_ids=sources or ['S019','S024','S033'],
            source_ids_role='Data-provenance/access references only; empirical support is in evidence_paths and experiment_ids, not these documentation pages.',experiment_ids=experiments,
            scope=scope or 'Agreement with mapped palustrine patches in the fixed four NWI projects, production AEF v2.1 and the saved 2020 optical construction; no ecological completeness, causal architecture, labour or national inference.',
            verify='Run code/verify.py on a prepared committed input copy with --out pointing to a new external directory; inspect the named fields in the regenerated artifacts and compare the frozen expected values (absolute tolerance1e-12).',
            expected=expected,exploratory=exploratory,reader_implication=implication))
    original=s['primary_contrasts'];h=original['H1_interaction']
    add('C01','Within the original geographically separated regional split, the observed oracle-allocation gain in small-patch recovery is larger for annual embeddings than for the seasonal optical baseline at standardized5% reference-upland FPR.',
        ['analysis/summary.json','analysis/scores.csv','analysis/tables/primary.md','data/results/fits'],
        {'primary_contrasts':{k:original[k] for k in ['H1_interaction','aef_oracle_gain','optical_oracle_gain']}},
        ['E32','E33','E34','E35','E36','E37','E41','E61'],False,
        'Patch-first allocation improved within-project recovery for both predictors in pooled fixed splits; the embedding-specific excess was a few points and split dependent. This original-split estimate is conditional on four test cores per region and fixed fitted training sets, and does not establish an absence of optical benefit.')
    add('C02','The original optical-derived proposal rule did not reproduce the observed embedding oracle gain; its embedding proposal-minus-area estimate is close to zero with an interval spanning zero. This is not an equivalence test or a universal impossibility result.',
        ['analysis/summary.json','analysis/tables/contrasts.md','analysis/allocation-audit.csv'],
        {'primary_contrasts':{k:original[k] for k in ['aef_proposal_gain','optical_proposal_gain']}},
        ['E32','E33','E34','E35','E36','E37','E41','E61'],False,
        'Do not treat the oracle frame as a demonstrated image-only or cheap acquisition workflow; assess the actual proposal rule and counted initialization.')
    replay=scores[(scores.scope=='within')&(scores.decoder=='rf')&(scores.budget==2000)&
        (scores.version=='raw')&(scores.condition=='validation_0.05')&(scores.boundary_tolerance_m==0)]
    expected_replay={}
    for rep in ['aef','optical']:
        for policy in ['area','object']:
            part=replay[(replay.representation==rep)&(replay.policy==policy)]
            expected_replay[rep+'_'+policy]={k:float(part[k].mean()) for k in ['small_macro_recovery_50','upland_fpr']}
    add('C03','Thresholds targeting5% reference-upland FPR in validation geography produce higher mean test FPR in the original area/oracle arms; standardized test performance is not a demonstrated deployment guarantee.',
        ['analysis/scores.csv','analysis/tables/threshold-replay.md'],expected_replay,
        ['E41','E61'],False,'Check threshold transport using appropriate local validation and report achieved FPR beside patch recovery.')
    geographic={r['scope']:r['contrasts']['H1_interaction'] for r in s['secondary_condition_contrasts'] if r['scope'].startswith('leave_')}
    reviewed=json.loads((analysis/'review-response/summary.json').read_text())
    from freeze_expected import without_times
    add('C04','Whole-project transfer does not retain the within-project result: held-project-standardized interactions are uncertain, while the planned other-project-threshold replay gives a negative pooled embedding oracle-minus-area gain and widely varying achieved FPR. The replay is not a matched-FPR allocation effect.',
        ['analysis/summary.json','analysis/robustness/summary.json','analysis/tables/geographic-transfer.md','analysis/review-response/summary.json','analysis/tables/review-transfer-replay.md'],
        dict(held_project_standardized=geographic,planned_transfer_replay=reviewed['transfer_replay'],regional_mean_fpr_range=reviewed['transfer_regional_mean_fpr_range'],seed_fpr_range=reviewed['transfer_seed_fpr_range']),
        ['E46','E47','E48','E61','E68'],True,
        'Validate threshold transport with suitable local reference data before extending a within-project allocation result to an unrepresented project. The negative replay gain accompanies lower FPR and cannot isolate an allocation effect at fixed error rate.',
        scope='Four convenience held-region cases, each testing all16 held-region cores; original within split tested4cores per region. Transfer fits/replay were planned; extended conditional intervals and complete tabulation were added after the primary outcome/review. Models, maps and chosen thresholds fixed; no national inference.')
    add('C05','A deterministic one-cell cardinal translation retains a positive interaction in every direction on the shared restricted reference cohort; this does not cover the excluded patches or estimate actual reference error.',
        ['data/alignment-stress/summary.json','data/alignment-stress/cohort.json','data/alignment-stress/objects.csv'],
        {k:v for k,v in json.loads((ROOT/a.alignment/'summary.json').read_text()).items() if k!='completed_at_utc'},['E59','E60'],True,
        'The observed interaction is not erased by these synthetic offsets on retained patches; ecological accuracy and other positional errors remain unverified.',
        scope='Synthetic10m cardinal translations of existing reference center masks; common cohort selected from reference masks before loading scores; unchanged models and directional test quantiles; domain intersection excludes original no-score areas.')
    robustness=analysis/'robustness/summary.json'
    if robustness.exists():
        r=json.loads(robustness.read_text())['families']
        rotated=r['rotations_all']['conditional_contrasts']['standardized_0.05']['H1_interaction']
        rotation_count=int(pd.read_csv(analysis/'robustness/arm-means.csv').query("scope == 'rotations_all'").patches_per_seed.iloc[0])
        pooled=r['rotations_all']['conditional_contrasts']['standardized_0.05']
        add('C06',f"Pooling all fixed held-out rotations gives oracle-allocation gains for both predictors: embeddings {pooled['aef_oracle_gain']['estimate']*100:.1f} percentage points and optical {pooled['optical_oracle_gain']['estimate']*100:.1f}, with an interaction of {rotated['estimate']*100:.1f} across {rotation_count} eligible small patches. Optical gains in each added split, and each new-split interaction is smaller than the original; intervals omit split-selection uncertainty.",
            ['analysis/summary.json','analysis/robustness/summary.json','analysis/robustness/arm-means.csv','protocol/rotation-splits.json'],
            dict(cohort_families=r,per_split_contrasts={x['scope']:x['contrasts'] for x in s['secondary_condition_contrasts'] if x['scope'].startswith('rotation')}),
            ['E53','E56','E57','E61'],True,
            'Try patch-first allocation for both predictors within these inventory-owning workflows, and use the complete fixed-split results rather than treating the largest original interaction as a general effect. Overlapping training sets are not independent replication.',
            scope='Fixed rotations of the same64cores and reference maps; subgroup transfer retains its original wider-cohort threshold, so subgroup FPR need not equal5%.')
    exploratory={k:v for k,v in original.items() if any(token in k for token in ['proposal_aef','uncertainty_aef','uniform_aef','corematched','regionmatched']) and v.get('status')=='complete'}
    weighting={str(r['decoder']):r['contrasts'] for r in s['secondary_condition_contrasts'] if r['scope']=='within' and r['decoder']=='rf_noboot' and r['budget']==2000}
    nb=weighting['rf_noboot']
    add('C07',f"Inverse-component-size loss weights improve embedding recovery using the same area-sampled fitting positions: the truncated variant gains {nb['aef_weighted_area_cap10_gain']['estimate']*100:.1f} percentage points over its matched no-bootstrap area control, while its mean remains below the matched oracle.",
        ['analysis/summary.json','analysis/tables/weight-controls.md','analysis/fits.csv','analysis/allocation-audit.csv','data/results/weights'],
        {k:v for k,v in nb.items() if 'weighted_area' in k or k=='aef_oracle_gain'},
        ['E50','E52','E61'],True,
        'Existing-reference workflows can investigate loss weighting alongside point allocation. This establishes an improvement without new fitting positions under the no-bootstrap decoder; it does not decompose the original bootstrapped-forest effect or avoid the object frame.',
        scope='Exploratory v7; identical positions/labels, inverse common-valid component size, fixed truncation rule, matched RF bootstrapFalse comparators, five seeds. No annotation cost measured.')
    add('C08',f"Embedding-guided uncertainty improves embedding recovery by {original['aef_uncertainty_aef_gain']['estimate']*100:.1f} percentage points over the original balanced area baseline, while uniform-initialization image-guided policies also improve their natural-area baseline. The original optical-teacher failure cannot establish failure of all image-derived allocation.",
        ['analysis/summary.json','analysis/tables/embedding-proposals.md','analysis/tables/uniform-initialization.md'],
        {k:v for k,v in exploratory.items() if any(x in k for x in ['proposal_aef','uncertainty_aef','uniform_aef'])},
        ['E54','E61'],True,
        'Evaluate proposal predictors and initialization information explicitly; these are simulated query comparisons within a supplied land domain, not evidence of cheaper human annotation.',
        scope='Exploratory v7 stronger proposals and uniform initialization; original fixed RF/2,000-position budget/five seeds. Full inventory-derived scoring domain and label oracle remain available; no equivalence test against oracle performance.')
    add('C09',f"Matching oracle positive counts by training core improves the embedding area control by {original['aef_area_corematched_gain']['estimate']*100:.1f} percentage points, but leaves an oracle-minus-core-matched representation interaction of {original['oracle_vs_area_corematched_interaction']['estimate']*100:.1f} percentage points.",
        ['analysis/summary.json','analysis/tables/geographical-quotas.md','analysis/allocation-audit.csv'],
        {k:v for k,v in exploratory.items() if 'corematched' in k or 'regionmatched' in k},
        ['E55','E58','E61'],True,
        'Between-core mixture contributes in this diagnostic, while within-core sampling remains relevant. Do not add this gain to the weighting gain as though the controls formed an orthogonal causal decomposition.',
        scope='Exploratory v9, original primary decoder/split; exact oracle negative positions and oracle-derived positive geographical quotas, with uniform positive selection within groups. Privileged quota information is retained.')
    pixel=scores[(scores.scope=='within')&(scores.decoder=='rf')&(scores.budget==2000)&
        (scores.version=='raw')&(scores.condition=='standardized_0.05')&(scores.boundary_tolerance_m==0)&
        scores.policy.isin(['area','object'])&scores.representation.isin(['aef','optical'])]
    pixel_values={rep+'_'+policy:{column:float(part[column].mean()) for column in ['producer_accuracy','user_accuracy','iou','small_macro_recovery_50']}
        for (rep,policy),part in pixel.groupby(['representation','policy'])}
    add('C10','The original embedding area and oracle arms have near-constant observed pooled pixel producer accuracy and IoU while their region-macro small-patch recovery differs; this descriptive result is not a statistical equivalence test.',
        ['analysis/scores.csv','paper.md'],pixel_values,['E41','E61','E64','E65'],False,
        'Report patch outcomes beside area metrics: the observed small-patch change is not visible in those pooled area summaries alone.',
        scope='Preplanned descriptive pixel metrics at original standardized5% FPR; observed five-seed means. Area weights and region-macro patch weights differ; no general equivalence or absence of ecological cost is claimed.')
    add('C11','The preplanned operating-point and coverage sensitivities change the magnitude and interpretation of allocation differences: optical touches more small patches across the four fixed splits, while embeddings recover more at >=50% coverage. The original validation-replay interaction interval includes zero. Complete condition-specific tabulations were added after review.',
        ['analysis/review-response/summary.json','analysis/tables/review-definition-sensitivity.md','analysis/tables/review-rotation-replay.md','analysis/tables/review-patch-size.md','analysis/tables/review-pixel-secondary.md'],
        without_times(reviewed),['E68'],True,
        'Choose a coverage objective and examine threshold transport explicitly; no predictor dominates every patch/area metric or every geography in these data.',
        scope='Definitions planned in v1/v4/v6/v8; expanded summaries and intervals are review-prompted v11. Any/75% coverage and supplementary size/without-Vermont/three-new-split results are point estimates only; >=50% intervals use existing paired blocks. Fixed convenience projects/models/maps; no ecological completeness or causal smoothness claim.')
    for claim in claims:
        if claim['claim_id'] in ['C01','C04','C06']:
            claim['revision']=dict(review_points={'C01':['R1-1'],'C04':['R1-3'],'C06':['R1-1']}[claim['claim_id']],
                status_changed=False,reason='Numerical support retained; interpretation expanded/narrowed to represent component gains, split dependence and planned transfer replay.',response='review/response-1.md')
        elif claim['claim_id']=='C11':
            claim['revision']=dict(review_points=['R1-2'],new_claim=True,reason='Expose omitted preplanned sensitivity outcomes and review-prompted complete summaries.',response='review/response-1.md')
    (ROOT/a.out).write_text(''.join(json.dumps(c,ensure_ascii=False,allow_nan=False)+'\n' for c in claims))
    print(json.dumps({'claims':len(claims),'analysis':a.analysis}))

if __name__=='__main__':main()
