"""Offline verification. Source files are read only; outputs go to a fresh path."""
import sys
sys.dont_write_bytecode=True
import argparse,json,os,time,subprocess,hashlib
from pathlib import Path
import numpy as np,pandas as pd
from records import ROOT,now,digest

def same_csv(expected,observed):
    a=pd.read_csv(expected);b=pd.read_csv(observed)
    assert list(a.columns)==list(b.columns) and a.shape==b.shape,(str(expected),'schema differs')
    maximum=0.
    for c in a:
        if pd.api.types.is_numeric_dtype(a[c]) and pd.api.types.is_numeric_dtype(b[c]):
            x=a[c].to_numpy(float);y=b[c].to_numpy(float)
            assert np.array_equal(np.isnan(x),np.isnan(y)),(str(expected),c,'missingness differs')
            finite=np.isfinite(x)&np.isfinite(y)
            assert np.allclose(x,y,atol=1e-10,rtol=1e-9,equal_nan=True),(str(expected),c,'values differ')
            if finite.any():maximum=max(maximum,float(np.abs(x[finite]-y[finite]).max()))
        else:assert a[c].fillna('<NA>').astype(str).equals(b[c].fillna('<NA>').astype(str)),(str(expected),c)
    return dict(path=str(expected.relative_to(ROOT)),rows=len(a),maximum_absolute_numeric_difference=maximum)

def same_npz_file(source,target,share_identical=False):
    assert target.exists(),('Missing regenerated raw array file',str(target))
    maximum=0.;arrays=0
    with np.load(source,allow_pickle=False) as a,np.load(target,allow_pickle=False) as b:
        assert set(a.files)==set(b.files),(str(source),'array names differ')
        for key in a.files:
            x=a[key];y=b[key];assert x.shape==y.shape and x.dtype==y.dtype,(str(source),key,'schema differs')
            if x.dtype.kind in 'fc':
                assert np.allclose(x,y,atol=1e-10,rtol=1e-9,equal_nan=True),(str(source),key,'raw values differ')
                finite=np.isfinite(x)&np.isfinite(y)
                if finite.any():maximum=max(maximum,float(np.abs(x[finite]-y[finite]).max()))
            else:assert np.array_equal(x,y),(str(source),key,'raw values differ')
            arrays+=1
    row=dict(path=str(source.relative_to(ROOT)),arrays=arrays,maximum_absolute_numeric_difference=maximum)
    if share_identical:
        from deduplicate_verification import share_file
        row['storage_sharing_after_comparison']=share_file(source,target)
    return row

def same_npz_tree(expected,observed,share_identical=False):
    files={p.relative_to(expected) for p in expected.rglob('*.npz')}
    assert files=={p.relative_to(observed) for p in observed.rglob('*.npz')},'Raw array file layout differs'
    return [same_npz_file(expected/p,observed/p,share_identical) for p in sorted(files)]

def check_inputs(model_path,check_features):
    d=ROOT/model_path;fit=json.loads((d/'fit.json').read_text())
    mp=ROOT/fit['manifest_path'];assert digest(mp)==fit['manifest_sha256']
    m=json.loads(mp.read_text());records={r['landscape_id']:r for r in m['landscapes']}
    ids=m[fit['taxonomy']+'_ids'];lookup=np.full(256,-1,np.int16);lookup[ids]=np.arange(len(ids))
    checked=[]
    if check_features:
        assert fit['classifier']=='logistic','Feature reconstruction covers saved logistic coefficients'
        from predict_fixed import restore
        heads={year:restore(d,year=year) for year in (range(2021,2026) if fit['refreshed'] else [2021])}
    for entry in fit['prediction_files']:
        path=ROOT/entry['path'];assert digest(path)==entry['sha256']
        r=records[entry['landscape_id']];ix=np.asarray(r['valid_indices'],int)
        assert digest(ROOT/r['path'])==r['sha256']
        with np.load(ROOT/r['path']) as z:labels=lookup[z[fit['taxonomy']][:,ix]]
        with np.load(path) as z:p=z['probabilities'];assert np.array_equal(labels,z['labels'])
        maximum=0.;n=0
        for source in r['feature_inputs']:
            if source['representation']!=fit['representation']:continue
            assert digest(ROOT/source['path'])==source['sha256']
            if not check_features:continue
            model,scale=heads[source['year'] if fit['refreshed'] else 2021]
            with np.load(ROOT/source['path']) as z:
                if fit['representation']=='tessera':
                    x=z['values'][ix] if 'values' in z else z['raw_values'][ix].astype(np.float32)*z['scales'][ix,None]
                else:
                    raw=z['raw_values'][ix].astype(np.float32);x=np.sign(raw)*(raw/np.float32(127.5))**2
                    x[(raw==-128).any(axis=1)]=np.nan
            good=np.isfinite(x).all(axis=1);prediction=model.predict_proba(scale.transform(x[good]))
            expected=np.zeros((good.sum(),len(ids)),np.float32);expected[:,model.classes_]=prediction.astype(np.float32)
            observed=p[source['year']-2021][good]
            assert np.allclose(expected,observed,atol=2e-6,rtol=2e-6),'Feature-to-prediction reconstruction mismatch'
            maximum=max(maximum,float(np.abs(expected-observed).max()));n+=len(expected)
        checked.append(dict(landscape_id=r['landscape_id'],feature_prediction_rows_reconstructed=n,
                            maximum_probability_difference=maximum))
    return dict(model_path=model_path,checks=checked)

def timeline(allow_running=False):
    events=[json.loads(s) for s in (ROOT/'events.jsonl').read_text().splitlines() if s]
    for r in events:
        assert all(k in r for k in ['event_id','observed_at_utc','type','summary','artifact_paths','related_ids'])
    runs=[]
    for p in sorted((ROOT/'experiments').glob('*/run.json')):
        r=json.loads(p.read_text());sha=r['plan_commit_id'];plan=r['plan_path']
        blob=subprocess.check_output(['git','show',sha+':'+plan],cwd=ROOT)
        assert hashlib.sha256(blob).hexdigest()==r['plan_sha256']
        subprocess.run(['git','cat-file','-e',r['code_commit_id']+'^{commit}'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
        assert allow_running or r['status']!='running','An experiment was still marked running in the snapshot'
        runs.append(dict(experiment_id=r['experiment_id'],status=r['status'],plan_commit_id=sha))
    return dict(event_lines=len(events),experiments=runs,preliminary_running_allowed=allow_running,
                qualification='Git and recorded wall times are self-reported chronology. The documented duplicate E0103 is retained with correction E0104; they do not prove absence of tampering.')

def main():
    p=argparse.ArgumentParser();p.add_argument('--config',default='verification-config.json')
    p.add_argument('--output',required=True);p.add_argument('--quick',action='store_true')
    p.add_argument('--all',action='store_true');p.add_argument('--skip-feature-reconstruction',action='store_true')
    p.add_argument('--allow-running',action='store_true',help='Preliminary debugging only; invalid for the final pre-submission check')
    p.add_argument('--share-identical-arrays',action='store_true',help='Same-filesystem self-rerun storage optimization after exact array checks; all numerical computation still runs')
    a=p.parse_args();out=Path(a.output).expanduser().resolve()
    assert out!=ROOT and (not out.is_relative_to(ROOT) or out.is_relative_to(ROOT/'verification-work')),'Use an external output directory, or designated self-check verification-work/'
    if out.exists():raise FileExistsError('Choose a fresh verification output directory')
    out.mkdir(parents=True);os.environ['MPLCONFIGDIR']=str(out/'matplotlib-cache')
    begin=time.monotonic();config=json.loads((ROOT/a.config).read_text())
    result=dict(started_at_utc=now(),mode='quick' if a.quick else 'all' if a.all else 'primary',
                source_root=str(ROOT),output_root=str(out),network_used=False,ai_api_called=False,
                input_checks=[],table_checks=[],raw_array_checks=[],supplemental_checks=[],document_checks=[],timings=[],timeline=timeline(a.allow_running),
                valid_as_final_submission_check=not a.allow_running)
    analyses=config['analyses'] if a.all else [r for r in config['analyses'] if r['role']=='primary']
    from audit_inference import run
    from summarize_inference import build
    for i,r in enumerate(analyses):
        started=time.monotonic()
        meta=json.loads((ROOT/r['path']/'analysis.json').read_text())
        result['input_checks'].append(check_inputs(meta['model_path'],r.get('reconstruct_features',r['role']=='primary') and not a.skip_feature_reconstruction))
        if a.quick:
            result['timings'].append(dict(kind='input_check',path=r['path'],elapsed_seconds=time.monotonic()-started));continue
        dest=out/'inference'/str(i)
        run(meta['model_path'],meta['draw_manifest_path'],str(dest))
        result['raw_array_checks']+=same_npz_tree(ROOT/r['path'],dest,a.share_identical_arrays)
        r['recomputed_path']=str(dest)
        result['timings'].append(dict(kind='input_and_inference',path=r['path'],elapsed_seconds=time.monotonic()-started))
    if a.quick:
        # Quick mode regenerates all tables from saved full Monte Carlo outputs.
        # It checks summaries, not the estimator simulation itself.
        for group in config['table_groups']:
            build(group['analyses'],str(out/group['name']),primary=group.get('primary_filter',True))
            for name in group['csv_files']:
                result['table_checks'].append(same_csv(ROOT/group['expected_path']/name,out/group['name']/name))
    else:
        by_path={r['path']:r['recomputed_path'] for r in analyses}
        for group in config['table_groups']:
            if not all(s in by_path for s in group['analyses']):continue
            dest=out/group['name'];build([by_path[s] for s in group['analyses']],str(dest),primary=group.get('primary_filter',True))
            for name in group['csv_files']:
                result['table_checks'].append(same_csv(ROOT/group['expected_path']/name,dest/name))
    assert result['table_checks'],'No complete main table group was checked'
    if a.all or a.quick:
        import importlib
        for task in config.get('supplemental_tasks',[]):
            if a.quick and not task.get('quick'):continue
            started=time.monotonic()
            dest=out/'supplements'/task['name'];dest.parent.mkdir(exist_ok=True)
            function=getattr(importlib.import_module(task['module']),task['function'])
            kwargs=dict(task.get('kwargs',{}));streamed=[];streamed_paths=set();expected_base=ROOT/task['expected_path']
            if a.share_identical_arrays and task['module']=='reference_frame_analysis':
                def observer(target):
                    relative=target.relative_to(dest)
                    assert relative not in streamed_paths
                    row=same_npz_file(expected_base/relative,target,True)
                    row['compared_fresh_before_sharing']=True
                    streamed.append(row);streamed_paths.add(relative)
                kwargs['array_observer']=observer
            function(*task['args'],destination=str(dest),**kwargs)
            checks=[same_csv(ROOT/task['expected_path']/name,dest/name) for name in task['csv_files']]
            if streamed:
                assert streamed_paths=={p.relative_to(expected_base) for p in expected_base.rglob('*.npz')}
                assert streamed_paths=={p.relative_to(dest) for p in dest.rglob('*.npz')}
                raw_checks=streamed
            else:raw_checks=same_npz_tree(expected_base,dest,a.share_identical_arrays)
            result['supplemental_checks'].append(dict(name=task['name'],csv_checks=checks,raw_array_checks=raw_checks,elapsed_seconds=time.monotonic()-started))
    if a.all and config.get('render_documents'):
        from render_paper import render
        dest=out/'rendered-documents';render(str(dest))
        for name in ['paper.md','claims.jsonl']:
            assert (ROOT/name).read_bytes()==(dest/name).read_bytes(),(name,'rendered document differs')
            result['document_checks'].append(dict(path=name,status='exact_match'))
    result.update(completed_at_utc=now(),elapsed_seconds=time.monotonic()-begin,status='passed')
    (out/'verification-result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],mode=result['mode'],elapsed_seconds=result['elapsed_seconds'],
                          table_checks=len(result['table_checks']),supplemental_tasks=len(result['supplemental_checks']),output=str(out))))

if __name__=='__main__':main()
