"""Run the documented offline procedure in a fresh committed-input location."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from records import ROOT,now

def size(directory):return sum(p.stat().st_size for p in directory.rglob('*') if p.is_file() and not p.is_symlink())

def main():
    p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--revision',default='HEAD');a=p.parse_args()
    base=ROOT/a.base
    if base.exists():raise ValueError('Use a fresh verification working location')
    usage=size(ROOT)
    # Existing corresponding artifact classes bound the size of a fresh rerun;
    # add room for input metadata, font caches, logs and subsequent small records.
    artifact_bytes=sum(size(ROOT/x) for x in ['data/evaluation','analysis','figures','data/alignment-stress','data/threshold-bootstrap'])
    reserve=160*1024**2;bound=usage+int(1.1*artifact_bytes)+reserve
    if bound>10*1024**3:raise RuntimeError('Conservative self-verification storage preflight exceeds10GiB; preserve current files and reconsider preparation')
    base.mkdir(parents=True)
    (base/'storage-preflight.json').write_text(json.dumps(dict(observed_at_utc=now(),existing_bytes=usage,
        existing_corresponding_artifact_bytes=artifact_bytes,planning_bound_bytes=bound,
        reserve_bytes=reserve,limit_bytes=10*1024**3,interpretation='Conservative planning bound, not measured final consumption'),indent=2)+'\n')
    env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
    commands=[('prepare',[sys.executable,str(ROOT/'code/prepare_verification.py'),'--revision',a.revision,
        '--destination',str(base/'input'),'--reuse-read-only']),
        ('verify',[sys.executable,str(base/'input/code/verify.py'),'--out',str(base/'output')])]
    for name,command in commands:
        with (base/(name+'.stdout.txt')).open('w') as stdout,(base/(name+'.stderr.txt')).open('w') as stderr:
            result=subprocess.run(command,env=env,stdout=stdout,stderr=stderr,timeout=1740 if name=='verify' else 60)
        if result.returncode:raise RuntimeError(name+' failed; original logs retained under '+str(base.relative_to(ROOT)))
        print(name,'PASS',flush=True)
    report=json.loads((base/'output/verification.json').read_text())
    prepared=json.loads((base/'input/prepared-inputs.json').read_text())
    summary=dict(completed_at_utc=now(),prepared_revision=prepared['revision'],working_location=str(base.relative_to(ROOT)),
        shared_probability_inputs=True,verification=report,
        interpretation='Self-rerun in a fresh selected committed-code/input copy using shared probability bytes and the existing dedicated environment; not independent reproduction')
    (ROOT/'review').mkdir(exist_ok=True)
    (ROOT/'review/offline-verification.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],elapsed_seconds=report['elapsed_seconds'],prepared_revision=prepared['revision'])))

if __name__=='__main__':main()
