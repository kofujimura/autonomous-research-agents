"""Index only completed artifacts for the read-only reproduction entry point."""
import json
from records import ROOT,now,event

analyses={};groups=[];extras=[]
def group(name,paths,expected,primary=True):
    if not all((ROOT/p/'analysis.json').exists() for p in paths):return
    assert (ROOT/expected/'audit-performance.csv').exists()
    for path in paths:
        role='primary' if path in ['results/inference/logistic-broad-tessera','results/inference/logistic-broad-alphaearth'] else 'robustness'
        meta=json.loads((ROOT/path/'analysis.json').read_text())
        assert meta.get('max_units_requested') is None
        analyses[path]=dict(path=path,role=role,reconstruct_features=meta['classifier']=='logistic')
    groups.append(dict(name=name,analyses=paths,expected_path=expected,primary_filter=primary,csv_files=sorted(p.name for p in (ROOT/expected).glob('*.csv'))))

group('tables-main',[f'results/inference/logistic-broad-{r}' for r in ['tessera','alphaearth']],'results/tables/main')
group('tables-fine',[f'results/inference/logistic-fine-{r}' for r in ['tessera','alphaearth']],'results/tables/fine')
group('tables-census',[f'results/census-inference/logistic-broad-{r}' for r in ['tessera','alphaearth']],'results/tables/census')
for rep in ['tessera','alphaearth']:
    for name in [f'forest-broad-{rep}',f'logistic-broad-refreshed-{rep}']:
        group('tables-'+name,['results/inference/'+name],'results/tables/'+name)
    group('tables-hard-'+rep,[f'results/inference/hard-auxiliary-broad-{rep}'],f'results/tables/hard-auxiliary-{rep}')
for tax in ['broad','fine']:
    path=f'results/tables/secondary-{tax}'
    if (ROOT/path/'audit-performance.csv').exists():
        paths=[f'results/inference/logistic-{tax}-{rep}' for rep in ['tessera','alphaearth']]
        if tax=='broad':paths += [f'results/inference/forest-broad-{rep}' for rep in ['tessera','alphaearth']]
        group('tables-secondary-'+tax,paths,path,primary=False)

def extra(name,module,function,args,path,kwargs=None,quick=False):
    if not (ROOT/path).exists():return
    csv_files=sorted(p.name for p in (ROOT/path).glob('*.csv'))
    assert csv_files,(path,'No numerical tables to verify')
    extras.append(dict(name=name,module=module,function=function,args=args,kwargs=kwargs or {},expected_path=path,csv_files=csv_files,quick=quick))

for rep in ['tessera','alphaearth']:
    original=f'results/inference/logistic-broad-{rep}'
    for stage,module in [('jackknife','jackknife_analysis'),('stratified','stratified_audits'),('power','power_tuning_analysis')]:
        extra(f'{stage}-{rep}',module,'run',[original],f'results/{stage}/{rep}')
    for tax in ['broad','fine']:
        extra(f'gradient-{tax}-{rep}','gradient_sensitivity','run',[f'results/inference/logistic-{tax}-{rep}'],f'results/gradient/{tax}-{rep}')
        extra(f'projection-derivative-{tax}-{rep}','projection_derivative','run',[f'results/inference/logistic-{tax}-{rep}'],f'results/projection-derivative/{tax}-{rep}')
    for source,destination in [(f'forest-broad-{rep}',f'forest-broad-{rep}'),(f'logistic-broad-refreshed-{rep}',f'refreshed-broad-{rep}')]:
        extra('projection-derivative-'+destination,'projection_derivative','run',['results/inference/'+source],
              'results/projection-derivative/'+destination,dict(plan_path='protocol/plan-v14a-projection-controls.md'))
extra('projection-derivative-validation','validate_projection_derivative','run',[],'results/validation-projection-derivative',quick=True)
extra('sparse','sparse_change_analysis','run',['results/inference/logistic-broad-tessera'],'results/sparse/tessera')
extra('reference-frames','reference_frame_analysis','run',['data/population-source-v1.json'],'results/reference-frames')
extra('stable-arable','reference_frame_analysis','run',['data/population-source-v1.json'],'results/stable-arable',dict(arable_only=True))
cohort_path=ROOT/'data/validation-cohort-v1.json'
if cohort_path.exists():
    cohort=json.loads(cohort_path.read_text())
    kw=dict(selection_ledger='data/validation-selection-results.jsonl',expected_landscapes=cohort['accepted_landscapes'],plan_path='protocol/plan-v13-additional-geography.md')
    extra('additional-geography','reference_frame_analysis','run',['data/population-source-v1.json'],'results/additional-geography',kw)
    extra('additional-geography-context','reference_frame_summaries','run',['results/additional-geography'],'results/additional-geography-context',quick=True)
    extra('additional-geography-arable','reference_frame_analysis','run',['data/population-source-v1.json'],'results/additional-geography-arable',dict(kw,arable_only=True))
    extra('additional-arable-high-replication','reference_frame_analysis','run',['data/population-source-v1.json'],
          'results/additional-arable-high-replication',dict(kw,arable_only=True,plan_path='protocol/plan-v13b-monte-carlo-precision.md',replications=5000,keep_draws=False))
extra('reference-context','reference_frame_summaries','run',['results/reference-frames'],'results/reference-frame-context',quick=True)
extra('coherent-panel','panel_analysis','run',[],'results/coherent-panel')
extra('registration','registration_check','run',[[f'results/census-models/logistic-broad-{r}' for r in ['tessera','alphaearth']]],'results/registration')
extra('census-comparison','compare_census','compare',[[f'results/inference/logistic-broad-{r}' for r in ['tessera','alphaearth']],
    [f'results/census-inference/logistic-broad-{r}' for r in ['tessera','alphaearth']]],'results/census-comparison',quick=True)
extra('reference-sensitivity','reference_sensitivity','run',['data/population-main-v1.json'],'results/reference-sensitivity',quick=True)
extra('scope-baselines','scope_baselines','run',[],'results/scope-baselines',quick=True)
extra('covariance-context','covariance_context','run',[],'results/covariance-context',quick=True)
extra('refreshed-controls','check_refreshed_controls','run',[],'results/refreshed-controls',quick=True)
extra('review-label-error','review_label_error','run',[],'results/review-label-error')
extra('review-summaries','review_summaries','run',[],'results/review-summaries')
for name in ['main','final']:
    path=f'results/description-{name}';metadata=ROOT/path/'summary.json'
    if metadata.exists():
        d=json.loads(metadata.read_text())
        extra('description-'+name,'describe_data','describe',[d['manifest_path'],[r['path'] for r in d['models']]],path,quick=True)

obj=dict(created_at_utc=now(),analyses=list(analyses.values()),table_groups=groups,supplemental_tasks=extras,
    render_documents=(ROOT/'paper.md').exists(),
    scope='Original complete Monte Carlo comparisons plus completed robustness/exploratory tables. Quick mode checks summaries from saved Monte Carlo arrays and cheap context checks only.')
(ROOT/'verification-config.json').write_text(json.dumps(obj,indent=2)+'\n')
event('verification_index_updated','Index completed analyses without marking absent/unfinished outputs complete',['verification-config.json'])
print(json.dumps(dict(analyses=len(analyses),table_groups=len(groups),supplemental_tasks=len(extras))))
