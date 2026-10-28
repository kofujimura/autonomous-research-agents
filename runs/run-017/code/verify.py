"""One offline entry point; writes only to a newly supplied output directory."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
from freeze_expected import without_times

SOURCE=Path(__file__).resolve().parents[1]

def compare(actual,expected,path=''):
    failures=[]
    if isinstance(expected,dict):
        for key,value in expected.items():
            if key not in actual:failures.append(path+'/'+key+': missing')
            else:failures.extend(compare(actual[key],value,path+'/'+key))
    elif isinstance(expected,list):
        if len(actual)!=len(expected):failures.append(path+': length differs')
        else:
            for i,(a,e) in enumerate(zip(actual,expected)):failures.extend(compare(a,e,path+'/'+str(i)))
    elif isinstance(expected,(int,float)) and not isinstance(expected,bool):
        if actual is None or not np.isclose(actual,expected,rtol=0,atol=1e-12):failures.append(path+': numeric mismatch')
    elif actual!=expected:failures.append(path+': mismatch')
    return failures

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--expected',default='analysis/expected-results.json')
    a=p.parse_args();out=Path(a.out).resolve()
    if out==SOURCE or SOURCE in out.parents:raise ValueError('Output must be outside the immutable input copy')
    out.mkdir(parents=True,exist_ok=False)
    env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',MPLCONFIGDIR=str(out/'cache/matplotlib'),
        OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',MKL_NUM_THREADS='2',VECLIB_MAXIMUM_THREADS='2')
    commands=[['check_metrics.py'],['evaluate.py','--smoothing','--out',str(out/'evaluation')],
        ['summarize.py','--evaluation',str(out/'evaluation'),'--out',str(out/'analysis')],
        ['robustness.py','--analysis',str(out/'analysis'),'--out',str(out/'analysis/robustness'),'--evaluation',str(out/'evaluation')],
        ['review_sensitivities.py','--analysis',str(out/'analysis'),'--evaluation',str(out/'evaluation'),'--out',str(out/'analysis/review-response')],
        ['audit_samples.py','--out',str(out/'analysis')],['inventory_summary.py','--out',str(out/'analysis')],
        ['completion.py','--out',str(out/'analysis')],
        ['audit_evaluations.py','--evaluation',str(out/'evaluation'),'--analysis',str(out/'analysis'),'--out',str(out/'analysis')]]
    threshold_expected=SOURCE/'data/threshold-bootstrap/summary.json'
    if threshold_expected.exists():commands.append(['threshold_bootstrap.py','--out',str(out/'threshold-bootstrap')])
    alignment_expected=SOURCE/'data/alignment-stress/summary.json'
    if alignment_expected.exists():commands.append(['alignment_stress.py','--out',str(out/'alignment-stress')])
    render=['render_tables.py','--analysis',str(out/'analysis'),'--out',str(out/'tables')]
    if alignment_expected.exists():render+=['--alignment',str(out/'alignment-stress')]
    if threshold_expected.exists():render+=['--threshold-bootstrap',str(out/'threshold-bootstrap')]
    commands += [render,['plot_results.py','--analysis',str(out/'analysis'),'--evaluation',str(out/'evaluation'),'--out',str(out/'figures')]]
    prepared=SOURCE/'prepared-inputs.json'
    prepared_hashes=json.loads(prepared.read_text())['files'] if prepared.exists() else {}
    def check_input_files():
        return [name for name,expected in prepared_hashes.items()
            if hashlib.sha256((SOURCE/name).read_bytes()).hexdigest()!=expected]
    if check_input_files():raise RuntimeError('Prepared committed inputs already differ')
    tick=time.monotonic();records=[]
    for command in commands:
        elapsed=time.monotonic()-tick
        if elapsed>=1700:raise TimeoutError('Verification 1700-second internal deadline reached')
        args=[sys.executable,str(SOURCE/'code'/command[0]),*command[1:]]
        result=subprocess.run(args,cwd=SOURCE,env=env,timeout=1700-elapsed,capture_output=True,text=True)
        (out/(command[0]+'.stdout.txt')).write_text(result.stdout)
        (out/(command[0]+'.stderr.txt')).write_text(result.stderr)
        records.append(dict(command=args,exit_code=result.returncode))
        if result.returncode:raise RuntimeError(command[0]+' failed; see output logs')
        print(command[0],'PASS',flush=True)
    actual=json.loads((out/'analysis/summary.json').read_text())
    expected=json.loads((SOURCE/a.expected).read_text())
    failures=compare(actual,expected)
    if threshold_expected.exists():
        threshold_actual=json.loads((out/'threshold-bootstrap/summary.json').read_text())
        failures.extend(compare(threshold_actual['contrasts'],json.loads(threshold_expected.read_text())['contrasts'],'threshold_bootstrap'))
    details_path=SOURCE/'analysis/expected-artifacts.json'
    if details_path.exists():
        details=json.loads(details_path.read_text())
        for name,expected_value in details.items():
            if name=='tables':
                for filename,digest in expected_value.items():
                    if hashlib.sha256((out/'tables'/filename).read_bytes()).hexdigest()!=digest:
                        failures.append('tables/'+filename+': content mismatch')
            else:
                file=out/name/'summary.json' if name in ['alignment-stress','threshold-bootstrap'] else out/'analysis'/name
                failures.extend(compare(without_times(json.loads(file.read_text())),expected_value,name))
    changed=check_input_files()
    failures.extend('input_changed/'+name for name in changed)
    report=dict(status='PASS' if not failures else 'FAIL',failures=failures,
        numerical_tolerance=1e-12,elapsed_seconds=time.monotonic()-tick,steps=records,
        committed_input_files_checked_unchanged=len(prepared_hashes),input_copy_unchanged=not changed,
        interpretation='Offline recomputation from bundled probabilities/reference arrays; no network or AI API; this program never fits a model')
    (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    if failures:raise SystemExit(1)

if __name__=='__main__':main()
