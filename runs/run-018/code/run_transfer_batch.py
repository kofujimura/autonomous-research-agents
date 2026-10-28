"""Sequential transfer fits inside one1800-second run_process boundary."""
from pathlib import Path
import argparse,json,subprocess,sys,time
from records import ROOT,now
p=argparse.ArgumentParser();p.add_argument('--regions',nargs='+',required=True);p.add_argument('--inputs',type=Path,default=ROOT/'analysis/features');p.add_argument('--output',type=Path,default=ROOT/'analysis/transfer');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True);tasks=[];start=time.monotonic()
for rid in a.regions:
 command=[sys.executable,str(ROOT/'code/analyse_transfer.py'),'--region',rid,'--inputs',str(a.inputs),'--output',str(a.output/rid)];task=dict(region=rid,start_time_utc=now(),command=command);print(json.dumps(task),flush=True)
 proc=subprocess.run(command,timeout=max(1,1740-(time.monotonic()-start)));task.update(end_time_utc=now(),exit_code=proc.returncode);tasks.append(task);(a.output/('batch-'+'-'.join(a.regions)+'.json')).write_text(json.dumps(tasks,indent=2)+'\n')
 if proc.returncode:raise SystemExit(proc.returncode)
