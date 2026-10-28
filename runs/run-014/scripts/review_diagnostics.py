"""Exploratory saved-data diagnostics fixed after review-014-1."""
import os
os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
import argparse,json,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score
from features import load_features,matrix,unit,MODELS
from analyse import allocation,SEED
from record import ROOT


def run(output,baseline):
    output.mkdir(parents=True,exist_ok=False)
    vectors,availability,hashes,_=load_features(include_nlcd=True,include_controls=True)
    t=pd.read_csv(ROOT/'data/prepared/targets.csv');refs=pd.read_csv(ROOT/'data/prepared/references.csv');roles=allocation(refs,SEED)
    pred=pd.read_parquet(baseline/'predictions.parquet')
    pred=pred[(pred.availability_mode=='paired')&(pred.support=='centre')&(pred.seed==SEED)&(pred.reference_mode=='global')].copy()
    if baseline.is_relative_to(ROOT):
        hashes[str((baseline/'predictions.parquet').relative_to(ROOT))]=hashlib.sha256((baseline/'predictions.parquet').read_bytes()).hexdigest()
    for rel in ['data/prepared/targets.csv','data/prepared/references.csv']:
        hashes[rel]=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
    centroids={};counts=[];drifts=[];cohort_rows=[]
    for model in MODELS:
        annual={year:matrix(vectors,model,'centre',refs.point_id+'-'+str(year)) for year in range(2017,2024)}
        for fold in range(5):
            ri=(roles=='R')&(refs.region.to_numpy()!=fold);ci=(roles=='C')&(refs.region.to_numpy()!=fold)
            for year in range(2017,2024):
                rv=annual[year][ri];cv=annual[year][ci];valid=np.isfinite(rv).all(1)
                centroids[model,fold,year]=unit(rv[valid].mean(0))
                counts.append(dict(model=model,fold=fold,year=year,reference_pool_outside_fold=int(ri.sum()),control_pool_outside_fold=int(ci.sum()),reference_valid=int(valid.sum()),control_valid=int(np.isfinite(cv).all(1).sum())))
            for start in range(2017,2023):
                for end in [start+1]+([y for y in range(start+2,2024)] if start==2017 else []):
                    ra,rb=annual[start][ri],annual[end][ri];ca,cb=annual[start][ci],annual[end][ci]
                    va=np.isfinite(ra).all(1);vb=np.isfinite(rb).all(1);rp=va&vb;cp=np.isfinite(ca).all(1)&np.isfinite(cb).all(1)
                    r0=centroids[model,fold,start];r1=centroids[model,fold,end]
                    values={}
                    for role,a,b,mask in [('R',ra,rb,rp),('C',ca,cb,cp)]:
                        mag=1-np.einsum('ij,ij->i',a[mask],b[mask]);values[role]=mag
                        for index,value in zip(refs.loc[ri if role=='R' else ci,'point_id'].to_numpy()[mask],mag):cohort_rows.append(dict(model=model,fold=fold,start_year=start,end_year=end,role=role,point_id=index,cosine_dissimilarity=float(value)))
                    drifts.append(dict(model=model,fold=fold,start_year=start,end_year=end,interval='one_year' if end==start+1 else 'from_2017_multi_year',reference_before=int(va.sum()),reference_after=int(vb.sum()),reference_paired=int(rp.sum()),control_paired=int(cp.sum()),centroid_dissimilarity=float(1-r0@r1),same_membership_centroid_dissimilarity=float(1-unit(ra[rp].mean(0))@unit(rb[rp].mean(0))),reference_individual_median=float(np.median(values['R'])),control_individual_median=float(np.median(values['C'])),control_mean_projection_change=float(np.mean((cb[cp]-ca[cp])@r0)),available=bool(min(va.sum(),vb.sum(),cp.sum())>=8)))
    d=pd.DataFrame(drifts);c=pd.DataFrame(counts)
    old=pd.read_csv(baseline/'reference-availability.csv');old=old[(old.availability_mode=='paired')&(old.support=='centre')&(old.seed==SEED)&(old.reference_mode=='global')]
    check=old.merge(d[d.interval=='one_year'],left_on=['model','fold','before_year'],right_on=['model','fold','start_year'],suffixes=('_old','_new'),validate='one_to_one')
    assert len(check)==len(old)
    for col in ['reference_before','reference_after']:assert (check[col+'_old']==check[col+'_new']).all()
    assert (check.control_pairs==check.control_paired).all()
    c.to_csv(output/'reference-year-counts.csv',index=False);d.to_csv(output/'reference-drift.csv',index=False);pd.DataFrame(cohort_rows).to_csv(output/'individual-cohort-change.csv',index=False)
    selected=t.merge(pred[(pred.model=='aef')&(pred.method=='start_fixed')][['point_id','task','truth']].drop_duplicates('point_id'),on='point_id',validate='one_to_one')
    sample=[]
    for task,g in selected.groupby('task'):
        for dimension,columns in [('year',['before_year']),('region',['region']),('year_region',['before_year','region'])]:
            for key,h in g.groupby(columns):
                key=key if isinstance(key,tuple) else (key,);z=dict(zip(columns,key));positive=h.truth==1
                sample.append(dict(task=task,dimension=dimension,before_year=z.get('before_year'),region=z.get('region'),positive_pairs=int(positive.sum()),negative_pairs=int((~positive).sum()),positive_cells=int(h[positive].block.nunique()),negative_cells=int(h[~positive].block.nunique())))
    pd.DataFrame(sample).to_csv(output/'sample-support.csv',index=False)
    similarities=[];constants=[]
    keys=['point_id','fold','before_year','truth']
    for (model,task),g in pred.groupby(['model','task']):
        base=g[g.method=='start_fixed'][keys+['score','flag']]
        for method in ['concurrent','control_adjusted']:
            q=g[g.method==method][keys+['score','flag']].merge(base,on=keys,suffixes=('_corrected','_fixed'),validate='one_to_one')
            for label,h in [('all',q)]+[(str(y),h) for y,h in q.groupby('before_year')]:
                similarities.append(dict(model=model,task=task,method=method,period=label,cases=len(h),spearman_rho=float(spearmanr(h.score_corrected,h.score_fixed).statistic),changed_alerts=int((h.flag_corrected!=h.flag_fixed).sum()),changed_alert_fraction=float((h.flag_corrected!=h.flag_fixed).mean())))
            if method=='control_adjusted':
                for (fold,year),h in q.groupby(['fold','before_year']):
                    delta=h.score_fixed-h.score_corrected
                    constants.append(dict(model=model,task=task,fold=fold,before_year=year,cases=len(h),mean_subtraction=float(delta.mean()),sd_subtraction=float(delta.std(ddof=0))))
    pd.DataFrame(similarities).to_csv(output/'score-similarity.csv',index=False);pd.DataFrame(constants).to_csv(output/'control-constancy.csv',index=False)
    target_summary=[];all_target_magnitudes=[]
    ids=[t.point_id+'-'+t.before_year.astype(str),t.point_id+'-'+t.after_year.astype(str)]
    arrays={m:[matrix(vectors,m,'centre',idx) for idx in ids] for m in MODELS};good=np.logical_and.reduce([np.isfinite(a).all(1) for pair in arrays.values() for a in pair])
    for model,(a,b) in arrays.items():
        q=t[good].copy();q['magnitude']=1-np.einsum('ij,ij->i',a[good],b[good]);q['phase']=np.where(q.before_year<=2018,'earlier','test')
        q['task']=np.where(q.gain_task,'gain','loss');q['truth']=np.where(q.gain_task,q.gain_positive,q.loss_positive).astype(int)
        q['category']=np.where(q.truth==1,'target_transition',np.where(q.label_name_before==q.label_name_after,'unchanged_cover','Grass_Shrub_transition'))
        q['model']=model;all_target_magnitudes.append(q[['point_id','model','region','before_year','phase','task','truth','category','magnitude']])
        for key,h in q.groupby(['region','before_year','phase','task','truth','category']):target_summary.append(dict(model=model,**dict(zip(['fold','before_year','phase','task','truth','category'],key)),pairs=len(h),median_magnitude=float(h.magnitude.median())))
    pd.concat(all_target_magnitudes).to_csv(output/'target-magnitudes.csv',index=False);pd.DataFrame(target_summary).to_csv(output/'target-magnitude-summary.csv',index=False)
    magnitude=pred[pred.method=='cosine_change'].merge(t[['point_id','label_name_before','label_name_after']],on='point_id',validate='many_to_one')
    raw=pd.concat(all_target_magnitudes);joined=magnitude.merge(raw[['point_id','model','magnitude']],on=['point_id','model'],validate='one_to_one')
    error=float(abs(joined.score-joined.magnitude).max());assert error<=1e-12
    ranking=[];medians=[]
    for model,g in magnitude[magnitude.task=='gain'].groupby('model'):
        g=g.copy();g['category']=np.where(g.truth==1,'gain',np.where(g.label_name_before==g.label_name_after,'unchanged_non_tree','Grass_Shrub_transition'))
        for period,h in [('all',g)]+[(str(y),h) for y,h in g.groupby('before_year')]:
            for category,k in h.groupby('category'):medians.append(dict(model=model,period=period,category=category,pairs=len(k),median_magnitude=float(k.score.median())))
            for definition in ['all_negatives','unchanged_only']:
                k=h if definition=='all_negatives' else h[(h.truth==1)|(h.category=='unchanged_non_tree')]
                ranking.append(dict(model=model,period=period,negative_definition=definition,positive_pairs=int((k.truth==1).sum()),negative_pairs=int((k.truth==0).sum()),auroc=float(roc_auc_score(k.truth,k.score)),median_positive=float(k[k.truth==1].score.median()),median_negative=float(k[k.truth==0].score.median())))
    pd.DataFrame(ranking).to_csv(output/'magnitude-ranking.csv',index=False);pd.DataFrame(medians).to_csv(output/'magnitude-medians.csv',index=False)
    summary=dict(exploratory=True,added_after_review='review-014-1',support='centre',reference_allocation_seed=SEED,reference_availability_rows_reconstructed=len(check),raw_target_scores_reconstructed=len(joined),maximum_raw_target_score_error=error,reference_drift_rows=len(d),reference_count_rows=len(c),primary_similarity_rows=int((pd.DataFrame(similarities).period=='all').sum()),unchanged_original_predictions=True)
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');(output/'input-sha256.json').write_text(json.dumps(hashes,indent=2,sort_keys=True)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--baseline',type=Path,required=True);a=ap.parse_args();run(a.output,a.baseline.resolve())
