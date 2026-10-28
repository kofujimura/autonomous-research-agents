import json,subprocess,glob,os,sys,datetime
root=sys.argv[1]
def ct(c):
    try:return subprocess.check_output(['git','-C',root,'show','-s','--format=%cI',c],text=True,stderr=subprocess.DEVNULL).strip()
    except Exception:return None
P=lambda s:datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
out=[];bad=[]
for p in sorted(glob.glob(os.path.join(root,'experiments/*/run.json'))):
    r=json.load(open(p))
    pc=ct(r['plan_commit_id']);cc=ct(r['code_commit_id']);st=r['start_time_utc']
    ok = pc is not None and cc is not None and P(pc)<=P(st) and P(cc)<=P(st)
    row=dict(experiment=r['experiment_id'],start=st,plan=r['plan_path'],plan_commit_time=pc,code_commit_time=cc,status=r['status'],ok=ok)
    out.append(row)
    if not ok: bad.append(row)
json.dump(out,open(sys.argv[2],'w'),indent=1)
print('experiments',len(out),'plan&code commit precede start:',sum(r['ok'] for r in out),'violations',len(bad))
for b in bad: print(b)
for r in out:
    if any(k in r['experiment'] for k in ['E14','E17','E22','E25','E42','E50','E53']): print(r)
