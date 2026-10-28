"""Execute one bounded local research process with stdout/stderr and Git linkage."""
from pathlib import Path
import argparse, hashlib, json, os, subprocess, time
from records import ROOT, now, event, git

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--id',required=True);p.add_argument('--plan',required=True)
    p.add_argument('--input-manifest')
    p.add_argument('--timeout',type=int,default=1800);p.add_argument('command',nargs=argparse.REMAINDER)
    a=p.parse_args();assert 0<a.timeout<=1800
    command=a.command[1:] if a.command[:1]==['--'] else a.command
    if git('status','--porcelain','--','code',a.plan):
        raise RuntimeError('Commit code and the plan before execution')
    active=[]
    for path in (ROOT/'experiments').glob('*/record.json'):
        old=json.loads(path.read_text())
        if old.get('end_time_utc') is None and old.get('pid'):
            # Conservatively count unfinished records; no OS process probing.
            # A stale record requires explicit reconciliation, never extra capacity.
            active.append(old['experiment_id'])
    if len(active)>=2:raise RuntimeError('Two recorded experiment processes already active')
    folder=ROOT/'experiments'/a.id;folder.mkdir(parents=True,exist_ok=False)
    record=dict(experiment_id=a.id,start_time_utc=now(),end_time_utc=None,command=command,
                timeout_seconds=a.timeout,plan_path=a.plan,plan_commit=git('log','-1','--format=%H','--',a.plan),
                code_commit=git('rev-parse','HEAD'),input_manifest=a.input_manifest,exit_code=None,pid=None,
                plan_sha256=hashlib.sha256((ROOT/a.plan).read_bytes()).hexdigest(),
                code_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in (ROOT/'code').glob('*.py')},
                input_manifest_sha256=hashlib.sha256((ROOT/a.input_manifest).read_bytes()).hexdigest()
                                      if a.input_manifest else None)
    event('experiment_start',f'Start {a.id}',[str(folder.relative_to(ROOT)),a.plan],experiment_id=a.id)
    start=time.monotonic()
    with (folder/'stdout.log').open('w') as out,(folder/'stderr.log').open('w') as err:
        proc=subprocess.Popen(command,cwd=ROOT,stdout=out,stderr=err,start_new_session=True)
        record['pid']=proc.pid
        (folder/'record.json').write_text(json.dumps(record,indent=2)+'\n')
        try:
            record['exit_code']=proc.wait(timeout=a.timeout)
            record['timed_out']=False
        except subprocess.TimeoutExpired:
            import signal
            os.killpg(proc.pid,signal.SIGTERM)
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid,signal.SIGKILL);proc.wait()
            record['exit_code']=proc.returncode;record['timed_out']=True
    record['end_time_utc']=now();record['elapsed_seconds']=time.monotonic()-start
    (folder/'record.json').write_text(json.dumps(record,indent=2)+'\n')
    event('experiment_end' if record['exit_code']==0 else 'experiment_failure',
          f"End {a.id}: exit {record['exit_code']}",[str(folder.relative_to(ROOT))],experiment_id=a.id)
    print(json.dumps(record))
    return record['exit_code'] or 0

if __name__=='__main__':raise SystemExit(main())
