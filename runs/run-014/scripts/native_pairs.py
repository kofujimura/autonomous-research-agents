"""V21: stratified paired native target inputs with mosaic fitting/calibration fixed."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
from record import ROOT,now
from prepare import digest
from features import load_features,unit
from analyse import make_predictions,SEED
from initial_readouts import equality

def prepare_native_pairs(output):
    output.mkdir(parents=True,exist_ok=False)
    t=pd.read_csv(ROOT/'data/prepared/targets.csv');t=t[t.before_year>=2019].copy()
    t['selection_hash']=[digest(SEED,'native_pair',i) for i in t.point_id]
    groups=[]
    for task in ['gain','loss']:
        for positive in [True,False]:
            q=t[t[f'{task}_task']&(t[f'{task}_positive']==positive)].sort_values('selection_hash').head(4).copy()
            assert len(q)==4;q['sample_group']=task+('_positive' if positive else '_negative');groups.append(q)
    selected=pd.concat(groups,ignore_index=True);assert selected.point_id.is_unique
    selected.to_csv(output/'targets.csv',index=False)
    tasks=[]
    for r in selected.itertuples():
        for year in [r.before_year,r.after_year]:
            tid=f'{r.point_id}-{year}'
            tasks.append(dict(task_id=tid,point_id=r.point_id,x=r.x,y=r.y,year=year,role='native_pair_target',
                sample_group=r.sample_group,order_hash=digest(SEED,'native_pair_retrieval',tid)))
    tasks=pd.DataFrame(tasks).sort_values('order_hash').reset_index(drop=True);assert tasks.task_id.is_unique
    tasks.to_csv(output/'tasks.csv',index=False)
    summary=dict(created_at_utc=now(),pairs=len(selected),point_years=len(tasks),seed=SEED,
        groups=selected.sample_group.value_counts().to_dict(),
        already_present_at_preparation=sum((ROOT/'data/native-check'/f'{i}.npz').exists() for i in tasks.task_id),
        note='Presence at preparation is historical metadata, not a reproducible result from current files; pre-existing values not inspected for selection.')
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))

def prepare_native_available(output):
    output.mkdir(parents=True,exist_ok=False)
    t=pd.read_csv(ROOT/'data/prepared/targets.csv');t=t[t.before_year>=2019].copy()
    tasks=[];ids=[]
    for r in t.itertuples():
        years=[]
        for year in [r.before_year,r.after_year]:
            tid=f'{r.point_id}-{year}'
            if (ROOT/'data/native-check'/f'{tid}.npz').exists():
                years.append(year)
                tasks.append(dict(task_id=tid,point_id=r.point_id,x=r.x,y=r.y,year=year,role='saved_native_target',
                    sample_group=('gain' if r.gain_task else 'loss')+('_positive' if (r.gain_positive if r.gain_task else r.loss_positive) else '_negative')))
        if years:ids.append((r.point_id,r.before_year in years,r.after_year in years))
    selected=t[t.point_id.isin([i[0] for i in ids])].copy()
    meta=pd.DataFrame(ids,columns=['point_id','replace_before','replace_after'])
    selected=selected.merge(meta,on='point_id',validate='one_to_one')
    selected['sample_group']=[('gain' if r.gain_task else 'loss')+('_positive' if (r.gain_positive if r.gain_task else r.loss_positive) else '_negative') for r in selected.itertuples()]
    selected.to_csv(output/'targets.csv',index=False)
    pd.DataFrame(tasks).sort_values('task_id').to_csv(output/'tasks.csv',index=False)
    summary=dict(created_at_utc=now(),selected_pairs=len(selected),native_point_years=len(tasks),
        before_only=int((selected.replace_before&~selected.replace_after).sum()),
        after_only=int((~selected.replace_before&selected.replace_after).sum()),
        both_dates=int((selected.replace_before&selected.replace_after).sum()),
        groups=selected.sample_group.value_counts().to_dict(),
        selection='All saved native point-years for original later targets; availability-selected, no new retrieval.')
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))

def status_fields(selected,availability,comparison,partial_native_dates):
    available=availability.set_index('task_id')
    def both(field):
        return sum(all(f'{r.point_id}-{year}' in available.index and bool(available.loc[f'{r.point_id}-{year}',field])
                       for year in [r.before_year,r.after_year]) for r in selected.itertuples())
    evaluated={s:int(comparison[(comparison.support==s)&comparison.both_available].point_id.nunique()) for s in ['centre','patch']}
    return dict(design='saved_single_date_substitution' if partial_native_dates else 'fixed_paired_native',
        status=('evaluated_partial_date_cases' if partial_native_dates else 'evaluated_native_pairs') if evaluated['centre'] else 'not_tested_no_complete_native_pairs',
        complete_native_file_pairs=both('file_present'),complete_native_centre_pairs=both('centre_valid'),
        complete_native_patch_pairs=both('patch_valid'),evaluated_pairs_by_support=evaluated,
        missing_dates_remain_mosaic=bool(partial_native_dates),
        interpretation=('Saved single-date substitutions; other dates, fitting, references and calibration remain mosaic. Not full native pairs or population performance.'
            if partial_native_dates else ('No complete paired native score comparison. Zero raw counts at common_cases=0 are empty counts, not observed zero sensitivity or stability.'
            if not evaluated['centre'] else 'Small stratified target-input substitution; fitting/references/calibration remain mosaic. Not population native-grid performance.')))

def refresh_status(output,sample,partial_native_dates=False):
    report=json.loads((output/'checks.json').read_text())
    report.update(status_fields(pd.read_csv(sample/'targets.csv'),pd.read_csv(output/'availability.csv'),
        pd.read_csv(output/'comparisons.csv'),partial_native_dates))
    (output/'checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

def native_pairs(output,baseline,sample=ROOT/'data/native-pairs',partial_native_dates=False):
    output.mkdir(parents=True,exist_ok=False)
    vec,_,hashes,_=load_features();replacement={k:dict(v) for k,v in vec.items()}
    t=pd.read_csv(ROOT/'data/prepared/targets.csv');refs=pd.read_csv(ROOT/'data/prepared/references.csv')
    selected=pd.read_csv(sample/'targets.csv');tasks=pd.read_csv(sample/'tasks.csv')
    early=t[t.before_year<=2018]
    protected=set(early.point_id+'-'+early.before_year.astype(str))|set(early.point_id+'-'+early.after_year.astype(str))
    assert not set(tasks.task_id)&protected
    assert not set(selected.point_id)&set(refs.point_id)
    availability=[]
    for r in tasks.itertuples():
        p=ROOT/'data/native-check'/f'{r.task_id}.npz'
        for support in ['centre','patch']:replacement['aef',support][r.task_id]=np.full(64,np.nan)
        rec=dict(task_id=r.task_id,point_id=r.point_id,year=r.year,sample_group=r.sample_group,file_present=p.exists(),
                 centre_valid=False,patch_valid=False,acquisition_role=None)
        if p.exists():
            with np.load(p,allow_pickle=False) as f:raw=f['raw'];meta=json.loads(str(f['metadata']))
            assert raw.shape==(3,3,64) and raw.dtype==np.int8
            np.testing.assert_allclose([meta['lon'],meta['lat']],[r.x,r.y],rtol=0,atol=1e-10)
            assert meta['year']==r.year
            x=raw.astype(float);x=np.sign(x)*(x/127.5)**2;x[(raw==-128).any(-1)]=np.nan;u=unit(x)
            replacement['aef','centre'][r.task_id]=u[1,1]
            replacement['aef','patch'][r.task_id]=unit(u.mean((0,1))) if np.isfinite(u).all() else np.full(64,np.nan)
            rec.update(centre_valid=bool(np.isfinite(replacement['aef','centre'][r.task_id]).all()),
                patch_valid=bool(np.isfinite(replacement['aef','patch'][r.task_id]).all()),acquisition_role=meta['role'])
            hashes[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
        availability.append(rec)
    pred,th,_,_,_=make_predictions(replacement,t,refs,seeds=[SEED],reference_modes=['global'],models=['aef'])
    before=pd.read_parquet(baseline/'predictions.parquet')
    before=before[(before.availability_mode=='paired')&(before.model=='aef')&(before.seed==SEED)&(before.reference_mode=='global')]
    prior_th=pd.read_csv(baseline/'thresholds.csv')
    prior_th=prior_th[(prior_th.availability_mode=='paired')&(prior_th.model=='aef')&(prior_th.seed==SEED)&(prior_th.reference_mode=='global')]
    equality(th,prior_th).to_csv(output/'threshold-equality.csv',index=False)
    keys=['model','support','fold','seed','reference_mode','task','method','point_id']
    ids=set(selected.point_id)
    a=pred[~pred.point_id.isin(ids)].sort_values(keys).reset_index(drop=True)
    b=before[~before.point_id.isin(ids)].sort_values(keys).reset_index(drop=True)
    pd.testing.assert_frame_equal(a[keys+['truth','flag']],b[keys+['truth','flag']])
    np.testing.assert_allclose(a.score,b.score,rtol=0,atol=1e-12)
    old=before[before.point_id.isin(ids)][keys+['truth','score','threshold','flag']]
    new=pred[pred.point_id.isin(ids)][keys+['score','threshold','flag']]
    comparison=old.merge(new,on=keys,suffixes=('_mosaic','_native'),how='left',validate='one_to_one')
    comparison['sample_group']=comparison.point_id.map(selected.set_index('point_id').sample_group)
    comparison['both_available']=comparison.score_native.notna()
    comparison['changed_flag']=comparison.both_available&(comparison.flag_mosaic!=comparison.flag_native)
    comparison['absolute_score_difference']=(comparison.score_native-comparison.score_mosaic).abs()
    summaries=[]
    for (support,task,method),g in comparison.groupby(['support','task','method']):
        q=g[g.both_available];pos=q.truth==1;neg=q.truth==0
        summaries.append(dict(support=support,task=task,method=method,planned_cases=len(g),common_cases=len(q),
            positive_cases=int(pos.sum()),negative_cases=int(neg.sum()),changed_flags=int(q.changed_flag.sum()),
            mosaic_true_positive=int(q.loc[pos,'flag_mosaic'].sum()),native_true_positive=int(q.loc[pos,'flag_native'].sum()),
            mosaic_false_positive=int(q.loc[neg,'flag_mosaic'].sum()),native_false_positive=int(q.loc[neg,'flag_native'].sum()),
            maximum_absolute_score_difference=q.absolute_score_difference.max() if len(q) else None))
    comparison.to_csv(output/'comparisons.csv',index=False);pd.DataFrame(summaries).to_csv(output/'summary.csv',index=False)
    pd.DataFrame(availability).to_csv(output/'availability.csv',index=False)
    th.to_csv(output/'thresholds.csv',index=False)
    (output/'input-sha256.json').write_text(json.dumps(hashes,sort_keys=True,indent=2)+'\n')
    report=dict(exploratory=True,planned_pairs=len(selected),planned_point_years=len(tasks),
        present_point_years=sum(r['file_present'] for r in availability),unselected_invariance_rows=len(a),
        unselected_scores_flags_unchanged=True,earlier_thresholds_unchanged=True,
        **status_fields(selected,pd.DataFrame(availability),comparison,partial_native_dates))
    (output/'checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
    print(pd.DataFrame(summaries).to_string(index=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','prepare_available','analyse','refresh_status']);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--baseline',type=Path);p.add_argument('--sample',type=Path,default=ROOT/'data/native-pairs')
    p.add_argument('--partial-native-dates',action='store_true');a=p.parse_args()
    if a.action=='prepare':prepare_native_pairs(a.output)
    elif a.action=='prepare_available':prepare_native_available(a.output)
    elif a.action=='refresh_status':refresh_status(a.output,a.sample,a.partial_native_dates)
    else:native_pairs(a.output,a.baseline,a.sample,a.partial_native_dates)
