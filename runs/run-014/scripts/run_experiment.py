"""Run only a researcher-started process group, with time and provenance limits."""
import argparse, fcntl, hashlib, json, os, signal, subprocess, sys, time
from pathlib import Path
from record import ROOT, now, event

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while b:=f.read(1024*1024):h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('experiment_id');ap.add_argument('--plan',required=True)
    ap.add_argument('--additional-plan',action='append',default=[]);ap.add_argument('--seed',type=int)
    ap.add_argument('--timeout',type=int,default=1800);ap.add_argument('--input',action='append',default=[])
    ap.add_argument('command',nargs=argparse.REMAINDER);a=ap.parse_args()
    assert 0<a.timeout<=1800
    command=a.command[1:] if a.command[:1]==['--'] else a.command
    if not command:raise ValueError('missing command')
    # Enforce the trial limit before starting a child, including concurrent launchers.
    (ROOT/'.cache').mkdir(exist_ok=True)
    launch_lock=(ROOT/'.cache/experiment-launch.lock').open('a')
    fcntl.flock(launch_lock,fcntl.LOCK_EX)
    active=[]
    for previous in (ROOT/'experiments').glob('*/run.json'):
        item=json.loads(previous.read_text())
        if item.get('status')=='running':active.append(item['experiment_id'])
    if len(active)>=2:
        event('experiment_launch_blocked','Two registered experiments are already running; no child started',
              related=active,requested_experiment_id=a.experiment_id)
        raise SystemExit(2)
    dest=ROOT/'experiments'/a.experiment_id;dest.mkdir(exist_ok=False)
    git=lambda *x: subprocess.check_output(['git',*x],cwd=ROOT,text=True).strip()
    record=dict(experiment_id=a.experiment_id,start_at_utc=now(),end_at_utc=None,
        command=command,working_directory=str(ROOT),timeout_seconds=a.timeout,seed=a.seed,
        plan_path=a.plan,plan_commit_id=git('log','-1','--format=%H','--',a.plan),
        additional_plan_commits={p:git('log','-1','--format=%H','--',p) for p in a.additional_plan},
        code_commit_id=git('rev-parse','HEAD'),
        input_sha256={p:sha(ROOT/p) for p in a.input},exit_code=None,status='running')
    record['start_event_id']=event('experiment_start',a.experiment_id+' started',[str(dest.relative_to(ROOT)),a.plan])
    path=dest/'run.json'
    def write_record():
        temporary=path.with_suffix('.tmp.json')
        temporary.write_text(json.dumps(record,indent=2)+'\n');temporary.replace(path)
    write_record()
    tick=time.monotonic()
    with (dest/'stdout.log').open('w') as out,(dest/'stderr.log').open('w') as err:
        proc=subprocess.Popen(command,cwd=ROOT,stdout=out,stderr=err,start_new_session=True)
        record['pid']=proc.pid;write_record()
        fcntl.flock(launch_lock,fcntl.LOCK_UN);launch_lock.close()
        try:
            code=proc.wait(timeout=a.timeout);status='completed' if code==0 else 'failed'
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid,signal.SIGTERM)
            try:code=proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid,signal.SIGKILL);code=proc.wait()
            status='timeout'
    record.update(end_at_utc=now(),elapsed_seconds=time.monotonic()-tick,exit_code=code,status=status)
    record['end_event_id']=event('experiment_end' if code==0 else 'experiment_failure',
        a.experiment_id+' '+status,[str(dest.relative_to(ROOT))],[record['start_event_id']],exit_code=code)
    write_record();print(json.dumps(record,indent=2))
    raise SystemExit(0 if code==0 else 1)

if __name__=='__main__':main()
