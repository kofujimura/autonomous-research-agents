"""Freeze numerical and table expectations from a named completed analysis."""
import argparse
import hashlib
import json
from pathlib import Path
from records import ROOT,now

def without_times(value):
    if isinstance(value,dict):return {k:without_times(v) for k,v in value.items()
        if not k.endswith('_at_utc') and k not in ['generated_at_utc','checked_at_utc']}
    if isinstance(value,list):return [without_times(v) for v in value]
    return value

def main():
    p=argparse.ArgumentParser();p.add_argument('--analysis',default='analysis');p.add_argument('--tables',default='analysis/tables');a=p.parse_args()
    analysis=ROOT/a.analysis;tables=ROOT/a.tables
    summary=json.loads((analysis/'summary.json').read_text())
    expected=without_times(summary)
    (analysis/'expected-results.json').write_text(json.dumps(expected,indent=2,allow_nan=False)+'\n')
    extra={name:without_times(json.loads((analysis/name).read_text())) for name in
        ['comparison-audit.json','allocation-audit.json','inventory-summary.json','completion.json','robustness/summary.json','review-response/summary.json']}
    for source in ['alignment-stress','threshold-bootstrap']:
        file=ROOT/'data'/source/'summary.json'
        if file.exists():extra[source]=without_times(json.loads(file.read_text()))
    extra['tables']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(tables.glob('*.md'))}
    (analysis/'expected-artifacts.json').write_text(json.dumps(extra,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(frozen_at_utc=now(),fit_count=summary['fit_count'],table_count=len(extra['tables']),
        expected_numeric_path=str((analysis/'expected-results.json').relative_to(ROOT)))))

if __name__=='__main__':main()
