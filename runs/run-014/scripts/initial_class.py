"""Fixed exploratory class-rate control and subgroup reporting; no vector values."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
from analyse import summarize,SEED
from initial_readouts import equality,paired_initial
from record import ROOT

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def initial_class(output,dataset,main,initial,geography,extension=None,original=None):
    output.mkdir(parents=True,exist_ok=False)
    old=pd.read_csv(ROOT/'data/prepared/targets.csv')
    mask=pd.read_csv(main/'availability-targets.csv')
    mask=mask[(mask.model=='aef')&(mask.support=='centre')][['point_id','common_pair_available']]
    hashes={'data/prepared/targets.csv':sha(ROOT/'data/prepared/targets.csv')}
    if dataset=='nlcd':
        assert extension is not None and original is not None
        new=pd.read_csv(ROOT/'data/nlcd/prepared/targets.csv')
        t=pd.concat([old[old.before_year<=2018],new],ignore_index=True)
        more=pd.read_csv(extension/'availability-targets.csv')
        more=more[(more.model=='aef')&(more.support=='centre')]
        mask=pd.concat([mask,more[['point_id','common_pair_available']]],ignore_index=True)
        hashes['data/nlcd/prepared/targets.csv']=sha(ROOT/'data/nlcd/prepared/targets.csv')
    else:t=old
    assert mask.point_id.is_unique
    good=t.point_id.map(mask.set_index('point_id').common_pair_available)
    assert good.notna().all();good=good.to_numpy(bool)
    classes=t.label_name_before.to_numpy()
    pred=[];thresholds=[];fitting=[]
    for fold in range(5):
        early=(t.before_year.to_numpy()<=2018)&(t.region.to_numpy()!=fold)&good
        fit=early&~t.calibration_cell.to_numpy(bool);cal=early&t.calibration_cell.to_numpy(bool)
        test=(t.before_year.to_numpy()>=2019)&(t.region.to_numpy()==fold)&good
        for task in ['gain','loss']:
            relevant=t[f'{task}_task'].to_numpy(bool);truth=t[f'{task}_positive'].to_numpy(bool)
            ix=fit&relevant;pooled=(truth[ix].sum()+1)/(ix.sum()+2)
            score=np.full(len(t),pooled,dtype=float)
            for label in sorted(np.unique(classes[relevant])):
                use=ix&(classes==label);rate=(truth[use].sum()+1)/(use.sum()+2) if use.any() else pooled
                score[classes==label]=rate
                fitting.append(dict(fold=fold,task=task,initial_class=label,fit_pairs=int(use.sum()),
                    positive_pairs=int(truth[use].sum()),score=float(rate),pooled_fallback=not bool(use.any())))
            ci=cal&relevant&~truth;ti=test&relevant;valid=ci.sum()>=10
            threshold=float(np.quantile(score[ci],.9,method='higher')) if valid else None
            base=dict(availability_mode='paired',model='initial_class_only',support='centre',fold=fold,seed=SEED,
                reference_mode='not_applicable',task=task,method='initial_class_transition_rate')
            thresholds.append(dict(**base,calibration_negatives=int((ci&~truth).sum()),threshold=threshold,
                available=bool(valid),calibration_false_flags=None))
            thresholds[-1].update(threshold=threshold,available=bool(valid),
                calibration_false_flags=int((score[ci]>threshold).sum()) if valid else None,
                calibration_ties=int((score[ci]==threshold).sum()) if valid else None,test_rows=int(ti.sum()))
            if not valid:continue
            for j in np.flatnonzero(ti):
                pred.append(dict(**base,point_id=t.point_id[j],block=t.block[j],before_year=int(t.before_year[j]),
                    truth=int(truth[j]),score=float(score[j]),threshold=threshold,flag=int(score[j]>threshold)))
    pred=pd.DataFrame(pred);th=pd.DataFrame(thresholds);fit=pd.DataFrame(fitting)
    if dataset=='nlcd':
        equality(th,pd.read_csv(original/'thresholds.csv')).to_csv(output/'threshold-equality.csv',index=False)
        previous=pd.read_csv(original/'fitting-counts.csv')
        pd.testing.assert_frame_equal(fit,previous,check_exact=False,rtol=0,atol=1e-12)
        reports=[];meta=new.set_index('point_id')
        for horizon in ['overlapping_2019_2021','beyond_2021']:
            for agreement in ['primary','unambiguous']:
                ids=meta.index[(meta.horizon==horizon)&(meta.unambiguous if agreement=='unambiguous' else True)]
                q=pred[pred.point_id.isin(ids)].copy();q['availability_mode']=f'nlcd_{horizon}_{agreement}';reports.append(q)
        pred=pd.concat(reports,ignore_index=True)
    metrics,_,strata=summarize(pred)
    prior=pd.read_parquet(initial/'predictions.parquet')
    geo=pd.read_parquet(geography/'predictions.parquet')
    combined=pd.concat([prior,geo,pred],ignore_index=True)
    assert not combined.duplicated(['availability_mode','model','support','seed','reference_mode','task','method','point_id']).any()
    labels=t.set_index('point_id').label_name_before
    subgroup=[];counts=[]
    for label in sorted(labels.unique()):
        ids=labels.index[labels==label];q=combined[combined.point_id.isin(ids)].copy()
        q['availability_mode']=q.availability_mode+'_initial_'+label.replace('/','_')
        subgroup.append(q)
        for (mode,task),g in q.groupby(['availability_mode','task']):
            cases=g.drop_duplicates('point_id')
            counts.append(dict(availability_mode=mode,task=task,initial_class=label,
                n_positive=int(cases.truth.sum()),n_negative=int((cases.truth==0).sum()),n_cases=len(cases)))
    subgroup=pd.concat(subgroup,ignore_index=True)
    sm,_,ss=summarize(subgroup);sp=paired_initial(subgroup)
    for name,df in [('metrics',metrics),('strata',strata),('thresholds',th),('fitting-counts',fit),
                    ('subgroup-metrics',sm),('subgroup-strata',ss),('subgroup-initial-versus-subsequent',sp),
                    ('subgroup-counts',pd.DataFrame(counts))]:df.to_csv(output/f'{name}.csv',index=False)
    pred.to_parquet(output/'predictions.parquet',index=False)
    subgroup.to_parquet(output/'subgroup-predictions.parquet',index=False)
    (output/'input-sha256.json').write_text(json.dumps(hashes,sort_keys=True,indent=2)+'\n')
    (output/'dependency-sha256.json').write_text(json.dumps({str(k):sha(k) for k in [main/'availability-targets.csv',
        initial/'predictions.parquet',geography/'predictions.parquet']},sort_keys=True,indent=2)+'\n')
    summary=dict(dataset=dataset,exploratory=True,baseline_count=1,no_embedding_values=True,
        no_coordinates_or_year_features=True,unchanged_subgroup_thresholds=True,
        loss_initial_class_count=int(len(np.unique(classes[t.loss_task.to_numpy(bool)]))),
        loss_constant_by_construction=True)
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(metrics.to_string(index=False));print(pd.DataFrame(counts).to_string(index=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--dataset',choices=['lcmap','nlcd'],required=True)
    for name in ['main','initial','geography']:p.add_argument('--'+name,type=Path,required=True)
    for name in ['extension','original']:p.add_argument('--'+name,type=Path)
    a=p.parse_args();initial_class(a.output,a.dataset,a.main,a.initial,a.geography,a.extension,a.original)
