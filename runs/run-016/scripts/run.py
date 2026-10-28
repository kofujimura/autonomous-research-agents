"""Run only this study's child command with timeout and a two-process lock."""
import argparse, fcntl, json, os, signal, subprocess, sys, time
import hashlib
from pathlib import Path
from records import ROOT, now, digest, event

def main():
    p=argparse.ArgumentParser();p.add_argument('experiment_id');p.add_argument('--plan',required=True)
    p.add_argument('--timeout',type=int,default=1800)
    p.add_argument('--input',action='append',default=[])
    p.add_argument('command',nargs=argparse.REMAINDER)
    a=p.parse_args();cmd=a.command
    if cmd and cmd[0]=='--':cmd=cmd[1:]
    if not cmd or not 1<=a.timeout<=1800:raise SystemExit('Invalid command or timeout')
    code_changes=subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--','scripts'],cwd=ROOT,text=True)
    if code_changes.strip():raise SystemExit('Commit script changes and wait for the commit to finish before starting an experiment')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    plan_blob=subprocess.check_output(['git','show',head+':'+a.plan],cwd=ROOT)
    if hashlib.sha256(plan_blob).hexdigest()!=digest(ROOT/a.plan):raise SystemExit('Plan differs from the committed pre-execution version')
    slot=None
    for i in range(2):
        lock=(ROOT/'logs'/('experiment-slot-%s.lock'%i)).open('a+')
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);slot=lock;break
        except BlockingIOError:lock.close()
    if slot is None:raise SystemExit('Two experiment slots already in use')
    d=ROOT/'experiments'/a.experiment_id;d.mkdir(parents=True,exist_ok=True)
    if (d/'run.json').exists():raise SystemExit('Run record exists; use a new experiment ID')
    start=now();begin=time.monotonic()
    record=dict(experiment_id=a.experiment_id,start_time_utc=start,end_time_utc=None,
                command=cmd,timeout_seconds=a.timeout,plan_path=a.plan,plan_commit_id=head,
                plan_sha256=digest(ROOT/a.plan),code_commit_id=head,
                code_sha256={str(path.relative_to(ROOT)):digest(path) for path in sorted((ROOT/'scripts').glob('*.py'))},
                inputs=[dict(path=x,sha256=digest(ROOT/x)) for x in a.input],
                status='running',exit_code=None,stdout_path=str(d.relative_to(ROOT)/'stdout.txt'),
                stderr_path=str(d.relative_to(ROOT)/'stderr.txt'))
    record['start_event_id']=event('experiment_start',a.experiment_id,[str(d.relative_to(ROOT)),a.plan])
    (d/'run.json').write_text(json.dumps(record,indent=2)+'\n')
    env=dict(os.environ)
    for k,v in {'XDG_CACHE_HOME':'.cache','HF_HOME':'.cache/huggingface',
                'TORCH_HOME':'.cache/torch','MPLCONFIGDIR':'.cache/matplotlib',
                'NUMBA_CACHE_DIR':'.cache/numba'}.items():env[k]=str(ROOT/v)
    env['HF_HUB_DISABLE_TELEMETRY']='1';env['HF_HUB_DISABLE_IMPLICIT_TOKEN']='1'
    for name in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_MAX_THREADS']:
        env[name]='4'
    with (d/'stdout.txt').open('w') as out,(d/'stderr.txt').open('w') as err:
        child=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=out,stderr=err,start_new_session=True)
        record['pid']=child.pid;(d/'run.json').write_text(json.dumps(record,indent=2)+'\n')
        try:code=child.wait(timeout=a.timeout);status='completed' if code==0 else 'failed'
        except subprocess.TimeoutExpired:
            os.killpg(child.pid,signal.SIGTERM)
            try:child.wait(timeout=10)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
            code=124;status='timeout'
    record.update(end_time_utc=now(),elapsed_seconds=time.monotonic()-begin,exit_code=code,status=status)
    record['end_event_id']=event('experiment_end' if code==0 else 'experiment_failure',
                               a.experiment_id+' '+status,[str(d.relative_to(ROOT))],
                               [record['start_event_id']],exit_code=code)
    (d/'run.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:record[k] for k in ['experiment_id','status','exit_code','elapsed_seconds']}))
    raise SystemExit(code)

if __name__=='__main__':main()
