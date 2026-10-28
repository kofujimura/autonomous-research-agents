"""Standalone scientific plot of fixed direct-learner input comparisons."""
import os
from pathlib import Path
import pandas as pd
from figures import MODEL_LABELS

def generate_inputs(main,extension,output):
    output.mkdir(parents=True,exist_ok=True)
    os.environ.setdefault('MPLCONFIGDIR',str(output/'matplotlib-cache'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    a=pd.read_csv(main/'metrics.csv');b=pd.read_csv(extension/'metrics.csv')
    groups=[('LCMAP, end 2020–2021',a),
        ('NLCD Forest, end 2020–2021',b[b.availability_mode=='nlcd_overlapping_2019_2021_primary']),
        ('NLCD Forest, end 2022–2023',b[b.availability_mode=='nlcd_beyond_2021_primary'])]
    methods=['direct_before','direct_after','direct_difference','direct_gradient_boosting']
    fig,axes=plt.subplots(3,2,figsize=(10,10),sharex=True,sharey=True,layout='constrained')
    for row,(label,g) in enumerate(groups):
        for col,task in enumerate(['gain','loss']):
            ax=axes[row,col]
            for j,(model,colour,marker) in enumerate([('aef','tab:blue','o'),('tessera','tab:orange','s')]):
                q=g[(g.model==model)&(g.task==task)].set_index('method').loc[methods]
                for k,r in enumerate(q.itertuples()):
                    x=k+(-.08 if j==0 else .08)
                    ax.plot([x,x],[r.J_lo,r.J_hi],color=colour,lw=1,alpha=.65)
                    ax.plot(x,r.J,marker=marker,color=colour,ls='',label=MODEL_LABELS[model] if row==col==k==0 else None)
                count=q.iloc[0]
            ax.axhline(0,color='grey',lw=1);ax.grid(axis='y',alpha=.15)
            ax.set_title(f'{label}: {task}\n{int(count.n_positive)} positive / {int(count.n_negative)} negative pairs',fontsize=10)
            ax.set_ylim(-.6,1.025);ax.set_xticks(range(4),['Before','After','Difference','Both'])
            if col==0:ax.set_ylabel("Youden's J")
    handles,labels=axes[0,0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='outside lower center',ncol=2,fontsize=9)
    fig.suptitle('Exploratory matched direct learner: input choice\nOriginal earlier-negative calibration; conditional block intervals',fontsize=12)
    fig.savefig(output/'direct-inputs.png',dpi=200);fig.savefig(output/'direct-inputs.pdf');plt.close(fig)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser()
    for key in ['main','extension','output']:p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();generate_inputs(a.main,a.extension,a.output)
