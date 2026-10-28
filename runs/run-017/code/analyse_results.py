"""Recompute a dated analysis snapshot from completed saved fits."""
import argparse
import json
from pathlib import Path
import sys
import evaluate
import summarize
import audit_samples
import audit_evaluations
import completion
import inventory_summary
import render_tables
import plot_results
import check_metrics
import robustness
from records import ROOT,now

def invoke(module,args):
    sys.argv=[module.__name__+'.py',*map(str,args)];module.main()

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--canonical',action='store_true');a=p.parse_args()
    out=ROOT/a.out;analysis=out/'analysis';figures=out/'figures'
    tables=analysis/'tables' if a.canonical else out/'tables'
    invoke(check_metrics,[])
    invoke(evaluate,['--smoothing'])
    invoke(summarize,['--out',analysis])
    invoke(robustness,['--analysis',analysis,'--out',analysis/'robustness'])
    invoke(audit_samples,['--out',analysis])
    invoke(audit_evaluations,['--analysis',analysis,'--out',analysis])
    invoke(completion,['--out',analysis])
    invoke(inventory_summary,['--out',analysis])
    invoke(render_tables,['--analysis',analysis,'--out',tables])
    invoke(plot_results,['--analysis',analysis,'--out',figures])
    (out/'analysis-run.json').write_text(json.dumps(dict(completed_at_utc=now(),status='complete',
        source='data/results completed fits and data/evaluation',analysis_path=str(analysis.relative_to(ROOT)),
        note='During ongoing fitting this snapshot may cover fewer evaluated fits than the live completion audit; primary comparisons require all five seeds'),indent=2)+'\n')

if __name__=='__main__':main()
