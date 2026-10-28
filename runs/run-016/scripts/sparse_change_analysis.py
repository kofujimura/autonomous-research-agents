"""Exploratory sparse-change diagnostics from the original saved audit draws."""
import argparse,json
from pathlib import Path
from collections import defaultdict
import numpy as np,pandas as pd
from records import ROOT,now,digest
from audit_inference import clean_json
from inference_core import NUMERICAL_TOL
from sparse_change_core import changed_count_upper,entropy_envelope,no_change_probability
from summarize_inference import probability_summary

def run(analysis_path,destination):
    source=ROOT/analysis_path;meta=json.loads((source/'analysis.json').read_text())
    assert meta['max_units_requested'] is None and meta['taxonomy']=='broad'
    units=[r for r in map(json.loads,(source/'units.jsonl').read_text().splitlines()) if r['primary']]
    fit=json.loads((ROOT/meta['model_path']/'fit.json').read_text());k=len(fit['class_names'])
    files={r['landscape_id']:r for r in fit['prediction_files']}
    draw_meta=json.loads((ROOT/meta['draw_manifest_path']).read_text())
    draws={(r['landscape_id'],r['year_a'],r['year_b']):r for r in draw_meta['draws']}
    out=ROOT/destination
    if out.exists():raise FileExistsError('Preserve prior exploratory results')
    out.mkdir(parents=True);(out/'raw').mkdir();rows=[];conditional=[];aggregate=defaultdict(lambda:defaultdict(list));cache={}
    for u in units:
        lid=u['landscape_id'];a=u['year_a'];b=u['year_b'];N=u['N'];truth=u['true_change']
        if lid not in cache:
            entry=files[lid];assert digest(ROOT/entry['path'])==entry['sha256']
            with np.load(ROOT/entry['path']) as z:cache[lid]=z['labels']
        y=cache[lid];changed=y[a-2021]!=y[b-2021];M=int(changed.sum())
        draw=draws[lid,a,b];assert digest(ROOT/draw['path'])==draw['sha256']
        with np.load(ROOT/draw['path']) as z:ia=z['a']
        path=source/u['raw_path'];assert digest(path)==u['raw_sha256']
        raw={}
        with np.load(path) as z:
            for n in [32,64,128,256,512]:
                x=changed[ia[:,:n]].sum(axis=1);zero=x==0
                pre=f'direct_paired_{n}_';est=z[pre+'estimate'];se=z[pre+'se']
                original=z[pre+'covered'];directions=z[pre+'direction'];wrong=z[pre+'wrong']
                assert np.all(np.abs(est[zero])<=1e-12) and np.all(se[zero]==0)
                if abs(truth)>NUMERICAL_TOL:assert not original[zero].any()
                upper=np.array([changed_count_upper(N,n,int(v)) for v in x],int)
                half=entropy_envelope(upper/N,k);low=est-1.96*se;high=est+1.96*se
                guarded_low=np.where(zero,np.minimum(low,-half),low)
                guarded_high=np.where(zero,np.maximum(high,half),high)
                guard=(guarded_low<=truth+NUMERICAL_TOL)&(guarded_high>=truth-NUMERICAL_TOL)
                envelope=np.abs(truth)<=half+NUMERICAL_TOL
                guarded_direction=np.where(guarded_low>NUMERICAL_TOL,1,np.where(guarded_high< -NUMERICAL_TOL,-1,0))
                assert np.array_equal(guarded_direction,directions),'The zero-change guard must not change direction reports'
                p0=no_change_probability(N,M,n);cap=1-p0 if abs(truth)>NUMERICAL_TOL else 1.
                for name,value in dict(observed_changes=x,upper_changed_count=upper,envelope_half_width=half,
                                       guarded_low=guarded_low,guarded_high=guarded_high,guarded_covered=guard,
                                       envelope_covered=envelope).items():raw[f'n{n}_{name}']=value
                row=dict(unit_id=u['unit_id'],landscape_id=lid,year_a=a,year_b=b,n=n,N=N,population_changed=M,
                         changed_fraction=M/N,true_change=truth,true_change_nonzero=abs(truth)>NUMERICAL_TOL,
                         exact_no_sampled_change_probability=p0,exact_coverage_ceiling=cap,ceiling_below_0_95=cap<.95-1e-12,
                         empirical_no_sampled_change=float(zero.mean()),original_coverage=float(original.mean()),
                         guarded_coverage=float(guard.mean()),envelope_coverage=float(envelope.mean()),
                         zero_se_rate=float((se==0).mean()),original_report_rate=float((directions!=0).mean()),
                         wrong_report_rate=float(wrong.mean()),guarded_report_rate=float((guarded_direction!=0).mean()),
                         mean_original_width=float((3.92*se).mean()),mean_guarded_width=float((guarded_high-guarded_low).mean()),
                         mean_envelope_width=float((2*half).mean()),
                         mean_envelope_half_width_when_no_changes=float(half[zero].mean()) if zero.any() else None)
                rows.append(row)
                values=dict(original_coverage=original,guarded_coverage=guard,envelope_coverage=envelope,
                            zero_sampled_changes=zero,zero_se=(se==0),original_wrong_report=wrong,
                            miss_with_zero_changes=(~original)&zero,original_miss=~original,
                            original_width=3.92*se,guarded_width=guarded_high-guarded_low,envelope_width=2*half)
                for name,value in values.items():aggregate[n][name].append(value)
                for label,mask in [('0',x==0),('1',x==1),('2',x==2),('3-4',(x>=3)&(x<=4)),('>=5',x>=5)]:
                    conditional.append(dict(unit_id=u['unit_id'],n=n,observed_changed_bin=label,trials=int(mask.sum()),
                                            covered=int(original[mask].sum()),reports=int((directions[mask]!=0).sum()),
                                            wrong_reports=int(wrong[mask].sum()),zero_se=int((se[mask]==0).sum())))
        target=out/'raw'/f"{u['unit_id']}.npz";np.savez_compressed(target,**raw)
    frame=pd.DataFrame(rows);frame.to_csv(out/'unit-diagnostics.csv',index=False)
    cond=pd.DataFrame(conditional);grouped=cond.groupby(['n','observed_changed_bin'],sort=True)[['trials','covered','reports','wrong_reports','zero_se']].sum().reset_index()
    for name,denom in [('coverage','covered'),('report_rate','reports'),('wrong_report_rate','wrong_reports')]:
        grouped[name]=np.where(grouped.trials>0,grouped[denom]/grouped.trials,np.nan)
    grouped.to_csv(out/'conditional-on-observed-changes.csv',index=False)
    summaries=[]
    for n,values in aggregate.items():
        row=dict(n=n,units=len(units),replications=len(values['original_coverage'][0]),
                 true_nonzero_units=int(frame[(frame.n==n)].true_change_nonzero.sum()),
                 units_coverage_ceiling_below_0_95=int(frame[frame.n==n].ceiling_below_0_95.sum()),
                 mean_exact_coverage_ceiling=float(frame[frame.n==n].exact_coverage_ceiling.mean()))
        for name,value in values.items():
            mean,se=probability_summary(value);row[name]=mean;row[name+'_mcse']=se
        row['fraction_of_original_misses_with_zero_changes']=row['miss_with_zero_changes']/row['original_miss'] if row['original_miss'] else None
        summaries.append(row)
    pd.DataFrame(summaries).to_csv(out/'summary.csv',index=False)
    result=dict(completed_at_utc=now(),plan_path='protocol/plan-v6-sparse-change.md',exploratory=True,
                analysis_path=analysis_path,analysis_sha256=digest(source/'analysis.json'),units_sha256=digest(source/'units.jsonl'),
                units=len(units),taxonomy_groups=k,summary=summaries,
                interpretation='Exact ceiling/envelope are elementary consequences, not new empirical discoveries. The guard cannot improve direction reporting on zero-change samples and has no uniform guarantee outside its exact-envelope branch.')
    (out/'analysis.json').write_text(json.dumps(clean_json(result),indent=2,allow_nan=False)+'\n');print(json.dumps(clean_json(result)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--analysis',required=True);p.add_argument('--destination',required=True)
    a=p.parse_args();run(a.analysis,a.destination)
