"""Post-review within-cohort variability and decision-relevant saved-data summaries."""
import argparse,json
import numpy as np,pandas as pd
from records import ROOT,now,digest

def run(destination):
    out=ROOT/destination
    if out.exists():raise FileExistsError('Keep previous review summaries')
    out.mkdir(parents=True);raw={};bootstrap=[]
    main=pd.read_csv(ROOT/'results/tables/main/unit-performance.csv');direct=main[main.label=='reference-broad']
    assert len(direct[(direct.n==128)&(direct.design=='paired')])==90
    inputs=['results/tables/main/unit-performance.csv','results/additional-arable-high-replication/unit-performance.csv']
    additional=pd.read_csv(ROOT/inputs[1]);additional['label']='reference-'+additional.taxonomy;additional['landscape_id']=additional.unit_id.str.rsplit('-',n=2).str[0]
    for name,frame in [('original',direct),('additional_arable_broad',additional[additional.taxonomy=='broad']),('additional_arable_fine',additional[additional.taxonomy=='fine'])]:
        d=frame[frame.n==128];land=d.groupby(['landscape_id','design'])[['mse','coverage']].mean().unstack('design');lids=land.index.tolist();rng=np.random.default_rng(16016+len(bootstrap))
        ix=rng.integers(0,len(lids),size=(5000,len(lids)));raw[name+'_indices']=ix
        p=land['mse']['paired'].to_numpy();i=land['mse']['independent'].to_numpy();ratio=p[ix].mean(axis=1)/i[ix].mean(axis=1);raw[name+'_ratio']=ratio
        for metric,values in [('mse_ratio',ratio),('paired_coverage',land['coverage']['paired'].to_numpy()[ix].mean(axis=1)),('independent_coverage',land['coverage']['independent'].to_numpy()[ix].mean(axis=1))]:
            low,high=np.quantile(values,[.025,.975]);raw[name+'_'+metric]=values
            estimate=p.mean()/i.mean() if metric=='mse_ratio' else float(land['coverage'][metric.replace('_coverage','')].mean())
            bootstrap.append(dict(cohort=name,metric=metric,landscapes=len(lids),replications=5000,estimate=estimate,low=low,high=high))
    pd.DataFrame(bootstrap).to_csv(out/'landscape-resampling.csv',index=False);np.savez_compressed(out/'bootstrap-raw.npz',**raw)
    rows=[]
    for n in [32,64,128,256,512]:
        for design in ['paired','independent']:
            g=direct[(direct.n==n)&(direct.design==design)]
            for subset,mask in [('all',np.ones(len(g),bool)),('tiny',g.true_change.abs()<.01),('non_tiny',g.true_change.abs()>=.01)]:
                s=g[mask];reports=int(s.report_count.sum());wrong=int(s.wrong_count.sum())
                rows.append(dict(n=n,design=design,subset=subset,units=len(s),reports=reports,wrong_reports=wrong,wrong_conditional=wrong/reports if reports else None,
                    coverage_min=float(s.coverage.min()),coverage_p10=float(s.coverage.quantile(.1)),coverage_median=float(s.coverage.median()),coverage_p90=float(s.coverage.quantile(.9)),
                    coverage_below_0_90=int((s.coverage<.9).sum()),no_change_beats_unit_mse=int((s.true_change**2<s.mse).sum())))
    pd.DataFrame(rows).to_csv(out/'decision-context.csv',index=False)
    files=['results/tables/main/audit-performance.csv']+[f'results/tables/forest-broad-{r}/audit-performance.csv' for r in ['tessera','alphaearth']]
    allperf=pd.concat([pd.read_csv(ROOT/f) for f in files],ignore_index=True);allperf=allperf[allperf.subset=='all'].drop_duplicates(['label','design','n'])
    baseline=float(np.mean(direct[(direct.n==128)&(direct.design=='paired')].true_change**2));allperf['no_change_rmse']=np.sqrt(baseline);allperf['beats_no_change']=allperf.mse<baseline
    allperf.to_csv(out/'all-budget-point-baselines.csv',index=False)
    scales=[];long=[]
    for name in ['logistic-broad-tessera','logistic-broad-alphaearth','forest-broad-tessera','forest-broad-alphaearth']:
        path=ROOT/'results/inference'/name;units=[json.loads(s) for s in (path/'units.jsonl').read_text().splitlines()]
        for selection in ['primary','long']:
            us=[u for u in units if u['primary']] if selection=='primary' else [u for u in units if u['year_a']==2022 and u['year_b']==2025]
            for n in [32,64,128,256,512]:
                for design in ['paired','independent']:
                    for method in ['direct','model_assisted']:
                        if method=='direct' and name!='logistic-broad-tessera':continue
                        if selection=='long' and method!='direct':continue
                        errors=[];percent=[];coverage=[];reports=[];wrong=[]
                        for u in us:
                            with np.load(path/u['raw_path']) as z:
                                prefix=f'{method}_{design}_{n}_';est=z[prefix+'estimate'];se=z[prefix+'se'];direction=z[prefix+'direction']
                            e=est-u['true_change'];errors.append(e);percent.append((100*np.expm1(e))**2)
                            coverage.append((est-1.96*se<=u['true_change']+1e-10)&(est+1.96*se>=u['true_change']-1e-10));reports.append(direction!=0);wrong.append((direction!=0)&(direction!=np.sign(u['true_change']) if abs(u['true_change'])>1e-10 else direction!=0))
                        zero=np.array([u['true_change'] for u in us]);row=dict(label='reference-broad' if method=='direct' else name,method=method,design=design,n=n,units=len(us),rmse=float(np.sqrt(np.mean(np.array(errors)**2))),relative_effective_groups_rmse_percent=float(np.sqrt(np.mean(percent))),no_change_rmse=float(np.sqrt(np.mean(zero**2))),no_change_relative_rmse_percent=float(np.sqrt(np.mean((100*np.expm1(-zero))**2))),coverage=float(np.mean(coverage)),report_rate=float(np.mean(reports)),wrong_report_rate=float(np.mean(wrong)))
                        (scales if selection=='primary' else long).append(row)
    pd.DataFrame(scales).to_csv(out/'effective-group-errors.csv',index=False);pd.DataFrame(long).to_csv(out/'long-contrast.csv',index=False)
    ratios=pd.read_csv(ROOT/'results/tables/main/pairing-mse-ratios.csv');ratios[ratios.label=='reference-broad'].to_csv(out/'preplanned-subsets.csv',index=False)
    (out/'analysis.json').write_text(json.dumps(dict(completed_at_utc=now(),plan_path='protocol/plan-v15-review-response.md',exploratory=True,inputs=[dict(path=f,sha256=digest(ROOT/f)) for f in inputs+files],interpretation='Landscape percentile ranges are within-cohort resampling variability, not national intervals; relative error is actually transformed trial error, not exponentiated RMSE'),indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--destination',required=True);a=p.parse_args();run(a.destination)
