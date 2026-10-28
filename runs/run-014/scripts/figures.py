"""Scientific figures and Markdown tables generated directly from analysis outputs."""
import os
from pathlib import Path
import numpy as np
import pandas as pd

LABELS={'start_fixed':'Start-year reference','end_fixed':'End-year reference','pooled_fixed':'Pooled reference',
        'concurrent':'Concurrent reference','control_adjusted':'Tree controls','standardized_concurrent':'Standardized concurrent',
        'state_random_forest':'State random forest','direct_gradient_boosting':'Direct gradient boosting',
        'subsequent_state_random_forest':'Subsequent-state forest','subsequent_state_logistic':'Subsequent-state logistic',
        'cosine_change':'Cosine change magnitude','subsequent_reference_similarity':'Subsequent-reference similarity',
        'non_tree_control_adjusted':'Non-tree controls','class_matched_control_adjusted':'Initial-class controls',
        'nearest8_non_tree_control_adjusted':'Nearest non-tree controls','frozen_2017':'Frozen 2017 reference',
        'frozen_2017_control_adjusted':'Frozen 2017 + tree controls',
        'baseline_cohort_random_forest':'Baseline-cohort forest',
        'baseline_cohort_logistic':'Baseline-cohort logistic',
        'embedding_matched_controls':'Embedding-matched controls'}
MODEL_LABELS={'aef':'AlphaEarth V1 mosaic','tessera':'TESSERA v1'}
PLOT_ORDER=['start_fixed','concurrent','control_adjusted','standardized_concurrent','cosine_change',
            'subsequent_reference_similarity','state_random_forest','direct_gradient_boosting',
            'subsequent_state_random_forest','subsequent_state_logistic']
LABELS.update(initial_reference_similarity='Initial-year reference similarity',
              subsequent_start_reference_similarity='Subsequent similarity to start reference',
              initial_state_random_forest='Initial-vector state forest',
              initial_baseline_cohort_random_forest='Initial-vector cohort forest',
              initial_baseline_cohort_logistic='Initial-vector cohort logistic')
LABELS.update(direct_before='Direct learner: before only',direct_after='Direct learner: after only',
              direct_difference='Direct learner: difference only')

def markdown_table(df,columns,formatters=None):
    formatters=formatters or {}
    lines=['| '+' | '.join(columns.values())+' |','| '+' | '.join(['---']*len(columns))+' |']
    for _,row in df.iterrows():
        vals=[]
        for key in columns:
            v=row[key];f=formatters.get(key)
            vals.append(f(v) if f else str(v))
        lines.append('| '+' | '.join(vals)+' |')
    return '\n'.join(lines)+'\n'

def generate(main,secondary,output,overwrite=False):
    output.mkdir(parents=True,exist_ok=overwrite)
    os.environ.setdefault('MPLCONFIGDIR',str(output/'matplotlib-cache'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    t=pd.read_csv(main/'main-table.csv')
    # Complete tables retain every readout; the operating-point figure shows this explicit subset.
    order=PLOT_ORDER
    colours=plt.get_cmap('tab10')
    fig,axes=plt.subplots(2,2,figsize=(10,8),sharex=True,sharey=True,layout='constrained')
    for i,model in enumerate(['aef','tessera']):
        for j,task in enumerate(['gain','loss']):
            ax=axes[i,j];g=t[(t.model==model)&(t.task==task)]
            for k,m in enumerate(order):
                q=g[g.method==m]
                if not len(q):continue
                r=q.iloc[0]
                ax.plot([r.false_positive_rate_lo,r.false_positive_rate_hi],[r.sensitivity]*2,color=colours(k),alpha=.6,lw=1)
                ax.plot([r.false_positive_rate]*2,[r.sensitivity_lo,r.sensitivity_hi],color=colours(k),alpha=.6,lw=1)
                ax.plot(r.false_positive_rate,r.sensitivity,marker='o' if k<6 else 's',ls='',color=colours(k),alpha=.85,
                        label=LABELS[m] if i==0 and j==0 else None)
            ax.axvline(.1,color='grey',ls=':',lw=1)
            npos=int(g.n_positive.max());nneg=int(g.n_negative.max())
            prefix='up to ' if g.n_positive.nunique()>1 or g.n_negative.nunique()>1 else ''
            ax.set_title(f'{MODEL_LABELS[model]}: tree {task}\n{prefix}{npos} positive / {nneg} negative pairs',fontsize=10)
            ax.set(xlim=(-.025,1.025),ylim=(-.025,1.025));ax.grid(alpha=.15)
            if i==1:ax.set_xlabel('Held-out false-positive rate')
            if j==0:ax.set_ylabel('Held-out sensitivity')
    handles,labels=axes[0,0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='outside lower center',ncol=3,fontsize=8)
    fig.suptitle('Thresholds calibrated on earlier years outside the held-out region',fontsize=12)
    fig.savefig(output/'operating-points.png',dpi=200);fig.savefig(output/'operating-points.pdf');plt.close(fig)
    # Reference allocation and support sensitivity retain every prespecified run.
    p=pd.read_csv(main/'paired-comparisons.csv')
    p=p[(p.availability_mode=='paired')&(p.reference_mode=='global')&p.method.isin(['concurrent','control_adjusted'])]
    fig,axes=plt.subplots(1,2,figsize=(10,4),sharey=True,layout='constrained')
    for j,task in enumerate(['gain','loss']):
        ax=axes[j];labels=[];tick=[];pos=0
        for model in ['aef','tessera']:
            for support in ['centre','patch']:
                for method in ['concurrent','control_adjusted']:
                    q=p[(p.task==task)&(p.model==model)&(p.support==support)&(p.method==method)]
                    if not len(q):continue
                    ax.scatter(np.full(len(q),pos),q.delta_J,s=18,color=colours(PLOT_ORDER.index(method)),alpha=.75)
                    tick.append(pos);labels.append(f'{MODEL_LABELS[model]}\n{support}\n'+('Concurrent' if method=='concurrent' else 'Controls'));pos+=1
        ax.axhline(0,color='grey',lw=1);ax.set_title(f'Tree {task}')
        ax.set_xticks(tick,labels,rotation=65,ha='right',fontsize=7);ax.grid(axis='y',alpha=.15)
        if j==0:ax.set_ylabel('J difference versus start-year reference')
    fig.savefig(output/'allocation-support-sensitivity.png',dpi=200);plt.close(fig)
    t=t.copy();t['model']=t.model.map(MODEL_LABELS);t['method']=t.method.map(LABELS)
    fmt={k:(lambda v:'NA' if pd.isna(v) else f'{v:.3f}') for k in ['sensitivity','false_positive_rate','J','auroc']}
    (output/'main-table.md').write_text(markdown_table(t,{'model':'Representation','task':'Task','method':'Readout',
                 'true_positive':'True positives','n_positive':'Positives','false_positive':'False positives','n_negative':'Negatives',
                 'sensitivity':'Sensitivity','false_positive_rate':'False-positive rate','J':'J','auroc':'AUROC'},fmt))
    sec=pd.read_csv(secondary/'metrics.csv');sec=sec[(sec.support=='centre')&sec.method.isin(list(LABELS)[12:])].copy()
    sec['model']=sec.model.map(MODEL_LABELS);sec['method']=sec.method.map(LABELS)
    (output/'secondary-table.md').write_text(markdown_table(sec,{'model':'Representation','task':'Task','method':'Readout',
                 'n_positive':'Positives','n_negative':'Negatives','sensitivity':'Sensitivity','false_positive_rate':'False-positive rate','J':'J'},fmt))

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--main',type=Path,required=True);p.add_argument('--secondary',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();generate(a.main,a.secondary,a.output)
