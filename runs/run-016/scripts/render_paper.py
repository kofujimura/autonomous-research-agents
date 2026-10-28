"""Render manuscript numbers and claim expectations from recorded outputs only."""
import argparse,json,re
from pathlib import Path
import numpy as np,pandas as pd
from records import ROOT,now,digest

def read(path):return pd.read_csv(ROOT/path)
def obj(path):return json.loads((ROOT/path).read_text())
def one(dataframe,**filters):
    for key,value in filters.items():dataframe=dataframe[dataframe[key]==value]
    assert len(dataframe)==1,(filters,len(dataframe))
    return dataframe.iloc[0]
def f(value,digits=4):return f'{float(value):.{digits}f}'
def pct(value,digits=1):return f'{100*float(value):.{digits}f}%'
def count(value):return f'{int(value):,}'
def pretty(label):
    if label.startswith('reference-'):return 'Direct reference'
    return label.replace('logistic_hard_auxiliary','Hard auxiliary LR').replace('logistic','LR').replace('forest','RF').replace('-broad','').replace('-fine','').replace('-frozen','').replace('-refreshed',' refreshed').replace('-tessera',' + TESSERA').replace('-alphaearth',' + AlphaEarth')
def table(frame,columns):
    # Each specification is (column, printed heading, final-display formatter).
    header='| '+' | '.join(x[1] for x in columns)+' |'
    lines=[header,'| '+' | '.join('---' for _ in columns)+' |']
    for _,row in frame.iterrows():
        lines.append('| '+' | '.join(formatter(row[key]) for key,_,formatter in columns)+' |')
    return '\n'.join(lines)

def render(destination):
    out=Path(destination)
    if not out.is_absolute():out=ROOT/out
    out.mkdir(parents=True,exist_ok=True);(out/'manuscript').mkdir(exist_ok=True)
    main=read('results/tables/main/audit-performance.csv');ratios=read('results/tables/main/pairing-mse-ratios.csv')
    cases=read('results/tables/main/case-counts.csv').iloc[0];description=obj('results/description-main/summary.json')
    splits={r['split']:r for r in description['split_descriptions']}
    at128=main[(main.subset=='all')&(main.n==128)]
    direct={d:one(at128,label='reference-broad',design=d) for d in ['paired','independent']}
    assisted={r:one(at128,label=f'logistic-broad-frozen-{r}',design='paired') for r in ['tessera','alphaearth']}
    zero=one(read('results/tables/main/point-estimates.csv'),tag='logistic-broad-frozen-tessera',method='no_change')
    direct_ratios=ratios[(ratios.label=='reference-broad')&(ratios.subset=='all')]
    c=int(cases.units);land=int(cases.landscapes);arable=obj('results/stable-arable/analysis.json')
    arable_summary=read('results/stable-arable/summary.csv');ac=read('results/stable-arable/case-counts.csv')
    ap=one(arable_summary,taxonomy='broad',design='paired',n=128);ai=one(arable_summary,taxonomy='broad',design='independent',n=128)
    sparse=one(read('results/sparse/tessera/summary.csv'),n=128)
    gradient=read('results/gradient/broad-tessera/summary.csv')
    gradlo=one(gradient,method='model_assisted',design='paired',gradient_floor=.01)
    gradhi=one(gradient,method='model_assisted',design='paired',gradient_floor=1e-10)
    panel=read('results/coherent-panel/summary.csv')
    half=one(panel,label='direct',design='half_retained',interval='pointwise')
    census=obj('results/census-comparison/summary.json')
    old=[];revised=[]
    for tax in ['broad','fine']:
        for rep in ['tessera','alphaearth']:
            old.append(obj(f'results/source-models/logistic-{tax}-{rep}/fit.json'))
            revised.append(obj(f'results/source-models-v2/logistic-{tax}-{rep}/fit.json'))
    initial_failed=sum(bool(x['fit_records'][0]['convergence_warnings']) for x in old)
    refreshed=[f'results/inference/logistic-broad-refreshed-{rep}' for rep in ['tessera','alphaearth']]
    refresh_complete=all((ROOT/path/'analysis.json').exists() for path in refreshed)
    api_latest={r['call_id']:r for r in map(json.loads,(ROOT/'api_calls.jsonl').read_text().splitlines())}
    critic=next(iter(api_latest.values()))
    critic_identifier=critic['model_returned'];critic_date=critic['requested_at_utc'][:10]
    values={
      'BUDGET_LIST':'32,64,128,256 or512','TEST_LANDSCAPES':str(land),'PRIMARY_UNITS':str(c),'ILLUSTRATIVE_BUDGET':'128',
      'PRIMARY_RESULT_SENTENCES':f"Revisited direct sampling had {f(direct_ratios.paired_independent_mse_ratio.min(),3)}–{f(direct_ratios.paired_independent_mse_ratio.max(),3)} times the mean squared error of independent annual sampling across the prespecified budgets. At the prespecified illustrative budget of128 labels/year, its RMSE was {f(direct['paired'].rmse)} versus {f(direct['independent'].rmse)} entropy units; the no-change point baseline was lower at {f(zero.rmse)}.",
      'INTERVAL_RESULT_SENTENCES':f"Direct intervals covered {pct(direct['paired'].coverage)} of changes with revisiting versus {pct(direct['independent'].coverage)} with independent sampling. Revisited direct samples reported directions in {pct(direct['paired'].report_rate)} of trials and wrong directions in {pct(direct['paired'].wrong_report_rate)}, versus {pct(direct['independent'].report_rate)} and {pct(direct['independent'].wrong_report_rate)} independently. Under the original clipped-gradient rule, frozen soft-logistic assisted intervals covered {pct(min(x.coverage for x in assisted.values()))}–{pct(max(x.coverage for x in assisted.values()))}, but reported a direction in only {pct(min(x.report_rate for x in assisted.values()))}–{pct(max(x.report_rate for x in assisted.values()))} of trials",
      'TINY_CHANGE_COUNT':str(int(cases.tiny_change)),'FLOOR_COUNT':str(int(cases.entropy_floor)),
      'CENSUS_ABSTRACT_IF_COMPLETED':f"There were {int(cases.zero_change)} exact zero changes and {int(cases.labels_unchanged_all)} contrasts with all labels unchanged, with {int(cases.single_group_either_year)} single-group cases; {int(cases.grassland_dominated_landscapes)} landscapes were grassland-dominated and {int(cases.arable_dominated_landscapes)} arable-dominated. Exploratory boundary checks changed the interpretation: on stable arable land in {int(one(ac,taxonomy='broad').landscapes)} landscapes, direct coverage was {pct(ap.coverage)} and {pct(ai.coverage)}; soft-assisted coverage and reporting depended strongly on the numerical gradient floor.",
      'SWISS_REVISION':obj('data/population-main-v1.json').get('dataset_revision','5e68643e82aecd5716c2eab69fcf8b5f87d44c78'),
      'YEAR_RANGE':'2021–2025',
      'TAXONOMY_COUNTS_SENTENCE':f"The primary level contains {description['broad_taxonomy_groups']} agricultural groups and the finer level {description['fine_taxonomy_groups']}.",
      'SELECTION_COUNTS_SENTENCE':f"The fixed quotas were reached after {description['attempted_distinct_candidates']} distinct candidate attempts: {splits['train']['landscapes']} training, {splits['calibration']['landscapes']} calibration and {splits['test']['landscapes']} test landscapes.",
      'FINAL_POPULATION_SENTENCE':f"All test landscapes were retained, with {count(splits['test']['finite_population_points'])} locations in total and {count(splits['test']['minimum_points'])}–{count(splits['test']['maximum_points'])} per landscape. Training used {count(splits['train']['finite_population_points'])} source-year labels and calibration {count(splits['calibration']['finite_population_points'])}; those labels are outside the target-audit budget. The minimum test–training footprint gap is {count(description['minimum_test_train_gap_m'])}m and the median nearest-training gap {count(description['median_test_train_gap_m'])}m; supercell assignment does not establish full spatial independence.",
      'TESSERA_IDENTIFIER':'TESSERA v1.1-dclimate (model URI https://geotessera.org/model/1.1)',
      'AEF_IDENTIFIER':'AlphaEarth Foundations, public tge-labs/aef/v1/annual mirror',
      'REPRESENTATION_DIMENSIONS':'128 and64',
      'INPUT_VALIDATION_SENTENCE':'A second Zarr decoder matched the manually decoded label data. Every saved point-to-native-grid check in the three selected full-grid cases matched exactly; these checks establish adapter consistency, not independent verification of field registration.',
      'LOGISTIC_MAX_ITER':str(revised[0]['parameters']['max_iter']),'INITIAL_LOGISTIC_MAX_ITER':str(old[0]['parameters']['max_iter']),
      'INITIAL_NONCONVERGED_FITS':str(initial_failed),'SOURCE_FIT_COUNT':str(len(old)),
      'CLASSIFIER_DIAGNOSTICS_SENTENCE':f"The broad source classifiers observed {len(revised[0]['fit_records'][0]['classes'])} of {len(revised[0]['class_names'])} groups; the finer classifiers {len(revised[2]['fit_records'][0]['classes'])} of {len(revised[2]['class_names'])}. Their calibration matrices had ranks {revised[0]['calibration']['rank']} and {revised[2]['calibration']['rank']}, respectively, so unconstrained full-taxonomy identifiability is not established.",
      'COMPLETED_ROBUSTNESS_METHODS':robustness_methods(refresh_complete),
      'DEVIATIONS_SENTENCE':'After two diagnostic target units, exploratory plans added sparse-change, jackknife, stratified-sampling and prediction-weight checks. Later full-cohort results motivated hard auxiliary predictions, a stable-arable frame, a coherent rotating panel and numerical-gradient sensitivity. Original comparisons were retained; the timing and reasons are listed in protocol/deviations.md.',
      'CENSUS_LIMITATION_SENTENCE':f"the prospective native-grid check includes only {census['cases']} cases and {census['primary_transitions']} transitions, while the reference-only whole-support checks cover the original landscapes but supply no new geography",
      'CRITIC_MODEL':f'{critic_identifier}, reasoning effort xhigh, used on {critic_date}',
      'REMAINING_UNFINISHED_CHECKS':('The refreshed-head diagnostic was completed with an additional source-training label burden, detailed in the results.' if refresh_complete else 'The refreshed-head comparison remains unfinished while later training features are acquired; no refreshed result is asserted in this working draft.'),
    }
    values['RESULTS_GENERATED_TABLES_AND_TEXT']=results_sections(main,at128,ratios,cases,zero,description,sparse,arable_summary,gradient,panel,census,refresh_complete)
    values['DISCUSSION_WRITTEN_AFTER_RESULTS']=discussion()
    values['APPENDICES_AND_PROCESS_DISCLOSURE']=appendices(description,refresh_complete)
    geo=additional_geography()
    projection=projection_comparison()
    values['ADDITIONAL_GEOGRAPHY_METHODS']=geo['methods']
    values['ADDITIONAL_GEOGRAPHY_ABSTRACT']=geo['abstract']
    values['PROJECTION_METHODS']=projection['methods']
    values['PROJECTION_ABSTRACT']=projection['abstract']
    values['RESULTS_GENERATED_TABLES_AND_TEXT']+='\n\n'+projection['results']+'\n\n'+geo['main']
    values['CENSUS_LIMITATION_SENTENCE']+=geo['limitation']
    values['APPENDICES_AND_PROCESS_DISCLOSURE']+='\n\n'+geo['results']+'\n\n'+projection['appendix']
    from review_revision import fields
    review_fields=fields();values.update(review_fields)
    values['RESULTS_GENERATED_TABLES_AND_TEXT']=values['RESULTS_GENERATED_TABLES_AND_TEXT'].replace('### 4.2.',review_fields['REVIEW_EARLY']+'\n\n### 4.2.',1)
    values['RESULTS_GENERATED_TABLES_AND_TEXT']+='\n\n'+review_fields['REVIEW_RESULTS']
    values['DISCUSSION_WRITTEN_AFTER_RESULTS']=review_fields['REVIEW_DISCUSSION']
    values['APPENDICES_AND_PROCESS_DISCLOSURE']+='\n\n'+review_fields['REVIEW_APPENDIX']
    template=(ROOT/'manuscript/template.md').read_text()
    cited=['CROP-FITNESS2026','TESSERA2025','AEF2025','OLOFSSON2014','ROTATION-SAMPLE1981','LI2014','LIPTON2018','MASSEY2015','SENEGAL2026','PANINSKI2003','PPI-PLUS','STRAT-PPI2024','CLUSTER-PPI2026','SWISSCROP25','SWISSCROP25-CARD','AUDENAERT2007','SCIPY-HYPERGEOM','SIMPLEX-JACOBIAN2016','FANG-SANTOS2019','JESSEN1942','BROWN-WALD1999','LUCAS-METADATA2024','ALL-EMA-METHODS','NASS-AREA2009','LU-MAPS-V7','POLICY-DIVERSITY2025-READ']
    sources={r['source_id']:r for r in map(json.loads,(ROOT/'sources.jsonl').read_text().splitlines())}
    references=[]
    for sid in cited:
        source=sources[sid]
        assert source['access']=='full_text_relevant_passages_checked',(sid,'Supporting passage not marked checked')
        authors=str(source.get('authors','')).rstrip('. ')
        references.append(f"- **[{sid}]** {authors}. {source.get('year','')}. [{source['title']}]({source['url']}). {source.get('doi_or_version','')}.")
    values['REFERENCES_FROM_VERIFIED_SOURCES']='\n'.join(references)
    paper=template
    for key,value in values.items():
        slot='{{'+key+'}}'
        if str(value).endswith('.'):paper=paper.replace(slot+'.',str(value))
        paper=paper.replace(slot,str(value))
    for before,after in {
      '32,64,128,256 or512':'32, 64, 128, 256 or 512','of128':'of 128','At128':'At 128','and64':'and 64',
      'nominal95%':'nominal 95%','below95%':'below 95%','a95%':'a 95%','the30':'the 30','the4,096':'the 4,096',
      'n128':'n=128','floors10':'floors 10','through10':'through 10','uses1%,2%':'uses 1%, 2%','and5%':'and 5%',
      'secondary2021':'secondary 2021','and2022':'and 2022','coherent2022':'coherent 2022','one2022':'one 2022',
      'least1,024':'least 1,024','pool500':'pool 500','BY4.0':'BY 4.0','NeurIPS2024':'NeurIPS 2024',
      'runtime1.18.1':'runtime 1.18.1','A7.2025':'A7. 2025','at128':'at 128'}.items():paper=paper.replace(before,after)
    paper=paper.replace('than10^-10','than 10^-10').replace('The0.01','The 0.01').replace('and0.05','and 0.05')
    paper=paper.replace('within10^-10of','within 10^-10 of').replace('within10^-12','within 10^-12').replace('below10^-6','below 10^-6').replace('the six-case subset','the eligible subset')
    paper=re.sub(r'\b1 tiny changes\b','1 tiny change',paper)
    paper=re.sub(r'\b(Table|Figure|Appendix)([A-Z]?\d+|[A-Z])\b',r'\1 \2',paper)
    assert not re.search(r'\{\{[A-Z0-9_]+\}\}',paper),'Unfilled manuscript field'
    (out/'paper.md').write_text(paper)
    (out/'manuscript/values.json').write_text(json.dumps(dict(rendered_at_utc=now(),values=values,
        numerical_source_note='Display numbers read or arithmetically formatted from saved analysis outputs; no result transcribed by hand'),indent=2,ensure_ascii=False)+'\n')
    write_claims(out,main,ratios,cases,zero,sparse,ap,ai,gradlo,gradhi,panel,census)
    print(json.dumps(dict(completed_at_utc=now(),destination=str(out),refreshed_complete=refresh_complete,paper_bytes=(out/'paper.md').stat().st_size)))

def robustness_methods(refresh_complete):
    return """Prespecified checks include the finer hierarchy, frozen random forests, the secondary2021→2022 and2022→2025 contrasts, three native-grid cases selected by baseline category/static geometry, and one-pixel prediction-offset tests on a fixed interior subset. Reference-error sensitivity uses1%,2% and5% hypothetical total-variation contamination per year and the classical entropy continuity bound [AUDENAERT2007]. These are scenarios, not measured error rates. Grain/silage-maize ambiguity is assessed separately using the published hierarchy.

Exploratory checks retain all original comparisons. We analyse all stable agricultural reference pixels in the30 test landscapes without an embedding mask, and separately all-year stable `Arable Land` pixels with at least1,024 pixels per retained landscape. The latter changes the target population; no satellite-assisted estimate on that new frame is claimed. Other checks use the original audit draws: delete-one jackknife, an entropy envelope based on an exact hypergeometric upper bound for the proportion of changed labels, and bounded prediction weights. When no changed labels are observed, we take the union of this envelope with the original interval; this exploratory combination has no general coverage guarantee. The crossfitted weight calculation respects sampling without replacement and is exactly validated for raw proportions on a small constructed population; entropy and its intervals remain approximate. We also test a fixed two-stratum design that allocates half the labels to the quarter of locations with largest predicted annual probability change, hard-label auxiliary predictions, and gradient floors10^-2 through10^-10 at n128.

A separate exploratory monitoring simulation uses one coherent2022–2025 sample sequence, n128 labels/year, and independent, fully revisited or half-retained panels. Its partial-overlap influence variance includes covariance estimated on overlapping locations. A Bonferroni multiplier for three contrasts is assessed by empirical simultaneous coverage; it supplies no guarantee when marginal intervals are invalid. Detailed formulas, exclusions, seeds, synthetic validation and pre-execution revisions are in protocol/ and VERIFY.md."""+ (" The same-year refreshed logistic diagnostic is complete; its additional training labels are reported separately." if refresh_complete else " The same-year refreshed logistic diagnostic is unfinished in this working draft.")

def additional_geography():
    methods='A further exploratory plan fixes an additional reference-only cohort in test supercells absent from the accepted main cohort, preserving the unused original candidate order. It accepts the first eligible landscape per supercell using the original agricultural-support criteria, with no diversity-change or performance criterion. Adjacent supercells can contain nearby landscape footprints; this selection does not establish independent ecological or geographic replicates. Resource/time stopping rules and every failed attempt are retained. The attained cohort is committed before its inference, and its results are kept separate from the original primary cohort.'
    if not (ROOT/'results/additional-geography/analysis.json').exists():
        return dict(methods=methods,abstract='',main='',limitation='; the separately planned additional-geography check is not complete in this working version',results='### C. Additional geography\n\nThe fixed exploratory acquisition/analysis is not yet complete. No additional-cohort result is asserted.')
    cohort=obj('data/validation-cohort-v1.json');summary=read('results/additional-geography/summary.csv')
    cases=read('results/additional-geography/case-counts.csv');changes=read('results/additional-geography/reference-changes.csv')
    ratios=read('results/additional-geography/pairing-ratios.csv')
    full=summary[(summary.frame=='full_reference')&(summary.taxonomy=='broad')&(summary.n==128)]
    p=one(full,design='paired');i=one(full,design='independent');cc=one(cases,frame='full_reference',taxonomy='broad')
    ratio=one(ratios,frame='full_reference',taxonomy='broad',n=128)
    context=pd.DataFrame(cohort['context']);arable=int((context.baseline_arable_fraction>.5).sum());grass=int((context.baseline_grassland_fraction>.5).sum())
    baseline=[]
    for (frame,taxonomy),g in changes.groupby(['frame','taxonomy']):
        baseline.append(dict(frame=frame,taxonomy=taxonomy,no_change_rmse=float(np.sqrt(np.mean(g.true_change.to_numpy()**2)))))
    outcomes=summary[summary.n==128].merge(pd.DataFrame(baseline),on=['frame','taxonomy'])
    text=f"""### C. Exploratory additional geography

The separately frozen cohort attained {cohort['accepted_landscapes']} landscapes in distinct test supercells absent from the accepted main cohort, with {cohort['candidate_status_counts']['ineligible']} ineligible and {cohort['candidate_status_counts']['failed']} failed candidate attempts at its freeze. Selection preserved the original unused metadata order and used no diversity-change outcome. These additional landscapes contain {arable} arable-dominated and {grass} grassland-dominated cases under the original baseline majority rule. They remain a conditional geographic extension, not a nationally representative sample or independent reproduction.

On complete agricultural support, the broad comparison contains {int(cc.units)} contrasts: {int(cc.tiny_change)} with |ΔH|<0.01, {int(cc.zero_change)} exact zero changes, {int(cc.labels_unchanged_all)} entirely unchanged label populations, {int(cc.entropy_floor)} entropy-floor and {int(cc.single_group_either_year)} single-group cases. All are retained. At n128 the revisited/independent MSE ratio is {f(ratio.paired_independent_mse_ratio,3)}; coverage is {pct(p.coverage)} versus {pct(i.coverage)}, reports {pct(p.report_rate)} versus {pct(i.report_rate)}, and wrong-direction frequencies {pct(p.wrong_report_rate)} versus {pct(i.wrong_report_rate)}. TableA8 retains both frames and taxonomies; their cases overlap and must not be counted as independent geography.

**TableC1. Exploratory additional-geography reference-only comparisons, n128. No-change columns are point baselines without reporting intervals.**

"""+table(outcomes,[('frame','Frame',str),('taxonomy','Taxonomy',str),('design','Sample',str),('units','Contrasts',count),('rmse','RMSE',f),('no_change_rmse','No-change RMSE',f),('coverage','Coverage',pct),('report_rate','Reports',pct),('wrong_report_rate','Wrong reports',pct)])
    main=f"### 4.7. Exploratory additional geography and a precision boundary\n\nThe attained additional cohort contains {cohort['accepted_landscapes']} landscapes in distinct previously unused test supercells, with {arable} arable-dominated and {grass} grassland-dominated cases. Its complete agricultural support retains a revisiting MSE gain (ratio {f(ratio.paired_independent_mse_ratio,3)} at n128), with direct coverage {pct(p.coverage)} versus {pct(i.coverage)}. This supplies additional conditional geography, not a representative national sample. Acquisition stopped at the predeclared cache-growth cap; all {cohort['candidate_status_counts']['ineligible']} ineligible and {cohort['candidate_status_counts']['failed']} failed candidates remain recorded, without replacement chosen from change outcomes. TableC1 gives both point and complete-support comparisons and no-change baselines."
    abstract=''
    if (ROOT/'results/additional-geography-arable/analysis.json').exists():
        ar=read('results/additional-geography-arable/summary.csv');ar=ar[(ar.taxonomy=='broad')&(ar.n==128)]
        ac=one(read('results/additional-geography-arable/case-counts.csv'),taxonomy='broad')
        text+=f"\n\nThe prespecified-within-this-exploratory-plan arable-only rule retained {int(ac.landscapes)} additional landscapes and {int(ac.units)} contrasts. This changes support and signal together; all excluded candidates remain listed. There were {int(ac.tiny_change)} tiny changes, {int(ac.zero_change)} exact zeros, {int(ac.entropy_floor)} entropy-floor and {int(ac.single_group_either_year)} single-group cases.\n\n"+table(ar,[('design','Sample',str),('rmse','RMSE',f),('coverage','Coverage',pct),('report_rate','Reports',pct),('wrong_report_rate','Wrong reports',pct)])
        ars=read('results/additional-geography-arable/pairing-ratios.csv');br=one(ars,taxonomy='broad',n=128);fr=one(ars,taxonomy='fine',n=128)
        arbc=ars[ars.taxonomy=='broad']
        context=read('results/covariance-context/summary.csv');context=one(context,cohort='additional',frame='stable_arable',taxonomy='broad')
        main+=f"\n\nThe stable-arable rule retains {int(ac.landscapes)} additional landscapes and {int(ac.units)} contrasts. Here the observed broad-group MSE ratio exceeds one: {f(br.paired_independent_mse_ratio,3)} at n128 (MCSE {f(br.ratio_mcse,3)}), ranging {f(arbc.paired_independent_mse_ratio.min(),3)}–{f(arbc.paired_independent_mse_ratio.max(),3)} over all tested budgets. The fine-group ratio at n128 is {f(fr.paired_independent_mse_ratio,3)}. The broad subset has {int(ac.tiny_change)} tiny changes, {int(ac.zero_change)} exact zeros, {int(ac.entropy_floor)} entropy-floor and {int(ac.single_group_either_year)} single-group cases; none is excluded. These are outcomes on the six-case subset fixed by support eligibility, not evidence that revisiting is generally inferior on arable land.\n\nA post-result analysis of archived known-population influence diagnostics finds negative broad-group influence covariance in {int(context.negative_covariance)} of {int(context.units)} contrasts, with an aggregate paired/independent influence-variance ratio {f(context.aggregate_influence_variance_ratio,3)}. This is consistent with the observed MSE reversal, and illustrates the established covariance identity on this target. The proxy is not exact entropy variance, and the comparison changes support/composition/taxonomy rather than isolating a causal effect of rotation. All cohort/frame/taxonomy covariance summaries are in results/covariance-context/."
        abstract=f"Among {cohort['accepted_landscapes']} additional exploratory landscapes, stable arable support in {int(ac.landscapes)} gave a broad-group revisited/independent MSE ratio of {f(br.paired_independent_mse_ratio,3)} at128 labels/year ({int(ac.tiny_change)} tiny changes among {int(ac.units)} contrasts; {int(ac.entropy_floor)} entropy-floor and {int(ac.single_group_either_year)} single-group cases), limiting any universal precision claim."
        if (ROOT/'results/additional-arable-high-replication/analysis.json').exists():
            high=read('results/additional-arable-high-replication/pairing-ratios.csv');hb=one(high,taxonomy='broad',n=128);hf=one(high,taxonomy='fine',n=128)
            high_summary=read('results/additional-arable-high-replication/summary.csv');reps=int(high_summary.replications.iloc[0])
            main+=f"\n\nA further exploratory check increases simulation precision on these same cases to {count(reps)} replications. The broad ratio at n128 is {f(hb.paired_independent_mse_ratio,3)} (MCSE {f(hb.ratio_mcse,3)}) and the finer ratio {f(hf.paired_independent_mse_ratio,3)} (MCSE {f(hf.ratio_mcse,3)}). Original outcomes remain alongside the check in TableC2. The index arrays are regenerated from recorded seeds and array-byte hashes; all resulting estimates/SE/directions are saved. This is additional simulation on the same references, not independent geographic evidence."
            combined=ars[['taxonomy','n','paired_independent_mse_ratio','ratio_mcse']].merge(high[['taxonomy','n','paired_independent_mse_ratio','ratio_mcse']],on=['taxonomy','n'],suffixes=('_original','_check'))
            text+='\n\n**TableC2. Additional stable-arable MSE ratios: original simulation and higher-precision check. MCSE measures simulation precision on the fixed cohort.**\n\n'+table(combined,[('taxonomy','Taxonomy',str),('n','Labels/year',count),('paired_independent_mse_ratio_original','Original ratio',lambda x:f(x,3)),('ratio_mcse_original','Original MCSE',lambda x:f(x,3)),('paired_independent_mse_ratio_check','Check ratio',lambda x:f(x,3)),('ratio_mcse_check','Check MCSE',lambda x:f(x,3))])
            abstract=f"Among {cohort['accepted_landscapes']} additional exploratory landscapes, stable arable support in {int(ac.landscapes)} gave a broad-group revisited/independent MSE ratio of {f(hb.paired_independent_mse_ratio,3)} in a {count(reps)}-replication check at128 labels/year ({int(ac.tiny_change)} tiny changes among {int(ac.units)} contrasts; {int(ac.entropy_floor)} entropy-floor and {int(ac.single_group_either_year)} single-group cases), limiting any universal precision claim."
        cov=read('results/covariance-context/summary.csv')
        text+='\n\n**TableC3. Post-result summaries of established population influence diagnostics at n128. These are linearized proxies, not exact entropy variances.**\n\n'+table(cov,[('cohort','Cohort',str),('frame','Frame',str),('taxonomy','Taxonomy',str),('units','Contrasts',count),('negative_covariance','Negative covariance',count),('aggregate_influence_variance_ratio','Influence variance ratio',lambda x:f(x,3)),('empirical_entropy_mse_ratio','Original MSE ratio',lambda x:f(x,3))])
    elif cohort['eligible_arable_cases']<5:text+=f"\n\nOnly {cohort['eligible_arable_cases']} additional landscapes met the 1024-pixel stable-arable rule; the planned minimum for that extra comparison was not attained, so no additional arable-only result is asserted."
    else:text+='\n\nThe additional stable-arable comparison is unfinished; no result is asserted.'
    return dict(methods=methods,abstract=abstract,main=main,limitation=f"; a separate exploratory reference-only extension adds {cohort['accepted_landscapes']} landscapes but no nationally representative inference",results=text)

def projection_comparison():
    methods="""After the gradient-floor result, an exploratory comparison also differentiates through the probability-simplex projection. On locally fixed positive support A, its established Jacobian is J=diag(s)−ssᵀ/|A|, where s indicates membership in A [SIMPLEX-JACOBIAN2016]. The local entropy gradient is Jᵀg: g_j−mean_A(g) on A and zero elsewhere, using the exact positive projected proportions. The original interval rule does not apply this Jacobian. Both rules use identical point estimates, draws, FPC and normal multiplier; no original outcome is replaced. Finite differences validate the local calculation away from support changes. A separate zero-category fixture demonstrates a boundary where entropy has no finite derivative; local-face validation is not a coverage theorem. Nonsmooth-inference issues are established [FANG-SANTOS2019], whose results are not claimed as a validity proof for this approximation."""
    if not (ROOT/'results/projection-derivative/fine-alphaearth/analysis.json').exists():return dict(methods=methods,abstract='',results='',appendix='')
    frame=pd.concat([read(f'results/projection-derivative/{tax}-{rep}/summary.csv') for tax in ['broad','fine'] for rep in ['tessera','alphaearth']],ignore_index=True)
    selected=frame[(frame.taxonomy=='broad')&(frame.method=='model_assisted')]
    local=selected[(selected.design=='paired')&(selected.rule=='projection_chain_rule')]
    abstract=f"An exploratory projection-derivative comparison, with identical point estimates, gave soft-assisted coverage of {pct(local.coverage.min())}–{pct(local.coverage.max())} and reports in {pct(local.report_rate.min())}–{pct(local.report_rate.max())} of revisited trials; local support changes still prevent a general validity guarantee."
    checks=obj('results/validation-projection-derivative/result.json')
    text=f"""### 4.6. Exploratory derivative through projection

The original rule's conservatism is also sensitive to whether uncertainty is propagated through the projection itself (Table7). With the local projection derivative, revisited broad soft-logistic coverage is {pct(local.coverage.min())}–{pct(local.coverage.max())}, and reporting is {pct(local.report_rate.min())}–{pct(local.report_rate.max())}. Point estimates and RMSE are exactly unchanged. This strengthens the qualification of the original high-coverage result: it is not a property of satellite-assisted inference in general.

The software check passes {checks['cases']} finite-difference cases away from splitting points; its maximum gradient difference is {checks['maximum_gradient_difference']:.2e}. That is a local derivative check, not independent validation. The broad assisted draws contain no singleton positive supports; {pct(selected.near_split_either_year.min())}–{pct(selected.near_split_either_year.max())} have a raw coordinate within10^-10of a projection splitting threshold, and {pct(selected.small_positive_either_year.min())}–{pct(selected.small_positive_either_year.max())} have a positive projected proportion below10^-6. These draws are retained. Direct controls reproduce their original SEs within10^-12; this expected algebraic invariance is not a new empirical finding. The finer hierarchy and all per-unit outputs are retained in results/projection-derivative/. No local-face normal interval is certified by this experiment.

**Table7. Exploratory propagation through projection, broad groups, n128. Both rules share the same estimates and samples.**

"""
    display=selected.copy();display['rule']=display.rule.map({'original':'Original clipped gradient','projection_chain_rule':'Local projection derivative'})
    text+=table(display,[('representation','Representation',str),('design','Sample',str),('rule','Gradient rule',str),('mean_se','Mean SE',f),('coverage','Coverage',pct),('report_rate','Reports',pct),('wrong_report_rate','Wrong reports',pct),('reports','Report count',count),('wrong_reports','Wrong count',count)])
    controls=[]
    for rep in ['tessera','alphaearth']:
        for prefix,head in [('forest-broad','Frozen forest'),('refreshed-broad','Refreshed logistic')]:
            path=f'results/projection-derivative/{prefix}-{rep}/summary.csv'
            if not (ROOT/path).exists():continue
            d=read(path);d=d[d.method=='model_assisted'].copy();d['head']=head;controls.append(d)
    if controls:
        c=pd.concat(controls,ignore_index=True);cl=c[(c.rule=='projection_chain_rule')&(c.design=='paired')]
        text+=f"\n\nThe same exploratory calculation on all saved broad forest and refreshed-logistic controls gives revisited local-derivative coverage {pct(cl.coverage.min())}–{pct(cl.coverage.max())}. Point estimates remain unchanged in every control. Their complete comparisons and the finer frozen heads are in AppendixD. The annually refreshed controls retain their additional training-label burden."
    appendix='### D. Additional projection-derivative comparisons\n\nAll comparisons use unchanged estimates, the original samples and n128. They are exploratory normal approximations, with no guarantee at changing active supports.'
    if controls:
        display=c.copy();display['rule']=display.rule.map({'original':'Original','projection_chain_rule':'Projection derivative'})
        appendix+='\n\n**TableD1. All saved broad forest and refreshed-logistic controls.**\n\n'+table(display,[('head','Head',str),('representation','Representation',str),('design','Sample',str),('rule','Rule',str),('rmse','RMSE',f),('coverage','Coverage',pct),('report_rate','Reports',pct),('wrong_report_rate','Wrong reports',pct)])
    fine=frame[(frame.taxonomy=='fine')&(frame.method=='model_assisted')].copy();fine['rule']=fine.rule.map({'original':'Original','projection_chain_rule':'Projection derivative'})
    appendix+='\n\n**TableD2. Both finer-hierarchy frozen logistic heads.**\n\n'+table(fine,[('representation','Representation',str),('design','Sample',str),('rule','Rule',str),('rmse','RMSE',f),('coverage','Coverage',pct),('report_rate','Reports',pct),('wrong_report_rate','Wrong reports',pct)])
    return dict(methods=methods,abstract=abstract,results=text,appendix=appendix)

def discussion():
    return """In the main agricultural cohort, revisiting reduces reference-sampling error, including after prediction correction. That is consistent with established change-estimation theory. Lower magnitude-interval coverage coexists here with more frequent direct direction reports and fewer wrong directions in aggregate. A sample with no changed labels estimates zero change and abstains, so its zero-width interval can fail to cover a small nonzero change without issuing a wrong direction. Coverage and directional reporting are different outcomes. The aggregate direction frequencies still do not establish a per-landscape error guarantee or validate the magnitude intervals.

The original soft-logistic interval rule is often conservative and rarely reports a direction. Its coverage is partly a consequence of the clipped entropy gradient and of bypassing the derivative through projection. Applying the established local projection derivative substantially changes the reporting behavior without changing a point estimate. This local calculation still leaves uncertainty about support changes and does not validate nominal coverage. Treating either low wrong-report frequency or high coverage alone as success would miss the reporting tradeoff. No one method is selected as operationally best without specifying the consequences of a wrong direction, an unresolved direction and magnitude error; those consequences were not measured.

The agricultural support is consequential. Most main landscapes are grassland-dominated, and many agricultural-group proportions change little even when crop use changes elsewhere in the landscape. On stable arable land, turnover and the scale of entropy changes are larger, and the aggregate revisited-sample coverage deficit is much smaller. The additional stable-arable cohort also contains an observed broad-group precision reversal, while the finer hierarchy has an observed ratio below one. This demonstrates a boundary of a universal precision claim on the examined data. Its known-population influence covariance is consistent with the established mechanism, without identifying a causal effect of crop rotation. Neither the original nor the additional cohort establishes a universal preference for revisiting or independent sampling on arable land. The partial-retention panel is a useful established comparison, but its empirical tradeoff here does not select a universally preferred rotation rate or establish calibrated simultaneous reporting.

The no-change point baseline is also essential. A lower MSE than independent sampling can coexist with higher MSE than predicting zero. That result follows from the signal magnitude and sampling noise in this benchmark; it does not provide evidence that a particular landscape did not change. Practitioners should keep these decisions separate: estimating a small change, deciding whether its sign is resolved, and choosing whether an estimate improves on a simple baseline. The effect of abstention on actual decisions was not measured.

For a monitoring application, the evidence supports retaining a revisited or partially revisited reference design as a candidate, comparing it with independent sampling at the intended support and budget, and testing its reporting intervals on representative reference data. Prediction weighting, a different classifier or stratification can improve point accuracy without establishing uncertainty calibration. The results do not justify choosing a numerical gradient floor by its apparent coverage on the same benchmark, or converting a declared-use change into an ecological or policy claim."""

def results_sections(main,at128,ratios,cases,zero,description,sparse,arable,gradient,panel,census,refresh_complete):
    blocks=[]
    blocks.append(f"""### 4.1. Reference changes and the no-change comparison

The main comparison includes {int(cases.units)} landscape–transition units. Of these, {int(cases.tiny_change)} have |ΔH|<0.01, {int(cases.zero_change)} have exactly zero change within the prespecified tolerance, and {int(cases.labels_unchanged_all)} have identical labels at every reference location in the two years. There are {int(cases.entropy_floor)} entropy-floor cases and {int(cases.single_group_either_year)} single-group cases. Auxiliary probability vectors are temporally identical in {int(cases.identical_predictions)} cases and spatially constant in {int(cases.spatially_constant_predictions_either_year)}. Thus the aggregate precision benefit cannot be described as a result about entirely unchanged populations, but its size depends on the many small changes and grassland-dominated landscapes. The direct estimator is the same across representations because its references and sample draws are shared; those identical values are counted once.

The no-change point baseline has RMSE {f(zero.rmse)} entropy units. It outperforms the direct and frozen-model-assisted n128 estimates shown below under squared error on this cohort. It supplies neither a reporting interval nor evidence that a particular landscape did not change. Unadjusted map-count and source-confusion point estimates also fail to beat this baseline (Table3). Their sign mismatches are point-estimate diagnostics, not confidence-qualified false reports.

### 4.2. Original audit comparison and prespecified forest robustness

Table1 reports n128, selected before outcomes. RMSE is the square root of equally weighted landscape–transition MSE; rates pool500 trials for each unit. Wrong/report gives the actual count of wrong directions divided by reports, not a posterior error probability. Monte Carlo uncertainty concerns simulation precision on this fixed benchmark, not geographic generalization. The source training/calibration labels and supplied five-year frame are outside the audit budget.

**Table1. Broad-group audit outcomes,128 labels per year. LR denotes the primary frozen logistic condition; RF is the prespecified frozen random-forest check.**""")
    frames=[at128]
    for rep in ['tessera','alphaearth']:
        rf=read(f'results/tables/forest-broad-{rep}/audit-performance.csv')
        frames.append(rf[(rf.subset=='all')&(rf.n==128)&(rf.method=='model_assisted')])
    frame=pd.concat(frames,ignore_index=True)
    frame['wrong_over_reports']=[f'{int(w)}/{int(r)}' for w,r in zip(frame.wrong_reports,frame.reports)]
    blocks.append(table(frame,[('label','Estimator',pretty),('design','Sample',str),('rmse','RMSE',f),('coverage','Coverage',pct),
        ('report_rate','Reports',pct),('wrong_report_rate','Wrong reports',pct),('wrong_over_reports','Wrong/report',str),('projection_any_year','Projected',pct)]))
    from review_revision import fields
    blocks.append(fields()['REVIEW_ACCURACY'])
    covse=frame.coverage_mcse
    blocks.append(f"Coverage Monte Carlo standard errors range from {f(100*covse.min(),2)} to {f(100*covse.max(),2)} percentage points. They do not include uncertainty from landscape selection, reference errors or training-data choice. Forests change the point-accuracy comparison, so a failure or weak gain from the original logistic auxiliary must not be generalized to all model assistance.")
    dp=one(at128,label='reference-broad',design='paired');di=one(at128,label='reference-broad',design='independent')
    blocks.append(f"For direct estimation, revisiting produced more reports ({pct(dp.report_rate)} versus {pct(di.report_rate)}) and fewer wrong directions ({pct(dp.wrong_report_rate)} versus {pct(di.wrong_report_rate)}) in aggregate, alongside its lower interval coverage. A zero-width interval from unchanged sampled labels abstains; its failure to cover a nonzero magnitude is not itself a wrong-direction report. The aggregate frequencies do not establish uniform per-landscape error control.")
    direct=main[main.label=='reference-broad']
    rows=[]
    for subset in ['all','grassland_dominated','arable_dominated']:
      for n in [32,64,128,256,512]:
        p=one(direct,n=n,design='paired',subset=subset);i=one(direct,n=n,design='independent',subset=subset)
        ratio=one(ratios,label='reference-broad',subset=subset,n=n)
        rows.append(dict(subset=subset,n=n,paired_rmse=p.rmse,independent_rmse=i.rmse,ratio=ratio.paired_independent_mse_ratio,
                         paired_coverage=p.coverage,independent_coverage=i.coverage))
    blocks.append('**Table2. Prespecified direct-sampling budget curve. The no-change RMSE is fixed across budgets.**\n\n'+table(pd.DataFrame(rows),[
        ('subset','Prespecified subset',lambda x:{'all':'All','grassland_dominated':'Grassland-dominated','arable_dominated':'Arable-dominated'}[x]),('n','Labels/year',count),('paired_rmse','Revisited RMSE',f),('independent_rmse','Independent RMSE',f),
        ('ratio','MSE ratio',lambda x:f(x,3)),('paired_coverage','Revisited coverage',pct),('independent_coverage','Independent coverage',pct)]))
    blocks.append('![Budget curves for broad-group change estimation](results/tables/main/budget-curves.svg)\n\n**Figure1.** Original broad-group results over all five budgets. The black dotted line is the no-change point baseline; the grey horizontal line is nominal coverage, not a proven guarantee. Axes use a common scale within each row. The fixed-gradient influence comparison is in results/tables/main/pairing-variance.svg and is not an exact entropy-variance result at boundaries.')
    points=read('results/tables/main/point-estimates.csv')
    points=points[~((points.method=='no_change')&(points.representation=='alphaearth'))]
    blocks.append('**Table3. Point baselines without new target-audit labels. All still use the supplied reference frame; model conditions use source training/calibration. No confidence interval is claimed.**\n\n'+table(points,[
        ('tag','Head',pretty),('method','Point rule',str),('rmse','RMSE',f),('opposite_or_false_directions','Sign mismatches',count),('nonzero_point_estimates','Nonzero estimates',count)]))
    ar=one(main,label='reference-broad',subset='arable_dominated',n=128,design='paired')
    ag=one(main,label='reference-broad',subset='arable_dominated',n=128,design='independent')
    blocks.append(f"""### 4.3. Prespecified scope and input checks

In the arable-dominated subset ({int(ar.units)} transitions), direct coverage is {pct(ar.coverage)} with revisiting and {pct(ag.coverage)} with independent samples. This already limits a blanket interpretation of the aggregate coverage deficit. The finer taxonomy retains a revisited-sample MSE advantage but also displays imperfect direct interval coverage; its complete numerical comparison is in TableA1. The secondary contrasts are retained separately in results/tables/secondary-broad/ and secondary-fine/, with year-specific subsets; they do not replace the three primary contrasts.

The prospective full native-grid check contains {census['cases']} cases and {census['primary_transitions']} primary contrasts. Sampled-point and native reference changes differ in sign in {census['sign_disagreements']} contrasts; their discrepancy RMSE is {f(census['change_discrepancy_rmse'])}. The median first-phase reference linearization variance is {pct(census['median_first_phase_paired_fraction_n128'])} of the native n128 audit variance. This is a small conditional check, not a national estimate or a measurement of unconditional two-phase interval coverage. The fixed interior/offset sensitivity uses the same interior population for every prediction offset; direct estimates are consequently unchanged by offset by construction. All offsets and retained-population counts are in results/registration/.

Hypothetical reference-error scenarios are reported in AppendixA. They do not estimate the actual declaration or registration error rate. A broad-group grain/silage-maize swap cannot change the broad outcome because those fine categories share a parent; this is a taxonomy identity, not an empirical robustness discovery.""")
    if refresh_complete:
        fres=[];burden=[]
        for rep in ['tessera','alphaearth']:
            d=read(f'results/tables/logistic-broad-refreshed-{rep}/audit-performance.csv')
            fres.append(d[(d.subset=='all')&(d.n==128)&(d.method=='model_assisted')])
            fit=obj(f'results/models/logistic-broad-refreshed-{rep}/fit.json')
            burden += [r['training_points'] for r in fit['fit_records'] if r['year']>2021]
        blocks.append(f"The refreshed logistic diagnostic uses {count(min(burden))}–{count(max(burden))} additional training labels per later year, plus the audit labels. It is not budget-matched to n128 target auditing.\n\n"+table(pd.concat(fres),[
            ('label','Refreshed head',pretty),('design','Sample',str),('rmse','RMSE',f),('coverage','Coverage',pct),('report_rate','Reports',pct),('wrong_report_rate','Wrong reports',pct)]))
    else:blocks.append('The refreshed-head comparison is unfinished in this working draft; no refreshed result is included.')
    full=read('results/reference-frames/summary.csv');scopes=[]
    for name,data in [('All stable agriculture',full[full.frame=='full_reference']),('Stable arable land',arable)]:
        p=one(data,taxonomy='broad',design='paired',n=128);i=one(data,taxonomy='broad',design='independent',n=128)
        scopes.append(dict(frame=name,units=int(p.units),rmse_p=p.rmse,rmse_i=i.rmse,coverage_p=p.coverage,coverage_i=i.coverage))
    arable_case=one(read('results/stable-arable/case-counts.csv'),taxonomy='broad')
    blocks.append(f"""### 4.4. Exploratory reference-frame and interval checks

The complete reference-only agricultural grids reproduce the large precision gain and the aggregate direct-interval deficit without an embedding mask or the4,096-point approximation. Restricting to stable arable land changes the composition and signal magnitude as well as the support. It retains {int(arable_case.landscapes)} of the original {int(cases.landscapes)} landscapes, without replacement, and the coverage deficit between sample designs is much smaller (Table4). These frames are overlapping uses of the same declarations, not independent geographic replications.

**Table4. Exploratory full-reference frames, broad groups, n128.**""")
    blocks.append(table(pd.DataFrame(scopes),[('frame','Reference frame',str),('units','Transitions',count),('rmse_p','Revisited RMSE',f),('rmse_i','Independent RMSE',f),('coverage_p','Revisited coverage',pct),('coverage_i','Independent coverage',pct)]))
    blocks.append(f"In the main revisited direct samples, {pct(sparse.zero_sampled_changes)} of n128 draws observe no changed reference labels. Such a draw gives identical annual sample proportions, estimated change zero and zero paired standard error. For a nonzero population change it cannot cover the truth. The exact no-change-sample probability, computed from the known benchmark transition counts, places the attainable coverage below95% in {int(sparse.units_coverage_ceiling_below_0_95)} units. Of the observed direct-interval misses, {pct(sparse.fraction_of_original_misses_with_zero_changes)} occur in zero-observed-change samples. This elementary identity explains part, not all, of the deficit. It is not a newly discovered statistical theorem.")
    blocks.append(f"Taking the interval union with the entropy envelope when no changed labels are observed raises coverage from {pct(sparse.original_coverage)} to {pct(sparse.guarded_coverage)} at n128 but does not achieve nominal coverage. The envelope always contains zero and cannot establish a direction. Jackknife and prediction-based stratification also do not establish nominal revisited-sample coverage. Bounded prediction weighting improves revisited point accuracy relative to the original fixed soft-logistic correction, but does not uniformly improve independent-sample accuracy and retains the sparse-change limitation; detailed positive and negative results are in AppendixA.")
    grids=[]
    for rep in ['tessera','alphaearth']:
        g=read(f'results/gradient/broad-{rep}/summary.csv')
        grids.append(g[(g.method=='model_assisted')&(g.design=='paired')])
    blocks.append("The gradient-floor experiment isolates a separate mechanism: point estimates and RMSE are exactly unchanged, while interval widths and reporting change materially (Table5). Every tested floor is retained, and none is selected as a calibrated operational value. This result qualifies the apparent conservatism of the original soft-probability intervals.\n\n**Table5. Exploratory gradient floors, original soft-logistic revisited estimates, broad groups, n128.**\n\n"+table(pd.concat(grids),[
        ('representation','Representation',str),('gradient_floor','Floor',lambda x:f'{x:g}'),('mean_se','Mean SE',f),('coverage','Coverage',pct),('report_rate','Reports',pct),('wrong_report_rate','Wrong reports',pct)]))
    pdirect=panel[panel.label=='direct']
    blocks.append(f"""### 4.5. Exploratory coherent annual panels

The four-year monitoring simulation uses one coherent sample sequence rather than separate pairwise experiments. Half retention gives precision between independent and fully revisited sampling. The full-revisit direct intervals have poorer simultaneous coverage; Bonferroni widening alone does not repair invalid marginal intervals. Table6 reports both interval rules, including the probability of any wrong direction during the three-contrast sequence. The maximum negative-variance frequency across saved conditions is {pct(panel.negative_variance.max())}. These are results for the tested rotation rate and reference populations, not a general prescription for panel refresh frequency.

**Table6. Direct estimation in one2022–2025 panel,128 labels/year. Joint coverage concerns all three adjacent changes.**""")
    blocks.append(table(pdirect,[('design','Panel',str),('interval','Interval',str),('rmse','Marginal RMSE',f),('coverage','Marginal coverage',pct),('joint_coverage','Joint coverage',pct),('any_wrong_report','Any wrong report',pct),('any_report','Any report',pct)]))
    return '\n\n'.join(blocks)

def appendices(description,refresh_complete):
    blocks=['### A. Additional planned and exploratory results']
    fine=read('results/tables/fine/audit-performance.csv');fine=fine[(fine.subset=='all')&(fine.n==128)]
    blocks.append('**TableA1. Prespecified finer taxonomy, n128.**\n\n'+table(fine,[('label','Estimator',pretty),('design','Sample',str),('rmse','RMSE',f),('coverage','Coverage',pct),('report_rate','Reports',pct),('wrong_report_rate','Wrong reports',pct)]))
    powers=pd.concat([read(f'results/power/{rep}/summary.csv') for rep in ['tessera','alphaearth']],ignore_index=True)
    blocks.append('**TableA2. Exploratory bounded prediction weighting, n128; same samples as the original broad comparison. Crossfitting concerns raw proportions, not unbiased projected entropy or guaranteed intervals.**\n\n'+table(powers,[
        ('representation','Representation',str),('mode','Weight rule',str),('design','Sample',str),('rmse','RMSE',f),('coverage','Coverage',pct),('report_rate','Reports',pct),('wrong_report_rate','Wrong reports',pct),('mean_lambda','Mean weight',lambda x:f(x,3))]))
    jk=pd.concat([read(f'results/jackknife/{rep}/summary.csv') for rep in ['tessera','alphaearth']],ignore_index=True)
    jk=jk[jk.variant=='fpc'];jk=jk[~((jk.method=='direct')&(jk.representation=='alphaearth'))]
    blocks.append('**TableA3. Exploratory jackknife with the prospectively corrected finite-population bias scaling, n128. The ordinary variant is retained in results/jackknife/ and does not replace this variant after observing performance.**\n\n'+table(jk,[
        ('representation','Representation',str),('method','Estimator',str),('design','Sample',str),('rmse','RMSE',f),('coverage','Coverage',pct),('report_rate','Reports',pct),('wrong_report_rate','Wrong reports',pct)]))
    strat=pd.concat([read(f'results/stratified/{rep}/summary.csv') for rep in ['tessera','alphaearth']],ignore_index=True);strat=strat[strat.n==128]
    blocks.append('**TableA4. Exploratory prediction-stratified sampling, n128. Different representations define different strata, so their direct estimates are distinct comparisons.**\n\n'+table(strat,[
        ('representation','Representation',str),('method','Estimator',str),('design','Sample',str),('rmse','RMSE',f),('coverage','Coverage',pct),('report_rate','Reports',pct),('stratified_original_mse_ratio','MSE/original SRS',lambda x:f(x,3))]))
    hard=[]
    for rep in ['tessera','alphaearth']:
        h=read(f'results/tables/hard-auxiliary-{rep}/audit-performance.csv');hard.append(h[(h.subset=='all')&(h.n==128)&(h.method=='model_assisted')])
    blocks.append('**TableA5. Exploratory hard-label auxiliary predictions, n128; no classifier refitting.**\n\n'+table(pd.concat(hard),[
        ('label','Auxiliary',pretty),('design','Sample',str),('rmse','RMSE',f),('coverage','Coverage',pct),('report_rate','Reports',pct),('projection_any_year','Projected',pct)]))
    sens=pd.DataFrame(obj('results/reference-sensitivity/summary.json')['summary'])
    blocks.append('**TableA6. Prespecified hypothetical reference-error scenarios. Bounds allow different directions of error in the two years; rates were not estimated from data. The broad maize invariance follows from the hierarchy.**\n\n'+table(sens,[
        ('taxonomy','Taxonomy',str),('rate','Per-year TV bound',pct),('general_change_error_bound','Change error bound',f),('general_sign_robust','General sign robust',count),('maize_ambiguity_sign_robust','Maize-only sign robust',count)]))
    classification=pd.DataFrame(description['classification_context']);classification=classification[(classification.split=='test')&(classification.year==2025)]
    blocks.append('**TableA7.2025 test classification context. This is accuracy against declared groups, not an independent harvest survey or a test of interval calibration.**\n\n'+table(classification,[
        ('tag','Head',pretty),('taxonomy','Taxonomy',str),('pixel_weighted_accuracy','Pixel accuracy',pct),('unsupported_points','Unsupported labels',count),('points','Reference locations',count)]))
    blocks.append("""All budgets and context subsets, per-unit distributions, source-confusion optimizer diagnostics, full native-grid outcomes, interior prediction offsets, both jackknife variants, fine-taxonomy gradient floors and model-assisted coherent panels remain in results/. They are included in the full offline verification index rather than selected by statistical significance. The stable-arable and full-agricultural scope baselines are in results/scope-baselines/. The source matrix rank and unavailable classes limit the source-confusion comparison; its poor performance does not refute label-shift methods under their own assumptions.

### B. Data attribution and process scope

SwissCrop25 is used under its published CC BY4.0 terms, including the specified cantonal, Agroscope, Copernicus and MeteoSwiss attributions listed in DATA_LICENSES.md. The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind. The public AlphaEarth mirror specifies CC BY4.0. The official TESSERA data catalogue specifies CC-BY-SA without a version; that ambiguity is retained in DATA_LICENSES.md and is not replaced with the separate model-weight licence.

One mandatory critique of topic candidates used another AI model; it did not write code, interpret results or write this paper. No human-participant experiment or independent reproduction was performed. A documented short unwrapped diagnostic briefly exceeded the two-experiment limit; its record is retained, and scientific sparse-change outputs were subsequently recomputed through the bounded runner. Human-confirmed usage-limit pauses adjusted the deadline according to the original trial condition; the second pause has a documented endpoint uncertainty because its final preceding clock output was unavailable after context compaction. Automatic Git packing occurred between storage checkpoints; its temporary peak was not measured, so a transient storage-limit breach cannot be ruled out. Subsequent individual commit commands disable automatic maintenance. All original plans, source-fit warnings, decoder failures, pilot exclusions and numerical corrections remain in the local record. Git times and hashes are self-reported records and do not establish independence or absence of tampering.

The paper is written by this session. The planned review by an AI agent has been received; the original review and response are in review/. Verification records in VERIFY.md and review/ identify reruns by this same session; none is independent reproduction.""")
    return '\n\n'.join(blocks)

def write_claims(out,main,ratios,cases,zero,sparse,ap,ai,gradlo,gradhi,panel,census):
    claims=[]
    def claim(cid,text,paths,expected,scope,implication,exploratory=False,experiments=None,sources=None,status='supported'):
        claims.append(dict(claim_id=cid,text=text,status=status,evidence_paths=paths,source_ids=sources or [],experiment_ids=experiments or [],
            scope=scope,verify={'command':'python scripts/verify.py --all --output /ABSOLUTE/FRESH/OUTPUT','inspect':paths},expected=expected,
            exploratory=exploratory,reader_implication=implication))
    r=ratios[(ratios.label=='reference-broad')&(ratios.subset=='all')]
    claim('C01','Revisiting lowers direct broad-group change MSE relative to independent annual samples across the five prespecified budgets.',
        ['results/tables/main/pairing-mse-ratios.csv'],{'minimum_ratio':float(r.paired_independent_mse_ratio.min()),'maximum_ratio':float(r.paired_independent_mse_ratio.max())},
        'Thirty fixed test landscapes, three primary2022–2025 contrasts, specified stable agricultural point populations; no national or field-cost inference.',
        'Reference-panel choice materially affects precision, but a relative precision gain alone does not validate reporting.',experiments=['E14-main-inference'],sources=['ROTATION-SAMPLE1981','MASSEY2015'])
    cp=one(main,label='reference-broad',subset='all',n=128,design='paired');ci=one(main,label='reference-broad',subset='all',n=128,design='independent')
    claim('C02','At n128 the direct revisited intervals have lower aggregate coverage than independent-sample intervals on the main agricultural cohort.',
        ['results/tables/main/audit-performance.csv','results/tables/main/case-counts.csv'],{'paired_coverage':float(cp.coverage),'independent_coverage':float(ci.coverage),'tiny_changes':int(cases.tiny_change),'zero_changes':int(cases.zero_change),'entropy_floor_cases':int(cases.entropy_floor)},
        f'Original delta intervals with gradient floor 1e-6; {int(cases.grassland_dominated_landscapes)} grassland-dominated and {int(cases.arable_dominated_landscapes)} arable-dominated landscapes; aggregate result is qualified by C05.',
        'Test coverage for the intended support and change frequency; do not interpret a nominal level as demonstrated reliability.',experiments=['E14-main-inference'],sources=['PANINSKI2003'])
    claim('C03','The no-change point baseline beats n128 direct and frozen-model-assisted broad estimates in squared error on this cohort.',
        ['results/tables/main/point-estimates.csv','results/tables/main/audit-performance.csv','results/tables/forest-broad-tessera/audit-performance.csv','results/tables/forest-broad-alphaearth/audit-performance.csv'],
        {'no_change_rmse':float(zero.rmse),'direct_revisited_rmse':float(cp.rmse)},
        'Main broad-group cohort and original frozen logistic/forest conditions, not the later refreshed or alternative-frame conditions. The point baseline supplies no confidence interval.',
        'Include a simple point baseline when assessing practical precision; its success under MSE does not establish absence of change.',experiments=['E14-main-inference','E27-forest-tessera','E27-forest-alphaearth'])
    assisted=main[(main.subset=='all')&(main.n==128)&(main.design=='paired')&(main.method=='model_assisted')]
    claim('C04','Original soft-logistic assisted intervals are conservative in aggregate and rarely report directions, with very frequent simplex projection.',
        ['results/tables/main/audit-performance.csv'],{'coverage_range':[float(assisted.coverage.min()),float(assisted.coverage.max())],
          'report_range':[float(assisted.report_rate.min()),float(assisted.report_rate.max())],'projection_range':[float(assisted.projection_any_year.min()),float(assisted.projection_any_year.max())]},
        'Two frozen logistic representations, broad groups, revisited n128 samples and the original1e-6 floor; not all model-assisted estimators or numerical settings.',
        'High aggregate coverage and low wrong reporting can coexist with little resolved directional information.',experiments=['E14-main-inference'])
    claim('C05','The aggregate coverage gap is much smaller on the exploratory complete stable-arable reference frame.',
        ['results/stable-arable/summary.csv','results/stable-arable/cohort.json','results/stable-arable/case-counts.csv'],
        {'landscapes':int(one(read('results/stable-arable/case-counts.csv'),taxonomy='broad').landscapes),'primary_transitions':int(ap.units),'paired_coverage':float(ap.coverage),'independent_coverage':float(ai.coverage)},
        'All-year Arable Land support, at least1024pixels, eligible subset of the original landscapes; changes support, composition and signal magnitude together; no causal attribution.',
        'Do not generalize the grassland-inclusive aggregate deficit to every arable crop-diversity application.',True,['E22-arable-boundary'])
    claim('C06','Revisited draws with no changed labels account for a substantial portion of direct interval misses; the exploratory conservative interval union does not restore nominal coverage.',
        ['results/sparse/tessera/summary.csv','results/sparse/tessera/unit-diagnostics.csv'],
        {'zero_observed_change_fraction':float(sparse.zero_sampled_changes),'miss_fraction_with_zero_changes':float(sparse.fraction_of_original_misses_with_zero_changes),
         'units_with_exact_ceiling_below_0_95':int(sparse.units_coverage_ceiling_below_0_95),'guarded_coverage':float(sparse.guarded_coverage)},
        'Exploratory n128 original broad direct samples; exact ceiling uses known benchmark transition counts; guard is not a uniformly valid replacement interval.',
        'Inspect transition sparsity and zero-standard-error draws before accepting approximate interval reports.',True,['E17-sparse-change'],['SCIPY-HYPERGEOM','AUDENAERT2007','PANINSKI2003'])
    claim('C07','Changing only the numerical entropy-gradient floor changes soft-assisted interval coverage and reporting while preserving point estimates exactly.',
        ['results/gradient/broad-tessera/summary.csv','results/gradient/broad-alphaearth/summary.csv','results/gradient/fine-tessera/analysis.json','results/gradient/fine-alphaearth/analysis.json'],
        {'broad_tessera_revisited_floor_0_01_coverage':float(gradlo.coverage),'floor_1e_minus10_coverage':float(gradhi.coverage),
         'report_rate_floor_0_01':float(gradlo.report_rate),'report_rate_floor_1e_minus10':float(gradhi.report_rate),'rmse_identical':float(gradlo.rmse)},
        'Exploratory frozen logistic n128 conditions, floors1e-2through1e-10; no floor selected as operationally calibrated.',
        'Numerical regularization of a boundary derivative must be part of the uncertainty assessment.',True,['E25-gradient-floors'])
    p=one(panel,label='direct',design='fully_revisited',interval='bonferroni');h=one(panel,label='direct',design='half_retained',interval='bonferroni')
    claim('C08','A coherent half-retained panel has intermediate direct precision and higher simultaneous coverage than the full-revisit panel in this benchmark, without reaching nominal95% joint coverage.',
        ['results/coherent-panel/summary.csv','results/validation-rotating/result.json'],
        {'full_revisit_joint_coverage_bonferroni':float(p.joint_coverage),'half_retained_joint_coverage_bonferroni':float(h.joint_coverage),
         'half_retained_rmse':float(h.rmse),'full_revisit_rmse':float(p.rmse)},
        'Exploratory coherent2022–2025 samples,128labels/year,30fixed landscapes, tested50%retention only; approximate entropy intervals.',
        'Partial rotation deserves comparison at the intended budget, but this result does not select a universally reliable refresh rate.',True,['E23-rotating-validation','E26-coherent-panel'],['ROTATION-SAMPLE1981'])
    claim('C09','The prospective native-grid case check exposes differences between sampled-point and whole-population reference changes.',
        ['results/census-comparison/summary.json','results/census-comparison/census-changes.csv'],
        {'cases':census['cases'],'transitions':census['primary_transitions'],'sign_disagreements':census['sign_disagreements'],'change_discrepancy_rmse':census['change_discrepancy_rmse']},
        'Three cases selected by baseline category/static geometry before target outcomes; no unconditional two-phase coverage estimate or new geography.',
        'A conditional finite-point audit target should not silently be treated as the complete landscape target.',False,['E16-native-grid-inference'])
    if (ROOT/'results/additional-geography-arable/analysis.json').exists():
        r=read('results/additional-geography-arable/pairing-ratios.csv');b=one(r,taxonomy='broad',n=128);fine=one(r,taxonomy='fine',n=128)
        context=one(read('results/covariance-context/summary.csv'),cohort='additional',frame='stable_arable',taxonomy='broad')
        expected={'landscapes':int(context.landscapes),'contrasts':int(context.units),'broad_mse_ratio_n128':float(b.paired_independent_mse_ratio),
             'broad_ratio_mcse':float(b.ratio_mcse),'fine_mse_ratio_n128':float(fine.paired_independent_mse_ratio),
             'negative_broad_influence_covariance_units':int(context.negative_covariance),'linearized_variance_ratio':float(context.aggregate_influence_variance_ratio)}
        paths=['results/additional-geography-arable/pairing-ratios.csv','results/additional-geography-arable/case-counts.csv','results/covariance-context/summary.csv','data/validation-cohort-v1.json']
        if (ROOT/'results/additional-arable-high-replication/analysis.json').exists():
            high=read('results/additional-arable-high-replication/pairing-ratios.csv');h=one(high,taxonomy='broad',n=128);hf=one(high,taxonomy='fine',n=128)
            expected.update(high_replication_broad_ratio=float(h.paired_independent_mse_ratio),high_replication_broad_mcse=float(h.ratio_mcse),high_replication_fine_ratio=float(hf.paired_independent_mse_ratio))
            paths.append('results/additional-arable-high-replication/pairing-ratios.csv')
        claim('C10','The additional stable-arable broad-group subset has observed revisited MSE above independent MSE, while its finer hierarchy retains a modest gain.',
            paths,expected,
            'Exploratory separate geographic cohort, complete stable Arable Land support and the fixed primary period; no independent reproduction, representative national inference or causal rotation effect.',
            'A precision gain on broad agricultural support should not be treated as a universal gain for another crop-group support or taxonomy.',True,['E42-additional-inference','E51-covariance-context','E53-arable-high-replication'],['ROTATION-SAMPLE1981'])
    if (ROOT/'results/projection-derivative/fine-alphaearth/analysis.json').exists():
        p=pd.concat([read(f'results/projection-derivative/broad-{rep}/summary.csv') for rep in ['tessera','alphaearth']],ignore_index=True)
        p=p[(p.method=='model_assisted')&(p.design=='paired')&(p.rule=='projection_chain_rule')]
        claim('C11','Applying the local projection derivative changes soft-assisted interval coverage and reporting while preserving all point estimates.',
            ['results/projection-derivative/broad-tessera/summary.csv','results/projection-derivative/broad-alphaearth/summary.csv','results/validation-projection-derivative/result.json'],
            {'paired_coverage_range':[float(p.coverage.min()),float(p.coverage.max())],
             'paired_reporting_range':[float(p.report_rate.min()),float(p.report_rate.max())],'point_estimates_identical':True},
            'Exploratory original frozen logistic heads at n128, both hierarchies/representations, locally fixed sampled positive support; support changes and entropy boundaries prevent a general normal-coverage guarantee.',
            'High coverage under the original clipped-gradient rule is not intrinsic evidence of reliable model assistance; specify propagation through the actual transformation.',True,['E49-projection-derivative-validation','E50-projection-derivative'],['SIMPLEX-JACOBIAN2016','FANG-SANTOS2019'])
    from review_revision import revise_claims
    revise_claims(claims)
    for row in claims:
        assert row['evidence_paths'] and all((ROOT/path).exists() for path in row['evidence_paths'])
        for experiment in row['experiment_ids']:
            assert (ROOT/'experiments'/experiment/'run.json').exists(),('Unknown claim experiment',experiment)
        for key in ['text','scope','reader_implication']:
            if row[key]:row[key]=re.sub(r'\bn128\b','n=128',row[key])
    (out/'claims.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n' for r in claims))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--destination',default='.');a=p.parse_args();render(a.destination)
