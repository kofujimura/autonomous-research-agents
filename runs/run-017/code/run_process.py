"""Run only this study's child process with a strict timeout and a saved record."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time
from records import ROOT, event, now

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--id',required=True)
    p.add_argument('--plan',required=True)
    p.add_argument('--timeout',type=int,default=1800)
    p.add_argument('--input',action='append',default=[])
    p.add_argument('command',nargs=argparse.REMAINDER)
    a=p.parse_args()
    if not 0<a.timeout<=1800: raise ValueError('Timeout must not exceed 1800 seconds')
    command=a.command[1:] if a.command[:1]==['--'] else a.command
    out=ROOT/'experiments'/a.id
    out.mkdir(exist_ok=False)
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    hashes={path:hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in a.input}
    e=event('experiment_start',f'Started {a.id}',[str(out.relative_to(ROOT)),a.plan],
            experiment_id=a.id,plan_commit_id=commit,code_commit_id=commit)
    record=dict(experiment_id=a.id,started_at_utc=now(),command=command,timeout_seconds=a.timeout,
                plan_path=a.plan,plan_commit_id=commit,code_commit_id=commit,input_sha256=hashes,
                start_event_id=e,seed='see command and settings in experiment outputs')
    (out/'run.json').write_text(json.dumps(record,indent=2)+'\n')
    t=time.monotonic()
    env=os.environ.copy()
    env.update({'PYTHONUNBUFFERED':'1','MPLCONFIGDIR':str(ROOT/'.cache/matplotlib'),
                'HF_HOME':str(ROOT/'.cache/huggingface'),'TORCH_HOME':str(ROOT/'.cache/torch'),
                'RESEARCH_EXPERIMENT_ID':a.id,'OMP_NUM_THREADS':'2','OPENBLAS_NUM_THREADS':'2',
                'MKL_NUM_THREADS':'2','VECLIB_MAXIMUM_THREADS':'2'})
    with (out/'stdout.txt').open('w') as stdout,(out/'stderr.txt').open('w') as stderr:
        process=subprocess.Popen(command,cwd=ROOT,stdout=stdout,stderr=stderr,env=env,start_new_session=True)
        record['pid']=process.pid
        (out/'run.json').write_text(json.dumps(record,indent=2)+'\n')
        try:
            code=process.wait(timeout=a.timeout)
            timed_out=False
        except subprocess.TimeoutExpired:
            os.killpg(process.pid,signal.SIGTERM)
            try: process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid,signal.SIGKILL);process.wait()
            code=process.returncode;timed_out=True
    record.update(ended_at_utc=now(),elapsed_seconds=time.monotonic()-t,exit_code=code,timed_out=timed_out)
    record['end_event_id']=event('experiment_end' if code==0 else 'experiment_failure',
        f'{a.id} exited with code {code}; timeout={timed_out}',[str(out.relative_to(ROOT))],
        related=[e],experiment_id=a.id)
    (out/'run.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2))
    raise SystemExit(0 if code==0 else 1)

if __name__=='__main__':main()
