import json, glob, subprocess, os, sys, datetime
root = sys.argv[1]
def ctime(c):
    try:
        out = subprocess.run(['git','--no-optional-locks','-C',root,'show','-s','--format=%cI',c],capture_output=True,text=True)
        if out.returncode: return None
        return datetime.datetime.fromisoformat(out.stdout.strip()).astimezone(datetime.timezone.utc)
    except Exception: return None
def anc(a,b):
    return subprocess.run(['git','--no-optional-locks','-C',root,'merge-base','--is-ancestor',a,b]).returncode==0
rows=[]
for f in sorted(glob.glob(os.path.join(root,'experiments/*/run.json'))):
    r=json.load(open(f)); eid=r.get('experiment_id')
    st=r.get('start_at_utc'); st=datetime.datetime.fromisoformat(st.replace('Z','+00:00')) if st else None
    pc=r.get('plan_commit_id'); cc=r.get('code_commit_id')
    pt=ctime(pc) if pc else None; ct=ctime(cc) if cc else None
    row=dict(exp=eid,start=str(st),plan=r.get('plan_path'),plan_commit=pc,plan_exists=pt is not None,code_commit=cc,code_exists=ct is not None,
             plan_before_start=(pt<=st) if (pt and st) else None, code_before_start=(ct<=st) if (ct and st) else None,
             plan_ancestor_of_code=anc(pc,cc) if (pt and ct) else None, exit=r.get('exit_code'), status=r.get('status'))
    # check plan file exists at plan commit
    if pc and r.get('plan_path'):
        row['plan_file_at_commit']=subprocess.run(['git','--no-optional-locks','-C',root,'cat-file','-e',f"{pc}:{r['plan_path']}"]).returncode==0
    rows.append(row)
json.dump(rows,open(sys.argv[2],'w'),indent=1)
bad=[r for r in rows if not (r['plan_exists'] and r['code_exists'] and r['plan_before_start'] and r['code_before_start'] and r['plan_ancestor_of_code'] is not False and r.get('plan_file_at_commit',True))]
print('experiments',len(rows),'problem rows',len(bad))
for b in bad: print(b)
