"""Sequential acquisition/analysis units within one bounded worker process.

No subprocess delegation or background daemon. Run under scripts/run.py; at
most two workers total, and the enclosing timeout is at most thirty minutes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import traceback

import acquire
from analyze_unit import analyze
from record import ROOT,append,now

def main():
    p=argparse.ArgumentParser();p.add_argument('--model',choices=['aifs-ens','ifs'],required=True)
    p.add_argument('--start',type=int,required=True);p.add_argument('--count',type=int,default=2)
    p.add_argument('--log',required=True);p.add_argument('--chunk-bytes',type=int,default=65536,choices=[32768,65536,262144,1048576])
    p.add_argument('--subsets',action='store_true')
    a=p.parse_args();design=json.loads((ROOT/'protocol/design-v1.json').read_text())
    units=[(date,lead) for date in design['dates'] for lead in design['leads']]
    assert a.start>=0 and 1<=a.count<=5
    failures=0
    for date,lead in units[a.start:a.start+a.count]:
        source=ROOT/'data/weather'/date/a.model/str(lead)
        output=ROOT/'results/units'/date/a.model/str(lead)
        record={'date':date,'model':a.model,'lead':lead,'started_at_utc':now(),'chunk_bytes':a.chunk_bytes}
        print(json.dumps({'unit_start':record}),flush=True)
        try:
            acquire.main(['--date',date,'--model',a.model,'--lead',str(lead),'--chunk-bytes',str(a.chunk_bytes)])
            record['acquisition_status']='completed'
            summary_path=output/'summary-50.json'
            if summary_path.exists():
                summary=json.loads(summary_path.read_text())
                assert summary['source_sha256']==hashlib.sha256((source/'temperatures.npz').read_bytes()).hexdigest()
                record['analysis_reused']=True
            else:
                summary=analyze(source,output,50);record['analysis_reused']=False
            record.update(primary_analysis_status='completed',source_sha256=summary['source_sha256'],analysis_sha256=summary['output_sha256'])
            if a.subsets:
                from analyze_subsets import analyze as analyze_subsets
                subset_summary=analyze_subsets(source,ROOT/'results/subsets-units'/date/a.model/str(lead))
                record.update(subset_analysis_status='completed',subset_analysis_sha256=subset_summary['output_sha256'])
            else:record['subset_analysis_status']='not_requested'
            record['status']='completed'
        except Exception as error:
            failures+=1;record.update(status='failed',error_type=type(error).__name__,error=str(error))
            traceback.print_exc()
        record['ended_at_utc']=now();append(a.log,record)
        print(json.dumps({'unit_end':record}),flush=True)
    raise SystemExit(1 if failures else 0)

if __name__=='__main__':main()
