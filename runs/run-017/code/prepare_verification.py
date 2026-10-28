"""Prepare only committed inputs required by offline verification.

This omits unneeded raw optical clips/literature and large caches. All reported
fits are still verified. Large probabilities are subsequently copied or linked
by copy_large_inputs.py with per-fit SHA checks.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
from records import ROOT,now

def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)

def main():
    p=argparse.ArgumentParser();p.add_argument('--destination',required=True);p.add_argument('--revision',default='HEAD')
    p.add_argument('--reuse-read-only',action='store_true');a=p.parse_args()
    destination=Path(a.destination).resolve()
    if destination==ROOT or destination.exists():raise ValueError('Use a fresh destination')
    revision=git('rev-parse',a.revision).decode().strip()
    tree=git('ls-tree','-r','--name-only',revision).decode().splitlines()
    manifest=json.loads(git('show',revision+':data/derived/dataset-manifest.json'))
    required={'requirements-verify.txt','data/derived/dataset-manifest.json',
        'analysis/expected-results.json','analysis/expected-artifacts.json'}
    required.update(x for x in tree if x.startswith('code/') or x.startswith('protocol/'))
    for e in manifest['cores']:required.update([e['reference_path'],e['metadata_path']])
    fits=[x for x in tree if x.startswith('data/results/fits/') and x.endswith('.json')]
    for path in fits:
        required.add(path);m=json.loads(git('show',revision+':'+path));required.add(m['sampling']['sample_path'])
        if m.get('sample_weight'):required.add(m['sample_weight']['path'])
    for source in ['data/threshold-bootstrap/summary.json','data/alignment-stress/summary.json']:
        if source in tree:required.add(source)
    missing=required-set(tree)
    if missing:raise RuntimeError('Required files not committed: '+str(sorted(missing)))
    archive=git('archive',revision,*sorted(required))
    destination.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:tar.extractall(destination,filter='data')
    hashes={name:hashlib.sha256((destination/name).read_bytes()).hexdigest() for name in sorted(required)}
    report=dict(prepared_at_utc=now(),revision=revision,files=hashes,
        interpretation='Selected committed inputs; all final fits included. This omits files unused by offline numerical verification, not any statistical condition.')
    (destination/'prepared-inputs.json').write_text(json.dumps(report,indent=2)+'\n')
    args=[sys.executable,str(destination/'code/copy_large_inputs.py'),
        '--bundle',str(ROOT),'--copy',str(destination)]
    if a.reuse_read_only:args.append('--reuse-read-only')
    subprocess.run(args,check=True)
    print(json.dumps(dict(revision=revision,committed_files=len(required),final_fits=len(fits),
        destination=str(destination),mode='Shared probability inputs; used read-only' if a.reuse_read_only else 'Copied probability inputs')))

if __name__=='__main__':main()
