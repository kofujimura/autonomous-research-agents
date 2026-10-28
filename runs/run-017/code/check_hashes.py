"""Check output hashes against tagged tracked bytes plus bundled non-Git files."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from records import ROOT
from hash_outputs import digest

def main():
    p=argparse.ArgumentParser();p.add_argument('--revision');p.add_argument('--list',default='OUTPUT_SHA256.jsonl');a=p.parse_args()
    tracked=set()
    if a.revision:tracked=set(subprocess.check_output(['git','ls-tree','-r','--name-only',a.revision],cwd=ROOT,text=True).splitlines())
    failures=[];checked=0
    for line in (ROOT/a.list).read_text().splitlines():
        row=json.loads(line)
        if row.get('type')=='scope':continue
        relative=row['path'];path=ROOT/relative
        if a.revision and relative in tracked:
            data=subprocess.check_output(['git','show',a.revision+':'+relative],cwd=ROOT)
            actual=hashlib.sha256(data).hexdigest();size=len(data)
        elif path.is_file():actual=digest(path);size=path.stat().st_size
        else:failures.append(relative+': missing');continue
        if actual!=row['sha256'] or size!=row['bytes']:failures.append(relative+': bytes differ')
        checked+=1
    print(json.dumps(dict(status='PASS' if not failures else 'FAIL',checked_files=checked,failures=failures),indent=2))
    if failures:raise SystemExit(1)

if __name__=='__main__':main()
