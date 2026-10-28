"""Single offline entry point. All writes go outside the source directory."""
import os,sys
sys.dont_write_bytecode=True
os.environ['OMP_NUM_THREADS']='1'
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['MKL_NUM_THREADS']='1'
os.environ['PROJ_NETWORK']='OFF'
import argparse,json,hashlib,time
from pathlib import Path

def compare_csv(pd,np,actual,expected,ignore=()):
    a=pd.read_csv(actual);b=pd.read_csv(expected)
    a=a.drop(columns=[k for k in ignore if k in a]);b=b.drop(columns=[k for k in ignore if k in b])
    assert a.shape==b.shape,(actual.name,a.shape,b.shape)
    assert list(a.columns)==list(b.columns),actual.name
    for c in a:
        if pd.api.types.is_numeric_dtype(a[c]) and pd.api.types.is_numeric_dtype(b[c]):
            np.testing.assert_allclose(a[c].to_numpy(float),b[c].to_numpy(float),rtol=1e-10,atol=1e-12,equal_nan=True,err_msg=f'{actual.name}:{c}')
        else:
            assert a[c].fillna('<NA>').astype(str).equals(b[c].fillna('<NA>').astype(str)),f'{actual.name}:{c}'
    return dict(file=actual.name,rows=len(a),columns=len(a.columns),status='matched')

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();root=Path(__file__).resolve().parents[1];out=a.output.resolve()
    if out==root or out.is_relative_to(root):raise ValueError('Output must be outside the source checkout')
    out.mkdir(parents=True,exist_ok=False)
    os.environ['MPLCONFIGDIR']=str(out/'matplotlib-cache')
    import numpy as np,pandas as pd
    from prepare import prepare
    from prepare_controls import prepare_controls
    from analyse import analyse
    from secondary import secondary
    from figures import generate
    from prepare_nlcd import prepare_nlcd
    from extend_nlcd import extend
    from native_check import analyse as analyse_native
    from native_check import prepare as prepare_native
    from closed_aef import closed_aef
    from robustness import robust
    from presentation import display_tables
    from diagnostic_figures import generate_diagnostics
    from endpoint import endpoint
    from reference_completeness import reference_completeness
    from route_recover import recover as recover_route
    from initial_readouts import initial_readouts
    from geography import geography
    from initial_class import initial_class
    from reference_access import reference_access
    from native_pairs import prepare_native_pairs,prepare_native_available,native_pairs
    from native_identity import native_identity
    from api_wrapper import cost as saved_response_cost
    from audit_saved import audit_saved
    from direct_inputs import direct_inputs
    from partition_sensitivity import partition_sensitivity,PARTITION_SEEDS
    from input_figures import generate_inputs
    from cohort_history_feasibility import feasibility as cohort_history_feasibility
    from review_diagnostics import run as review_diagnostics
    tick=time.monotonic();checks=[];stage_timings=[]
    from record import now
    def stage(name,function,*args,**kwargs):
        started=now();before=time.monotonic()
        value=function(*args,**kwargs)
        stage_timings.append(dict(stage=name,start_at_utc=started,end_at_utc=now(),elapsed_seconds=time.monotonic()-before))
        (out/'progress.json').write_text(json.dumps(stage_timings,indent=2)+'\n')
        print(json.dumps(dict(completed_stage=name,elapsed_seconds=stage_timings[-1]['elapsed_seconds'])),flush=True)
        return value
    latest_api={}
    for line in (root/'api_calls.jsonl').read_text().splitlines():
        record=json.loads(line);latest_api[record['call_id']]=record
    for record in latest_api.values():
        assert record['status']=='completed'
        response=json.loads((root/record['response_path']).read_text())
        calculated=saved_response_cost(response)
        np.testing.assert_allclose(calculated,record['cost_usd'],rtol=0,atol=1e-10)
        assert response['usage']==record['usage']
        checks.append(dict(check='Saved AI-response usage and computed cost; no API call',call_id=record['call_id'],
            model=response['model'],computed_cost_usd=calculated,status='matched',
            caveat='Default30m cache-write accounting; legacy retention field lacks lifetime token breakdown. Invoice not observed.'))
    route= root/'experiments/route-check-v15-recovery/results'
    for name,sha in json.loads((route/'input-sha256.json').read_text()).items():
        assert hashlib.sha256((root/name).read_bytes()).hexdigest()==sha,name
    stage('route_recovery',recover_route,out/'route-check-v15-recovery')
    checks.append(compare_csv(pd,np,out/'route-check-v15-recovery/comparisons.csv',route/'comparisons.csv'))
    assert json.loads((out/'route-check-v15-recovery/summary.json').read_text())==json.loads((route/'summary.json').read_text())
    for folder in ['aef-closed-v11','robustness-aef-v12','main-v1','endpoint-v13','reference-completeness-v14','secondary-v2','robustness-paired-v12','initial-vector-v17','geography-v18','initial-class-v19','reference-access-v20','direct-inputs-v23','review-diagnostics-r1','partition-sensitivity-v24','cohort-history-feasibility','nlcd-v4','nlcd-initial-v17','nlcd-geography-v18','nlcd-class-v19','nlcd-reference-access-v20','nlcd-direct-inputs-v23','native-v5','native-pairs-v21','native-single-date-v22']:
        expected=json.loads((root/'analysis'/folder/'input-sha256.json').read_text())
        for name,sha in expected.items():
            assert hashlib.sha256((root/name).read_bytes()).hexdigest()==sha,f'Input hash mismatch: {name}'
        checks.append(dict(check=f'{folder} raw input hashes',files=len(expected),status='matched'))
    stage('prepare_lcmap',prepare,out/'prepared')
    for name in ['targets.csv','references.csv','tasks.csv','sample_counts.csv']:
        checks.append(compare_csv(pd,np,out/'prepared'/name,root/'data/prepared'/name))
    stage('prepare_controls',prepare_controls,out/'controls')
    for name in ['controls.csv','tasks.csv']:
        checks.append(compare_csv(pd,np,out/'controls'/name,root/'data/controls'/name))
    stage('cohort_history_feasibility',cohort_history_feasibility,out/'cohort-history-feasibility')
    checks.append(compare_csv(pd,np,out/'cohort-history-feasibility/coordinate-matches.csv',root/'analysis/cohort-history-feasibility/coordinate-matches.csv'))
    assert json.loads((out/'cohort-history-feasibility/summary.json').read_text())==json.loads((root/'analysis/cohort-history-feasibility/summary.json').read_text())
    stage('prepare_nlcd',prepare_nlcd,out/'nlcd-prepared')
    for name in ['targets.csv','tasks.csv','sample-counts.csv']:
        checks.append(compare_csv(pd,np,out/'nlcd-prepared'/name,root/'data/nlcd/prepared'/name))
    stage('prepare_native_sample',prepare_native,out/'native-prepared')
    checks.append(compare_csv(pd,np,out/'native-prepared/tasks.csv',root/'data/native-check/tasks.csv'))
    stage('prepare_native_pairs',prepare_native_pairs,out/'native-pairs-prepared')
    for name in ['tasks.csv','targets.csv']:
        checks.append(compare_csv(pd,np,out/'native-pairs-prepared'/name,root/'data/native-pairs'/name))
    stage('prepare_saved_native_dates',prepare_native_available,out/'native-available-prepared')
    for name in ['tasks.csv','targets.csv']:
        checks.append(compare_csv(pd,np,out/'native-available-prepared'/name,root/'data/native-available'/name))
    stage('aef_closed_v11',closed_aef,out/'aef-closed-v11')
    for name in ['availability.csv','metrics.csv','paired-comparisons.csv','main-table.csv','thresholds.csv','strata.csv','identities.csv']:
        checks.append(compare_csv(pd,np,out/'aef-closed-v11'/name,root/'analysis/aef-closed-v11'/name))
    stage('robustness_aef_v12',robust,out/'robustness-aef-v12',out/'aef-closed-v11',['aef'])
    robust_tables=['metrics.csv','paired-comparisons.csv','thresholds.csv','fitting-counts.csv','matching-counts.csv',
        'calibration-metrics.csv','calibration-paired.csv','calibration-thresholds.csv','partial-label-audit.csv','partial-label-audit-summary.csv']
    for name in robust_tables:
        checks.append(compare_csv(pd,np,out/'robustness-aef-v12'/name,root/'analysis/robustness-aef-v12'/name))
    stage('main_v1',analyse,out/'main-v1')
    for name in ['availability.csv','availability-targets.csv','coverage.csv','metrics.csv','paired-comparisons.csv','main-table.csv','thresholds.csv','strata.csv','identities.csv']:
        checks.append(compare_csv(pd,np,out/'main-v1'/name,root/'analysis/main-v1'/name))
    stage('review_diagnostics_r1',review_diagnostics,out/'review-diagnostics-r1',out/'main-v1')
    for name in ['reference-year-counts.csv','reference-drift.csv','individual-cohort-change.csv','sample-support.csv','score-similarity.csv','control-constancy.csv','target-magnitudes.csv','target-magnitude-summary.csv','magnitude-ranking.csv','magnitude-medians.csv']:
        checks.append(compare_csv(pd,np,out/'review-diagnostics-r1'/name,root/'analysis/review-diagnostics-r1'/name))
    assert json.loads((out/'review-diagnostics-r1/summary.json').read_text())==json.loads((root/'analysis/review-diagnostics-r1/summary.json').read_text())
    stage('partition_sensitivity_v24',partition_sensitivity,out/'partition-sensitivity-v24',out/'main-v1')
    for name in ['metrics.csv','paired-comparisons.csv','thresholds.csv','fitting-counts.csv','cell-assignments.csv','invariance-checks.csv','condition-availability.csv','primary-ranges.csv']:
        checks.append(compare_csv(pd,np,out/'partition-sensitivity-v24'/name,root/'analysis/partition-sensitivity-v24'/name))
    for split_seed in PARTITION_SEEDS:
        for name in ['metrics.csv','paired-comparisons.csv','strata.csv','thresholds.csv','reference-availability.csv']:
            checks.append(compare_csv(pd,np,out/'partition-sensitivity-v24'/f'seed-{split_seed}'/name,root/'analysis/partition-sensitivity-v24'/f'seed-{split_seed}'/name))
    assert json.loads((out/'partition-sensitivity-v24/summary.json').read_text())==json.loads((root/'analysis/partition-sensitivity-v24/summary.json').read_text())
    stage('endpoint_v13',endpoint,out/'endpoint-v13',out/'main-v1')
    for name in ['metrics.csv','paired-comparisons.csv','thresholds.csv','strata.csv','excluded-gain-negative-pairs.csv',
                 'class-route-counts.csv','reference-state-pairs.csv','scalar-reconstruction-check.csv','reference-state-summary.csv']:
        checks.append(compare_csv(pd,np,out/'endpoint-v13'/name,root/'analysis/endpoint-v13'/name))
    stage('reference_completeness_v14',reference_completeness,out/'reference-completeness-v14',out/'main-v1')
    for name in ['metrics.csv','paired-comparisons.csv','thresholds.csv','reference-membership.csv','changes-versus-original.csv']:
        checks.append(compare_csv(pd,np,out/'reference-completeness-v14'/name,root/'analysis/reference-completeness-v14'/name))
    stage('secondary_v2',secondary,out/'secondary-v2',out/'main-v1')
    for name in ['metrics.csv','paired-comparisons.csv','thresholds.csv','strata.csv','control-availability.csv']:
        checks.append(compare_csv(pd,np,out/'secondary-v2'/name,root/'analysis/secondary-v2'/name))
    stage('robustness_paired_v12',robust,out/'robustness-paired-v12',out/'main-v1',['aef','tessera'])
    for name in robust_tables:
        checks.append(compare_csv(pd,np,out/'robustness-paired-v12'/name,root/'analysis/robustness-paired-v12'/name))
    stage('initial_lcmap_v17',initial_readouts,out/'initial-vector-v17','lcmap',out/'secondary-v2',out/'robustness-paired-v12')
    initial_tables=['metrics.csv','paired-comparisons.csv','strata.csv','initial-versus-subsequent.csv','thresholds.csv','cohort-fitting-counts.csv']
    for name in initial_tables+['permutation-map.csv']:
        checks.append(compare_csv(pd,np,out/'initial-vector-v17'/name,root/'analysis/initial-vector-v17'/name))
    assert json.loads((out/'initial-vector-v17/permutation-check.json').read_text())==json.loads((root/'analysis/initial-vector-v17/permutation-check.json').read_text())
    stage('geography_lcmap_v18',geography,out/'geography-v18','lcmap',out/'main-v1')
    for name in ['metrics.csv','strata.csv','thresholds.csv','fitting-counts.csv']:
        checks.append(compare_csv(pd,np,out/'geography-v18'/name,root/'analysis/geography-v18'/name))
    stage('class_lcmap_v19',initial_class,out/'initial-class-v19','lcmap',out/'main-v1',out/'initial-vector-v17',out/'geography-v18')
    class_tables=['metrics.csv','strata.csv','thresholds.csv','fitting-counts.csv','subgroup-metrics.csv',
                  'subgroup-strata.csv','subgroup-initial-versus-subsequent.csv','subgroup-counts.csv']
    for name in class_tables:
        checks.append(compare_csv(pd,np,out/'initial-class-v19'/name,root/'analysis/initial-class-v19'/name))
    stage('reference_access_lcmap_v20',reference_access,out/'reference-access-v20','lcmap',out/'main-v1')
    access_tables=['metrics.csv','paired-comparisons.csv','strata.csv','thresholds.csv','reference-availability.csv',
                   'identities.csv','nearest-reference-distances.csv']
    for name in access_tables:
        checks.append(compare_csv(pd,np,out/'reference-access-v20'/name,root/'analysis/reference-access-v20'/name))
    stage('direct_inputs_lcmap_v23',direct_inputs,out/'direct-inputs-v23','lcmap',out/'main-v1')
    direct_tables=['metrics.csv','strata.csv','contrasts.csv','thresholds.csv','fitting-counts.csv','both-threshold-equality.csv']
    for name in direct_tables:
        checks.append(compare_csv(pd,np,out/'direct-inputs-v23'/name,root/'analysis/direct-inputs-v23'/name))
    assert json.loads((out/'direct-inputs-v23/summary.json').read_text())==json.loads((root/'analysis/direct-inputs-v23/summary.json').read_text())
    stage('main_figures',generate,out/'main-v1',out/'secondary-v2',out/'figures')
    for name in ['main-table.md','secondary-table.md']:
        assert (out/'figures'/name).read_bytes()==(root/'figures'/name).read_bytes(),name
    stage('diagnostic_figures',generate_diagnostics,out/'robustness-paired-v12',out/'secondary-v2',out/'figures/diagnostics')
    for expected in (root/'figures/diagnostics').glob('*.md'):
        assert (out/'figures/diagnostics'/expected.name).read_bytes()==expected.read_bytes(),expected.name
    stage('nlcd_v4',extend,out/'nlcd-v4',out/'main-v1',out/'secondary-v2')
    for name in ['metrics.csv','paired-comparisons.csv','thresholds.csv','strata.csv','threshold-equality.csv','availability-targets.csv','coverage.csv']:
        checks.append(compare_csv(pd,np,out/'nlcd-v4'/name,root/'analysis/nlcd-v4'/name))
    stage('initial_nlcd_v17',initial_readouts,out/'nlcd-initial-v17','nlcd',out/'nlcd-v4',out/'robustness-paired-v12',out/'initial-vector-v17')
    for name in initial_tables+['post-threshold-equality.csv','initial-threshold-equality.csv']:
        checks.append(compare_csv(pd,np,out/'nlcd-initial-v17'/name,root/'analysis/nlcd-initial-v17'/name))
    stage('geography_nlcd_v18',geography,out/'nlcd-geography-v18','nlcd',out/'main-v1',out/'nlcd-v4',out/'geography-v18')
    for name in ['metrics.csv','strata.csv','thresholds.csv','fitting-counts.csv','threshold-equality.csv']:
        checks.append(compare_csv(pd,np,out/'nlcd-geography-v18'/name,root/'analysis/nlcd-geography-v18'/name))
    stage('class_nlcd_v19',initial_class,out/'nlcd-class-v19','nlcd',out/'main-v1',out/'nlcd-initial-v17',out/'nlcd-geography-v18',out/'nlcd-v4',out/'initial-class-v19')
    for name in class_tables+['threshold-equality.csv']:
        checks.append(compare_csv(pd,np,out/'nlcd-class-v19'/name,root/'analysis/nlcd-class-v19'/name))
    stage('reference_access_nlcd_v20',reference_access,out/'nlcd-reference-access-v20','nlcd',out/'main-v1',out/'nlcd-v4',out/'reference-access-v20')
    for name in access_tables+['threshold-equality.csv']:
        checks.append(compare_csv(pd,np,out/'nlcd-reference-access-v20'/name,root/'analysis/nlcd-reference-access-v20'/name))
    stage('direct_inputs_nlcd_v23',direct_inputs,out/'nlcd-direct-inputs-v23','nlcd',out/'nlcd-v4',out/'direct-inputs-v23')
    for name in direct_tables+['threshold-equality.csv']:
        checks.append(compare_csv(pd,np,out/'nlcd-direct-inputs-v23'/name,root/'analysis/nlcd-direct-inputs-v23'/name))
    assert json.loads((out/'nlcd-direct-inputs-v23/summary.json').read_text())==json.loads((root/'analysis/nlcd-direct-inputs-v23/summary.json').read_text())
    stage('direct_input_figures',generate_inputs,out/'direct-inputs-v23',out/'nlcd-direct-inputs-v23',out/'figures')
    stage('native_v5',analyse_native,out/'native-v5')
    for name in ['comparisons.csv','summary.csv']:
        checks.append(compare_csv(pd,np,out/'native-v5'/name,root/'analysis/native-v5'/name))
    stage('unfinished_native_pairs_v21',native_pairs,out/'native-pairs-v21',out/'main-v1')
    for name in ['comparisons.csv','summary.csv','availability.csv','thresholds.csv','threshold-equality.csv']:
        checks.append(compare_csv(pd,np,out/'native-pairs-v21'/name,root/'analysis/native-pairs-v21'/name))
    assert json.loads((out/'native-pairs-v21/checks.json').read_text())==json.loads((root/'analysis/native-pairs-v21/checks.json').read_text())
    stage('native_single_date_v22',native_pairs,out/'native-single-date-v22',out/'main-v1',out/'native-available-prepared',True)
    for name in ['comparisons.csv','summary.csv','availability.csv','thresholds.csv','threshold-equality.csv']:
        checks.append(compare_csv(pd,np,out/'native-single-date-v22'/name,root/'analysis/native-single-date-v22'/name))
    assert json.loads((out/'native-single-date-v22/checks.json').read_text())==json.loads((root/'analysis/native-single-date-v22/checks.json').read_text())
    stage('native_identity_v22',native_identity,out/'native-single-date-v22/identity',out/'native-available-prepared/tasks.csv',out/'native-single-date-v22/comparisons.csv')
    for name in ['input-identity.csv','decision-identity.csv']:
        checks.append(compare_csv(pd,np,out/'native-single-date-v22/identity'/name,root/'analysis/native-single-date-v22/identity'/name))
    assert json.loads((out/'native-single-date-v22/identity/summary.json').read_text())==json.loads((root/'analysis/native-single-date-v22/identity/summary.json').read_text())
    stage('display_tables',display_tables,out/'main-v1',out/'secondary-v2',out/'nlcd-v4',out/'native-v5',out/'tables')
    for expected in (root/'tables').glob('*.md'):
        assert (out/'tables'/expected.name).read_bytes()==expected.read_bytes(),expected.name
    # Separately recompute confusion counts using saved flags, without fitting code.
    predictions=pd.read_parquet(out/'main-v1/predictions.parquet')
    tab=pd.read_csv(out/'main-v1/main-table.csv')
    for r in tab.itertuples():
        g=predictions[(predictions.availability_mode=='paired')&(predictions.model==r.model)&
                      (predictions.support=='centre')&(predictions.seed==14014)&
                      (predictions.reference_mode=='global')&(predictions.task==r.task)&(predictions.method==r.method)]
        assert ((g.truth==1)&(g.flag==1)).sum()==r.true_positive
        assert ((g.truth==0)&(g.flag==1)).sum()==r.false_positive
        assert (g.truth==1).sum()==r.n_positive and (g.truth==0).sum()==r.n_negative
        np.testing.assert_allclose(g[g.truth==1].flag.mean()-g[g.truth==0].flag.mean(),r.J,atol=1e-12)
    threshold=pd.read_csv(out/'main-v1/thresholds.csv');v=threshold[threshold.available]
    assert (v.calibration_false_flags/v.calibration_negatives<=.1+1e-12).all()
    checks.append(dict(check='independent confusion recount and calibration operating point',status='matched',rows=len(tab)))
    saved=stage('saved_flag_audit',audit_saved,out)
    (out/'saved-flag-audit.json').write_text(json.dumps(saved,indent=2)+'\n')
    checks.append(dict(check='separate saved-flag recount across all result sets',status=saved['status'],folders=len(saved['checks'])))
    summary=dict(status='PASS',elapsed_seconds=time.monotonic()-tick,checks=checks,stage_timings=stage_timings,
                 network_used=False,ai_api_calls=0,note='Self reruns and third-party reruns must be distinguished in reporting.')
    (out/'verification.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
