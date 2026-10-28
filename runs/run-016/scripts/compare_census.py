"""Compare fixed point populations with the prospectively selected full grids."""
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd
from records import ROOT,now,digest
from inference_core import population_influence

def load_units(path):
    d=ROOT/path
    return {r['unit_id']:r for r in map(json.loads,(d/'units.jsonl').read_text().splitlines())},d

def compare(point_analyses,census_analyses,destination):
    assert len(point_analyses)==len(census_analyses)
    out=ROOT/destination
    if out.exists():raise FileExistsError('Preserve prior census comparisons')
    out.mkdir(parents=True);changes=[];performance=[]
    for point_path,census_path in zip(point_analyses,census_analyses):
        pu,pd_=load_units(point_path);cu,cd=load_units(census_path)
        cm=json.loads((cd/'analysis.json').read_text());pm=json.loads((pd_/'analysis.json').read_text())
        assert cm['taxonomy']==pm['taxonomy']=='broad' and cm['representation']==pm['representation']
        fit=json.loads((ROOT/cm['model_path']/'fit.json').read_text())
        manifest=json.loads((ROOT/fit['manifest_path']).read_text())
        pop={r['landscape_id']:r for r in manifest['landscapes']}
        predictions={r['landscape_id']:r for r in fit['prediction_files']}
        cache={};k=len(fit['class_names'])
        for uid,c in cu.items():
            if not c['primary']:continue
            p=pu[uid];lid=c['landscape_id'];r=pop[lid]
            if lid not in cache:
                with np.load(ROOT/predictions[lid]['path']) as z:cache[lid]=z['labels']
            y=cache[lid];a=c['year_a']-2021;b=c['year_b']-2021
            _,phi_a=population_influence(y[a],None,k);_,phi_b=population_influence(y[b],None,k)
            M=c['N'];N=p['N'];fpc=(1-N/M)/N
            component_pair=float(np.var(phi_b-phi_a,ddof=1)*fpc)
            component_ind=float((np.var(phi_a,ddof=1)+np.var(phi_b,ddof=1))*fpc)
            changes.append(dict(unit_id=uid,representation=cm['representation'],stratum=r.get('stratum'),
                                native_population=M,point_population=N,
                                point_change=p['true_change'],native_change=c['true_change'],
                                point_minus_native=p['true_change']-c['true_change'],
                                opposite_sign=(p['true_change']*c['true_change']< -1e-20),
                                first_phase_paired_variance=component_pair,
                                first_phase_independent_variance=component_ind,
                                first_phase_paired_se=float(np.sqrt(component_pair)),
                                first_phase_independent_se=float(np.sqrt(component_ind)),
                                first_phase_paired_fraction_of_native_audit_variance_n128=(component_pair/c['oracle']['direct']['paired_variance'] if c['oracle']['direct']['paired_variance']>1e-20 else None),
                                first_phase_independent_fraction_of_native_audit_variance_n128=(component_ind/c['oracle']['direct']['independent_variance'] if c['oracle']['direct']['independent_variance']>1e-20 else None)))
            for method in ['direct','model_assisted']:
                for design in ['paired','independent']:
                    for n in [32,64,128,256,512]:
                        for label,u in [('point',p),('native',c)]:
                            s=next(s for s in u['summaries'] if s['method']==method and s['design']==design and s['n']==n)
                            performance.append(dict(unit_id=uid,representation=cm['representation'],stratum=r.get('stratum'),
                                                    population=label,**s))
    cframe=pd.DataFrame(changes);pframe=pd.DataFrame(performance)
    cframe.to_csv(out/'census-changes.csv',index=False);pframe.to_csv(out/'census-unit-performance.csv',index=False)
    unique=cframe.drop_duplicates('unit_id')
    result=dict(generated_at_utc=now(),point_analyses=point_analyses,census_analyses=census_analyses,
                cases=int(unique.unit_id.str.rsplit('-',n=2).str[0].nunique()),primary_transitions=len(unique),
                sign_disagreements=int(unique.opposite_sign.sum()),
                change_discrepancy_rmse=float(np.sqrt(np.mean(unique.point_minus_native**2))),
                maximum_absolute_change_discrepancy=float(unique.point_minus_native.abs().max()),
                median_first_phase_paired_fraction_n128=float(unique.first_phase_paired_fraction_of_native_audit_variance_n128.median()),
                maximum_first_phase_paired_fraction_n128=float(unique.first_phase_paired_fraction_of_native_audit_variance_n128.max()),
                interpretation='Prospectively selected small case check. First-phase components are reference-only linearization diagnostics, not unconditional two-phase coverage estimates.')
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--point-analysis',action='append',required=True)
    p.add_argument('--census-analysis',action='append',required=True);p.add_argument('--destination',required=True)
    a=p.parse_args();compare(a.point_analysis,a.census_analysis,a.destination)
