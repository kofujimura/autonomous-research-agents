"""Render manuscript numbers and tables directly from saved analysis outputs."""
import argparse
import json
from pathlib import Path

import pandas as pd

from record import ROOT
from summarize import markdown_table

def number(x,digits=4):return 'undefined' if pd.isna(x) else f'{float(x):.{digits}f}'
def count(x):return f'{int(x):,}'
def percent(x):return 'undefined' if pd.isna(x) else f'{100*float(x):.1f}%'
def interval(row,mode):return f"{number(row[mode+'_width'])} [{number(row[mode+'_low'])}, {number(row[mode+'_high'])}]"
def calendar_date(value):return f'{value[:4]}-{value[4:6]}-{value[6:8]}'

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--root',default=str(ROOT));a=p.parse_args()
    root=Path(a.root);target=Path(a.output);design=json.loads((root/'protocol/design-v1.json').read_text())
    primary=root/'results/primary';ps=json.loads((primary/'summary.json').read_text())
    widths=pd.read_csv(primary/'width-summary.csv');decisions=pd.read_csv(primary/'decision-summary.csv')
    reconstruction=pd.read_csv(primary/'reconstruction-summary.csv')
    leading=widths[(widths['n_sites']==12)&(widths['lead']=='all')&(widths['geometry']=='all')]
    allrow=leading[(leading['model']=='all')&(leading['stratum']=='all')].iloc[0]
    info=leading[(leading['model']=='all')&(leading['stratum']=='informative')].iloc[0]
    S={}
    S['REPEATED_MEMBER_METHOD']=''
    S['INTEGER_PRECISION_METHOD']=''
    api_path=root/'api_calls.jsonl'
    if api_path.exists():
        calls={item['call_id']:item for item in map(json.loads,api_path.read_text().splitlines())}
        names=[f"`{item.get('model_returned') or 'identifier unconfirmed'}` on {item['requested_at_utc'][:10]} UTC"
               for item in calls.values() if item.get('status')=='completed']
        S['CRITIC_IDENTIFICATION']=("Topic selection consulted "+'; '.join(names)+
            ". These are provider-returned identifiers; the critique was consultation, not a numerical evaluation dataset or peer review.") if names else 'No completed topic-critique model identifier is available in this source.'
    else:S['CRITIC_IDENTIFICATION']='Topic-critique model records are not available in this source.'
    S['ABSTRACT_PRIMARY']=(f"Across {count(ps['matched_dates'])} matched initialization dates, {count(allrow['cases'])} twelve-site queries had mean identification interval widths "
        f"{number(allrow['marginal_width'])}, {number(allrow['aggregate_width'])} and {number(allrow['pair_width'])}, respectively. "
        f"Among all queries, {count(allrow['q_zero'])} reference probabilities were zero and {count(allrow['q_one'])} were one; {count(allrow['at_most_two_uncertain'])} queries had at most two uncertain sites. "
        f"In the {count(info['cases'])} prespecified informative queries, the corresponding widths were {number(info['marginal_width'])}, {number(info['aggregate_width'])} and {number(info['pair_width'])}; "
        f"pairs numerically identified {count(info['pair_exact_count'])} tails. The aggregate moment captured {percent(info['aggregate_reduction_share'])} of the marginal-to-pair interval narrowing in that stratum.")
    missing=[x for x in json.loads((primary/'availability.json').read_text()) if not x['complete']]
    S['DESIGN_AND_AVAILABILITY']=(f"The primary design scheduled {count(ps['scheduled_dates'])} initialization dates from {calendar_date(design['dates'][0])} to {calendar_date(design['dates'][-1])}, "
        f"two ensemble products, and leads {design['leads'][0]} and {design['leads'][1]} hours, giving {count(ps['scheduled_forecast_units'])} fifty-member forecast units. "
        f"Each unit contains twelve portfolios of twelve sites, three temperature thresholds and three capacity fractions. "
        f"The primary analysis uses {count(ps['matched_dates'])} dates for which all four product/lead units are complete, yielding {count(ps['primary_cases'])} queries. "
        f"Overall, {count(ps['complete_forecast_units'])} scheduled forecast units completed. The fixed adequate-date criterion was twelve. "
        f"The analysis status is `{ps['status']}`. Smaller portfolio analyses retain their separate denominators. "
        f"There {'was' if len(missing)==1 else 'were'} {count(len(missing))} unavailable scheduled {'unit' if len(missing)==1 else 'units'}; availability and every retained partial input are recorded. No replacement dates were selected.")
    main_table=[]
    for _,r in leading.iterrows():
        main_table.append({'system':r['model'],'stratum':r['stratum'],'n':count(r['cases']),
            'floors':f"{count(r['q_zero'])}/{count(r['q_one'])}",'simple':count(r['at_most_two_uncertain']),
            'marginal':interval(r,'marginal'),'aggregate':interval(r,'aggregate'),'pair':interval(r,'pair'),
            'identified':count(r['pair_exact_count'])})
    S['RESULTS_PRIMARY']=("### 4.1 Primary identification results\n\n"+
        f"Table 1 separates all queries from the informative stratum. Brackets are 95% date-block resampling intervals, not uncertainty about true weather probabilities. "
        f"For the informative stratum, the aggregate moment captured {percent(info['aggregate_reduction_share'])} of the total width reduction from margins to pairs, computed as a ratio of summed reductions. "
        "Nested tightening itself follows from the constraints; these numerical magnitudes and the case composition are the empirical outcomes.\n\n"+
        "**Table 1. Primary compatible probability widths.**\n\n"+
        markdown_table(main_table,[('system','Product'),('stratum','Stratum'),('n','N'),('floors','q=0 / q=1'),('simple','≤2 uncertain'),
            ('marginal','Marginal width [interval]'),('aggregate','Aggregate width [interval]'),('pair','Pair width [interval]'),('identified','Pair identified')])+"\n\n"+
        f"Across all available original analyses, the maximum checked primal residual was {ps['max_primal_residual']:.3g}, dual violation {ps['max_dual_violation']:.3g}, and primal–dual gap {ps['max_duality_gap']:.3g}. "
        "These are numerical checks, not independent validation. Figure 1 shows width distributions and identification by the number of uncertain sites.\n\n"+
        "![Primary information retention; annotations in panel C are query counts.](results/figures/primary-information.png)")
    dr=[]
    for _,r in decisions[decisions['model']=='all'].iterrows():
        dr.append({'stratum':{'all':'All','near_boundary':'Near threshold','informative_near_boundary':'Informative near threshold'}[r['stratum']], 'c':r['cost_ratio'],'n':count(r['cases']),'ties':count(r['ties']),
                   'act':count(r['oracle_act_strict']),'skip':count(r['oracle_skip_strict']),
                   **{mode:percent(r[mode+'_certified']) for mode in ['marginal','aggregate','pair']}})
    rec=reconstruction[(reconstruction['availability']=='historical_matched')&(reconstruction['stratum']=='informative')]
    rr=[{'method':r['method'],'n':count(r['cases']),'mae':number(r['mean_absolute_error']),
         'interval':f"[{number(r['mae_low'])}, {number(r['mae_high'])}]",'regret':number(r['regret_0.25'])} for _,r in rec.iterrows()]
    S['RESULTS_DECISIONS']=("### 4.2 Decisions and point reconstruction\n\n"+
        "Table 2 reports all queries, queries within 0.1 of each illustrative action threshold, and their informative subset. Ties admit either action. The overall rates answer how often a summary settles the sampled action; the boundary strata describe selected difficult queries. Certification concerns the empirical forecast law.\n\n"+
        "**Table 2. Release-only action certification, with all prespecified strata.**\n\n"+
        markdown_table(dr,[('stratum','Stratum'),('c','Cost ratio'),('n','N'),('act','q>c'),('skip','q<c'),('ties','q=c ties'),('marginal','Marginal certified'),('aggregate','Aggregate certified'),('pair','Pair certified')])+"\n\n"+
        "Large marginal intervals and selection near a threshold make low certification unsurprising. Their mean width alone does not imply non-certification: certification depends on whether the interval crosses the threshold. Appendix M reports a post-review width/window diagnostic, without changing the decision rule.\n\n"+
        "The action-side counts were added during the exploratory self-check. Because the informative filter requires q≥0.1, at cost ratio 0.1 the filter itself supplies a weakly optimal protective action for every included query. Certification here deliberately uses only released moments, not knowledge of that evaluation selection. The lowest-cost row therefore measures release-only certification on a one-sided evaluation set; it is not an operational error rate or evidence that a user supplied with the filter would remain uncertain.\n\n"+
        f"The historical baseline was unavailable for {count(ps['primary_historical_missing'])} primary queries before sufficient prior dates existed. "
        "Table 3 holds its availability set fixed for all point methods. Error and normalized expected regret are relative to the original ensemble; lower values do not establish more accurate weather forecasts.\n\n"+
        "**Table 3. Point reconstruction against the retained ensemble.**\n\n"+
        markdown_table(rr,[('method','Reconstruction'),('n','N'),('mae','Mean absolute error'),('interval','Resampling interval'),('regret','Expected regret at c=0.25')]))
    sensitivity=root/'results/sensitivity';sens=json.loads((sensitivity/'summary.json').read_text()) if (sensitivity/'summary.json').exists() else None
    if sens:
        eps={float(r['epsilon']):r for r in sens['epsilon']}
        S['ABSTRACT_SENSITIVITY']=(f"In the fixed {count(sens['expected_selected_cases'])}-query sensitivity cohort, allowing each individual and pairwise moment to change by 0.005 changed mean pair width from "
            f"{number(eps[0.0]['mean_width'])} to {number(eps[.005]['mean_width'])}. All {count(sens['expected_selected_cases'])} relaxed query sets have a positive-width floor by construction; these neighborhoods are not statistical confidence sets.") if .005 in eps and 0.0 in eps else 'The prespecified sensitivity analysis is incomplete.'
        S['RESULTS_SENSITIVITIES']=("### 4.3 Prespecified sensitivity checks\n\n"+
            f"The fixed hash ordering selected {count(sens['expected_selected_cases'])} informative queries. Integer and perturbation outputs were retained for {count(sens['integer_cases_recorded'])} and {count(sens['epsilon_cases_recorded'])} queries, respectively. "
            "Only solver status 0 is counted as an optimal integer result; unresolved cases are not assigned exact endpoints. Completed comparisons use their own stated denominators.\n\n"+
            "**Table 4. Exact fifty-member integer comparison.**\n\n"+
            (sensitivity/'table-integer.md').read_text()+"\n\n**Table 5. Arbitrary-weight moment neighborhoods.**\n\n"+(sensitivity/'table-epsilon.md').read_text()+"\n\n"+
            "Moment relaxation preserves the original empirical law as feasible, so widening is structurally expected; its size is the sensitivity outcome. For every query in this cohort, mixing the original law with all-zero or all-one states at weight epsilon changes each individual and pair probability by at most epsilon. These two feasible mixtures give an interval of width epsilon. Thus the loss of exact identification at positive tolerance is structurally required, not a separate empirical discovery. Allowances change deterministic margins and zero pair cells as well as nonzero moments. The prespecified check cannot attribute widening to one of those channels; the exploratory controlled comparisons address exact individual and aggregate information separately.\n\n"+
            "The nested member subsets below use one deterministic selection per forecast unit. Their informative strata are defined within each member subset and therefore differ in composition; these are not repeated-sampling estimates of the true forecast law.\n\n"+
            "**Table 6. One prescribed member subset per forecast.**\n\n"+
            (sensitivity/'table-members.md').read_text())
    else:
        S['ABSTRACT_SENSITIVITY']='The planned sensitivity analyses were not completed.'
        S['RESULTS_SENSITIVITIES']='### 4.3 Prespecified sensitivities\n\nThe planned sensitivities remain uncompleted; no results are asserted.'
    exploratory=[];appendix=[];subsets=root/'results/subsets'
    if (subsets/'summary.json').exists():
        ss=json.loads((subsets/'summary.json').read_text());sw=pd.read_csv(subsets/'width-summary.csv')
        ir=sw[(sw['model']=='all')&(sw['query_size']=='all')&(sw['stratum']=='informative')].iloc[0]
        S['ABSTRACT_EXPLORATORY']=(f"Exploratory subset queries found the parent portfolio's full count distribution gave narrower intervals than the pairwise table in {count(ir['count_narrower_cases'])} of {count(ir['cases'])} informative cases; "
            f"the pairwise table gave narrower intervals in {count(ir['pair_narrower_cases'])}. A coherent binary mask answers all tested fixed-threshold subset queries exactly by construction. "
            "No observed-weather skill, public-health benefit or practical traffic saving was measured.")
        e=ss['encoding']
        exploratory.append("### 4.4 Exploratory reuse for subset queries\n\n"+
            f"The subset extension includes {count(ss['matched_dates'])} matched dates and {count(ss['matched_cases'])} queries, of which {count(ss['informative_cases'])} meet the stronger informative criterion. "
            "Table 7 shows full and informative strata. Deterministic outside sites are separated because they make the full count curve a shifted query-specific count curve. This condition is stronger than a constant outside count observed only in the original ensemble.\n\n"+
            "**Table 7. Reusing the universe count distribution or pair table for subset queries.**\n\n"+
            (subsets/'table-subsets.md').read_text()+"\n\n"+
            f"The maximum oracle probability discrepancy was {ss['oracle_max_absolute_error']:.3g}. "
            "The count and pair information sets are non-nested; neither observed average nor narrower cases establish a universal ordering.\n\n"+
            f"For the fixed {count(e['members'])}-member, {count(e['universe_sites'])}-site binary problem, the simple fixed-width encodings require {count(e['coherent_mask_bits'])} bits ({count(e['coherent_mask_bytes'])} bytes) for coherent rows, "
            f"{count(e['pair_bits'])} bits ({count(e['pair_bytes'])} bytes) for margins and pairs, and {count(e['count_bits'])} bits ({count(e['count_bytes'])} bytes) for margins and the universe count curve. "
            "These are format calculations with round-trip checks, not measured network traffic or optimal coding. Count/mask sufficiency is known by construction, not a discovered weather result. A mask at one temperature threshold does not retain arbitrary other thresholds or raw temperatures.\n\n"+
            "![Exploratory subset information comparisons.](results/figures/subset-information.png)")
    else:S['ABSTRACT_EXPLORATORY']='Exploratory extensions were not completed. No observed-weather or health outcomes were evaluated.'
    city=root/'results/city-time'
    if (city/'summary.json').exists():
        cs=json.loads((city/'summary.json').read_text())
        if (city/'width-summary.csv').exists():
            cw=pd.read_csv(city/'width-summary.csv');cp=pd.read_csv(city/'paired-width-summary.csv')
            selected=cw[(cw['model']=='all')&(cw['horizon']=='all')&cw['stratum'].isin(['all','common_informative'])]
            ct=[]
            for _,r in selected.iterrows():
                ct.append({'type':r['portfolio_type'],'endpoint':r['endpoint'],'stratum':r['stratum'],'n':count(r['cases']),
                    'floors':f"{count(r['q_zero'])}/{count(r['q_one'])}",'simple':count(r['at_most_two_uncertain']),
                    'marginal':number(r['marginal_width']),'aggregate':number(r['aggregate_width']),'pair':number(r['pair_width'])})
            appendix.append("### A. City locations and four-time maximum (exploratory)\n\n"+
                f"The schedule contains {count(cs['scheduled_dates'])} dates and {count(4*cs['scheduled_dates'])} product/horizon combinations. "
                f"The boundary analysis completed {count(cs['complete_raw_forecast_units'])} raw fields and {count(cs['complete_horizons'])} combinations, with {count(cs['matched_dates'])} fully matched dates. "
                f"Its predefined adequacy threshold is {count(cs['minimum_matched_dates'])} matched dates and its status is `{cs['status']}`; adequacy does not imply completion of the full schedule. "
                f"Re-extracted original snapshots compared {count(cs['old_members_compared'])} member fields, with {count(cs['temperature_value_mismatches'])} value mismatches and {count(cs['grib_hash_mismatches'])} field-hash mismatches. "
                "These are extraction checks on overlapping forecasts, not new independent forecast samples.\n\n"+
                markdown_table(ct,[('type','Locations'),('endpoint','Time definition'),('stratum','Stratum'),('n','N'),('floors','q=0 / q=1'),('simple','≤2 uncertain'),('marginal','Marginal'),('aggregate','Aggregate'),('pair','Pair')])+"\n\n"+
                "Paired width differences, own informative strata and the all-cells-at-least-half-land conditional diagnostic are in the city/time numerical outputs. The latter is exploratory, uses one IFS mask, and does not remove any original locations. No increase in event probabilities from taking a maximum is interpreted as a discovery.\n\n"+
                "![Exploratory time definitions on the same informative query set.](results/figures/city-time-boundary.png)")
    coverage=root/'results/coverage'
    if (coverage/'summary.json').exists():
        cov=json.loads((coverage/'summary.json').read_text())
        appendix.append("### B. Coverage, weighting and resampling (exploratory)\n\n"+
            f"Of {count(cov['scheduled_primary_cases'])} fixed scheduled primary queries, {count(cov['missing_primary_cases'])} lack a complete original forecast unit. "
            "The following conservative envelopes use all known complete-unit rows, including otherwise unmatched dates, and permit every missing width in [0,1]. Informative eligibility of missing rows is unknown. These are missing-data envelopes, not resampling intervals or sharp feasible-weather bounds.\n\n"+
            (coverage/'table-missingness.md').read_text()+"\n\n"+
            "`weighting-summary.csv` reports equal-eligible-center means and leave-one-center-out ranges; `block-sensitivity.csv` reports block lengths 1, 3, 5. These describe sensitivity to a convenience design, not population inference. Center tables are descriptive and are not regional performance rankings.")
    mask=root/'data/cities/land-mask/summary.json'
    if mask.exists():
        ms=json.loads(mask.read_text())
        appendix.append("### C. Coarse-cell land fractions\n\n"+
            markdown_table(ms['groups'],[('portfolio_type','Locations'),('site_slots','Site slots'),('below_half_land','Land fraction <0.5'),('strictly_mixed','0 < land fraction <1'),('min_land_fraction','Minimum'),('max_land_fraction','Maximum')])+"\n\n"+
            "The diagnostic uses one IFS mask field. Repeated portfolio slots can represent the same cell. It does not verify AIFS surface classes or urban microclimates, and no locations were removed.")
    mechanisms=root/'results/identification'
    if (mechanisms/'summary.json').exists():
        ids=json.loads((mechanisms/'summary.json').read_text())
        appendix.append("### D. Sufficient explanations for identification (exploratory)\n\n"+
            f"The numerical rank diagnostic covers {count(ids['unit_count'])} available forecast units. The categories below are mutually exclusive in their displayed priority order. "
            "A constant event can also occur in a full-column-rank system, so the category count alone is not the total number of full-rank systems. Constant events are absent from the informative stratum by construction, because its empirical tail lies strictly between zero and one. Rank deficiency does not prove joint-law nonuniqueness under nonnegative constraints.\n\n"+
            (mechanisms/'table-categories.md').read_text()+"\n\n"+
            "These familiar sufficient conditions help interpret the observed exact tails; they are not new mathematical results or evidence of meteorological calibration.")
    midpoint=root/'results/midpoints/table-midpoints.md'
    if midpoint.exists():
        mr=pd.read_csv(midpoint.parent/'midpoint-summary.csv')
        mr=mr[(mr['availability']=='historical_matched')&(mr['stratum']=='informative')]
        marginal_control=mr[mr['mode']=='marginal'].iloc[0];pair_control=mr[mr['mode']=='pair'].iloc[0]
        extra=(f"On {count(marginal_control['cases'])} common informative queries, exploratory marginal-midpoint absolute error was {number(marginal_control['mean_absolute_error'])}, "
               f"versus {number(pair_control['mean_absolute_error'])} for the pair midpoint. Wide compatible intervals did not imply comparably large observed point errors. ")
        S['ABSTRACT_EXPLORATORY']=S['ABSTRACT_EXPLORATORY'].replace('No observed-weather',extra+'No observed-weather')
        appendix.append("### E. Additional midpoint controls (exploratory)\n\n"+
            "The following common-availability comparison applies the same interval-midpoint construction to each release. It complements the planned independence/historical/pair-midpoint table and prevents a poor independence choice from being conflated with every possible use of margins.\n\n"+midpoint.read_text())
    recovered=root/'results/overlap-recovery/recovery.json'
    if recovered.exists():
        rs=json.loads(recovered.read_text())
        if rs['status']=='checks_passed':
            rw=pd.read_csv(root/'results/overlap-recovery/summary/width-summary.csv')
            rw=rw[(rw['n_sites']==12)&(rw['model']=='all')&(rw['lead']=='all')&(rw['geometry']=='all')]
            rz=json.loads((root/'results/overlap-recovery/summary/summary.json').read_text())
            appendix.append("### F. Overlapping extraction coverage check (exploratory)\n\n"+
                f"All {count(rs['original_members_compared'])} retained original members agreed in selected values and global field hashes with the prospectively scheduled city extraction. The original cached index was reused for extraction; byte identity is a cache-consistency check, not a second archive retrieval. "
                f"The separately reconstructed calendar has {count(rz['matched_dates'])} matched dates. The original missing unit, two-invocation ledger and primary sample remain intact. Agreement cannot be checked for fields never observed originally. This is not independent confirmation.\n\n"+
                markdown_table(rw.to_dict('records'),[('stratum','Stratum'),('cases','N'),('marginal_width','Marginal'),('aggregate_width','Aggregate'),('pair_width','Pair'),('aggregate_reduction_share','Aggregate narrowing share')]))
    small=widths[(widths['n_sites'].isin([4,8]))&(widths['model']=='all')&(widths['lead']=='all')&(widths['geometry']=='all')]
    appendix.append("### G. Prespecified smaller portfolios\n\n"+
        "These fixed nested locations change portfolio size and spatial selection together. They do not isolate a pure size effect. All-case and informative denominators retain the original stratum definition.\n\n"+
        markdown_table(small.to_dict('records'),[('n_sites','Sites'),('stratum','Stratum'),('cases','N'),('q_zero','q=0'),('q_one','q=1'),('at_most_two_uncertain','≤2 uncertain'),('marginal_width','Marginal'),('aggregate_width','Aggregate'),('pair_width','Pair'),('pair_exact_count','Pair identified')]))
    common=root/'results/common-members/table-common-members.md'
    if common.exists():
        appendix.append("### H. Member counts on common query identities (exploratory)\n\n"+
            "Holding query identities fixed preserves the large difference in pairwise identification across these nested member selections. The common-informative set excludes empirical floor/ceiling tails and portfolios with fewer than four uncertain sites at any member size. The empirical moments and laws still differ, so this does not establish a pure causal size effect or repeated-sampling behavior.\n\n"+common.read_text())
    controlled=root/'results/controlled-moments/summary.json'
    if controlled.exists():
        cm=json.loads(controlled.read_text());cr=pd.read_csv(controlled.parent/'width-summary.csv')
        fixed=cr[(cr['epsilon']==.005)&(cr['condition']=='exact_margins_and_aggregate')].iloc[0]
        if not (root/'results/integer-precision/summary.json').exists():
            S['ABSTRACT_EXPLORATORY']=(f"An exploratory control holding individual and aggregate moments exact left mean width {number(fixed['mean_width'])} under the 0.005 pair allowance. "+S['ABSTRACT_EXPLORATORY'])
        display=cr.to_dict('records')
        for row in display:row['condition']={'exact_margins':'Individual probabilities','exact_margins_and_aggregate':'Individual probabilities and aggregate moment'}[row['condition']]
        appendix.append("### I. Controlled moment precision (exploratory)\n\n"+
            "These conditions were planned after the prespecified all-moments-relaxed result. Both retain exact individual probabilities; the second also retains the exact aggregate second binomial moment. Only pair probabilities have the displayed allowance. All binary states are restored. The same frozen cohort and LP tolerances are used, and interval nesting and empirical-law feasibility are checked.\n\n"+
            markdown_table(display,[('epsilon','Pair allowance'),('condition','Exact moments'),('cases','N'),('dates','Dates'),('mean_width','Mean width'),('identified','Identified')])+"\n\n"+
            "The sensitivity persists with individual and aggregate information held exact. This is a controlled mathematical comparison, not an attribution to one particular zero-cell channel or an estimated rounding, publication or sampling-error process.")
    repeated=root/'results/repeated-members/summary.json'
    if repeated.exists():
        rs=json.loads(repeated.read_text())
        S['REPEATED_MEMBER_METHOD']=(f"A further exploratory selection check planned {count(rs['planned_draws'])} nested member draws and completed {count(rs['completed_draws'])}. "
            "Each draw samples ten and twenty-five members without replacement from the original fifty, sharing one nested permutation across all queries from the same forecast. "
            "The same frozen sensitivity cohort is retained. Both all fixed query identities and common informative identities are summarized. "
            "The stated draw quantiles describe conditional selection variation in this fixed finite dataset, not confidence about weather probabilities or additional independent forecasts.")
        appendix.append("### J. Repeated member selections (exploratory)\n\n"+
            f"The prospective stopping target was {count(rs['planned_draws'])} draws; {count(rs['completed_draws'])} completed, status `{rs['status']}`. "
            "The table reports the mean of per-draw means and the 2.5th/97.5th percentiles of those means, with denominators per draw. Forecasts and query identities are reused; the draw count is not an independent forecast sample size. "
            "M50 rows reuse saved original endpoints. The changed smaller empirical laws prevent a pure causal size interpretation.\n\n"+
            (repeated.parent/'table-repeated-members.md').read_text())
    ip=root/'results/integer-precision/summary.json'
    if ip.exists():
        ir=json.loads(ip.read_text())
        S['INTEGER_PRECISION_METHOD']=("An exploratory interaction check recognizes that probabilities from exactly fifty equally weighted members are multiples of 0.02. "
            "A 0.005 allowance around their exact observed individual and pair probabilities therefore admits no changed count; it leaves the exact-count integer feasible set unchanged. "
            "The original optimal integer endpoints are reused for that structural comparison. At radius 0.02 we instead solve new integer problems with each moment count allowed to differ by one, retaining the original five-second endpoint limit. "
            "Incumbent/dual bounds give all-case width envelopes when exact optimization is unresolved. Replacing an event row by all zeros or a non-event row by all ones supplies a structural 0.04 width floor in this informative cohort, checked from source arrays. These facts are class/precision boundaries, not new mathematical discoveries or measured publication processes.")
        appendix.append("### K. Known ensemble size and moment precision (exploratory)\n\n"+
            f"The 0.005 condition is lattice-equivalent to exact counts for all {count(ir['epsilon005_lattice_equivalent_cases'])} selected queries. "
            "The 0.02 condition has a one-row-replacement width floor of 0.04 for every selected query with both empirical outcomes. These are structural facts. The table separates reused exact-count optima from new time-limited solves and reports bounds on the mean over every recorded case, so unresolved optimization is not silently excluded.\n\n"+
            (ip.parent/'table-integer-precision.md').read_text()+"\n\n"+
            f"Of {count(ir['recorded_cases'])} new query pairs, {count(ir['optimal_cases'])} had both endpoints optimal and {count(ir['unresolved_cases'])} remained unresolved. "
            f"The optimal-case mean width was {number(ir['epsilon02_optimal_mean_width'])}; its denominator differs from the all-case envelope above. "
            "These floating-point solver bounds and separately checked feasible integer witnesses are not formal exact-arithmetic proofs.\n\n"+
            "![The same fixed cohort under arbitrary weights and known M=50. Purple segments are optimization bounds on the all-case mean width, not confidence intervals; no intermediate radii were measured.](results/figures/moment-sensitivity.png)")
        S['ABSTRACT_EXPLORATORY']=S['ABSTRACT_EXPLORATORY'].replace('No observed-weather',
            f"An exploratory fixed-size check shows that 0.005 admits no changed moment counts for all {count(ir['epsilon005_lattice_equivalent_cases'])} queries. At 0.02, the all-case mean width was bounded by {number(ir['epsilon02_mean_width_lower_bound'])} and {number(ir['epsilon02_mean_width_upper_bound'])}; {count(ir['unresolved_cases'])} queries had an unresolved endpoint. No observed-weather")
    S['ABSTRACT_EXPLORATORY']=S['ABSTRACT_EXPLORATORY'].replace('No observed-weather',f"An exploratory self-check notes that the informative filter itself fixes a weakly optimal action at cost ratio 0.1 for all {count(info['cases'])} informative queries; certification uses only the released moments. No observed-weather")
    # Post-review reporting: primary quantities remain in their original strata.
    member_rows=pd.read_csv(sensitivity/'member-summary.csv')
    mi=member_rows[member_rows['stratum']=='informative'].sort_values('members')
    member_gradient=' / '.join(number(r['pair_width']) for _,r in mi.iterrows())
    member_denominators=' / '.join(count(r['cases']) for _,r in mi.iterrows())
    overall_dec=decisions[(decisions['model']=='all')&(decisions['stratum']=='all')].sort_values('cost_ratio')
    near_dec=decisions[(decisions['model']=='all')&(decisions['stratum']=='informative_near_boundary')].sort_values('cost_ratio')
    rates=lambda frame,mode:' / '.join(percent(r[mode+'_certified']) for _,r in frame.iterrows())
    rate_range=lambda frame,mode:percent(frame[mode+'_certified'].min())+'–'+percent(frame[mode+'_certified'].max())
    S['ABSTRACT_PRIMARY']=(f"Across {count(ps['matched_dates'])} matched initialization dates and {count(allrow['cases'])} twelve-site queries, mean compatible probability widths were "
        f"{number(allrow['marginal_width'])} / {number(allrow['aggregate_width'])} / {number(allrow['pair_width'])} in that release order; "
        f"{count(allrow['q_zero'])} reference tails were zero, {count(allrow['q_one'])} were one, and {count(allrow['at_most_two_uncertain'])} queries had at most two uncertain sites. "
        f"The {count(info['cases'])} prespecified informative queries had widths {number(info['marginal_width'])} / {number(info['aggregate_width'])} / {number(info['pair_width'])}; "
        f"pairs numerically identified {count(info['pair_exact_count'])} tails and the aggregate captured {percent(info['aggregate_reduction_share'])} of marginal-to-pair narrowing. "
        f"Across illustrative cost–loss ratios 0.1, 0.25 and 0.5, margins certified {rate_range(overall_dec,'marginal')} of all {count(allrow['cases'])} queries at each ratio, versus {rate_range(overall_dec,'aggregate')} for the aggregate and {rate_range(overall_dec,'pair')} for pairs. "
        f"Among informative queries within 0.1 of those thresholds (N={' / '.join(count(r['cases']) for _,r in near_dec.iterrows())}, in cost-ratio order), certification ranged from {rate_range(near_dec,'marginal')} for margins, {rate_range(near_dec,'aggregate')} for the aggregate and {rate_range(near_dec,'pair')} for pairs. At ratio 0.1 the informative filter itself fixes a weakly optimal action; certification uses only released moments.")
    S['ABSTRACT_SENSITIVITY']=(f"Pair near-identification is conditional on exact moments of the fifty-member empirical law. With 10 / 25 / 50 members, informative-stratum pair widths were {member_gradient} "
        f"(N={member_denominators}; the empirical laws and informative strata differ). "
        f"In the fixed {count(sens['expected_selected_cases'])}-query cohort, an arbitrary-weight moment allowance of 0.005 raised pair width from {number(eps[0.0]['mean_width'])} to {number(eps[.005]['mean_width'])}; "
        "these neighborhoods are not confidence sets. Compact and dispersed portfolios differ substantially; transfer to larger ensembles or other spacings was not tested.")
    S['ABSTRACT_EXPLORATORY']=("Exploratory controls distinguish interval ambiguity from midpoint error and show that the same 0.005 allowance changes no moment counts when exactly fifty equal-weight members are required. "
        "No observed-weather skill, health benefit, realized economic value or network saving was measured.")
    review_results=root/'results/review-response'
    if (review_results/'summary.json').exists():
        rs=json.loads((review_results/'summary.json').read_text())
        strata=pd.read_csv(review_results/'geometry-lead-summary.csv')
        pooled=strata[(strata['model']=='all')&(strata['stratum']=='informative')]
        S['RESULTS_PRIMARY']+=(f"\n\nPrespecified geometry and lead strata show heterogeneity: informative pair widths range from {number(pooled['pair_width'].min())} to {number(pooled['pair_width'].max())} across geometry × lead cells. "
            "Appendix L reports all widths, aggregate narrowing shares and identified counts by geometry, lead and product for both strata. Pooled values apply to the two tested spacings, rather than arbitrary region sizes.")
        appendix.append("### L. Prespecified geometry, lead and product strata\n\nThe following strata were specified in plan v1 and are now displayed rather than only bundled as CSV. Aggregate shares are ratios of summed narrowing, within each row.\n\n"+(review_results/'table-geometry-lead.md').read_text())
        diag=pd.read_csv(review_results/'width-window-diagnostic.csv')
        appendix.append("### M. Surviving states and threshold position (post-review exploratory)\n\n"+
            f"In the informative primary stratum, the median number of distinct member patterns was {number(rs['median_observed_patterns_informative'],0)}. "
            "The bins below were fixed after review and before aggregation. Fewer surviving states are associated with more identification. Exact zero pair cells rule out states, but pattern count alone does not determine a count-tail bound; this association does not quantify a causal share attributable to finite support.\n\n"+
            (review_results/'table-pruning.md').read_text()+"\n\nA marginal width greater than 0.2 is compared with the ±0.1 evaluation window below. The intersection with certified intervals shows why width alone is insufficient to infer threshold crossing.\n\n"+
            markdown_table(diag.to_dict('records'),[('cost_ratio','Cost ratio'),('stratum','Stratum'),('cases','N'),('wide_cases','Width >0.2'),('certified_cases','Marginal certified'),('wide_and_certified','Both')]))
    S['RESULTS_EXPLORATORY']='\n\n'.join(exploratory)
    S['APPENDIX_RESULTS']='\n\n'.join(appendix) or 'No additional completed analyses.'
    S['DISCUSSION_RESULTS']=(f"In this sampled informative stratum, pairwise information left a mean compatible width of {number(info['pair_width'])}, "
        f"compared with {number(info['marginal_width'])} from margins alone. That empirical narrowing must be read beside the {count(info['cases'])}-query denominator, "
        "the all-case floor/ceiling composition and the moment/member sensitivities. Numerical identification in a finite ensemble is a statement about exact supplied moments, not a guarantee under rounded, estimated or future forecast distributions.")
    if midpoint.exists():
        S['DISCUSSION_RESULTS']+=(f" The exploratory midpoint controls qualify a practical interpretation: on their common informative set, marginal-only midpoint absolute error was {number(marginal_control['mean_absolute_error'])}, "
            f"and pair-midpoint error {number(pair_control['mean_absolute_error'])}. These observed errors describe one original ensemble per query, whereas compatibility ranges concern every law meeting the release. "
            "A lack of certification therefore does not show that all marginal-only point reconstructions perform poorly on the sampled queries or that a real operational shortfall has been measured.")
    S['DISCUSSION_RESULTS']+=(" The within-study increase in pair widths from ten to twenty-five to fifty members makes wider intervals plausible for larger ensembles or smoother forecast laws, but neither was tested. "
        "The results should not be assumed to transfer to the thousand-member products discussed in the conference abstract [4]. The common-query and repeated-draw checks retain the gradient while changing empirical laws; they do not establish a general monotonicity theorem or isolate a causal support effect.")
    if (subsets/'summary.json').exists():
        S['PRACTICAL_ENCODING']=(f"At one fixed threshold for {count(e['members'])} members and {count(e['universe_sites'])} sites, the aligned binary member mask uses {count(e['coherent_mask_bits'])} bits, "
            f"only {percent(e['coherent_mask_bits']/e['pair_bits']-1)} more than the {count(e['pair_bits'])}-bit margins-plus-pairs table, while answering every fixed-threshold subset query exactly. "
            f"For one fixed portfolio, margins plus its full count curve use {count(e['count_bits'])} bits and answer every count threshold exactly. These are specified fixed-width formats; headers, compression and measured network traffic are excluded. A mask does not preserve other temperature thresholds.")
    else:S['PRACTICAL_ENCODING']='Encoding comparisons remain incomplete.'
    S['REVIEW_STATUS']=('A review by an AI agent was supplied by the human as REVIEW-1. It reports same-machine re-runs and a separately written primary LP check; these are not independent reproduction. The pointwise response is in `review/response-1.md`.' if (root/'review/review-1.md').exists() else 'A review by another AI agent is planned after this first draft and has not yet been received.')
    verification=root/'review/verification-summary.json'
    if verification.exists():
        v=json.loads(verification.read_text());S['VERIFICATION_RESULT']=(f"The author ran the documented `{v['mode']}` procedure in a fresh working copy: status `{v['status']}`. "
            "This is an author re-run, not independent reproduction. The verification report states which costly LPs were re-solved and which saved outputs supplied aggregate recomputation.")
    else:S['VERIFICATION_RESULT']='The end-to-end author verification is not yet completed; this manuscript is not ready for submission.'
    urls=[]
    for line in (root/'sources.jsonl').read_text().splitlines():
        item=json.loads(line)
        if item.get('path') in ['literature/aifs-data-specification.html','literature/ecmwf-general-terms.html','literature/ecmwf-open-data.html','literature/ecmwf-model-cycle-history.html','literature/ecmwf-joint-upgrade-2026.html'] and item.get('url'):
            urls.append(f"[Official archived source]({item['url']})")
    S['ECMWF_OFFICIAL_LINKS']=', '.join(dict.fromkeys(urls))
    text=(root/'manuscript/paper-template.md').read_text()
    text=text.replace('<!-- Working manuscript template. Numerical blocks are generated from analysis\noutputs by the rendering script; this is not a submitted or completed paper. -->\n','')
    for key,value in S.items():text=text.replace('{{'+key+'}}',value)
    assert '{{' not in text,'Unrendered manuscript placeholder'
    target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text)
    (target.parent/'paper-numbers.json').write_text(json.dumps({'primary_summary':ps,'abstract_primary':S['ABSTRACT_PRIMARY'],'abstract_sensitivity':S['ABSTRACT_SENSITIVITY'],'abstract_exploratory':S['ABSTRACT_EXPLORATORY']},indent=2)+'\n')
    print('Manuscript rendered from analysis artifacts:',target)

if __name__=='__main__':main()
