"""Publication figures generated from numerical analysis outputs only."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

COLORS={'marginal':'#6f6f6f','aggregate':'#dc8a22','pair':'#187f8c','count':'#9b5ca3'}

def save(fig,out,name):
    fig.text(.01,-.055,
        'This figure is based on data and products of the European Centre\n'
        'for Medium-Range Weather Forecasts (ECMWF). © 2026 ECMWF.\n'
        'CC BY 4.0: https://creativecommons.org/licenses/by/4.0/\n'
        'Location extraction and analysis by this study; no ECMWF endorsement.',
        ha='left',va='top',fontsize=6.5,linespacing=1.15)
    for suffix in ['png','svg','pdf']:fig.savefig(out/f'{name}.{suffix}',dpi=180,bbox_inches='tight')
    plt.close(fig)

def errorbar(ax,x,row,mode,label=None):
    y=float(row[mode+'_width']);lo=float(row[mode+'_low']);hi=float(row[mode+'_high'])
    ax.plot(x,y,marker='o',linestyle='none',color=COLORS[mode],label=label)
    ax.vlines(x,lo,hi,color=COLORS[mode]);ax.hlines([lo,hi],x-.025,x+.025,color=COLORS[mode])

def main():
    p=argparse.ArgumentParser();p.add_argument('--primary',required=True);p.add_argument('--subsets');p.add_argument('--city')
    p.add_argument('--secondary');p.add_argument('--integer-precision');p.add_argument('--output',required=True);a=p.parse_args()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
    primary=Path(a.primary);width=pd.read_csv(primary/'width-summary.csv');cases=pd.read_csv(primary/'cases.csv')
    primary_rows=width[(width['n_sites']==12)&(width['model']=='all')&(width['lead']=='all')&(width['geometry']=='all')]
    selected=cases[(cases['matched_date'])&(cases['n']==12)]
    fig,axes=plt.subplots(1,3,figsize=(12,3.5),layout='constrained')
    for si,stratum in enumerate(['all','informative']):
        row=primary_rows[primary_rows['stratum']==stratum].iloc[0]
        for j,mode in enumerate(['marginal','aggregate','pair']):errorbar(axes[0],si+(j-1)*.17,row,mode,mode if si==0 else None)
    axes[0].set(xticks=[0,1],xticklabels=['All queries','Informative queries'],ylabel='Mean compatible probability width',title='A. Information retained',ylim=(-.02,1.02))
    axes[0].legend(frameon=False,fontsize=8)
    informative=selected[selected['informative']==1]
    for mode in ['marginal','aggregate','pair']:
        values=np.sort(informative[mode+'_width'].clip(lower=0).to_numpy())
        axes[1].step(values,np.arange(1,len(values)+1)/len(values),where='post',color=COLORS[mode],label=mode)
    axes[1].set(xlabel='Compatible probability width',ylabel='Fraction of informative queries',title='B. Distribution of ambiguity',xlim=(-.02,1.02),ylim=(0,1.02))
    grouped=selected.groupby('uncertain_sites').agg(cases=('q','size'),identified=('exact_pair','mean'))
    axes[2].plot(grouped.index,grouped['identified'],marker='o',color=COLORS['pair'])
    for n,row in grouped.iterrows():axes[2].annotate(str(int(row['cases'])),(n,row['identified']),xytext=(0,5),textcoords='offset points',ha='center',fontsize=7)
    axes[2].set(xlabel='Sites with 0 < p < 1',ylabel='Fraction numerically identified by pairs',title='C. Denominators and simple cases',xticks=range(0,13,2),ylim=(-.04,1.13))
    save(fig,out,'primary-information')
    reconstruction=pd.read_csv(primary/'reconstruction-summary.csv')
    rec=reconstruction[(reconstruction['availability']=='historical_matched')&(reconstruction['stratum']=='informative')]
    if len(rec):
        fig,ax=plt.subplots(figsize=(6,3.2),layout='constrained')
        names={'independent':'Independence','historical_copula':'Past forecast ranks','pair_midpoint':'Pair-interval midpoint'}
        for x,(_,row) in enumerate(rec.iterrows()):
            y=row['mean_absolute_error'];lo=row['mae_low'];hi=row['mae_high']
            ax.plot(x,y,marker='o',linestyle='none',color='#253f5e')
            ax.vlines(x,lo,hi,color='#253f5e');ax.hlines([lo,hi],x-.025,x+.025,color='#253f5e')
        ax.set(xticks=range(len(rec)),xticklabels=[names[x] for x in rec['method']],ylabel='Mean absolute error against original ensemble',title='Point reconstruction on common informative queries')
        save(fig,out,'reconstruction')
    if a.subsets and (Path(a.subsets)/'width-summary.csv').exists():
        width=pd.read_csv(Path(a.subsets)/'width-summary.csv');rows=width[(width['model']=='all')&(width['stratum']=='informative')]
        fig,axes=plt.subplots(1,2,figsize=(9,3.3),layout='constrained')
        for si,n in enumerate([4,8]):
            row=rows[rows['query_size']==str(n)]
            if row.empty:row=rows[pd.to_numeric(rows['query_size'],errors='coerce')==n]
            if row.empty:continue
            row=row.iloc[0]
            for j,mode in enumerate(['marginal','pair','count']):errorbar(axes[0],si+(j-1)*.18,row,mode,mode if si==0 else None)
            total=row['cases'];counts=[row['pair_narrower_cases'],row['count_narrower_cases'],row['equal_width_cases']]
            bottom=0
            for j,(value,label,color) in enumerate(zip(counts,['Pairs narrower','Count narrower','Equal width'],['#187f8c','#9b5ca3','#bbb'])):
                axes[1].bar(si,value/total,bottom=bottom,color=color,label=label if si==0 else None,width=.6);bottom+=value/total
        axes[0].set(xticks=[0,1],xticklabels=['4-site queries','8-site queries'],ylabel='Mean compatible probability width',ylim=(-.02,1.02),title='A. Reusing a universe summary')
        axes[1].set(xticks=[0,1],xticklabels=['4-site queries','8-site queries'],ylabel='Fraction of informative queries',ylim=(0,1),title='B. Non-nested information products')
        axes[0].legend(frameon=False,fontsize=8);axes[1].legend(frameon=False,fontsize=8)
        save(fig,out,'subset-information')
    if a.city and (Path(a.city)/'width-summary.csv').exists():
        width=pd.read_csv(Path(a.city)/'width-summary.csv')
        rows=width[(width['model']=='all')&(width['horizon']=='all')&(width['stratum']=='common_informative')]
        fig,axes=plt.subplots(1,2,figsize=(9,3.3),layout='constrained')
        for ai,kind in enumerate(['regular','city']):
            for si,endpoint in enumerate(['snapshot12','maximum4']):
                part=rows[(rows['portfolio_type']==kind)&(rows['endpoint']==endpoint)]
                if part.empty:continue
                row=part.iloc[0]
                for j,mode in enumerate(['marginal','aggregate','pair']):errorbar(axes[ai],si+(j-1)*.18,row,mode,mode if si==0 else None)
            axes[ai].set(xticks=[0,1],xticklabels=['12 UTC snapshot','Max of 4 samples'],ylabel='Mean compatible probability width',ylim=(-.02,1.02),title=f'{kind.capitalize()} locations; common informative queries')
            axes[ai].legend(frameon=False,fontsize=8)
        save(fig,out,'city-time-boundary')
    if a.secondary and (Path(a.secondary)/'epsilon-summary.csv').exists():
        eps=pd.read_csv(Path(a.secondary)/'epsilon-summary.csv')
        if len(eps):
            fig,ax=plt.subplots(figsize=(5.5,3),layout='constrained')
            ax.plot(eps['epsilon'],eps['mean_width'],marker='o',linestyle='none',color=COLORS['pair'],label='Arbitrary probability weights')
            if a.integer_precision:
                ip=json.loads((Path(a.integer_precision)/'summary.json').read_text())
                xs=[0,.005,.02]
                lows=[ip['exact_integer_width_mean'],ip['epsilon005_integer_width_mean'],ip['epsilon02_mean_width_lower_bound']]
                highs=[ip['exact_integer_width_mean'],ip['epsilon005_integer_width_mean'],ip['epsilon02_mean_width_upper_bound']]
                ax.vlines(xs,lows,highs,color=COLORS['count'],linewidth=3)
                for x,low,high in zip(xs,lows,highs):ax.hlines([low,high],x-.00035,x+.00035,color=COLORS['count'],linewidth=2)
                ax.plot([],[],color=COLORS['count'],linewidth=3,label='Known M=50: optimization bounds')
            ax.set(xlabel='Allowance for each individual/pair probability',ylabel='Mean compatible pair width',title='Moment precision and admissible laws; fixed cohort',ylim=(0,None))
            ax.legend(frameon=False,fontsize=8)
            save(fig,out,'moment-sensitivity')
    print('Figures regenerated from supplied analysis outputs')

if __name__=='__main__':main()
