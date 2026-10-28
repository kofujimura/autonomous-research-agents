"""Finish input-only checks and freeze the complete manifest before models."""
import argparse
import json
from pathlib import Path
import sys
from features import build
from input_qc import main as qc
from source_consistency import main as consistency
from dataset_manifest import main as manifest
from inventory_summary import main as inventory
from records import ROOT,now

def main():
    p=argparse.ArgumentParser();p.add_argument('--build-cores',nargs='*',default=[])
    p.add_argument('--qc-cores',nargs='+',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
    for cid in a.build_cores:
        result=build(ROOT/'data/main/cores'/cid,ROOT/'data/derived/features')
        print(json.dumps(result),flush=True)
    sys.argv=['input_qc.py','--cores',*a.qc_cores,'--out',str(out.relative_to(ROOT))]
    qc()
    consistency()
    manifest()
    sys.argv=['inventory_summary.py'];inventory()
    (out/'finalization.json').write_text(json.dumps(dict(completed_at_utc=now(),status='complete',
        dataset_manifest='data/derived/dataset-manifest.json',mapping_performance_computed=False,
        qc_cores=a.qc_cores,features_built=a.build_cores),indent=2)+'\n')

if __name__=='__main__':main()
