"""Interpret the saved reference-frame experiment using fixed context subsets."""
import argparse,json
from collections import defaultdict
import numpy as np,pandas as pd
from records import ROOT,now,digest
from summarize_inference import probability_summary
from audit_inference import clean_json

def run(source_path,destination):
    source=ROOT/source_path;units=[json.loads(s) for s in (source/'units.jsonl').read_text().splitlines()]
    out=ROOT/destination
    if out.exists():raise FileExistsError('Preserve previous context summaries')
    out.mkdir(parents=True);rows=[];groups=defaultdict(list)
    for u in units:groups[u['frame'],u['taxonomy']].append(u)
    for (frame,taxonomy),uu in groups.items():
        for subset in ['all','absolute_change_at_least_0.01','absolute_change_below_0.01','nonzero_change']:
            selected=[u for u in uu if subset=='all' or (not u['tiny_change'] if subset=='absolute_change_at_least_0.01' else u['tiny_change'] if subset=='absolute_change_below_0.01' else not u['zero_change'])]
            if not selected:continue
            raw=[]
            for u in selected:
                p=source/u['raw_path'];assert digest(p)==u['raw_sha256']
                with np.load(p) as z:raw.append({k:z[k] for k in z.files})
            truth=np.array([u['true_change'] for u in selected])[:,None]
            for n in [32,64,128,256,512]:
                for design in ['paired','independent']:
                    prefix=f'{design}_{n}_';est=np.stack([r[prefix+'estimate'] for r in raw]);error=est-truth
                    covered=np.stack([r[prefix+'covered'] for r in raw]);wrong=np.stack([r[prefix+'wrong'] for r in raw])
                    direction=np.stack([r[prefix+'direction'] for r in raw]);se=np.stack([r[prefix+'se'] for r in raw])
                    row=dict(frame=frame,taxonomy=taxonomy,subset=subset,design=design,n=n,units=len(selected),replications=est.shape[1])
                    for name,value in dict(squared_error=error**2,coverage=covered,report_rate=direction!=0,wrong_report_rate=wrong,zero_se=se==0).items():
                        mean,mcse=probability_summary(value);row[name]=mean;row[name+'_mcse']=mcse
                    row['mse']=row.pop('squared_error');row['mse_mcse']=row.pop('squared_error_mcse');row['rmse']=float(np.sqrt(row['mse']))
                    row['rmse_mcse']=row['mse_mcse']/(2*row['rmse']) if row['rmse'] else 0.
                    row['reports']=int((direction!=0).sum());row['wrong_reports']=int(wrong.sum())
                    row['wrong_conditional']=row['wrong_reports']/row['reports'] if row['reports'] else None
                    row['median_unit_coverage']=float(np.median(covered.mean(axis=1)))
                    row['coverage_q10']=float(np.quantile(covered.mean(axis=1),.1));row['coverage_q90']=float(np.quantile(covered.mean(axis=1),.9))
                    row['maximum_unit_wrong_report_rate']=float(wrong.mean(axis=1).max())
                    row['units_observed_wrong_report_rate_above_0_05']=int((wrong.mean(axis=1)>.05).sum())
                    row['warning']='Observed case rate thresholds are descriptive Monte Carlo counts, not significance tests or population inference.'
                    rows.append(row)
    pd.DataFrame(rows).to_csv(out/'subset-performance.csv',index=False)
    change=pd.DataFrame([{k:u[k] for k in ['unit_id','landscape_id','frame','taxonomy','N','true_change','changed_fraction','first_phase_paired_reference_variance_n4096']} for u in units])
    comparisons=[]
    for (uid,taxonomy),g in change.groupby(['unit_id','taxonomy']):
        v=g.set_index('frame');a=float(v.loc['original_points','true_change']);c=float(v.loc['full_reference','true_change'])
        comparisons.append(dict(unit_id=uid,landscape_id=g.landscape_id.iloc[0],taxonomy=taxonomy,point_change=a,full_change=c,
                                point_minus_full=a-c,opposite_nonzero_signs=a*c< -1e-20,
                                point_zero_full_nonzero=abs(a)<=1e-10 and abs(c)>1e-10,
                                point_nonzero_full_zero=abs(a)>1e-10 and abs(c)<=1e-10,
                                first_phase_paired_variance=float(v.loc['full_reference','first_phase_paired_reference_variance_n4096'])))
    comp=pd.DataFrame(comparisons);comp.to_csv(out/'frame-change-comparisons.csv',index=False);comparison_summary=[]
    for taxonomy,g in comp.groupby('taxonomy'):
        comparison_summary.append(dict(taxonomy=taxonomy,units=len(g),opposite_nonzero_signs=int(g.opposite_nonzero_signs.sum()),
                                       point_zero_full_nonzero=int(g.point_zero_full_nonzero.sum()),point_nonzero_full_zero=int(g.point_nonzero_full_zero.sum()),
                                       change_discrepancy_rmse=float(np.sqrt(np.mean(g.point_minus_full**2))),
                                       maximum_absolute_discrepancy=float(g.point_minus_full.abs().max())))
    result=dict(completed_at_utc=now(),plan_path='protocol/plan-v7-reference-frame.md',exploratory=True,
                source_path=source_path,source_analysis_sha256=digest(source/'analysis.json'),source_units_sha256=digest(source/'units.jsonl'),
                subset_definitions='0.01 threshold fixed in v1; nonzero means abs(change)>1e-10. Subsets describe target reference values, not operational selection rules.',
                summary=rows,frame_comparison=comparison_summary)
    (out/'analysis.json').write_text(json.dumps(clean_json(result),indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(completed_at_utc=now(),subset_rows=len(rows),frame_comparisons=comparison_summary)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--destination',required=True)
    a=p.parse_args();run(a.source,a.destination)
