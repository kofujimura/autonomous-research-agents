"""Offline verification entry point. Never writes into the source checkout.

Reduced mode re-solves every primary unit, a deterministic subset of the more
costly subset LP units, and all complete city/time horizons. It recomputes every
reported aggregate from the bundled outputs. Subset-chunk mode supports a full
LP replay in individually bounded runs. No downloads or AI API calls occur.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

sys.dont_write_bytecode=True

import numpy as np
import pandas as pd

from record import ROOT,now
from bounds import TOL

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def compare_csv(original,replayed,columns=None,tolerance=TOL):
    a=pd.read_csv(original,dtype={'date':str});b=pd.read_csv(replayed,dtype={'date':str})
    assert a.shape==b.shape,(str(original),a.shape,b.shape)
    assert list(a)==list(b)
    selected=columns or list(a);max_difference=0.0
    for column in selected:
        if pd.api.types.is_numeric_dtype(a[column]) and pd.api.types.is_numeric_dtype(b[column]):
            av=a[column].to_numpy(dtype=float);bv=b[column].to_numpy(dtype=float)
            assert np.array_equal(np.isnan(av),np.isnan(bv)),(str(original),column,'missing mismatch')
            good=np.isfinite(av)&np.isfinite(bv)
            difference=float(np.max(np.abs(av[good]-bv[good]))) if good.any() else 0.0
            assert difference<=tolerance,(str(original),column,difference)
            max_difference=max(max_difference,difference)
        else:
            assert a[column].fillna('<missing>').astype(str).equals(b[column].fillna('<missing>').astype(str)),(str(original),column)
    label=str(original.relative_to(ROOT)) if original.is_relative_to(ROOT) else str(original)
    return {'file':label,'rows':len(a),'max_absolute_difference':max_difference,'columns':selected}

def link(source,target):
    target.parent.mkdir(parents=True,exist_ok=True);target.symlink_to(source.resolve(),target_is_directory=source.is_dir())

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True)
    p.add_argument('--mode',choices=['reduced','summary','subset-chunk'],default='reduced')
    p.add_argument('--start',type=int,default=0);p.add_argument('--count',type=int,default=10);a=p.parse_args()
    out=Path(a.output).resolve()
    if out==ROOT or ROOT in out.parents:raise SystemExit('Output must be outside the source checkout')
    out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic();report={'mode':a.mode,'started_at_utc':now(),'source_root':str(ROOT),'comparisons':[],
                                'network_calls':0,'ai_api_calls':0,'reduced':a.mode=='reduced'}
    env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',MPLCONFIGDIR=str(out/'.cache/matplotlib'),XDG_CACHE_HOME=str(out/'.cache'))
    def command(script,*arguments):
        with (out/'commands.jsonl').open('a') as f:f.write(json.dumps({'observed_at_utc':now(),'command':[script,*map(str,arguments)]})+'\n')
        with (out/'stdout.txt').open('a') as stdout,(out/'stderr.txt').open('a') as stderr:
            subprocess.run([sys.executable,str(ROOT/'scripts'/script),*map(str,arguments)],cwd=out,env=env,
                           stdout=stdout,stderr=stderr,check=True,timeout=1500)
    design=json.loads((ROOT/'protocol/design-v1.json').read_text())
    units=[(date,model,lead) for date in design['dates'] for model in design['models'] for lead in design['leads']
           if (ROOT/'data/weather'/date/model/str(lead)/'complete.json').exists()]
    if a.mode=='subset-chunk':
        from analyze_subsets import analyze
        selected=units[a.start:a.start+a.count]
        for date,model,lead in selected:
            original=ROOT/'results/subsets-units'/date/model/str(lead)/'bounds.csv'
            if not original.exists():continue
            target=out/'units'/date/model/str(lead)
            analyze(ROOT/'data/weather'/date/model/str(lead),target)
            columns=[c for c in pd.read_csv(original,nrows=0) if c not in ['max_primal_residual','max_dual_violation','max_duality_gap']]
            report['comparisons'].append(compare_csv(original,target/'bounds.csv',columns))
        report['unit_count']=len(selected)
    else:
        replay=out/'replay-root';replay.mkdir();link(ROOT/'protocol',replay/'protocol')
        for folder in ['weather','weather-v4','cities']:
            if (ROOT/'data'/folder).exists():link(ROOT/'data'/folder,replay/'data'/folder)
        if a.mode=='reduced':
            command('check_inputs.py','--output',out/'input-consistency.json')
            command('validate_bounds.py','--output',out/'validation-bounds')
            command('validate_subsets.py','--output',out/'validation-subsets')
            command('validate_transport.py','--output',out/'validation-transport')
            if (ROOT/'data/cities/naturalearth-populated-places.zip').exists():
                command('prepare_cities.py','--offline','--output',out/'city-selection')
                old_design=json.loads((ROOT/'protocol/design-v4.json').read_text())
                new_design=json.loads((out/'city-selection/design-v4.json').read_text())
                old_design.pop('created_at_utc');new_design.pop('created_at_utc')
                assert old_design==new_design,'City selection changed beyond the replay timestamp'
            if (ROOT/'data/cities/ifs-land-mask.grib2').exists():
                command('land_mask.py','--offline','--output',out/'land-mask')
                report['comparisons'].append(compare_csv(ROOT/'data/cities/land-mask/land-fractions.csv',out/'land-mask/land-fractions.csv'))
                if (ROOT/'protocol/plan-v2.4-indexed-extraction.md').exists():
                    command('extract_points.py','--output',out/'grid-index-validation')
                    report['decoder_validation_fields']=json.loads((out/'grid-index-validation/verification.json').read_text())['fields_checked']
            from analyze_unit import analyze
            for date,model,lead in units:
                original=ROOT/'results/units'/date/model/str(lead)/'bounds-50.csv'
                if not original.exists():continue
                target=replay/'results/units'/date/model/str(lead)
                analyze(ROOT/'data/weather'/date/model/str(lead),target,50)
                columns=[c for c in pd.read_csv(original,nrows=0) if c not in ['max_primal_residual','max_dual_violation','max_duality_gap','lp_count']]
                report['comparisons'].append(compare_csv(original,target/'bounds-50.csv',columns))
                for M in [10,25]:
                    old_member=ROOT/'results/member-sensitivity'/date/model/str(lead)/f'bounds-{M}.csv'
                    if old_member.exists():
                        new_member=out/'member-sensitivity'/date/model/str(lead)
                        analyze(ROOT/'data/weather'/date/model/str(lead),new_member,M)
                        report['comparisons'].append(compare_csv(old_member,new_member/f'bounds-{M}.csv',columns))
            # Hash selection cannot favor an observed outcome or method.
            subset_units=[u for u in units if (ROOT/'results/subsets-units'/u[0]/u[1]/str(u[2])/'summary.json').exists()]
            selected=sorted(subset_units,key=lambda u:hashlib.sha256(('|'.join(map(str,u))+'|verify').encode()).hexdigest())[:4]
            from analyze_subsets import analyze as analyze_subset
            for date,model,lead in subset_units:
                target=replay/'results/subsets-units'/date/model/str(lead)
                original=ROOT/'results/subsets-units'/date/model/str(lead)
                if (date,model,lead) in selected:
                    analyze_subset(ROOT/'data/weather'/date/model/str(lead),target)
                    columns=[c for c in pd.read_csv(original/'bounds.csv',nrows=0) if c not in ['max_primal_residual','max_dual_violation','max_duality_gap']]
                    report['comparisons'].append(compare_csv(original/'bounds.csv',target/'bounds.csv',columns))
                else:link(original,target)
            report['subset_lp_units_recomputed']=len(selected);report['subset_lp_units_bundled_only']=len(subset_units)-len(selected)
            if (ROOT/'data/weather-v4').exists():
                from city_time_pipeline import derive
                city_design=json.loads((ROOT/'protocol/design-v4.json').read_text());city_count=0
                for date in city_design['dates']:
                    for model in city_design['models']:
                        for horizon in [3,7]:
                            original=ROOT/'results/city-time-units/snapshot12'/date/model/str(24*horizon+12)/'bounds.csv'
                            if not original.exists():continue
                            result=derive(date,model,horizon,city_design,ROOT,replay);assert result['status']=='completed_horizon'
                            for endpoint in ['snapshot12','maximum4']:
                                old=ROOT/'results/city-time-units'/endpoint/date/model/str(24*horizon+12)/'bounds.csv'
                                new=replay/'results/city-time-units'/endpoint/date/model/str(24*horizon+12)/'bounds.csv'
                                columns=[c for c in pd.read_csv(old,nrows=0) if c not in ['max_primal_residual','max_dual_violation','max_duality_gap','lp_count']]
                                report['comparisons'].append(compare_csv(old,new,columns))
                                old_array=ROOT/'data/weather-v4-derived'/endpoint/date/model/str(24*horizon+12)/'temperatures.npz'
                                new_array=replay/'data/weather-v4-derived'/endpoint/date/model/str(24*horizon+12)/'temperatures.npz'
                                with np.load(old_array,allow_pickle=False) as oa,np.load(new_array,allow_pickle=False) as na:
                                    for name in ['kelvin','members','points','grid_locations']:assert np.array_equal(oa[name],na[name])
                            city_count+=1
                report['city_horizons_recomputed']=city_count
        else:
            for kind in ['units','subsets-units','city-time-units']:
                if (ROOT/'results'/kind).exists():link(ROOT/'results'/kind,replay/'results'/kind)
            if (ROOT/'data/weather-v4-derived').exists():link(ROOT/'data/weather-v4-derived',replay/'data/weather-v4-derived')
        command('summarize.py','--root',replay,'--output',out/'primary')
        if (replay/'results/subsets-units').exists():command('summarize_subsets.py','--root',replay,'--output',out/'subsets')
        if (replay/'results/city-time-units').exists():command('summarize_city_time.py','--root',replay,'--output',out/'city')
        if (out/'city/paired-cases.csv').exists():
            command('check_city_condition.py','--directory',out/'city','--output',out/'city-condition-check.json')
        if (ROOT/'results/sensitivity/summary.json').exists():
            member_root=out/'member-sensitivity' if a.mode=='reduced' else ROOT/'results/member-sensitivity'
            command('report_secondary.py','--cases',out/'primary/cases.csv','--secondary',ROOT/'results/secondary-runs',
                    '--members',member_root,'--output',out/'sensitivity')
            command('check_witnesses.py','--cases',ROOT/'results/primary/cases.csv','--secondary',ROOT/'results/secondary-runs',
                    '--output',out/'continuous-witness-checks.json')
            if a.mode=='reduced':
                # Re-solve all perturbation endpoints, rather than verifying
                # their aggregation alone. Integer solver statuses remain
                # explicitly machine/time dependent and use saved witnesses.
                command('secondary.py','--task','epsilon','--cases',ROOT/'results/primary/cases.csv',
                        '--start','0','--count','120','--output',out/'epsilon-replay')
                old_epsilon={json.loads(path.read_text())['case_key']:json.loads(path.read_text())
                             for path in (ROOT/'results/secondary-runs').rglob('*-epsilon.json')}
                checks=0;maximum=0.0
                for path in (out/'epsilon-replay').glob('*-epsilon.json'):
                    fresh=json.loads(path.read_text());old=old_epsilon[fresh['case_key']]
                    for epsilon,result in fresh['perturbed_pair'].items():
                        for side in ['lower','upper']:
                            difference=abs(result[side]['value']-old['perturbed_pair'][epsilon][side]['value'])
                            assert difference<=TOL
                            maximum=max(maximum,difference);checks+=1
                assert checks==4*len(old_epsilon)
                report['perturbation_endpoint_comparisons']=checks
                report['perturbation_max_absolute_difference']=maximum
            if (ROOT/'results/common-members/summary.json').exists():
                command('common_member_queries.py','--cases',out/'sensitivity/member-cases.csv',
                        '--output',out/'common-members')
        if (ROOT/'results/coverage/summary.json').exists():
            command('coverage_robustness.py','--primary',out/'primary','--subsets',out/'subsets','--output',out/'coverage')
        if (ROOT/'results/midpoints/summary.json').exists():
            command('midpoint_controls.py','--cases',out/'primary/cases.csv','--output',out/'midpoints')
        if (ROOT/'results/identification/summary.json').exists():
            command('identification_diagnostics.py','--cases',out/'primary/cases.csv','--start','0','--count',len(units),
                    '--output',out/'identification')
            command('identification_diagnostics.py','--cases',out/'primary/cases.csv','--output',out/'identification','--summarize')
        if (ROOT/'results/controlled-moments/summary.json').exists():
            command('controlled_moments.py','--cases',ROOT/'results/primary/cases.csv',
                    '--output',out/'controlled-moments')
        recovery=ROOT/'results/overlap-recovery/recovery.json'
        if recovery.exists() and json.loads(recovery.read_text())['status']=='checks_passed':
            command('overlap_recovery.py','--output',out/'overlap-recovery')
            fresh=json.loads((out/'overlap-recovery/recovery.json').read_text())
            old=json.loads(recovery.read_text())
            for key in ['status','original_members_compared','new_raw_sha256','index_sha256','old_attempt_ledger_sha256']:
                assert fresh[key]==old[key],key
            for original in sorted((recovery.parent/'summary').glob('*.csv')):
                columns=[c for c in pd.read_csv(original,nrows=0) if c not in
                         ['source_path','source_sha256','max_primal_residual','max_dual_violation','max_duality_gap','lp_count']]
                report['comparisons'].append(compare_csv(original,out/'overlap-recovery/summary'/original.name,columns))
            old_array=next((recovery.parent/'derived-input').rglob('temperatures.npz'))
            new_array=next((out/'overlap-recovery/derived-input').rglob('temperatures.npz'))
            with np.load(old_array,allow_pickle=False) as oa,np.load(new_array,allow_pickle=False) as na:
                for key in ['kelvin','points','grid_locations','members','portfolios_json']:assert np.array_equal(oa[key],na[key])
            report['overlap_recovery_recomputed']=True
        repeated=ROOT/'results/repeated-members/summary.json'
        if repeated.exists():
            from repeated_members import selection
            from secondary import choose_cases
            rs=json.loads(repeated.read_text());draws=rs['draw_ids']
            fixed=pd.read_csv(ROOT/'results/primary/cases.csv',dtype={'date':str})
            chosen=choose_cases(fixed,design)
            forecasts=set(tuple(r) for r in chosen[['date','model','lead']].drop_duplicates().itertuples(index=False,name=None))
            selections={}
            for file in sorted(repeated.parent.glob('chunk-*/selections.jsonl')):
                if not (file.parent/'complete.json').exists():continue
                for line in file.read_text().splitlines():
                    item=json.loads(line);key=(item['draw'],item['date'],item['model'],item['lead'])
                    assert key not in selections;selections[key]=item
                    indices,digest=selection(*key)
                    assert item['seed_sha256']==digest
                    assert item['members10']==(indices[:10]+1).tolist()
                    assert item['members25']==(indices[:25]+1).tolist()
            assert set(selections)=={(d,*f) for d in draws for f in forecasts}
            destination=out/'repeated-members';destination.mkdir()
            for chunk in sorted(repeated.parent.glob('chunk-*')):link(chunk,destination/chunk.name)
            command('repeated_members.py','--summarize','--output',destination)
            if a.mode=='reduced' and 0 in draws:
                command('repeated_members.py','--cases',ROOT/'results/primary/cases.csv','--start','0','--count','1',
                        '--output',out/'repeated-member-solve')
                old=pd.read_csv(repeated.parent/'chunk-000/cases.csv',dtype={'date':str})
                reference=out/'repeated-draw-zero-reference.csv';old[old['draw']==0].to_csv(reference,index=False)
                report['comparisons'].append(compare_csv(reference,out/'repeated-member-solve/chunk-000/cases.csv'))
                report['repeated_member_draws_recomputed']=1
            report['repeated_member_draws_aggregated']=len(draws)
            report['repeated_member_selections_checked']=len(selections)
        integer_precision=ROOT/'results/integer-precision/summary.json'
        if integer_precision.exists():
            from integer_precision import fixtures as integer_precision_fixtures
            checks=integer_precision_fixtures()
            assert checks==json.loads((integer_precision.parent/'fixtures.json').read_text())
            destination=out/'integer-precision';destination.mkdir()
            link(integer_precision.parent/'raw',destination/'raw')
            command('integer_precision.py','--cases',ROOT/'results/primary/cases.csv',
                    '--summarize','--output',destination)
            report['integer_precision_fixture_conditions']=len(checks)
        # Summary tables and all individual intervals are regenerated; compare
        # numeric values, not timestamps, paths, solver iteration counts or PDFs.
        if (ROOT/'results/review-response/summary.json').exists():
            command('review_response_summary.py','--primary',out/'primary','--output',out/'review-response')
        expected={'primary':'primary','subsets':'subsets','city':'city-time','sensitivity':'sensitivity','coverage':'coverage','midpoints':'midpoints','identification':'identification','common-members':'common-members','controlled-moments':'controlled-moments'}
        if (out/'overlap-recovery').exists():expected['overlap-recovery']='overlap-recovery'
        if (out/'repeated-members').exists():expected['repeated-members']='repeated-members'
        if (out/'integer-precision').exists():expected['integer-precision']='integer-precision'
        if (out/'review-response').exists():expected['review-response']='review-response'
        for generated,stored in expected.items():
            destination=out/generated;reference=ROOT/'results'/stored
            if not destination.exists() or not reference.exists():continue
            for old in sorted(reference.glob('*.csv')):
                new=destination/old.name
                if new.exists():
                    excluded=['max_primal_residual','max_dual_violation','max_duality_gap','lp_count','source_sha256']
                    columns=[c for c in pd.read_csv(old,nrows=0) if c not in excluded]
                    report['comparisons'].append(compare_csv(old,new,columns,tolerance=TOL))
        fig_args=['--primary',out/'primary','--output',out/'figures']
        if (out/'subsets').exists():fig_args+=['--subsets',out/'subsets']
        if (out/'city/width-summary.csv').exists():fig_args+=['--city',out/'city']
        if (out/'sensitivity').exists():fig_args+=['--secondary',out/'sensitivity']
        if (out/'integer-precision/summary.json').exists():fig_args+=['--integer-precision',out/'integer-precision']
        command('make_figures.py',*fig_args)
        link(ROOT/'manuscript',replay/'manuscript');link(ROOT/'sources.jsonl',replay/'sources.jsonl')
        if (ROOT/'api_calls.jsonl').exists():link(ROOT/'api_calls.jsonl',replay/'api_calls.jsonl')
        if (ROOT/'review').exists():link(ROOT/'review',replay/'review')
        for name,stored in expected.items():
            if (out/name).exists():link(out/name,replay/'results'/stored)
        if (ROOT/'paper.md').exists():command('render_paper.py','--root',replay,'--output',out/'paper.md')
    report.update(status='passed',completed_at_utc=now(),elapsed_seconds=time.monotonic()-start)
    (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='comparisons'},indent=2))

if __name__=='__main__':main()
