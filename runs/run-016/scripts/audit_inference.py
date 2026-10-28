"""Recompute planned finite-budget audit inference from saved predictions/draws."""
import argparse,json
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from records import ROOT,now,digest
from inference_core import entropy,simplex,estimate_change,influence_diagnostic,NUMERICAL_TOL

def clean_json(obj):
    if isinstance(obj,dict):return {str(k):clean_json(v) for k,v in obj.items()}
    if isinstance(obj,(list,tuple)):return [clean_json(v) for v in obj]
    if isinstance(obj,np.ndarray):return clean_json(obj.tolist())
    if isinstance(obj,np.integer):return int(obj)
    if isinstance(obj,(float,np.floating)):return float(obj) if np.isfinite(obj) else None
    if isinstance(obj,np.bool_):return bool(obj)
    return obj

def quantification(C,q,prior):
    lam=1e-6
    def fun(p):
        d=C@p-q
        return np.dot(d,d)+lam*np.dot(p-prior,p-prior)
    def jac(p):return 2*C.T@(C@p-q)+2*lam*(p-prior)
    result=minimize(fun,prior,method='SLSQP',jac=jac,bounds=[(0.,1.)]*len(q),
                    constraints=[dict(type='eq',fun=lambda p:p.sum()-1,jac=lambda p:np.ones(len(p)))],
                    options=dict(maxiter=1000,ftol=1e-12))
    return simplex(result.x),dict(success=bool(result.success),status=int(result.status),
                message=str(result.message),iterations=int(result.nit),objective=float(result.fun),
                prior_regularizer=lam,residual_norm=float(np.linalg.norm(C@result.x-q)))

def sign(x):return int(np.sign(x)) if abs(x)>NUMERICAL_TOL else 0

def run(model_path,draw_manifest_path,destination,max_units=None):
    model_dir=ROOT/model_path;fit=json.loads((model_dir/'fit.json').read_text())
    draws=json.loads((ROOT/draw_manifest_path).read_text())
    manifest=json.loads((ROOT/fit['manifest_path']).read_text())
    out=Path(destination)
    if not out.is_absolute():out=ROOT/out
    if out.exists():raise FileExistsError('Preserve prior inference outputs')
    out.mkdir(parents=True);(out/'raw').mkdir()
    k=len(fit['class_names']);files={r['landscape_id']:r for r in fit['prediction_files']}
    population={r['landscape_id']:r for r in manifest['landscapes']}
    classes_by_year={r['year']:np.array(r['classes']) for r in fit['fit_records']}
    with np.load(model_dir/'source-calibration.npz') as z:C=z['soft_confusion'];prior=z['prior']
    cache={};rows=[]
    for unit in draws['draws']:
        if max_units is not None and len(rows)>=max_units:break
        lid=unit['landscape_id'];a=unit['year_a'];b=unit['year_b'];uid=f'{lid}-{a}-{b}'
        print('INFERENCE',uid,fit['representation'],fit['taxonomy'],flush=True)
        if lid not in cache:
            entry=files[lid];assert digest(ROOT/entry['path'])==entry['sha256']
            with np.load(ROOT/entry['path']) as z:cache[lid]=(z['probabilities'],z['labels'])
        p,y=cache[lid];pa=p[a-2021];pb=p[b-2021];ya=y[a-2021];yb=y[b-2021]
        classes_a=classes_by_year[a if fit['refreshed'] else 2021]
        classes_b=classes_by_year[b if fit['refreshed'] else 2021]
        assert np.isfinite(pa).all() and np.isfinite(pb).all() and len(ya)==unit['N']
        assert digest(ROOT/unit['path'])==unit['sha256']
        with np.load(ROOT/unit['path']) as z:ia=z['a'];ib=z['b']
        qa=np.bincount(ya,minlength=k)/len(ya);qb=np.bincount(yb,minlength=k)/len(yb)
        ha=float(entropy(qa));hb=float(entropy(qb));truth=hb-ha
        softa=simplex(pa.mean(axis=0,dtype=np.float64));softb=simplex(pb.mean(axis=0,dtype=np.float64))
        harda=np.bincount(pa.argmax(axis=1),minlength=k)/len(ya)
        hardb=np.bincount(pb.argmax(axis=1),minlength=k)/len(yb)
        if fit['refreshed']:
            cca=ccb=None;qda=qdb=dict(success=False,message='Not applicable: different current-year heads')
        else:cca,qda=quantification(C,softa,prior);ccb,qdb=quantification(C,softb,prior)
        point_estimates={'no_change':0.,'soft_count':float(entropy(softb)-entropy(softa)),
                         'hard_count':float(entropy(hardb)-entropy(harda)),
                         'source_confusion':float(entropy(ccb)-entropy(cca)) if qda['success'] and qdb['success'] else None}
        row=dict(unit_id=uid,landscape_id=lid,year_a=a,year_b=b,primary=unit['primary'],N=len(ya),
                 true_entropy_a=ha,true_entropy_b=hb,true_change=truth,
                 true_counts_a=np.bincount(ya,minlength=k),true_counts_b=np.bincount(yb,minlength=k),
                 tiny_change=abs(truth)<.01,entropy_floor=min(ha,hb)<.05,
                 entropy_ceiling=np.log(k)-max(ha,hb)<.05,
                 observed_groups_a=int((qa>0).sum()),observed_groups_b=int((qb>0).sum()),
                 observed_support_entropy_ceiling=(np.log((qa>0).sum())-ha<.05 or np.log((qb>0).sum())-hb<.05),
                 positive_class_mass_below_1_over_128_a=float(qa[(qa>0)&(qa<1/128)].sum()),
                 positive_class_mass_below_1_over_128_b=float(qb[(qb>0)&(qb<1/128)].sum()),
                 prediction_mass_on_absent_groups_a=float(softa[qa==0].sum()),
                 prediction_mass_on_absent_groups_b=float(softb[qb==0].sum()),
                 single_group_a=int((qa>0).sum())==1,single_group_b=int((qb>0).sum())==1,
                 labels_unchanged_fraction=float((ya==yb).mean()),
                 reference_proportions_identical=bool(np.array_equal(np.bincount(ya,minlength=k),np.bincount(yb,minlength=k))),
                 predicted_probabilities_identical=bool(np.max(np.abs(pa-pb))<=1e-6),
                 spatially_constant_predictions_a=bool(np.max(np.ptp(pa,axis=0))<=1e-6),
                 spatially_constant_predictions_b=bool(np.max(np.ptp(pb,axis=0))<=1e-6),
                 source_unsupported_fraction_a=float((~np.isin(ya,classes_a)).mean()),
                 source_unsupported_fraction_b=float((~np.isin(yb,classes_b)).mean()),
                 point_estimates=point_estimates,source_quantification_a=qda,source_quantification_b=qdb,
                 baseline_arable_fraction=population[lid].get('baseline_arable_fraction'),
                 baseline_grassland_fraction=population[lid].get('baseline_grassland_fraction'),
                 oracle={},summaries=[])
        raw={}
        for method in ['direct','model_assisted']:
            pp_a,pp_b=(None,None) if method=='direct' else (pa,pb)
            row['oracle'][method]=influence_diagnostic(ya,yb,pp_a,pp_b,k,128)
            for design in ['paired','independent']:
                for n in unit['budgets']:
                    sa=ia[:,:n].astype(int);sb=(ia if design=='paired' else ib)[:,:n].astype(int)
                    result=estimate_change(ya,yb,pp_a,pp_b,sa,sb,k,design=='paired')
                    error=result['estimate']-truth
                    covered=(result['low']<=truth+NUMERICAL_TOL)&(result['high']>=truth-NUMERICAL_TOL)
                    reported=result['direction']!=0;wrong=reported&(result['direction']!=sign(truth))
                    prefix=f'{method}_{design}_{n}_'
                    for name in ['estimate','se','direction','projected_a','projected_b','projection_l1_a','projection_l1_b']:
                        raw[prefix+name]=result[name]
                    raw[prefix+'covered']=covered;raw[prefix+'wrong']=wrong
                    row['summaries'].append(dict(method=method,design=design,n=n,replications=len(error),
                            bias=float(error.mean()),mse=float(np.mean(error**2)),variance=float(np.var(result['estimate'],ddof=0)),
                            coverage=float(covered.mean()),report_rate=float(reported.mean()),wrong_report_rate=float(wrong.mean()),
                            report_count=int(reported.sum()),wrong_count=int(wrong.sum()),
                            wrong_conditional=float(wrong.sum()/reported.sum()) if reported.any() else None,
                            mean_se=float(result['se'].mean()),projection_rate_a=float(result['projected_a'].mean()),
                            projection_rate_b=float(result['projected_b'].mean())))
        raw_path=out/'raw'/f'{uid}.npz';np.savez_compressed(raw_path,**raw)
        row['raw_path']=str(raw_path.relative_to(out));row['raw_sha256']=digest(raw_path)
        rows.append(clean_json(row))
        # Checkpoint completed units so a timeout/failure cannot erase their results.
        with (out/'units.jsonl').open('a') as f:f.write(json.dumps(clean_json(row),allow_nan=False)+'\n')
    result=dict(completed_at_utc=now(),model_path=model_path,model_fit_sha256=digest(model_dir/'fit.json'),
                draw_manifest_path=draw_manifest_path,draw_manifest_sha256=digest(ROOT/draw_manifest_path),
                representation=fit['representation'],taxonomy=fit['taxonomy'],classifier=fit['classifier'],
                refreshed=fit['refreshed'],class_names=fit['class_names'],units=len(rows),
                primary_units=sum(r['primary'] for r in rows),settings=dict(gradient_epsilon=1e-6,numerical_tolerance=1e-10,
                           interval='delta-method normal 1.96; empirical coverage is evaluated, not guaranteed',
                           source_quantification_prior_regularizer=1e-6))
    result['max_units_requested']=max_units
    (out/'analysis.json').write_text(json.dumps(clean_json(result),indent=2,allow_nan=False)+'\n')
    print(json.dumps(result),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--draw-manifest',required=True)
    p.add_argument('--destination',required=True);p.add_argument('--max-units',type=int);a=p.parse_args()
    run(a.model,a.draw_manifest,a.destination,a.max_units)
