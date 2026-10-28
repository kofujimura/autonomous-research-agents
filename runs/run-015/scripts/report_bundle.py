"""Run the committed deterministic report/figure programs in one local worker."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from record import ROOT,now

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--interim',action='store_true');a=p.parse_args()
    out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
    def run(name,*args):
        command=[sys.executable,str(ROOT/'scripts'/name),*map(str,args)]
        print(json.dumps({'started_at_utc':now(),'command':command}),flush=True)
        subprocess.run(command,cwd=ROOT,check=True,timeout=1500)
    run('summarize.py','--root',ROOT,'--output',out/'primary')
    locked=ROOT/'protocol/sensitivity-cohort-v1.json'
    if out==ROOT/'results' and locked.exists():
        assert hashlib.sha256((out/'primary/cases.csv').read_bytes()).hexdigest()==json.loads(locked.read_text())['primary_cases_sha256'],'Frozen primary case file changed'
    run('summarize_subsets.py','--root',ROOT,'--output',out/'subsets')
    run('summarize_city_time.py','--root',ROOT,'--output',out/'city-time')
    if (out/'city-time/paired-cases.csv').exists():
        run('check_city_condition.py','--directory',out/'city-time','--output',out/'city-time/condition-audit.json')
    run('coverage_robustness.py','--primary',out/'primary','--subsets',out/'subsets','--output',out/'coverage')
    run('midpoint_controls.py','--cases',out/'primary/cases.csv','--output',out/'midpoints')
    if (ROOT/'results/secondary-runs').exists():
        run('report_secondary.py','--cases',out/'primary/cases.csv','--secondary',ROOT/'results/secondary-runs',
            '--members',ROOT/'results/member-sensitivity','--output',out/'sensitivity')
        if (ROOT/'protocol/plan-v9-common-member-queries.md').exists():
            run('common_member_queries.py','--cases',out/'sensitivity/member-cases.csv','--output',out/'common-members')
    if out==ROOT/'results' and (out/'repeated-members/summary.json').exists():
        run('repeated_members.py','--summarize','--output',out/'repeated-members')
    if out==ROOT/'results' and (out/'integer-precision/summary.json').exists():
        run('integer_precision.py','--cases',out/'primary/cases.csv','--summarize','--output',out/'integer-precision')
    run('review_response_summary.py','--primary',out/'primary','--output',out/'review-response')
    args=['--primary',out/'primary','--subsets',out/'subsets','--output',out/'figures']
    city=json.loads((out/'city-time/summary.json').read_text())
    if city['matched_dates']>0:args+=['--city',out/'city-time']
    if (out/'sensitivity').exists():args+=['--secondary',out/'sensitivity']
    if (out/'integer-precision/summary.json').exists():args+=['--integer-precision',out/'integer-precision']
    run('make_figures.py',*args)
    if not a.interim:
        assert out==ROOT/'results','Final rendering expects the canonical results directory'
        run('render_paper.py','--root',ROOT,'--output',ROOT/'paper.md')
        run('write_claims.py','--output',ROOT/'claims.jsonl')
    else:(out/'INTERIM.md').write_text('Interim report/code check, not a completed study or submission. Scientific definitions remain in fixed plans.\n')
    print(json.dumps({'status':'completed','interim':a.interim,'output':str(out),'completed_at_utc':now()}),flush=True)

if __name__=='__main__':main()
