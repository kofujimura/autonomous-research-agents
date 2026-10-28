"""Exploratory v24: fixed perturbations of earlier cell fit/calibration assignment."""
import os
os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
import argparse,json,time
from pathlib import Path
import numpy as np
import pandas as pd
from analyse import make_predictions,summarize,SEED,UNSUP
from features import load_features,matrix,MODELS,SUPPORTS
from prepare import digest
from record import ROOT,now

PARTITION_SEEDS=tuple(range(14014,14024))
SUPERVISED=['direct_gradient_boosting','state_random_forest','subsequent_state_random_forest','subsequent_state_logistic']
KEYS=['availability_mode','model','support','fold','seed','reference_mode','task','method','point_id']
THKEYS=[k for k in KEYS if k!='point_id']


def partition_sensitivity(output,baseline):
    output.mkdir(parents=True,exist_ok=False)
    vectors,availability,hashes,_=load_features()
    targets=pd.read_csv(ROOT/'data/prepared/targets.csv');refs=pd.read_csv(ROOT/'data/prepared/references.csv')
    original=pd.read_parquet(baseline/'predictions.parquet')
    original=original[(original.availability_mode=='paired')&(original.seed==SEED)&(original.reference_mode=='global')]
    original_th=pd.read_csv(baseline/'thresholds.csv')
    original_th=original_th[(original_th.availability_mode=='paired')&(original_th.seed==SEED)&(original_th.reference_mode=='global')]
    ids0=targets.point_id+'-'+targets.before_year.astype(str);ids1=targets.point_id+'-'+targets.after_year.astype(str)
    common={s:np.logical_and.reduce([np.isfinite(matrix(vectors,m,s,ids)).all(1) for m in MODELS for ids in [ids0,ids1]]) for s in SUPPORTS}
    allmetrics=[];allpairs=[];allthresholds=[];fits=[];assignments=[];checks=[];timings=[];expected_rows=[]
    for partition_seed in PARTITION_SEEDS:
        start=now();tick=time.monotonic();t=targets.copy()
        t['calibration_cell']=[int(digest(partition_seed,'calibration',b)[:16],16)/16**16<.3 for b in t.block]
        folder=output/f'seed-{partition_seed}';folder.mkdir()
        assignments.extend(dict(partition_seed=partition_seed,block=block,calibration_cell=bool(value)) for block,value in t[['block','calibration_cell']].drop_duplicates().itertuples(index=False,name=None))
        pred,th,refavail,identities,near=make_predictions(vectors,t,refs,seeds=[SEED],reference_modes=['global'])
        pred.to_parquet(folder/'predictions.parquet',index=False);th.to_csv(folder/'thresholds.csv',index=False)
        metrics,pairs,strata=summarize(pred)
        for name,frame in [('metrics',metrics),('paired-comparisons',pairs),('strata',strata),('reference-availability',refavail)]:frame.to_csv(folder/f'{name}.csv',index=False)
        for frame,items in [(metrics,allmetrics),(pairs,allpairs),(th,allthresholds)]:
            frame=frame.copy();frame.insert(0,'partition_seed',partition_seed);items.append(frame)
        for support in SUPPORTS:
            for fold in range(5):
                early=(t.before_year.to_numpy()<=2018)&(t.region.to_numpy()!=fold)&common[support]
                cal=early&t.calibration_cell.to_numpy(bool);fit=early&~t.calibration_cell.to_numpy(bool)
                test=(t.before_year.to_numpy()>=2019)&(t.region.to_numpy()==fold)&common[support]
                for task in ['gain','loss']:
                    relevant=t[f'{task}_task'].to_numpy(bool);truth=t[f'{task}_positive'].to_numpy(bool)
                    for model in MODELS:
                        fits.append(dict(partition_seed=partition_seed,model=model,support=support,fold=fold,task=task,
                            fitting_pairs=int(fit.sum()),fitting_task_positive=int((fit&relevant&truth).sum()),
                            fitting_task_negative=int((fit&relevant&~truth).sum()),calibration_task_positive=int((cal&relevant&truth).sum()),
                            calibration_task_negative=int((cal&relevant&~truth).sum()),test_task_positive=int((test&relevant&truth).sum()),
                            test_task_negative=int((test&relevant&~truth).sum())))
                        for method in UNSUP+SUPERVISED:
                            expected_rows.append(dict(partition_seed=partition_seed,model=model,support=support,fold=fold,task=task,method=method))
        join=pred[pred.method.isin(UNSUP)].merge(original[original.method.isin(UNSUP)][KEYS+['score']],on=KEYS,suffixes=('_new','_old'),validate='one_to_one')
        error=float(np.max(abs(join.score_new-join.score_old))) if len(join) else None
        if len(join):np.testing.assert_allclose(join.score_new,join.score_old,rtol=0,atol=1e-12)
        check=dict(partition_seed=partition_seed,common_unsupervised_test_rows=len(join),maximum_unsupervised_score_error=error)
        if partition_seed==SEED:
            both=pred.merge(original[KEYS+['score','threshold','flag']],on=KEYS,suffixes=('_new','_old'),validate='one_to_one')
            assert len(both)==len(pred)==len(original)
            for name in ['score','threshold','flag']:np.testing.assert_allclose(both[name+'_new'],both[name+'_old'],rtol=0,atol=1e-12)
            both_th=th.merge(original_th[THKEYS+['threshold','calibration_negatives','calibration_false_flags','available']],on=THKEYS,suffixes=('_new','_old'),validate='one_to_one')
            assert len(both_th)==len(th)==len(original_th)
            for name in ['threshold','calibration_negatives','calibration_false_flags']:np.testing.assert_allclose(both_th[name+'_new'],both_th[name+'_old'],rtol=0,atol=1e-12,equal_nan=True)
            assert (both_th.available_new==both_th.available_old).all()
            check.update(original_prediction_rows=len(both),original_threshold_rows=len(both_th),original_reconstruction=True)
        checks.append(check)
        timings.append(dict(partition_seed=partition_seed,start_at_utc=start,end_at_utc=now(),elapsed_seconds=time.monotonic()-tick))
        (output/'progress.json').write_text(json.dumps(timings,indent=2)+'\n')
        print(json.dumps(timings[-1]),flush=True)
    metric=pd.concat(allmetrics,ignore_index=True);pair=pd.concat(allpairs,ignore_index=True);threshold=pd.concat(allthresholds,ignore_index=True)
    for name,frame in [('metrics',metric),('paired-comparisons',pair),('thresholds',threshold),('fitting-counts',pd.DataFrame(fits)),('cell-assignments',pd.DataFrame(assignments)),('invariance-checks',pd.DataFrame(checks))]:frame.to_csv(output/f'{name}.csv',index=False)
    expected=pd.DataFrame(expected_rows);status=expected.merge(threshold[['partition_seed','model','support','fold','task','method','available','calibration_negatives']],how='left',validate='one_to_one')
    status['threshold_record_present']=status.available.notna();status['available']=status.available.fillna(False).astype(bool)
    status.to_csv(output/'condition-availability.csv',index=False)
    primary=pair[(pair.support=='centre')&pair.method.isin(['concurrent','control_adjusted','direct_gradient_boosting'])]
    ranges=[]
    for key,g in primary.groupby(['model','task','method'],sort=True):
        row=dict(zip(['model','task','method'],key))
        row.update(available_partitions=len(g),positive_directions=int((g.delta_J>0).sum()),zero_directions=int((g.delta_J==0).sum()),negative_directions=int((g.delta_J<0).sum()),
            delta_J_min=float(g.delta_J.min()),delta_J_max=float(g.delta_J.max()),positive_cases_min=int(g.paired_n_positive.min()),positive_cases_max=int(g.paired_n_positive.max()),
            negative_cases_min=int(g.paired_n_negative.min()),negative_cases_max=int(g.paired_n_negative.max()),changed_flags_min=int(g.changed_flags.min()),changed_flags_max=int(g.changed_flags.max()))
        ranges.append(row)
    pd.DataFrame(ranges).to_csv(output/'primary-ranges.csv',index=False)
    summary=dict(exploratory=True,partition_seeds=list(PARTITION_SEEDS),planned_partitions=len(PARTITION_SEEDS),completed_partitions=len(timings),
        original_reconstructed_prediction_rows=checks[0]['original_prediction_rows'],original_reconstructed_threshold_rows=checks[0]['original_threshold_rows'],
        unsupervised_scores_invariant=True,expected_method_fold_conditions=len(status),available_method_fold_conditions=int(status.available.sum()),
        missing_threshold_record_conditions=int((~status.threshold_record_present).sum()),invalid_threshold_conditions=int((status.threshold_record_present&~status.available).sum()),
        primary_range_rows=len(ranges),reference_allocation_seed=SEED,learner_seed=SEED,bootstrap_condition='Conditional on each fitted split, not an interval over independent training datasets')
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (output/'input-sha256.json').write_text(json.dumps(hashes,indent=2,sort_keys=True)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--baseline',type=Path,required=True);a=ap.parse_args()
    partition_sensitivity(a.output,a.baseline)
