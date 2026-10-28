"""Generate evidence and usage summaries from saved records, never hand-copy results."""
import argparse,ast,collections,datetime as dt,hashlib,json,re,subprocess
from pathlib import Path
import pandas as pd
import numpy as np
from record import ROOT,now

def scientific_script_hashes(checkout=ROOT):
    scripts=checkout/'scripts';pending=['reproduce.py'];seen={}
    while pending:
        name=pending.pop()
        if 'scripts/'+name in seen:continue
        p=scripts/name
        if not p.exists():continue
        seen['scripts/'+name]=hashlib.sha256(p.read_bytes()).hexdigest()
        tree=ast.parse(p.read_text())
        for node in ast.walk(tree):
            if isinstance(node,ast.ImportFrom) and node.module:
                child=node.module.split('.')[0]+'.py'
                if (scripts/child).exists() and 'scripts/'+child not in seen:pending.append(child)
    return dict(sorted(seen.items()))

def latest_self_rerun():
    candidates=[(int(m.group(1)),p) for p in (ROOT/'review').glob('self-rerun-*.json')
        if (m:=re.fullmatch(r'self-rerun-(\d+)\.json',p.name))]
    if not candidates:return None,None
    path=max(candidates)[1];return path,json.loads(path.read_text())

def rerun_covers_current(result):
    return bool(result and result.get('scientific_script_sha256')==scientific_script_hashes())

def clean(x):
    if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [clean(v) for v in x]
    if isinstance(x,(np.integer,)):return int(x)
    if isinstance(x,(float,np.floating)) and not np.isfinite(x):return None
    if isinstance(x,(np.floating,)):return float(x)
    if isinstance(x,(np.bool_,)):return bool(x)
    return x

def record_summary():
    runs=[]
    for p in sorted((ROOT/'experiments').glob('*/run.json')):
        r=json.loads(p.read_text());r['record_path']=str(p.relative_to(ROOT));runs.append(r)
    api={}
    for line in (ROOT/'api_calls.jsonl').read_text().splitlines():
        r=json.loads(line);api[r['call_id']]=r
    intervention=[json.loads(s) for s in (ROOT/'interventions.jsonl').read_text().splitlines()]
    boundaries=[]
    for r in runs:
        boundaries.append((r['start_at_utc'],1,r['experiment_id']))
        if r.get('end_at_utc'):boundaries.append((r['end_at_utc'],-1,r['experiment_id']))
    active=peak=0
    for _,change,_ in sorted(boundaries,key=lambda t:(t[0],t[1])):
        active+=change;peak=max(peak,active)
    raw={m:len(list((ROOT/'data/embeddings'/m).glob('*.npz'))) for m in ['aef','tessera']}
    history={}
    for model in raw:
        p=ROOT/f'data/{model}-retrievals.jsonl'
        rows=[json.loads(s) for s in p.read_text().splitlines()] if p.exists() else []
        history[model]=dict(attempts=len(rows),status_counts=dict(collections.Counter(r['status'] for r in rows)),
                            saved_files=raw[model],max_attempt=max([r['attempt'] for r in rows],default=0))
    logical=0
    for p in ROOT.rglob('*'):
        try:
            if p.is_file() and not p.is_symlink():logical+=p.stat().st_size
        except FileNotFoundError:
            pass # An atomically renamed transient retrieval file is not a stable output.
    allocated=int(subprocess.check_output(['du','-sk',str(ROOT)],text=True).split()[0])*1024
    result=dict(observed_at_utc=now(),runs=runs,run_status_counts=dict(collections.Counter(r['status'] for r in runs)),
                registered_experiment_count=len(runs),maximum_registered_concurrency=peak,
                maximum_completed_duration_seconds=max([r.get('elapsed_seconds',0) for r in runs if r.get('end_at_utc')],default=0),
                api_latest_records=list(api.values()),intervention_counts=dict(collections.Counter(r['type'] for r in intervention)),
                intervention_count=len(intervention),retrievals=history,logical_storage_bytes=logical,allocated_storage_bytes=allocated,
                git_commit_count=int(subprocess.check_output(['git','rev-list','--count','HEAD'],cwd=ROOT,text=True)),
                caveats=['Durations/times are locally reported. Same-second ends sort before starts.',
                         'Model generation calls are deduplicated by call_id; polling/accounting rows are not separate generations.',
                         'Session-token usage, deployment identifier, invoice and normal-tool billing remain unobservable.'])
    native_tasks=pd.read_csv(ROOT/'data/native-check/tasks.csv')
    result['native_acquisition']=dict(planned_point_years=len(native_tasks),present_point_years=sum(
        (ROOT/'data/native-check'/f'{i}.npz').exists() for i in native_tasks.task_id),
        paired_test=json.loads((ROOT/'analysis/native-pairs-v21/checks.json').read_text()),
        single_date_cases=json.loads((ROOT/'analysis/native-single-date-v22/checks.json').read_text()))
    return clean(result)

def evidence_summary():
    main=pd.read_csv(ROOT/'analysis/main-v1/main-table.csv')
    comparisons=pd.read_csv(ROOT/'analysis/main-v1/paired-comparisons.csv')
    primary=comparisons[(comparisons.availability_mode=='paired')&(comparisons.support=='centre')&
                         (comparisons.seed==14014)&(comparisons.reference_mode=='global')]
    ident=pd.read_csv(ROOT/'analysis/main-v1/identities.csv')
    ident=ident[(ident.availability_mode=='paired')&(ident.support=='centre')&(ident.seed==14014)&(ident.reference_mode=='global')]
    thresholds=pd.read_csv(ROOT/'analysis/main-v1/thresholds.csv')
    thresholds=thresholds[(thresholds.availability_mode=='paired')&(thresholds.support=='centre')&
                          (thresholds.seed==14014)&(thresholds.reference_mode=='global')]
    cases=[]
    for (model,task),g in main[main.method=='start_fixed'].groupby(['model','task']):
        r=g.iloc[0];n=int(r.n_positive+r.n_negative)
        cases.append(dict(model=model,task=task,n=n,n_positive=int(r.n_positive),n_negative=int(r.n_negative),
                          initial_class_supplied=n,initial_class_fraction=1.0))
    native=pd.read_csv(ROOT/'analysis/native-v5/comparisons.csv')
    native_summary=pd.read_csv(ROOT/'analysis/native-v5/summary.csv')
    ext=pd.read_csv(ROOT/'analysis/nlcd-v4/metrics.csv')
    extension=ext[(ext.support=='centre')&ext.availability_mode.str.endswith('_primary')]
    result=dict(main_table=main.to_dict('records'),primary_comparisons=primary.to_dict('records'),
                primary_thresholds=thresholds.to_dict('records'),conditional_task_counts=cases,
                anchor_diagnostics=ident.to_dict('records'),
                native_counts=dict(sample=len(native),native_present=int(native.native_present.sum()),
                                   mosaic_present=int(native.mosaic_present.sum()),
                                   valid_centres=int(native.centre_valid.fillna(False).sum()) if 'centre_valid' in native else 0,
                                   raw_centre_equal=int(native.raw_centre_equal.fillna(False).sum()) if 'raw_centre_equal' in native else 0),
                native_summary=native_summary.to_dict('records'),extension_table=extension.to_dict('records'),
                extension_summary=json.loads((ROOT/'analysis/nlcd-v4/summary.json').read_text()))
    return clean(result)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['records','evidence']);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();value=record_summary() if a.action=='records' else evidence_summary()
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in value.items() if k not in ['runs','api_latest_records','main_table','primary_comparisons','primary_thresholds','anchor_diagnostics','extension_table','native_summary']},indent=2))
