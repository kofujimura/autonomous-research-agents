"""Check current manuscript/claims against the fresh offline rerun's numbers."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from records import ROOT,now
from verify import compare

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--fresh',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    fresh=ROOT/a.fresh;out=ROOT/a.out;out.mkdir(parents=True,exist_ok=False)
    commands=[['render_tables.py','--analysis',str(fresh/'analysis'),'--out',str(out/'tables'),
        '--alignment',str(fresh/'alignment-stress'),'--threshold-bootstrap',str(fresh/'threshold-bootstrap'),
        '--paper-out',str(out/'paper.md')],
        ['write_claims.py','--analysis',str(fresh/'analysis'),'--alignment',str(fresh/'alignment-stress'),'--out',str(out/'claims.jsonl')]]
    for command in commands:
        result=subprocess.run([sys.executable,str(ROOT/'code'/command[0]),*command[1:]],capture_output=True,text=True,check=True)
        (out/(command[0]+'.stdout.txt')).write_text(result.stdout)
        (out/(command[0]+'.stderr.txt')).write_text(result.stderr)
    failures=[]
    if sha(ROOT/'paper.md')!=sha(out/'paper.md'):failures.append('Current manuscript differs from rendering on fresh numerical outputs')
    current=[json.loads(x) for x in (ROOT/'claims.jsonl').read_text().splitlines() if x]
    regenerated=[json.loads(x) for x in (out/'claims.jsonl').read_text().splitlines() if x]
    failures.extend(compare(regenerated,current,'claims'))
    tables={p.name:sha(p) for p in sorted((ROOT/'analysis/tables').glob('*.md'))}
    for name,digest in tables.items():
        if sha(out/'tables'/name)!=digest:failures.append('Table mismatch: '+name)
    result=dict(checked_at_utc=now(),status='PASS' if not failures else 'FAIL',failures=failures,
        manuscript_sha256=sha(ROOT/'paper.md'),numeric_tables_checked=len(tables),claims_checked=len(current),
        absolute_numeric_tolerance=1e-12,
        interpretation='Current prose generation and claims checked against the independently recomputed-in-a-fresh-location numerical outputs by this same session; not independent reproduction')
    (out/'comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
    if failures:raise SystemExit(1)

if __name__=='__main__':main()
