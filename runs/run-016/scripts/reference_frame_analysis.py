"""Exploratory direct-sampling scope checks without any embedding requirement."""
import argparse,hashlib,json
from collections import defaultdict
import numpy as np,pandas as pd
from records import ROOT,now,digest
from inference_core import entropy,estimate_change,influence_diagnostic,population_influence,NUMERICAL_TOL
from audit_inference import clean_json,sign
from summarize_inference import probability_summary
from sparse_change_core import no_change_probability
from draw_audits import PAIRS

def run(source_manifest_path,destination,arable_only=False,selection_ledger='data/selection-results.jsonl',expected_landscapes=30,plan_path=None,replications=500,keep_draws=True,array_observer=None):
    source=json.loads((ROOT/source_manifest_path).read_text())
    latest={r['landscape_id']:r for r in map(json.loads,(ROOT/selection_ledger).read_text().splitlines())}
    tests=[r for r in latest.values() if r['status']=='accepted' and r['split']=='test'];assert len(tests)==expected_landscapes
    out=ROOT/destination
    if out.exists():raise FileExistsError('Preserve reference-frame results')
    out.mkdir(parents=True);(out/'draws').mkdir();(out/'raw').mkdir()
    inputs=[];units=[];table=[];aggregate=defaultdict(lambda:defaultdict(list));ratio_inputs=defaultdict(lambda:defaultdict(list));cohort=[]
    if arable_only:
        taxonomy=json.loads((ROOT/'data/taxonomy.json').read_text())
        hierarchy=pd.read_csv(ROOT/'sources/swisscrop25-crop-classes.csv').dropna(subset=['Crop_Label_lv1','Crop_Label_lv3'])
        parents=dict(hierarchy[['Crop_Label_lv1','Crop_Label_lv3']].values)
        arable_ids=[i for i,name in enumerate(taxonomy['fine']) if parents.get(name)=='Arable Land']
        assert arable_ids
    for rec in tests:
        lid=rec['landscape_id'];assert digest(ROOT/rec['path'])==rec['sha256'];inputs.append(dict(path=rec['path'],sha256=rec['sha256']))
        with np.load(ROOT/rec['path']) as z:
            if arable_only:
                support=z['support']&np.isin(z['fine_raster'],arable_ids).all(axis=0)
                count=int(support.sum());eligible=count>=1024
                cohort.append(dict(landscape_id=lid,stable_arable_pixels=count,included=eligible,
                    reason='at_least_1024' if eligible else 'fewer_than_1024',support_sha256=hashlib.sha256(support.tobytes()).hexdigest()))
                frames={'stable_arable':{t:z[t+'_raster'][:,support] for t in ['broad','fine']}} if eligible else {}
            else:
                frames={'original_points':{t:z[t] for t in ['broad','fine']},
                        'full_reference':{t:z[t+'_raster'][:,z['support']] for t in ['broad','fine']}}
        for frame,labels in frames.items():
            N=labels['broad'].shape[1]
            if frame=='original_points':assert N==4096
            elif frame=='full_reference':assert N==rec['stable_agricultural_pixels']
            for a,b in PAIRS[:3]:
                uid=f'{lid}-{a}-{b}';seed=int.from_bytes(hashlib.sha256(f'16016/reference-frame/{frame}/{lid}/{a}/{b}'.encode()).digest()[:8],'little')
                rng=np.random.default_rng(seed);dtype=np.uint16 if N<=65535 else np.uint32
                ia=np.stack([rng.choice(N,512,replace=False).astype(dtype) for _ in range(replications)])
                ib=np.stack([rng.choice(N,512,replace=False).astype(dtype) for _ in range(replications)])
                dp=out/'draws'/f'{frame}-{uid}.npz'
                if keep_draws:
                    np.savez_compressed(dp,a=ia,b=ib,N=N,seed=seed)
                    if array_observer is not None:array_observer(dp)
                draw_spec=dict(seed=seed,shape=list(ia.shape),dtype=ia.dtype.str,
                    a_array_sha256=hashlib.sha256(ia.tobytes()).hexdigest(),b_array_sha256=hashlib.sha256(ib.tobytes()).hexdigest(),
                    generation='NumPy default_rng(seed); all A choice(N,512,replace=False) rows, then all B rows; saved source labels define N')
                for taxonomy in ['broad','fine']:
                    print('REFERENCE FRAME',frame,taxonomy,uid,N,flush=True)
                    ids=source[taxonomy+'_ids'];k=len(ids);lookup=np.full(256,-1,np.int16);lookup[ids]=np.arange(k)
                    ya=lookup[labels[taxonomy][a-2021]];yb=lookup[labels[taxonomy][b-2021]]
                    assert (ya>=0).all() and (yb>=0).all()
                    qa=np.bincount(ya,minlength=k)/N;qb=np.bincount(yb,minlength=k)/N
                    ha=float(entropy(qa));hb=float(entropy(qb));truth=hb-ha;changed=ya!=yb;M=int(changed.sum())
                    _,phi_a=population_influence(ya,None,k);_,phi_b=population_influence(yb,None,k)
                    first_phase=(1-4096/N)*float(np.var(phi_b-phi_a,ddof=1))/4096 if frame=='full_reference' else None
                    unit=dict(unit_id=uid,landscape_id=lid,frame=frame,taxonomy=taxonomy,k=k,N=N,
                              true_entropy_a=ha,true_entropy_b=hb,true_change=truth,
                              true_counts_a=np.bincount(ya,minlength=k),true_counts_b=np.bincount(yb,minlength=k),
                              changed_reference_locations=M,changed_fraction=M/N,
                              zero_change=abs(truth)<=NUMERICAL_TOL,tiny_change=abs(truth)<.01,entropy_floor=min(ha,hb)<.05,
                              single_group_either_year=(qa>0).sum()==1 or (qb>0).sum()==1,
                              single_group_both_years=(qa>0).sum()==1 and (qb>0).sum()==1,
                              reference_proportions_identical=bool(np.array_equal(np.bincount(ya,minlength=k),np.bincount(yb,minlength=k))),
                              first_phase_paired_reference_variance_n4096=first_phase,
                              oracle=influence_diagnostic(ya,yb,None,None,k,128),
                              draw_path=str(dp.relative_to(out)) if keep_draws else None,draw_sha256=digest(dp) if keep_draws else None,summaries=[])
                    if not keep_draws:unit['draw_generation']=draw_spec
                    raw={}
                    for n in [32,64,128,256,512]:
                        sa=ia[:,:n].astype(int);sample_changes=changed[sa].sum(axis=1);p0=no_change_probability(N,M,n)
                        raw[f'n{n}_paired_sampled_reference_changes']=sample_changes
                        for design in ['paired','independent']:
                            sb=sa if design=='paired' else ib[:,:n].astype(int)
                            result=estimate_change(ya,yb,None,None,sa,sb,k,design=='paired')
                            error=result['estimate']-truth
                            covered=(result['low']<=truth+NUMERICAL_TOL)&(result['high']>=truth-NUMERICAL_TOL)
                            reported=result['direction']!=0;wrong=reported&(result['direction']!=sign(truth))
                            prefix=f'{design}_{n}_'
                            for name in ['estimate','se','direction']:raw[prefix+name]=result[name]
                            raw[prefix+'covered']=covered;raw[prefix+'wrong']=wrong
                            s=dict(design=design,n=n,replications=len(error),mse=float(np.mean(error**2)),bias=float(error.mean()),
                                   coverage=float(covered.mean()),report_rate=float(reported.mean()),wrong_report_rate=float(wrong.mean()),
                                   reports=int(reported.sum()),wrong_reports=int(wrong.sum()),zero_se_rate=float((result['se']==0).mean()),
                                   exact_paired_no_change_probability=p0,empirical_paired_no_change=float((sample_changes==0).mean()))
                            s['exact_paired_coverage_ceiling']=1-p0 if abs(truth)>NUMERICAL_TOL else 1.
                            unit['summaries'].append(s);table.append(dict(frame=frame,taxonomy=taxonomy,unit_id=uid,landscape_id=lid,N=N,true_change=truth,**s))
                            key=(frame,taxonomy,design,n)
                            for name,value in dict(squared_error=error**2,error=error,coverage=covered,report_rate=reported,
                                                   wrong_report_rate=wrong,zero_se=result['se']==0,paired_no_change=sample_changes==0).items():aggregate[key][name].append(value)
                            ratio_inputs[frame,taxonomy,n][design].append(error**2)
                    rp=out/'raw'/f'{frame}-{taxonomy}-{uid}.npz';np.savez_compressed(rp,**raw)
                    if array_observer is not None:array_observer(rp)
                    unit.update(raw_path=str(rp.relative_to(out)),raw_sha256=digest(rp));units.append(clean_json(unit))
                    with (out/'units.jsonl').open('a') as f:f.write(json.dumps(clean_json(unit),allow_nan=False)+'\n')
    perf=pd.DataFrame(table);perf.to_csv(out/'unit-performance.csv',index=False);summary=[]
    for (frame,taxonomy,design,n),values in aggregate.items():
        row=dict(frame=frame,taxonomy=taxonomy,design=design,n=n,units=len(values['coverage']),replications=replications)
        for name,value in values.items():
            mean,se=probability_summary(value);row[name]=mean;row[name+'_mcse']=se
        row['mse']=row.pop('squared_error');row['mse_mcse']=row.pop('squared_error_mcse');row['rmse']=float(np.sqrt(row['mse']))
        row['rmse_mcse']=row['mse_mcse']/(2*row['rmse']) if row['rmse'] else 0.;row['bias']=row.pop('error');row.pop('error_mcse')
        g=perf[(perf.frame==frame)&(perf.taxonomy==taxonomy)&(perf.design==design)&(perf.n==n)]
        row['reports']=int(g.reports.sum());row['wrong_reports']=int(g.wrong_reports.sum())
        row['wrong_conditional']=row['wrong_reports']/row['reports'] if row['reports'] else None
        summary.append(row)
    pd.DataFrame(summary).to_csv(out/'summary.csv',index=False);ratios=[]
    for (frame,taxonomy,n),values in ratio_inputs.items():
        p=np.asarray(values['paired']).mean(axis=0);i=np.asarray(values['independent']).mean(axis=0);mp=p.mean();mi=i.mean()
        ratios.append(dict(frame=frame,taxonomy=taxonomy,n=n,units=len(values['paired']),
                           paired_independent_mse_ratio=float(mp/mi) if mi>1e-20 else None,
                           ratio_mcse=float(np.std(p/mi-mp*i/mi**2,ddof=1)/np.sqrt(len(p))) if mi>1e-20 else None))
    pd.DataFrame(ratios).to_csv(out/'pairing-ratios.csv',index=False)
    changes=pd.DataFrame([{k:u[k] for k in ['unit_id','landscape_id','frame','taxonomy','N','true_change','changed_fraction','zero_change','tiny_change','entropy_floor','single_group_either_year','single_group_both_years','reference_proportions_identical','first_phase_paired_reference_variance_n4096']} for u in units])
    changes.to_csv(out/'reference-changes.csv',index=False);cases=[]
    for (frame,taxonomy),g in changes.groupby(['frame','taxonomy']):
        cases.append(dict(frame=frame,taxonomy=taxonomy,units=len(g),landscapes=g.landscape_id.nunique(),
                          zero_change=int(g.zero_change.sum()),tiny_change=int(g.tiny_change.sum()),entropy_floor=int(g.entropy_floor.sum()),
                          single_group_either_year=int(g.single_group_either_year.sum()),single_group_both_years=int(g.single_group_both_years.sum()),
                          labels_unchanged_all=int((g.changed_fraction==0).sum()),reference_proportions_identical=int(g.reference_proportions_identical.sum()),
                          median_changed_fraction=float(g.changed_fraction.median()),population_points_sum=int(g.groupby('landscape_id').N.first().sum())))
    pd.DataFrame(cases).to_csv(out/'case-counts.csv',index=False)
    result=dict(completed_at_utc=now(),plan_path=plan_path or ('protocol/plan-v10-arable-boundary.md' if arable_only else 'protocol/plan-v7-reference-frame.md'),exploratory=True,
                source_manifest_path=source_manifest_path,source_manifest_sha256=digest(ROOT/source_manifest_path),
                label_inputs=inputs,units=len(units),cases=cases,summary=summary,pairing_ratios=ratios,
                cohort=cohort,selection_ledger=selection_ledger,
                scope=(f'Stable Arable Land support in the same{len(tests)}candidates; inclusion requires1024pixels, no replacements, no satellite-assisted estimates on this changed frame.' if arable_only else f'The{len(tests)}fixed test landscapes in the recorded selection ledger; full stable declared agricultural support versus initial unmasked points, no embeddings or new models. Not nationally representative or independent reproduction.'))
    if arable_only:
        (out/'cohort.json').write_text(json.dumps(dict(cohort=cohort,hierarchy_sha256=digest(ROOT/'sources/swisscrop25-crop-classes.csv'),arable_fine_ids=arable_ids),indent=2)+'\n')
    (out/'analysis.json').write_text(json.dumps(clean_json(result),indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(completed_at_utc=now(),units=len(units),destination=destination)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-manifest',required=True);p.add_argument('--destination',required=True)
    p.add_argument('--arable-only',action='store_true')
    a=p.parse_args();run(a.source_manifest,a.destination,a.arable_only)
