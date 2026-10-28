"""A bounded sequential batch of predefined rotation fits; use run_process outside."""
import argparse,json,os,subprocess,sys,time
sys.dont_write_bytecode=True
os.environ['PYTHONDONTWRITEBYTECODE']='1'
from pathlib import Path
from records import ROOT,now

def main():
 p=argparse.ArgumentParser();p.add_argument('--kind',choices=['primary','hgb','seed','permute','noise','metric'],required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--inputs',type=Path,default=ROOT/'analysis/features');p.add_argument('--primary',type=Path,default=ROOT/'analysis/main');p.add_argument('--rotations',type=int,nargs='+',default=[0,1,2,3]);p.add_argument('--seed-offset',type=int,default=0);p.add_argument('--permutation',type=int,default=0);p.add_argument('--extra',nargs=argparse.REMAINDER,default=[]);a=p.parse_args()
 a.output.mkdir(parents=True,exist_ok=True);tasks=[];start=time.monotonic()
 for r in a.rotations:
  assert r in range(4)
  output=a.output/f'r{r}';command=[sys.executable,'-B',str(ROOT/'code'/('analyse_matching.py' if a.kind=='primary' else 'analyse_controls.py')),'--inputs',str(a.inputs),'--rotation',str(r),'--output',str(output)]
  if a.kind!='primary':command+=['--mode',a.kind,'--primary',str(a.primary),'--seed-offset',str(a.seed_offset),'--permutation',str(a.permutation)]
  command+=a.extra;task=dict(rotation=r,command=command,start_time_utc=now());print(json.dumps(task),flush=True)
  proc=subprocess.run(command,timeout=max(1,1740-(time.monotonic()-start)))
  task.update(end_time_utc=now(),exit_code=proc.returncode);tasks.append(task);(a.output/'batch.json').write_text(json.dumps(tasks,indent=2)+'\n')
  if proc.returncode:return proc.returncode
 return 0
if __name__=='__main__':raise SystemExit(main())
