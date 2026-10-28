"""Sequential predefined tasks in one run_process group; outer timeout is mandatory."""
from pathlib import Path
import argparse,json,subprocess,time
from records import now
p=argparse.ArgumentParser();p.add_argument('--tasks',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();tasks=json.loads(a.tasks.read_text());results=[];t0=time.monotonic()
for task in tasks:
 if time.monotonic()-t0>1680:raise RuntimeError('Insufficient remaining batch time to start another task')
 item=dict(task_id=task['task_id'],command=task['command'],start_time_utc=now());print(json.dumps(item),flush=True)
 proc=subprocess.run(task['command'])
 item.update(end_time_utc=now(),exit_code=proc.returncode);results.append(item);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(results,indent=2)+'\n')
 if proc.returncode:raise SystemExit(proc.returncode)
