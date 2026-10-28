"""Publication figures regenerated entirely from the numeric analysis tables."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from records import ROOT

from labels import LABELS,COLORS,REPS

def save(fig,out,name):
    fig.savefig(out/(name+'.png'),dpi=220,bbox_inches='tight')
    fig.savefig(out/(name+'.svg'),bbox_inches='tight',metadata={'Date':None})
    plt.close(fig)

def main():
    p=argparse.ArgumentParser();p.add_argument('--analysis',default='analysis');p.add_argument('--out',default='figures')
    p.add_argument('--evaluation',default='data/evaluation')
    a=p.parse_args();analysis=ROOT/a.analysis;out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
    plt.rcParams['svg.hashsalt']='free-research-017'
    scores=pd.read_csv(analysis/'scores.csv')
    primary=scores[(scores.scope=='within')&(scores.decoder=='rf')&(scores.budget==2000)&
        (scores.version=='raw')&(scores.boundary_tolerance_m==0)]
    standard=primary[primary.condition=='standardized_0.05']
    policies=['area','interior','object','proposal','uncertainty']
    fig,ax=plt.subplots(figsize=(8,4.8))
    fig.subplots_adjust(bottom=.30,top=.91,left=.10,right=.98)
    for j,rep in enumerate(['aef','optical','optical_context']):
        for i,policy in enumerate(policies):
            values=standard[(standard.representation==rep)&(standard.policy==policy)].small_macro_recovery_50.dropna().to_numpy()*100
            if len(values)!=5:continue
            x=i+(j-1)*.21
            ax.plot([x,x],[min(values),max(values)],color=COLORS[rep],alpha=.5,lw=2)
            ax.scatter(np.full(len(values),x)+np.linspace(-.035,.035,len(values)),values,color=COLORS[rep],s=10,alpha=.5)
            ax.scatter(x,np.mean(values),color=COLORS[rep],s=48,label=REPS[rep] if i==0 else None)
    ax.set_xticks(range(len(policies)),[LABELS[x] for x in policies],rotation=16,ha='right')
    ax.set_ylabel('Small mapped patches recovered (%)');ax.set_ylim(0,100)
    ax.set_title('Equal fitting budget and 5% reference-upland FPR')
    ax.grid(axis='y',alpha=.2);ax.legend(fontsize=9,loc='best')
    fig.text(.01,.015,'Large points: mean of five training seeds; small points and bars: observed seeds and range.\nRecovery requires ≥50% coverage of common-valid reference pixels; each region has equal weight.',fontsize=8)
    save(fig,out,'primary-recovery')
    summary=json.loads((analysis/'summary.json').read_text())['primary_contrasts']
    names=['H1_interaction','aef_oracle_gain','optical_oracle_gain','aef_proposal_gain','optical_proposal_gain']
    text=['Representation × allocation interaction','Oracle gain, embeddings','Oracle gain, optical','Proposal gain, embeddings','Proposal gain, optical']
    fig,ax=plt.subplots(figsize=(8,4.3))
    fig.subplots_adjust(bottom=.25,left=.46,top=.97,right=.98)
    for i,(name,title) in enumerate(zip(names,text)):
        row=summary.get(name,{})
        if row.get('status')!='complete':continue
        value=row['estimate']*100;lo,hi=np.array(row['conditional_block_bootstrap_95_percent_interval'])*100
        ax.plot([lo,hi],[i,i],color='#333333',lw=2);ax.scatter(value,i,color='#0072B2',s=45)
    ax.set_yticks(range(len(names)),text,fontsize=9);ax.invert_yaxis();ax.axvline(0,color='grey',ls='--')
    ax.set_xlabel('Difference in patch recovery (percentage points)');ax.grid(axis='x',alpha=.2)
    fig.text(.01,.015,'95% paired block-bootstrap intervals condition on fitted models, operating thresholds and reference maps.\nFour convenience regions are fixed; they do not support national inference.',fontsize=8)
    save(fig,out,'primary-contrasts')
    deployment=primary[primary.condition=='validation_0.05']
    fig,axes=plt.subplots(1,2,figsize=(9,4.7),sharey=True)
    fig.subplots_adjust(bottom=.27,left=.08,right=.98,top=.91,wspace=.12)
    for ax,condition,title in zip(axes,[standard,deployment],['Test-standardized threshold','Validation threshold replay']):
        for rep in ['aef','optical']:
            for policy in policies:
                part=condition[(condition.representation==rep)&(condition.policy==policy)]
                if len(part)!=5:continue
                ax.scatter(part.upland_fpr*100,part.small_macro_recovery_50*100,color=COLORS[rep],s=20,alpha=.6,
                    marker={'area':'o','interior':'v','object':'s','proposal':'D','uncertainty':'^'}[policy])
        ax.axvline(5,color='grey',ls='--');ax.set_title(title);ax.set_xlabel('Achieved reference-upland FPR (%)');ax.grid(alpha=.2)
    axes[0].set_ylabel('Small-patch recovery (%)');axes[0].set_ylim(0,100)
    from matplotlib.lines import Line2D
    handles=[Line2D([],[],marker='o',ls='',color=COLORS[r],label=REPS[r]) for r in ['aef','optical']]
    handles += [Line2D([],[],marker=m,ls='',color='#555555',label=LABELS[p]) for p,m in
        [('area','o'),('interior','v'),('object','s'),('proposal','D'),('uncertainty','^')]]
    axes[0].legend(handles=handles,fontsize=7,ncol=2,loc='upper left')
    fig.text(.01,.015,'Each point is one fitted model/seed. The validation replay applies its previously chosen threshold\nwithout using test labels to set it. Reference definitions and study regions remain fixed.',fontsize=8)
    save(fig,out,'threshold-transfer')
    fig,axes=plt.subplots(2,2,figsize=(9,7.6),sharex=True,sharey=True)
    fig.subplots_adjust(bottom=.18,left=.10,right=.98,top=.94,hspace=.22,wspace=.18)
    for ax,(rep,policy) in zip(axes.ravel(),[(r,p) for r in ['aef','optical'] for p in ['area','object']]):
        parts=[]
        for seed in [101,202,303,404,505]:
            path=ROOT/a.evaluation/f'within_rf_{rep}_{policy}_n2000_s{seed}'/'objects.csv'
            if not path.exists():continue
            frame=pd.read_csv(path)
            frame=frame[(frame.version=='raw')&(frame.condition=='standardized_0.05')&(frame.boundary_tolerance_m==0)]
            parts.append(frame)
        if len(parts)!=5:continue
        data=pd.concat(parts).groupby(['core_id','object_id','vector_area_m2','isolated_50m'],as_index=False).coverage.mean()
        for isolated,marker,color in [(False,'x','#777777'),(True,'o','#0072B2')]:
            part=data[data.isolated_50m==isolated]
            ax.scatter(part.vector_area_m2/10000,part.coverage,s=9,marker=marker,color=color,alpha=.45,
                label=('≥50 m isolation' if isolated else '<50 m isolation'))
        ax.set_xscale('log');ax.set_title(REPS[rep]+'; '+LABELS[policy]);ax.grid(alpha=.2)
        ax.axvline(1,color='grey',ls=':',lw=1);ax.axhline(.5,color='grey',ls='--',lw=1)
        ax.set_ylim(-.02,1.02)
    fig.supxlabel('Reference patch vector area (ha, log scale)',y=.10,fontsize=10)
    fig.supylabel('Mean predicted coverage of valid patch pixels',fontsize=10)
    axes[0,0].legend(fontsize=8)
    fig.text(.01,.015,'One point per complete mapped patch, averaged over the five training seeds; the plot is descriptive.\nThe horizontal line marks primary recovery coverage; the vertical line is the small-patch upper boundary.',fontsize=8)
    save(fig,out,'coverage-by-size')
    print('Saved primary-recovery, primary-contrasts, threshold-transfer and coverage-by-size as PNG/SVG')

if __name__=='__main__':main()
