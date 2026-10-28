"""Exploratory fixed-budget reference allocation by predicted annual change."""
import argparse,hashlib,json
from collections import defaultdict
import numpy as np,pandas as pd
from records import ROOT,now,digest
from inference_core import entropy,NUMERICAL_TOL
from stratified_core import stratified_change
from audit_inference import clean_json,sign
from sparse_change_core import no_change_probability
from summarize_inference import probability_summary

def run(analysis_path,destination):
    source=ROOT/analysis_path;meta=json.loads((source/'analysis.json').read_text())
    assert meta['max_units_requested'] is None and meta['taxonomy']=='broad' and not meta['refreshed']
    units=[r for r in map(json.loads,(source/'units.jsonl').read_text().splitlines()) if r['primary']]
    fit=json.loads((ROOT/meta['model_path']/'fit.json').read_text());k=len(fit['class_names'])
    files={r['landscape_id']:r for r in fit['prediction_files']};out=ROOT/destination
    if out.exists():raise FileExistsError('Preserve earlier stratified results')
    out.mkdir(parents=True);(out/'raw').mkdir();(out/'draws').mkdir()
    cache={};rows=[];contexts=[];aggregate=defaultdict(lambda:defaultdict(list));comparison=defaultdict(lambda:defaultdict(list))
    for u in units:
        lid=u['landscape_id'];a=u['year_a']-2021;b=u['year_b']-2021;truth=u['true_change'];N=u['N']
        print('STRATIFIED',meta['representation'],u['unit_id'],flush=True)
        if lid not in cache:
            entry=files[lid];assert digest(ROOT/entry['path'])==entry['sha256']
            with np.load(ROOT/entry['path']) as z:cache[lid]=(z['probabilities'],z['labels'])
        p,y=cache[lid];pa=p[a];pb=p[b];ya=y[a];yb=y[b]
        score=np.abs(pa.astype(np.float64)-pb).sum(axis=1)
        assert np.isfinite(score).all() and len(score)==N
        ranked=np.lexsort((np.arange(N),-score));hi=np.sort(ranked[:(N+3)//4]);lo=np.sort(ranked[(N+3)//4:])
        populations=[hi,lo];sizes=[len(hi),len(lo)];assert min(sizes)>=256
        seed=int.from_bytes(hashlib.sha256(f"16016/stratified/{meta['representation']}/{lid}/{a+2021}/{b+2021}".encode()).digest()[:8],'little')
        rng=np.random.default_rng(seed);dtype=np.uint16 if N<=65535 else np.uint32;aa=[];bb=[]
        for population in populations:
            aa.append(np.stack([rng.choice(population,256,replace=False).astype(dtype) for _ in range(500)]))
            bb.append(np.stack([rng.choice(population,256,replace=False).astype(dtype) for _ in range(500)]))
        draw_path=out/'draws'/f"{u['unit_id']}.npz"
        np.savez_compressed(draw_path,score=score,high_population=hi,low_population=lo,a_high=aa[0],a_low=aa[1],b_high=bb[0],b_low=bb[1],seed=seed)
        changed=ya!=yb;changed_sizes=[int(changed[v].sum()) for v in populations]
        context=dict(unit_id=u['unit_id'],landscape_id=lid,representation=meta['representation'],N=N,
                     high_population=len(hi),low_population=len(lo),high_reference_changed=changed_sizes[0],low_reference_changed=changed_sizes[1],
                     high_changed_fraction=changed_sizes[0]/len(hi),low_changed_fraction=changed_sizes[1]/len(lo),
                     high_fraction_of_all_changed=changed_sizes[0]/sum(changed_sizes) if sum(changed_sizes) else None,
                     score_threshold=float(score[ranked[(N+3)//4-1]]),draw_path=str(draw_path.relative_to(out)),draw_sha256=digest(draw_path),
                     reference_labels_used_for_strata=False)
        contexts.append(context);raw={}
        original_path=source/u['raw_path'];assert digest(original_path)==u['raw_sha256']
        with np.load(original_path) as orig:
            for n in [32,64,128,256,512]:
                nh=n//2;sa=[z[:,:nh].astype(int) for z in aa];indb=[z[:,:nh].astype(int) for z in bb]
                sampled_changes=sum(changed[z].sum(axis=1) for z in sa)
                exact_p0=float(np.prod([no_change_probability(Nh,Mh,nh) for Nh,Mh in zip(sizes,changed_sizes)]))
                raw[f'n{n}_paired_sampled_reference_changes']=sampled_changes
                for method in ['direct','model_assisted']:
                    ppa,ppb=(None,None) if method=='direct' else (pa,pb)
                    for design in ['paired','independent']:
                        sb=sa if design=='paired' else indb
                        result=stratified_change(ya,yb,ppa,ppb,sa,sb,sizes,k,design=='paired')
                        error=result['estimate']-truth
                        covered=(result['low']<=truth+NUMERICAL_TOL)&(result['high']>=truth-NUMERICAL_TOL)
                        reported=result['direction']!=0;wrong=reported&(result['direction']!=sign(truth))
                        pre=f'{method}_{design}_{n}_'
                        for name in ['estimate','se','direction','projected_a','projected_b']:raw[pre+name]=result[name]
                        raw[pre+'covered']=covered;raw[pre+'wrong']=wrong
                        row=dict(unit_id=u['unit_id'],landscape_id=lid,representation=meta['representation'],method=method,design=design,n=n,N=N,
                                 true_change=truth,replications=len(error),mse=float(np.mean(error**2)),bias=float(error.mean()),
                                 coverage=float(covered.mean()),report_rate=float(reported.mean()),wrong_report_rate=float(wrong.mean()),
                                 reports=int(reported.sum()),wrong_reports=int(wrong.sum()),
                                 projection_any_year=float((result['projected_a']|result['projected_b']).mean()),
                                 zero_se_rate=float((result['se']==0).mean()),
                                 exact_paired_no_change_probability=exact_p0,empirical_paired_no_change=float((sampled_changes==0).mean()))
                        rows.append(row);key=(method,design,n)
                        for name,value in dict(squared_error=error**2,error=error,coverage=covered,report_rate=reported,
                                               wrong_report_rate=wrong,projection=(result['projected_a']|result['projected_b']),
                                               zero_se=result['se']==0,paired_no_change=sampled_changes==0).items():aggregate[key][name].append(value)
                        comparison[key]['original_squared_error'].append((orig[pre+'estimate']-truth)**2)
                        comparison[key]['stratified_squared_error'].append(error**2)
        target=out/'raw'/f"{u['unit_id']}.npz";np.savez_compressed(target,**raw)
        with (out/'contexts.jsonl').open('a') as f:f.write(json.dumps(clean_json(context),allow_nan=False)+'\n')
    frame=pd.DataFrame(rows);frame.to_csv(out/'unit-performance.csv',index=False)
    pd.DataFrame(contexts).drop(columns=['draw_path','draw_sha256']).to_csv(out/'stratum-context.csv',index=False)
    summary=[]
    for (method,design,n),values in aggregate.items():
        row=dict(representation=meta['representation'],method=method,design=design,n=n,units=len(units),replications=500)
        for name,value in values.items():
            mean,se=probability_summary(value);row[name]=mean;row[name+'_mcse']=se
        row['mse']=row.pop('squared_error');row['mse_mcse']=row.pop('squared_error_mcse');row['rmse']=float(np.sqrt(row['mse']))
        row['rmse_mcse']=row['mse_mcse']/(2*row['rmse']) if row['rmse'] else 0.;row['bias']=row.pop('error');row.pop('error_mcse')
        selected=frame[(frame.method==method)&(frame.design==design)&(frame.n==n)]
        row['reports']=int(selected.reports.sum());row['wrong_reports']=int(selected.wrong_reports.sum())
        row['wrong_conditional']=row['wrong_reports']/row['reports'] if row['reports'] else None
        c=comparison[method,design,n];base=np.asarray(c['original_squared_error']).mean(axis=0);alt=np.asarray(c['stratified_squared_error']).mean(axis=0)
        mb=base.mean();ma=alt.mean();row['stratified_original_mse_ratio']=float(ma/mb) if mb>1e-20 else None
        row['mse_ratio_mcse']=float(np.std(alt/mb-ma*base/mb**2,ddof=1)/np.sqrt(len(base))) if mb>1e-20 else None
        summary.append(row)
    pd.DataFrame(summary).to_csv(out/'summary.csv',index=False)
    result=dict(completed_at_utc=now(),plan_path='protocol/plan-v6-sparse-change.md',exploratory=True,
                analysis_path=analysis_path,analysis_sha256=digest(source/'analysis.json'),units_sha256=digest(source/'units.jsonl'),
                representation=meta['representation'],units=len(units),summary=summary,
                strata='Highest ceil(N/4) L1 annual probability differences, ties by original population index; equal n/2 allocation',
                interpretation='Same number of labels, no measured field costs. Strata differ by representation; all original SRS results retained; nominal intervals remain approximate.')
    (out/'analysis.json').write_text(json.dumps(clean_json(result),indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(completed_at_utc=now(),units=len(units),destination=destination)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--analysis',required=True);p.add_argument('--destination',required=True)
    a=p.parse_args();run(a.analysis,a.destination)
