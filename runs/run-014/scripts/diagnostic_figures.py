"""Exploratory displays from saved v12 and preplanned secondary estimates."""
import argparse,os
from pathlib import Path
import pandas as pd
from figures import LABELS,MODEL_LABELS,markdown_table,PLOT_ORDER

def generate_diagnostics(robustness,secondary,output):
    output.mkdir(parents=True,exist_ok=True) # Presentation files may be rerendered; earlier versions remain in Git.
    os.environ.setdefault('MPLCONFIGDIR',str(output/'matplotlib-cache'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    cal=pd.read_csv(robustness/'calibration-metrics.csv')
    cal['nominal_fpr']=cal.availability_mode.str.extract(r'_fpr_(\d+)$')[0].astype(int)/100
    order=['start_fixed','concurrent','control_adjusted','state_random_forest','direct_gradient_boosting']
    colours=plt.get_cmap('tab10');fig,axes=plt.subplots(2,2,figsize=(10,8),sharex=True,sharey=True,layout='constrained')
    levels=sorted(cal.nominal_fpr.unique());sizes={f:20+300*f for f in levels}
    for i,model in enumerate(['aef','tessera']):
        for j,task in enumerate(['gain','loss']):
            ax=axes[i,j]
            for k,method in enumerate(order):
                colour=colours(PLOT_ORDER.index(method))
                q=cal[(cal.model==model)&(cal.task==task)&(cal.method==method)].sort_values('nominal_fpr')
                if not len(q):continue
                ax.plot(q.false_positive_rate,q.sensitivity,color=colour,lw=1,
                        label=LABELS[method] if i==0 and j==0 else None)
                for r in q.itertuples():
                    ax.scatter(r.false_positive_rate,r.sensitivity,s=sizes[r.nominal_fpr],color=colour,alpha=.7)
            ax.set(xlim=(-.02,1.02),ylim=(-.02,1.02),title=f'{MODEL_LABELS[model]}: tree {task}')
            ax.grid(alpha=.15)
            if i==1:ax.set_xlabel('Test false-positive rate')
            if j==0:ax.set_ylabel('Test sensitivity')
    handles,labels=axes[0,0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='outside lower center',ncol=3,fontsize=8)
    fig.suptitle('Exploratory calibration sensitivity\nSmall / medium / large markers: '+
        ' / '.join(f'{f:.0%}' for f in levels)+' nominal earlier-calibration FPR',fontsize=11)
    fig.savefig(output/'calibration-sensitivity.png',dpi=200)
    fig.savefig(output/'calibration-sensitivity.pdf');plt.close(fig)
    fmt={k:lambda v:'NA' if pd.isna(v) else f'{v:.3f}' for k in ['sensitivity','false_positive_rate','J','delta_J']}
    def table(q,name,extra=None):
        q=q.copy();q['model']=q.model.map(MODEL_LABELS);q['method']=q.method.map(LABELS)
        columns={'model':'Representation','task':'Task','method':'Readout'}
        if extra:columns.update(extra)
        columns.update({'n_positive':'Positives','n_negative':'Negatives','sensitivity':'Sensitivity',
                        'false_positive_rate':'False-positive rate','J':'J'})
        if 'delta_J' in q:columns['delta_J']='Paired J difference versus start-fixed'
        (output/name).write_text(markdown_table(q,columns,fmt))
    raw=pd.read_csv(robustness/'metrics.csv');pairs=pd.read_csv(robustness/'paired-comparisons.csv')
    new=raw[raw.method.isin(['baseline_cohort_random_forest','baseline_cohort_logistic','embedding_matched_controls'])]
    table(new,'exploratory-readouts.md')
    sec=pd.read_csv(secondary/'metrics.csv');sp=pd.read_csv(secondary/'paired-comparisons.csv')
    sec=sec[(sec.availability_mode=='paired')&(sec.support=='centre')&(sec.seed==14014)&(sec.reference_mode=='global')]
    sp=sp[(sp.availability_mode=='paired')&(sp.support=='centre')&(sp.seed==14014)&(sp.reference_mode=='global')]
    matching=pd.concat([raw[raw.method.isin(['start_fixed','control_adjusted','embedding_matched_controls'])],
        sec[sec.method.isin(['non_tree_control_adjusted','class_matched_control_adjusted','nearest8_non_tree_control_adjusted'])]],ignore_index=True)
    differences=pd.concat([pairs,sp],ignore_index=True).drop_duplicates(['model','task','method'])
    matching=matching.merge(differences[['model','task','method','delta_J']],on=['model','task','method'],how='left',validate='one_to_one')
    table(matching,'control-matching.md')
    cal['calibration']=cal.nominal_fpr.map(lambda f:f'{f:.0%}')
    table(cal,'all-calibration-operating-points.md',{'calibration':'Nominal calibration FPR'})
    audit=pd.read_csv(robustness/'partial-label-audit-summary.csv')
    audit['role']=audit.role.map({'reference':'Reference cohort','tree_control':'Independent tree controls','non_tree_control':'Non-tree controls'})
    (output/'partial-label-audit.md').write_text(markdown_table(audit,{'role':'Baseline cohort','cohort':'Plots',
        'unique_matches':'Unique spatial matches','later_labels':'One later label available',
        'later_binary_disagreement':'Known later binary-cover disagreements','unknown_later':'No later label checked'}))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for k in ['robustness','secondary','output']:p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();generate_diagnostics(a.robustness,a.secondary,a.output)
