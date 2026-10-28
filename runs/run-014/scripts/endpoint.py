"""Exploratory v13 negative-class counterfactual and reference-state diagnostics."""
import os
os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from features import load_features,matrix,unit
from analyse import make_predictions,summarize,allocation,SEED
from record import ROOT
from figures import LABELS,MODEL_LABELS,markdown_table

def endpoint(output,baseline):
    output.mkdir(parents=True,exist_ok=False)
    vec,availability,hashes,_=load_features()
    assert availability.file_present.all()
    t=pd.read_csv(ROOT/'data/prepared/targets.csv');refs=pd.read_csv(ROOT/'data/prepared/references.csv')
    new,th,*_=make_predictions(vec,t,refs,seeds=[SEED],reference_modes=['global'],gain_stable_negatives=True)
    old=pd.read_parquet(baseline/'predictions.parquet')
    old=old[(old.availability_mode=='paired')&(old.seed==SEED)&(old.reference_mode=='global')].copy()
    keys=['model','support','fold','task','method','point_id']
    joined=new.merge(old[keys+['score','flag','threshold']],on=keys,suffixes=('_new','_old'),validate='one_to_one')
    assert len(joined)==len(new)
    np.testing.assert_allclose(joined.score_new,joined.score_old,rtol=0,atol=1e-12)
    loss=joined.task=='loss'
    np.testing.assert_allclose(joined.loc[loss,'threshold_new'],joined.loc[loss,'threshold_old'],rtol=0,atol=1e-12)
    assert (joined.loc[loss,'flag_new']==joined.loc[loss,'flag_old']).all()
    new['availability_mode']='paired_stable_negatives';th['availability_mode']='paired_stable_negatives'
    new.to_parquet(output/'predictions.parquet',index=False);th.to_csv(output/'thresholds.csv',index=False)
    metrics,pairs,strata=summarize(new)
    for name,df in [('metrics',metrics),('paired-comparisons',pairs),('strata',strata)]:df.to_csv(output/f'{name}.csv',index=False)
    excluded=t[t.gain_task&~t.gain_positive&(t.label_name_before!=t.label_name_after)].copy()
    excluded['phase']=np.where(excluded.before_year<=2018,'earlier','later')
    excluded[['point_id','before_year','label_name_before','label_name_after','phase']].to_csv(output/'excluded-gain-negative-pairs.csv',index=False)
    counts=t.copy();counts['phase']=np.where(counts.before_year<=2018,'earlier','later')
    counts.groupby(['phase','before_year','label_name_before','label_name_after']).size().rename('n').reset_index().to_csv(output/'class-route-counts.csv',index=False)
    # Reconstruct scalar components from independently saved method outputs.
    centre=old[old.support=='centre']
    index=['model','task','point_id','fold','before_year','truth']
    states=centre.pivot(index=index,columns='method',values='score').reset_index()
    direction=np.where(states.task=='gain',1,-1)
    states['before_similarity']=direction*(states.subsequent_reference_similarity-states.concurrent)
    states['after_similarity']=states.before_similarity+direction*states.start_fixed
    states=states.merge(t[['point_id','label_name_before','label_name_after']],on='point_id',validate='many_to_one')
    roles=allocation(refs,SEED);checks=[]
    for (model,fold,year),g in states.groupby(['model','fold','before_year']):
        active=(roles=='R')&(refs.region.to_numpy()!=fold)
        rv=matrix(vec,model,'centre',refs.loc[active,'point_id']+'-'+str(year))
        rv=rv[np.isfinite(rv).all(1)];reference=unit(rv.mean(0))
        before=matrix(vec,model,'centre',g.point_id+'-'+str(year))@reference
        after=matrix(vec,model,'centre',g.point_id+'-'+str(year+1))@reference
        error=max(float(abs(before-g.before_similarity).max()),float(abs(after-g.after_similarity).max()))
        assert error<=1e-12
        checks.append(dict(model=model,fold=int(fold),before_year=int(year),pairs=len(g),maximum_absolute_error=error))
    pd.DataFrame(checks).to_csv(output/'scalar-reconstruction-check.csv',index=False)
    states.to_csv(output/'reference-state-pairs.csv',index=False)
    summaries=[]
    for key,g in states.groupby(['model','task','truth','label_name_before','label_name_after']):
        row=dict(zip(['model','task','truth','label_name_before','label_name_after'],key));row['n']=len(g)
        for label in ['before_similarity','after_similarity']:
            for quantile in [.1,.5,.9]:row[f'{label}_q{int(quantile*100)}']=float(g[label].quantile(quantile))
        row['median_absolute_change']=float(abs(g.after_similarity-g.before_similarity).median())
        summaries.append(row)
    pd.DataFrame(summaries).to_csv(output/'reference-state-summary.csv',index=False)
    os.environ.setdefault('MPLCONFIGDIR',str(output/'matplotlib-cache'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(2,2,figsize=(9,8),layout='constrained')
    for i,model in enumerate(['aef','tessera']):
        product=states[states.model==model]
        lower=float(min(product.before_similarity.min(),product.after_similarity.min()))-.025
        for j,task in enumerate(['gain','loss']):
            ax=axes[i,j];g=product[product.task==task]
            categories=[(g.truth==1,'Target transition (positive)','tab:green','o'),
                ((g.truth==0)&(g.label_name_before==g.label_name_after),'Unchanged cover (negative)','tab:blue','o'),
                ((g.truth==0)&(g.label_name_before!=g.label_name_after),'Grass/Shrub transition (negative)','tab:orange','x')]
            for mask,label,colour,marker in categories:
                q=g[mask]
                if len(q):ax.scatter(q.before_similarity,q.after_similarity,s=17,alpha=.65,color=colour,marker=marker,label=label)
            ax.plot([lower,1.025],[lower,1.025],color='grey',ls=':',lw=1)
            ax.set(xlim=(lower,1.025),ylim=(lower,1.025),title=f'{MODEL_LABELS[model]}: tree {task}')
            ax.grid(alpha=.15)
            if i==1:ax.set_xlabel('Before similarity to start-year reference')
            if j==0:ax.set_ylabel('After similarity to start-year reference')
    handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside lower center',ncol=1,fontsize=8)
    fig.savefig(output/'reference-similarity.png',dpi=200);fig.savefig(output/'reference-similarity.pdf');plt.close(fig)
    table=metrics[(metrics.support=='centre')&(metrics.task=='gain')].copy()
    table['model']=table.model.map(MODEL_LABELS);table['method']=table.method.map(LABELS)
    fmt={k:lambda v:f'{v:.3f}' for k in ['sensitivity','false_positive_rate','J','auroc']}
    (output/'stable-negative-gain-table.md').write_text(markdown_table(table,{'model':'Representation','method':'Readout',
        'n_positive':'Positives','n_negative':'Unchanged-cover negatives','true_positive':'True positives','false_positive':'False positives',
        'sensitivity':'Sensitivity','false_positive_rate':'False-positive rate','J':'J','auroc':'AUROC'},fmt))
    summary=dict(exploratory=True,score_invariance=True,loss_flags_invariant=True,common_scored_rows=len(joined),
        excluded_planned_gain_negatives=len(excluded),excluded_later_gain_negatives=int((excluded.phase=='later').sum()),
        scalar_pairs=len(states),maximum_scalar_reconstruction_error=max(r['maximum_absolute_error'] for r in checks))
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (output/'input-sha256.json').write_text(json.dumps(hashes,sort_keys=True,indent=2)+'\n')
    print(json.dumps(summary,indent=2));print(metrics[(metrics.support=='centre')&(metrics.task=='gain')].to_string(index=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True)
    a=p.parse_args();endpoint(a.output,a.baseline)
