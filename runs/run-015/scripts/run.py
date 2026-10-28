"""Timeout-limited, locally logged subprocesses (only manages its own child)."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time
from record import ROOT, event, now

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--id',required=True);p.add_argument('--plan',required=True)
    p.add_argument('--timeout',type=int,default=1800);p.add_argument('--inputs',nargs='*',default=[])
    p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
    if a.command and a.command[0]=='--':a.command=a.command[1:]
    if not 0<a.timeout<=1800:raise SystemExit('Timeout must be 1..1800 seconds')
    directory=ROOT/'experiments'/a.id
    directory.mkdir(parents=True,exist_ok=False)
    # At most two started experiment processes, even if a later invocation overlaps.
    held=None
    for i in range(2):
        slot=(ROOT/'.cache'/f'experiment-slot-{i}.lock');slot.parent.mkdir(exist_ok=True)
        handle=slot.open('a')
        try:fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB);held=handle;break
        except BlockingIOError:handle.close()
    if held is None:raise SystemExit('Two experiment slots already occupied')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    plan_commit=subprocess.check_output(['git','log','-1','--format=%H','--',a.plan],cwd=ROOT,text=True).strip()
    record=dict(experiment_id=a.id,started_at_utc=now(),command=a.command,timeout_seconds=a.timeout,
                plan_path=a.plan,plan_commit_id=plan_commit,code_commit_id=commit,
                input_sha256={path:sha(ROOT/path) for path in a.inputs},status='running')
    record['start_event_id']=event('experiment_start',f'Start {a.id}',[str(directory.relative_to(ROOT)),a.plan],experiment_id=a.id,plan_commit_id=plan_commit,code_commit_id=commit)
    (directory/'record.json').write_text(json.dumps(record,indent=2)+'\n')
    env=os.environ.copy()
    env.update(XDG_CACHE_HOME=str(ROOT/'.cache'),MPLCONFIGDIR=str(ROOT/'.cache/matplotlib'),PYTHONDONTWRITEBYTECODE='1')
    start=time.monotonic()
    with (directory/'stdout.txt').open('w') as out,(directory/'stderr.txt').open('w') as err:
        child=subprocess.Popen(a.command,cwd=ROOT,stdout=out,stderr=err,env=env,start_new_session=True)
        record['child_pid']=child.pid
        (directory/'record.json').write_text(json.dumps(record,indent=2)+'\n')
        try:code=child.wait(timeout=a.timeout);record['status']='completed' if code==0 else 'failed'
        except subprocess.TimeoutExpired:
            os.killpg(child.pid,signal.SIGTERM)
            try:child.wait(timeout=5)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
            code=124;record['status']='timed_out'
    record.update(exit_code=code,ended_at_utc=now(),elapsed_seconds=time.monotonic()-start)
    record['end_event_id']=event('experiment_end' if code==0 else 'experiment_failure',f'{a.id}: {record["status"]}, exit {code}',[str(directory.relative_to(ROOT))],experiment_id=a.id)
    (directory/'record.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record));held.close()
    raise SystemExit(code)

if __name__=='__main__':main()
