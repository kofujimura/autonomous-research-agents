"""Publication figures from generated report inputs; no new model fitting."""
from pathlib import Path
import argparse,os,json
from records import ROOT

def make(data,out):
 data=Path(data);out=Path(out);out.mkdir(parents=True,exist_ok=True)
 os.environ.setdefault('MPLCONFIGDIR',str(out/'.matplotlib-cache'))
 import numpy as np,pandas as pd,matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'svg.hashsalt':'free-research-018','pdf.fonttype':42,'axes.titlesize':10})
 metrics=pd.read_csv(data/'metrics-all.csv');contrasts=pd.read_csv(data/'contrasts-all.csv');canonical=json.loads((data/'report.json').read_text())['canonical_paths'];palette={'hydro_pair':'#333333','hydro_decoder':'#777777','pair_aef':'#0072B2','pair_tessera':'#D55E00'};labels={'hydro_pair':'Hydrological pair','hydro_decoder':'Hydrological category','pair_aef':'+ AlphaEarth distance','pair_tessera':'+ TESSERA distance'};produced=[]
 def save(fig,name):
  fig.savefig(out/(name+'.png'),dpi=300,bbox_inches='tight',metadata={'Software':'free-research-018'})
  fig.savefig(out/(name+'.pdf'),bbox_inches='tight',metadata={'CreationDate':None,'ModDate':None})
  fig.savefig(out/(name+'.svg'),bbox_inches='tight',metadata={'Date':None});plt.close(fig);produced.append(name)
 panels=[(canonical['primary_summary'],'Original panel · random forest'),(canonical['hgb_summary'],'Original panel · boosted trees'),(canonical['recent_summary'],'Recent-image panel · random forest\nExploratory panel')]
 fig,axes=plt.subplots(1,3,figsize=(11.4,3.35),sharey=True)
 for ax,(key,title) in zip(axes,panels):
  for method,color in palette.items():
   g=metrics[(metrics.analysis==key)&(metrics.method==method)].sort_values('coverage')
   if len(g):ax.plot(g.coverage*100,g.macro_risk*100,marker='o',ms=4,lw=1.7,ls='--' if method=='hydro_decoder' else '-',color=color,label=labels[method])
  ax.set(title=title,xlabel='Nominal retained queries (%)',xticks=[20,50,80,100]);ax.set_ylim(bottom=0);ax.grid(axis='y',alpha=.2);ax.axvline(50,color='#cccccc',lw=.7,zorder=0)
 axes[0].set_ylabel('Inventory-category mismatch\nWindow mean (%)');handles,legend_labels=axes[0].get_legend_handles_labels();fig.legend(handles,legend_labels,loc='lower center',bbox_to_anchor=(.5,-.08),ncol=4,frameon=False,fontsize=8);fig.tight_layout();save(fig,'risk-coverage')
 fig,axes=plt.subplots(1,2,figsize=(10,4.25),sharex=True,sharey=True)
 rows=[('pair_aef','hydro_pair','AlphaEarth · pair baseline'),('pair_aef','hydro_decoder','AlphaEarth · category baseline'),('pair_tessera','hydro_pair','TESSERA · pair baseline'),('pair_tessera','hydro_decoder','TESSERA · category baseline'),('pair_both','hydro_pair','Both distances · pair baseline'),('pair_both','hydro_decoder','Both distances · category baseline')]
 for ax,(key,title) in zip(axes,panels[:2]):
  for i,(method,base,label) in enumerate(rows):
   g=contrasts[(contrasts.analysis==key)&(contrasts.coverage==.5)&(contrasts.method==method)&(contrasts.baseline==base)]
   if not len(g):continue
   r=g.iloc[0];color=palette.get(method,'#009E73');ax.errorbar(r.difference*100,i,xerr=np.array([[r.difference-r.low],[r.high-r.difference]])*100,fmt='o',ms=5,color=color,capsize=3,lw=1.3)
  ax.axvline(0,color='#333333',lw=.8);ax.axvline(-2,color='#aaaaaa',lw=.8,ls=':');ax.set(title=title,xlabel='Augmented − baseline mismatch (percentage points)',yticks=np.arange(len(rows)),yticklabels=[v[2] for v in rows]);ax.grid(axis='x',alpha=.15)
 axes[0].invert_yaxis();fig.tight_layout();save(fig,'paired-contrasts')
 variants=[('Planned · initial forest seed','analysis/primary-summary'),('Planned · forest seed +1000','analysis/controls/seed-1000-summary'),('Planned · forest seed +2000','analysis/controls/seed-2000-summary')]+[(f'Planned · stratum shuffle {i+1}',f'analysis/controls/permute-{i}-summary') for i in range(3)]+[(f'Independent scalar {i+1}',f'analysis/controls/noise-{i}-summary') for i in range(3)]+[(f'Constant column · seed +{i}',f'analysis/controls/constant-seed-{i}-summary') for i in [0,1000,2000]]+[('All features at each split','analysis/controls/full-features-summary')]+[(f'All features · scalar {i+1}',f'analysis/controls/noise-all-{i}-summary') for i in range(3)]+[('All features · constant','analysis/controls/constant-all-summary')]
 variants=[v for v in variants if v[1] in set(contrasts.analysis)];fig,axes=plt.subplots(1,2,figsize=(10.8,max(4,len(variants)*.34)),sharey=True)
 for ax,base,title in zip(axes,['hydro_pair','hydro_decoder'],['Compared with hydrological pair model','Compared with hydrological category model']):
  for i,(label,key) in enumerate(variants):
   for method,offset,color in [('pair_aef',-.12,'#0072B2'),('pair_tessera',.12,'#D55E00'),('pair_noise',0,'#444444'),('pair_constant',0,'#009E73')]:
    g=contrasts[(contrasts.analysis==key)&(contrasts.coverage==.5)&(contrasts.method==method)&(contrasts.baseline==base)]
    if len(g):ax.scatter(float(g.difference.iloc[0])*100,i+offset,c=color,s=27,marker='D' if method=='pair_noise' else 'o',edgecolor='white',linewidth=.4)
  ax.axvline(0,color='#333333',lw=.8);ax.axvline(-2,color='#aaaaaa',ls=':',lw=.8);ax.set(title=title,xlabel='Augmented − baseline (percentage points)',yticks=np.arange(len(variants)),yticklabels=[v[0] for v in variants]);ax.grid(axis='x',alpha=.15)
 from matplotlib.lines import Line2D
 control_handles=[Line2D([0],[0],marker=marker,color=color,lw=0,label=label) for marker,color,label in [('o','#0072B2','AlphaEarth distance'),('o','#D55E00','TESSERA distance'),('D','#444444','Independent scalar'),('o','#009E73','Constant column')]]
 axes[0].invert_yaxis();fig.legend(handles=control_handles,loc='lower center',bbox_to_anchor=(.5,-.035),ncol=4,frameon=False,fontsize=8);fig.tight_layout();save(fig,'control-sensitivity')
 d=pd.read_csv(data/'screen-decomposition.csv');d=d[d.selector=='hydro_pair'];fig,ax=plt.subplots(figsize=(7.6,3.9));names={'pair_aef':'AlphaEarth','pair_tessera':'TESSERA','pair_both':'Both distances'}
 for field,offset,color,label in [('total_difference',-.19,'#333333','Own screened query sets'),('ranking_on_fixed_screen',0,'#0072B2','Same hydrological query screen'),('selection_remainder',.19,'#D55E00','Algebraic selection remainder')]:ax.scatter(d[field]*100,np.arange(len(d))+offset,color=color,s=38,label=label)
 ax.axvline(0,color='#333333',lw=.8);ax.set(yticks=np.arange(len(d)),yticklabels=d.method.map(names),xlabel='Difference in mismatch (percentage points)',title='Reference ranking and query selection · original forest');ax.invert_yaxis();ax.grid(axis='x',alpha=.15);handles,legend_labels=ax.get_legend_handles_labels();fig.legend(handles,legend_labels,frameon=False,fontsize=8,loc='lower left',bbox_to_anchor=(.14,0),ncol=1);fig.tight_layout(rect=(0,.23,1,1));save(fig,'screen-components')
 polygon_keys=[f'analysis/polygon/{c}-{learner}-summary' for c in ['B','C'] for learner in ['rf','hgb']]
 if all(k in set(metrics.analysis) for k in polygon_keys):
  fig,axes=plt.subplots(1,2,figsize=(9.2,3.6),sharey=True)
  for ax,learner,title in zip(axes,['rf','hgb'],['Physical baselines · original forest','Physical baselines · boosted trees']):
   for method,color,marker,ls in [('hydro_pair','#333333','o','-'),('hydro_decoder','#777777','s','--')]:
    selected=[]
    for c in ['B','C']:
     q=metrics[(metrics.analysis==f'analysis/polygon/{c}-{learner}-summary')&(metrics.coverage==.5)&(metrics.method==method)];assert len(q)==1;selected.append(q.iloc[0])
    yy=np.array([q.macro_risk for q in selected])*100;lo=np.array([q.macro_low for q in selected])*100;hi=np.array([q.macro_high for q in selected])*100
    ax.errorbar([0,1],yy,yerr=np.vstack([yy-lo,hi-yy]),color=color,marker=marker,ls=ls,lw=1.5,capsize=3,label=labels[method])
   ax.set(title=title,xticks=[0,1],xticklabels=['Near the interior point','At dispersed polygon locations'],xlim=(-.25,1.25));ax.grid(axis='y',alpha=.2)
  axes[0].set_ylabel('Inventory-category mismatch\nWindow mean (%)');handles,legend_labels=axes[0].get_legend_handles_labels();fig.legend(handles,legend_labels,loc='lower center',bbox_to_anchor=(.5,-.08),ncol=2,frameon=False);fig.tight_layout();save(fig,'physical-sampling')
 (out/'figure-record.json').write_text(json.dumps(dict(source_data=str(data),figures=produced,scope='Generated from archived predictions and fixed summary outputs; no independent reproduction claim'),indent=2)+'\n');print(json.dumps(dict(figures=produced)))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();make(a.data,a.out)
