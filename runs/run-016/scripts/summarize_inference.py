"""Generate numerical tables and plots only from saved inference outputs."""
import argparse,json,os
from pathlib import Path
import numpy as np
import pandas as pd
from records import ROOT,now,digest
from audit_inference import clean_json

def probability_summary(values):
    x=np.asarray(values,dtype=float);rep=x.mean(axis=0)
    return float(x.mean()),float(rep.std(ddof=1)/np.sqrt(x.shape[1]))

def build(paths,destination,primary=True):
    out=Path(destination)
    if not out.is_absolute():out=ROOT/out
    if out.exists():raise FileExistsError('Use a fresh table/figure output directory')
    out.mkdir(parents=True);tables=[];points=[];oracles=[];cases=[];ratios=[];seen_direct={};unit_tables=[];seen_direct_units=set()
    input_records=[]
    for name in paths:
        d=ROOT/name;meta=json.loads((d/'analysis.json').read_text())
        if meta.get('max_units_requested') is not None:raise ValueError('Reduced diagnostic analysis is not a full paper input')
        units=[json.loads(x) for x in (d/'units.jsonl').read_text().splitlines()]
        units=[u for u in units if u['primary']==primary]
        assert units
        tag=f"{meta['classifier']}-{meta['taxonomy']}-{'refreshed' if meta['refreshed'] else 'frozen'}-{meta['representation']}"
        input_records.append(dict(path=name,analysis_sha256=digest(d/'analysis.json'),units_sha256=digest(d/'units.jsonl')))
        cases.append(dict(tag=tag,taxonomy=meta['taxonomy'],representation=meta['representation'],units=len(units),
                          landscapes=len(set(u['landscape_id'] for u in units)),
                          zero_change=sum(abs(u['true_change'])<=1e-10 for u in units),
                          tiny_change=sum(u['tiny_change'] for u in units),entropy_floor=sum(u['entropy_floor'] for u in units),
                          entropy_ceiling=sum(u['entropy_ceiling'] for u in units),
                          observed_support_entropy_ceiling=sum(u.get('observed_support_entropy_ceiling',False) for u in units),
                          single_group_either_year=sum(u['single_group_a'] or u['single_group_b'] for u in units),
                          single_group_both_years=sum(u['single_group_a'] and u['single_group_b'] for u in units),
                          labels_unchanged_all=sum(u['labels_unchanged_fraction']==1. for u in units),
                          reference_proportions_identical=sum(u.get('reference_proportions_identical',False) for u in units),
                          identical_predictions=sum(u['predicted_probabilities_identical'] for u in units),
                          spatially_constant_predictions_either_year=sum(u.get('spatially_constant_predictions_a',False) or u.get('spatially_constant_predictions_b',False) for u in units),
                          degenerate_direct_oracle=sum(u['oracle']['direct']['paired_independent_ratio'] is None for u in units),
                          degenerate_assisted_oracle=sum(u['oracle']['model_assisted']['paired_independent_ratio'] is None for u in units),
                          unsupported_target_any=sum(u['source_unsupported_fraction_a']>0 or u['source_unsupported_fraction_b']>0 for u in units),
                          arable_dominated_landscapes=len(set(u['landscape_id'] for u in units if (u.get('baseline_arable_fraction') or 0)>.5)),
                          grassland_dominated_landscapes=len(set(u['landscape_id'] for u in units if (u.get('baseline_grassland_fraction') or 0)>.5))))
        raw=[]
        for u in units:
            p=d/u['raw_path'];assert digest(p)==u['raw_sha256']
            with np.load(p) as z:raw.append({k:z[k] for k in z.files})
        truth=np.array([u['true_change'] for u in units])[:,None]
        subsets={'all':np.ones(len(units),bool),
                 'arable_dominated':np.array([(u.get('baseline_arable_fraction') or 0)>.5 for u in units]),
                 'grassland_dominated':np.array([(u.get('baseline_grassland_fraction') or 0)>.5 for u in units]),
                 'entropy_at_least_0.05_both_years':np.array([not u['entropy_floor'] for u in units]),
                 'absolute_change_at_least_0.01':np.array([not u['tiny_change'] for u in units])}
        for a,b in sorted(set((u['year_a'],u['year_b']) for u in units)):
            subsets[f'year_{a}_{b}']=np.array([u['year_a']==a and u['year_b']==b for u in units])
        for subset,mask in subsets.items():
            if not mask.any():continue
            for method in ['direct','model_assisted']:
                label=f"reference-{meta['taxonomy']}" if method=='direct' else tag
                for design in ['paired','independent']:
                    for n in [32,64,128,256,512]:
                        pre=f'{method}_{design}_{n}_'
                        est=np.stack([r[pre+'estimate'] for r in raw])[mask]
                        err=est-truth[mask];squared=err**2
                        covered=np.stack([r[pre+'covered'] for r in raw])[mask]
                        directions=np.stack([r[pre+'direction'] for r in raw])[mask]
                        wrong=np.stack([r[pre+'wrong'] for r in raw])[mask]
                        projected=np.stack([r[pre+'projected_a']|r[pre+'projected_b'] for r in raw])[mask]
                        mse=float(squared.mean());rmse=np.sqrt(mse)
                        mse_rep=squared.mean(axis=0);mse_se=float(mse_rep.std(ddof=1)/np.sqrt(est.shape[1]))
                        cov,covse=probability_summary(covered);rep,repse=probability_summary(directions!=0)
                        wr,wrse=probability_summary(wrong)
                        row=dict(label=label,classifier='none' if method=='direct' else meta['classifier'],
                                 taxonomy=meta['taxonomy'],representation='reference_only' if method=='direct' else meta['representation'],
                                 refreshed=False if method=='direct' else meta['refreshed'],subset=subset,
                                 method=method,design=design,n=n,units=int(mask.sum()),replications=est.shape[1],
                                 mse=mse,rmse=float(rmse),rmse_mcse=mse_se/(2*rmse) if rmse>0 else 0.,
                                 bias=float(err.mean()),coverage=cov,coverage_mcse=covse,report_rate=rep,report_mcse=repse,
                                 wrong_report_rate=wr,wrong_report_mcse=wrse,
                                 reports=int((directions!=0).sum()),wrong_reports=int(wrong.sum()),
                                 wrong_conditional=float(wrong.sum()/(directions!=0).sum()) if (directions!=0).any() else None,
                                 projection_any_year=float(projected.mean()))
                        key=(meta['taxonomy'],subset,design,n)
                        if method=='direct':
                            if key in seen_direct:
                                assert np.allclose([mse,cov,rep,wr],seen_direct[key],atol=1e-12), 'Direct estimates changed across model files'
                                continue
                            seen_direct[key]=[mse,cov,rep,wr]
                        tables.append(row)
                # Compare paired/independent MSE using the shared trial index.
                for n in [32,64,128,256,512]:
                    ep=np.stack([r[f'{method}_paired_{n}_estimate'] for r in raw])[mask]-truth[mask]
                    ei=np.stack([r[f'{method}_independent_{n}_estimate'] for r in raw])[mask]-truth[mask]
                    ap=(ep**2).mean(axis=0);ai=(ei**2).mean(axis=0)
                    mp=ap.mean();mi=ai.mean();ratio=mp/mi if mi>1e-20 else None
                    ratiose=float(np.std(ap/mi-mp*ai/mi**2,ddof=1)/np.sqrt(len(ap))) if mi>1e-20 else None
                    entry=dict(label=label,taxonomy=meta['taxonomy'],subset=subset,method=method,n=n,
                               units=int(mask.sum()),paired_independent_mse_ratio=ratio,ratio_mcse=ratiose)
                    if method!='direct' or not any(all(old.get(k)==entry.get(k) for k in ['label','taxonomy','subset','method','n']) for old in ratios):ratios.append(entry)
        for u in units:
            for s in u['summaries']:
                is_direct=s['method']=='direct'
                key=(meta['taxonomy'],u['unit_id'],s['design'],s['n'])
                if is_direct and key in seen_direct_units:continue
                if is_direct:seen_direct_units.add(key)
                unit_tables.append(dict(label=f"reference-{meta['taxonomy']}" if is_direct else tag,
                                        unit_id=u['unit_id'],landscape_id=u['landscape_id'],taxonomy=meta['taxonomy'],
                                        year_a=u['year_a'],year_b=u['year_b'],true_change=u['true_change'],
                                        baseline_arable_fraction=u.get('baseline_arable_fraction'),
                                        baseline_grassland_fraction=u.get('baseline_grassland_fraction'),
                                        rmse=float(np.sqrt(s['mse'])),**s))
            for method,diag in u['oracle'].items():
                oracles.append(dict(tag=tag,taxonomy=meta['taxonomy'],representation=meta['representation'],
                                    unit_id=u['unit_id'],landscape_id=u['landscape_id'],method=method,
                                    true_change=u['true_change'],baseline_arable_fraction=u.get('baseline_arable_fraction'),**diag))
        for method in ['no_change','hard_count','soft_count','source_confusion']:
            selected=[u for u in units if u['point_estimates'].get(method) is not None]
            if not selected:continue
            est=np.array([u['point_estimates'][method] for u in selected]);t=np.array([u['true_change'] for u in selected])
            direction=np.where(np.abs(est)>1e-10,np.sign(est),0);true_direction=np.where(np.abs(t)>1e-10,np.sign(t),0)
            points.append(dict(tag=tag,method=method,taxonomy=meta['taxonomy'],representation=meta['representation'],
                               units=len(selected),unavailable_units=len(units)-len(selected),rmse=float(np.sqrt(np.mean((est-t)**2))),
                               bias=float(np.mean(est-t)),opposite_or_false_directions=int(((direction!=0)&(direction!=true_direction)).sum()),
                               nonzero_point_estimates=int((direction!=0).sum()),note='Point estimates have no confidence interval; these counts are not confidence-qualified reports'))
    distributions=[]
    unit_frame=pd.DataFrame(unit_tables)
    for (label,design,n),g in unit_frame.groupby(['label','design','n']):
        distributions.append(dict(label=label,design=design,n=int(n),units=len(g),
                                  median_unit_rmse=float(g.rmse.median()),rmse_q10=float(g.rmse.quantile(.1)),
                                  rmse_q90=float(g.rmse.quantile(.9)),median_unit_coverage=float(g.coverage.median()),
                                  coverage_q10=float(g.coverage.quantile(.1)),coverage_q90=float(g.coverage.quantile(.9))))
    unit_ratios=[]
    for (label,uid,n),g in unit_frame.groupby(['label','unit_id','n']):
        assert len(g)==2 and set(g.design)=={'paired','independent'}
        v=g.set_index('design').mse
        unit_ratios.append(dict(label=label,unit_id=uid,n=int(n),paired_mse=float(v.paired),independent_mse=float(v.independent),
                                ratio=float(v.paired/v.independent) if v.independent>1e-20 else None,
                                paired_mse_larger=bool(v.paired>v.independent+1e-12)))
    for filename,rows in [('audit-performance.csv',tables),('point-estimates.csv',points),('oracle-diagnostics.csv',oracles),
                          ('unit-performance.csv',unit_tables),('unit-performance-distributions.csv',distributions),
                          ('unit-pairing-ratios.csv',unit_ratios),
                          ('case-counts.csv',cases),('pairing-mse-ratios.csv',ratios)]:
        pd.DataFrame(rows).to_csv(out/filename,index=False)
    summary=dict(generated_at_utc=now(),inputs=input_records,cases=cases,audit_performance=tables,
                 point_estimates=points,pairing_ratios=ratios,
                 scope='Equal weight per fixed test landscape/transition. MCSE describes simulation error, not a population-sampling confidence interval.')
    (out/'summary.json').write_text(json.dumps(clean_json(summary),indent=2,allow_nan=False)+'\n')
    plots(out,pd.DataFrame(tables),pd.DataFrame(oracles),pd.DataFrame(points))
    print(json.dumps(dict(destination=str(out),performance_rows=len(tables),input_analyses=len(paths))))

def plots(out,table,oracle,points=None):
    os.environ.setdefault('MPLCONFIGDIR',str(out/'.matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'svg.fonttype':'none'})
    t=table[(table.taxonomy=='broad')&(table.subset=='all')&((table.classifier=='none')|((table.classifier=='logistic')&(~table.refreshed)))]
    labels=list(t.label.unique())
    if labels:
        fig,axes=plt.subplots(2,len(labels),figsize=(4.1*len(labels),6),squeeze=False,sharex=True,sharey='row')
        baseline=None
        if points is not None:
            p=points[(points.taxonomy=='broad')&(points.method=='no_change')]
            if not p.empty:
                assert np.allclose(p.rmse,p.rmse.iloc[0],atol=1e-12)
                baseline=float(p.rmse.iloc[0])
        for j,label in enumerate(labels):
            for design,style in [('paired','-o'),('independent','--s')]:
                s=t[(t.label==label)&(t.design==design)].sort_values('n')
                axes[0,j].plot(s.n,s.rmse,style,label=design)
                axes[1,j].plot(s.n,s.coverage,style,label=design)
            title=label.replace('logistic-broad-frozen-','').replace('reference-broad','Direct reference')
            axes[0,j].set_title({'tessera':'TESSERA','alphaearth':'AlphaEarth'}.get(title,title))
            if baseline is not None:axes[0,j].axhline(baseline,color='black',linestyle=':',linewidth=.9,label='No-change point baseline')
            axes[0,j].set_ylim(bottom=0)
            axes[0,j].set_ylabel('RMSE of change in Shannon entropy')
            axes[1,j].set_ylabel('Empirical coverage');axes[1,j].axhline(.95,color='gray',linewidth=.8)
            axes[1,j].set_ylim(0,1.01)
            axes[1,j].set_xlabel('Reference labels per year')
            for ax in axes[:,j]:ax.set_xscale('log',base=2);ax.set_xticks([32,64,128,256,512],labels=['32','64','128','256','512']);ax.grid(alpha=.2)
            axes[0,j].legend()
        fig.tight_layout();fig.savefig(out/'budget-curves.svg');fig.savefig(out/'budget-curves.png',dpi=200);plt.close(fig)
    o=oracle[(oracle.taxonomy=='broad')&oracle.tag.str.startswith('logistic-broad-frozen-')]
    if not o.empty:
        fig,ax=plt.subplots(figsize=(6,5))
        for rep,g in o.groupby('representation'):
            wide=g.pivot(index='unit_id',columns='method',values='paired_independent_ratio').dropna()
            ax.scatter(wide.direct,wide.model_assisted,s=22,alpha=.65,label=rep)
        ax.plot([0,2],[0,2],color='gray',linewidth=.8);ax.axvline(1,color='gray',linestyle=':');ax.axhline(1,color='gray',linestyle=':')
        ax.set(xlim=(0,2),ylim=(0,2),xlabel='Paired / independent variance, direct reference',
               ylabel='Paired / independent variance, model-assisted')
        ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(out/'pairing-variance.svg');fig.savefig(out/'pairing-variance.png',dpi=200);plt.close(fig)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--analysis',action='append',required=True);p.add_argument('--destination',required=True)
    a=p.parse_args();build(a.analysis,a.destination)
