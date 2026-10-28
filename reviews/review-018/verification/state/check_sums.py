import hashlib, os, sys, json
root = sys.argv[1]; sums = sys.argv[2]; out = sys.argv[3]
match=0; mism=[]; missing=[]; n=0
with open(sums) as f:
    for line in f:
        line=line.rstrip('\n')
        if not line: continue
        h, p = line.split('  ',1)
        n+=1
        fp=os.path.join(root,p)
        if not os.path.isfile(fp):
            missing.append(p); continue
        d=hashlib.sha256()
        with open(fp,'rb') as g:
            for chunk in iter(lambda: g.read(1<<20), b''): d.update(chunk)
        if d.hexdigest()==h: match+=1
        else: mism.append(p)
# files present but not listed (excluding the excluded components)
listed=set()
with open(sums) as f:
    for line in f:
        if line.strip(): listed.add(line.rstrip('\n').split('  ',1)[1])
excl={'.cache','.git','.matplotlib-cache','.venv','__pycache__'}
unlisted=[]
for dp, dns, fns in os.walk(root):
    dns[:]=[d for d in dns if d not in excl]
    for fn in fns:
        rel=os.path.relpath(os.path.join(dp,fn),root)
        if fn=='SHA256SUMS': continue
        if rel not in listed: unlisted.append(rel)
res={'listed':n,'match':match,'mismatch':len(mism),'missing':len(missing),'mismatch_paths':mism,'missing_paths':missing,'unlisted_count':len(unlisted),'unlisted_paths':unlisted[:200]}
json.dump(res,open(out,'w'),indent=1)
print(json.dumps({k:v for k,v in res.items()},indent=1))
