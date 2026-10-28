"""Create machine-readable descriptive claims from final numerical reports."""
import argparse
import json
from pathlib import Path

import pandas as pd

from record import ROOT
from summarize import clean

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();claims=[]
    def add(cid,text,evidence,expected,scope,implication,exploratory=False,status='supported',sources=(),experiments=()):
        claims.append({'claim_id':cid,'text':text,'status':status,'evidence_paths':evidence,'source_ids':list(sources),
                       'experiment_ids':list(experiments),'scope':scope,'verify':'Run the offline entry point in VERIFY.md; inspect the cited CSV/JSON rows. Numeric tolerance 1e-7; counts exact.',
                       'expected':expected,'exploratory':exploratory,'reader_implication':implication})
    ps=json.loads((ROOT/'results/primary/summary.json').read_text());w=pd.read_csv(ROOT/'results/primary/width-summary.csv')
    lead=w[(w['n_sites']==12)&(w['model']=='all')&(w['lead']=='all')&(w['geometry']=='all')]
    info=lead[lead['stratum']=='informative'].iloc[0];allrow=lead[lead['stratum']=='all'].iloc[0]
    scope='Exact empirical moments of sampled fifty-member 2026 ECMWF operational forecast laws, twelve-site regular portfolios at the two tested compact/dispersed spacings and stated temperature/capacity grid. Complete-date matching. Primary compatibility permits arbitrary real probability weights; fixed-size and perturbation checks have their stated extra assumptions. No observed-weather skill, calibration, health or realized economic effect measured.'
    add('C01','The sampled informative queries have the reported mean compatible-tail widths under individual, aggregate-second-moment and pairwise releases.',
        ['results/primary/width-summary.csv','results/primary/cases.csv','scripts/bounds.py'],
        {'matched_dates':ps['matched_dates'],'informative_cases':int(info['cases']),
         'mean_widths':{m:float(info[m+'_width']) for m in ['marginal','aggregate','pair']}},scope,
        'Check retained joint-event information for the actual query; individual probabilities alone may leave substantial ambiguity.',sources=['PRIOR-BOUNDS','redundancy-bounds-2009','TREE-BOUNDS-2021'])
    add('C02','All-case identification is affected by floor/ceiling probabilities and portfolios with few uncertain sites; the informative stratum has a separate denominator.',
        ['results/primary/width-summary.csv','results/primary/uncertainty-strata.csv'],
        {'all_cases':int(allrow['cases']),'q_zero':int(allrow['q_zero']),'q_one':int(allrow['q_one']),
         'at_most_two_uncertain':int(allrow['at_most_two_uncertain']),'pair_identified_all':int(allrow['pair_exact_count']),
         'pair_identified_informative':int(info['pair_exact_count'])},scope,
        'Do not interpret a high full-sample exact-identification fraction without checking simple-case composition.')
    add('C03','One aggregate second binomial moment captures the reported fraction of the marginal-to-pair interval narrowing in informative queries.',
        ['results/primary/width-summary.csv','results/primary/summary.json'],
        {'aggregate_reduction_share_ratio_of_sums':float(info['aggregate_reduction_share'])},scope,
        'A small aggregate release can be audited against the larger pair table, while the exact known-portfolio count distribution remains a stronger reference.')
    dec=pd.read_csv(ROOT/'results/primary/decision-summary.csv');part=dec[dec['model']=='all']
    add('C04','Information releases certify the reported fractions of illustrative binary actions across all sampled queries and the prespecified near-threshold strata.',
        ['results/primary/decision-summary.csv'],part[['stratum','cost_ratio','cases','ties','oracle_act_strict','oracle_skip_strict','marginal_certified','aggregate_certified','pair_certified']].to_dict('records'),
        scope+' Cost ratios 0.1, 0.25, 0.5; all queries plus abs(q-c)<=0.1 strata; weak optimality includes ties. Certification ignores evaluation-selection information. At c=0.1 the informative filter itself fixes a weakly optimal action; action-side counts are exploratory diagnostics.',
        'Probability ambiguity need not imply action ambiguity; certification depends on the decision threshold.')
    rec=pd.read_csv(ROOT/'results/primary/reconstruction-summary.csv');part=rec[(rec['availability']=='historical_matched')&(rec['stratum']=='informative')]
    add('C05','Point reconstructions have the reported errors against the original ensemble on a common informative availability set.',
        ['results/primary/reconstruction-summary.csv','scripts/summarize.py'],part[['method','cases','dates','mean_absolute_error']].to_dict('records'),
        scope+' Historical ranks come from earlier forecasts, not observed climatology; no optimized/calibrated reconstruction claim.',
        'A dependence assumption used to create a point probability has an information-retention error distinct from observed forecast skill.',sources=['PRIOR-ECC','PRIOR-MULTIVARIATE-GLOBAL'])
    sensitivity=ROOT/'results/sensitivity/summary.json'
    if sensitivity.exists():
        s=json.loads(sensitivity.read_text())
        add('C06','Exact-M integer comparisons completed for the reported cohort and statuses; unresolved solves are retained.',
            ['results/sensitivity/integer-summary.csv','results/sensitivity/integer-cases.csv','results/secondary-runs'],s['integer'],
            scope+' Up to 120 hash-selected informative queries; five-second integer limit per endpoint; only status 0 optimal.',
            'The main arbitrary-weight law class and a fixed-size equally weighted ensemble are different assumptions.')
        add('C07','Allowing small absolute changes in released individual and pair moments gives the reported larger compatible intervals in the selected cohort.',
            ['results/sensitivity/epsilon-summary.csv','results/sensitivity/epsilon-cases.csv','results/secondary-runs'],s['epsilon'],
            scope+' Same selected cohort; arbitrary-weight neighborhoods. Epsilon 0.005 and 0.02 are sensitivity sets, not confidence intervals or measured publication rounding. Known M=50 integer counts are unchanged at 0.005; see C19.',
            'Specify both the admissible law class and precision before transferring exact-moment sufficiency to imprecise moments.')
        add('C08','The fixed 10/25-member nested subsets yield the reported identification widths and their own informative denominators.',
            ['results/sensitivity/member-summary.csv','results/member-sensitivity'],s['members'],
            scope+' One seeded nested subset per forecast; informative strata and empirical laws change. The gradient persists in existing common-query/repeated-draw checks, but no causal decomposition, monotonicity theorem, M>50 or population-law guarantee is established.',
            'Finite ensemble support can affect the apparent adequacy of low-order information.')
    subsets=ROOT/'results/subsets/summary.json'
    if subsets.exists():
        s=json.loads(subsets.read_text());sw=pd.read_csv(ROOT/'results/subsets/width-summary.csv')
        r=sw[(sw['model']=='all')&(sw['query_size']=='all')&(sw['stratum']=='informative')].iloc[0]
        add('C09','Universe count curves and universe pair summaries have the reported non-universal empirical ordering for fixed subset queries.',
            ['results/subsets/width-summary.csv','results/subsets/cases.csv','protocol/subset-design-v3.json'],
            {'cases':int(r['cases']),'pair_width':float(r['pair_width']),'count_width':float(r['count_width']),
             'count_narrower':int(r['count_narrower_cases']),'pair_narrower':int(r['pair_narrower_cases']),'equal_width':int(r['equal_width_cases'])},
            scope+' Exploratory four/eight-site subset queries; all universe constraints retained. No universal dominance or optimal compression claim.',
            'A summary exact for one portfolio may be incomplete for a changed query; compare information sets relevant to reuse.',True)
        add('C10','A coherent fixed-threshold binary mask and query-specific count PMFs reproduce all tested queries exactly, with the stated simple format sizes.',
            ['results/subsets/summary.json','scripts/subset_bounds.py','experiments/V002-subset-validation'],
            {'encoding':s['encoding'],'oracle_max_absolute_error':s['oracle_max_absolute_error']},
            'Constructive identity and round-trip checks for M50,N12,one fixed temperature threshold; no novelty, optimal coding, transport measurement or arbitrary-threshold retention claim.',
            'Exact query-specific summaries and coherent binary rows are necessary comparators before recommending lossy low-order products.',True)
    city=ROOT/'results/city-time/summary.json'
    if city.exists():
        s=json.loads(city.read_text())
        evidence=['results/city-time/summary.json','results/city-time/width-summary.csv','results/city-time/paired-width-summary.csv']
        if (ROOT/evidence[1]).exists():
            cw=pd.read_csv(ROOT/evidence[1]);r=cw[(cw['model']=='all')&(cw['horizon']=='all')&(cw['stratum']=='common_informative')]
            add('C11','The city/time extension reports the paired information widths on its own matched common-informative sample.',evidence,
                {'matched_dates':s['matched_dates'],'status':s['status'],'rows':r[['portfolio_type','endpoint','cases','pair_width','aggregate_width','marginal_width']].to_dict('records')},
                'Exploratory fixed city/cartographic locations; four sampled-time maximum, not continuous daily maximum or simultaneous peak load. Shared forecast dates are not independent confirmation. Coarse-cell mask diagnostic is conditional.',
                'Check whether a summary audit transfers to a different spatial sample and time definition before generalizing it.',True,
                status='supported' if s['matched_dates']>=8 else 'partially_supported')
    coverage=ROOT/'results/coverage/summary.json'
    if coverage.exists():
        s=json.loads(coverage.read_text());add('C12','The recorded conservative missing-data envelopes bound full-schedule mean widths without assuming random missingness.',
            ['results/coverage/summary.json','results/coverage/missingness-widths.csv','protocol/plan-v5-coverage-robustness.md'],s['width_envelopes'],
            'Exploratory safe width-in[0,1] envelopes; unknown informative eligibility; not sharp feasible-weather bounds or resampling intervals.',
            'Separate uncertainty from unavailable forecast units from variation among the observed complete cases.',True)
    mechanism=ROOT/'results/identification/summary.json'
    if mechanism.exists():
        s=json.loads(mechanism.read_text());add('C13','Exact pair tails have the reported sufficient-condition classifications in the sampled binary systems.',
            ['results/identification/summary.json','results/identification/category-summary.csv','results/identification/cases.csv'],s['categories'],
            'Exploratory numerical rank/row-space diagnostics; mutually exclusive priority classes, no new theory; rank deficiency is not proof of nonuniqueness.',
            'Interpret apparent pairwise sufficiency alongside restrictions that already determine the law or event.',True,
            status='supported' if s['unit_count']==ps['complete_forecast_units'] else 'partially_supported')
    midpoint=ROOT/'results/midpoints/summary.json'
    if midpoint.exists():
        s=json.loads(midpoint.read_text());add('C14','Common-availability midpoint controls have the reported empirical reconstruction errors.',
            ['results/midpoints/midpoint-summary.csv','protocol/plan-v7-midpoint-controls.md'],s['rows'],
            scope+' Additional exploratory comparison conditions, same outcome definitions; no observed-weather skill claim.',
            'Wide compatible intervals need not imply comparably large observed point errors; separate information loss from the chosen reconstruction.',True)
    common=ROOT/'results/common-members/summary.json'
    if common.exists():
        s=json.loads(common.read_text());add('C16','The saved nested member subsets retain the reported width differences when query identities and informative eligibility are held common.',
            ['results/common-members/common-member-summary.csv','protocol/plan-v9-common-member-queries.md'],s['rows'],
            scope+' Exploratory after own-stratum summaries; same fixed nested selections, changed empirical laws, no causal size effect or repeated-sampling estimate.',
            'Changing informative-query composition alone does not account for the observed member-subset differences.',True)
    controlled=ROOT/'results/controlled-moments/summary.json'
    if controlled.exists():
        s=json.loads(controlled.read_text());add('C17','Pair-moment imprecision retains the reported ambiguity when individual probabilities and the aggregate moment are held exact.',
            ['results/controlled-moments/cases.csv','results/controlled-moments/width-summary.csv','protocol/plan-v10-controlled-moment-precision.md'],s['rows'],
            scope+' Exploratory controlled conditions added after the prespecified perturbation result; same frozen 120-case cohort; not statistical confidence or actual publication errors.',
            'The exact-pair sensitivity cannot be attributed solely to relaxing individual probabilities or the aggregate moment.',True)
    repeated=ROOT/'results/repeated-members/summary.json'
    if repeated.exists():
        s=json.loads(repeated.read_text());add('C18','Repeated nested member selections have the reported conditional draw variation on the fixed sensitivity cohort.',
            ['results/repeated-members/per-draw-summary.csv','results/repeated-members/width-summary.csv','results/repeated-members','protocol/plan-v11-repeated-member-draws.md'],
            {'completed_draws':s['completed_draws'],'status':s['status'],'rows':s['rows']},
            scope+' Exploratory 100-draw target; draws reuse finite M=50 inputs, not independent forecasts or population confidence; M=10 nested within M=25 and shared per forecast/query.',
            'Check whether apparent low-order sufficiency is sensitive to member selection before generalizing a small-subset audit.',True,
            status='supported' if s['completed_draws']==100 else 'partially_supported')
    ip=ROOT/'results/integer-precision/summary.json'
    if ip.exists():
        s=json.loads(ip.read_text());add('C19','The fixed-size moment-precision comparison has the reported lattice boundary, optimization completion and compatible-width bounds.',
            ['results/integer-precision/summary.json','results/integer-precision/cases.csv','results/integer-precision/raw','protocol/plan-v13-integer-moment-precision.md'],s,
            scope+' Exploratory interaction of separate original sensitivities. Radius 0.005 around exact M=50 moments admits no new integer counts; radius 0.02 allows one count. Unresolved optimum values are not substituted. Width envelopes use checked feasible witnesses and numerical backend bounds.',
            'Distinguish arbitrary-weight moment neighborhoods from uncertainty within a known equal-weight ensemble before transferring precision conclusions.',True,
            status='supported' if s['recorded_cases']==s['selected_cases'] else 'partially_supported')
    recovery=ROOT/'results/overlap-recovery/recovery.json'
    if recovery.exists():
        s=json.loads(recovery.read_text())
        if s['status']=='checks_passed':
            r=json.loads((ROOT/'results/overlap-recovery/summary/summary.json').read_text())
            add('C15','The separately labelled overlapping-extraction coverage check reproduces the retained original fields and yields the reported recovered-calendar coverage.',
                ['results/overlap-recovery/recovery.json','results/overlap-recovery/summary/summary.json','protocol/plan-v8-overlap-recovery.md'],
                {'original_members_compared':s['original_members_compared'],'matched_dates':r['matched_dates'],'new_raw_sha256':s['new_raw_sha256']},
                'Exploratory saved-v4-input reuse, original exclusion/attempt cap intact; unknown original fields cannot be checked for archive changes; not independent confirmation.',
                'Assess complete-case sensitivity using prospectively scheduled overlapping inputs without erasing the original failure.',True)
    review_summary=ROOT/'results/review-response/summary.json'
    if review_summary.exists():
        rs=json.loads(review_summary.read_text())
        add('C20','Post-review saved-data diagnostics report association between surviving binary states and identification, and separate interval width from threshold crossing.',
            ['results/review-response/summary.json','results/review-response/pruning-summary.csv','results/review-response/width-window-diagnostic.csv','protocol/plan-v14-review-response.md'],
            {'pruning':rs['pruning'],'median_observed_patterns_informative':rs['median_observed_patterns_informative'],'width_window':rs['width_window']},
            scope+' Bins and intersections fixed after REVIEW-1, before aggregation; descriptive association, no causal support attribution or general monotonicity claim.',
            'Assess exact-zero-cell and threshold-selection explanations before transferring pairwise near-identification or non-certification.',True)
    for claim in claims:
        if claim['claim_id'] in ['C01','C02','C03','C04','C08']:
            claim['revision_reason']='REVIEW-1: clarify exact finite-ensemble/two-spacing scope and report all prespecified action strata; no changed primary endpoint or status.'
            claim['review_response_reference']='review/response-1.md'
    with Path(a.output).open('w') as f:
        runs=[]
        for path in sorted((ROOT/'experiments').glob('*/record.json')):
            item=json.loads(path.read_text())
            if item.get('status') in ['completed','failed','timed_out']:runs.append(item)
        for claim in claims:
            if claim['claim_id'] in ['C01','C02','C03','C04','C05']:
                wanted=['scripts/summarize.py','scripts/pipeline.py','scripts/analyze_unit.py','scripts/report_bundle.py']
            elif claim['claim_id'] in ['C06','C07','C08']:wanted=['scripts/secondary.py','scripts/report_secondary.py']
            elif claim['claim_id'] in ['C09','C10']:wanted=['scripts/analyze_subsets.py','scripts/summarize_subsets.py','scripts/validate_subsets.py','scripts/pipeline.py']
            elif claim['claim_id']=='C11':wanted=['scripts/city_time_pipeline.py','scripts/summarize_city_time.py']
            elif claim['claim_id']=='C13':wanted=['scripts/identification_diagnostics.py']
            elif claim['claim_id']=='C14':wanted=['scripts/midpoint_controls.py','scripts/report_bundle.py']
            elif claim['claim_id']=='C15':wanted=['scripts/overlap_recovery.py']
            elif claim['claim_id']=='C16':wanted=['scripts/common_member_queries.py','scripts/report_bundle.py']
            elif claim['claim_id']=='C17':wanted=['scripts/controlled_moments.py']
            elif claim['claim_id']=='C18':wanted=['scripts/repeated_members.py']
            elif claim['claim_id']=='C19':wanted=['scripts/integer_precision.py']
            elif claim['claim_id']=='C20':wanted=['scripts/review_response_summary.py','scripts/report_bundle.py']
            else:wanted=['scripts/coverage_robustness.py','scripts/report_bundle.py']
            claim['experiment_ids']=[r['experiment_id'] for r in runs if any(s in r.get('command',[]) for s in wanted)]
            f.write(json.dumps(clean(claim),sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps({'claims':len(claims),'exploratory':sum(c['exploratory'] for c in claims)}))

if __name__=='__main__':main()
