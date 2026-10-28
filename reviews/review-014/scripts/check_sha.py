import hashlib, sys, os, json
root, listfile, out = sys.argv[1], sys.argv[2], sys.argv[3]
match=mismatch=missing=0; mism=[]; miss=[]
with open(listfile) as f:
    for line in f:
        line=line.rstrip("\n")
        if not line.strip(): continue
        h, p = line.split("  ",1)
        fp=os.path.join(root,p)
        if not os.path.isfile(fp):
            missing+=1; miss.append(p); continue
        d=hashlib.sha256()
        with open(fp,'rb') as g:
            for chunk in iter(lambda: g.read(1<<20), b''): d.update(chunk)
        if d.hexdigest()==h: match+=1
        else: mismatch+=1; mism.append(p)
res=dict(listfile=listfile, root=root, entries=match+mismatch+missing, match=match, mismatch=mismatch, missing=missing, mismatch_paths=mism, missing_paths=miss)
json.dump(res, open(out,'w'), indent=1)
print(json.dumps({k:v for k,v in res.items() if k not in('mismatch_paths','missing_paths')}), mism[:20], miss[:20])
