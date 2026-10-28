"""Share unchanged bytes between two immutable self-rerun source copies."""
import argparse,json,os,subprocess
from records import ROOT,now,event,digest

def run(source,target,record):
    a=(ROOT/source).resolve();b=(ROOT/target).resolve()
    assert a.is_relative_to(ROOT/'verification-work') and b.is_relative_to(ROOT/'verification-work') and a!=b
    assert a.is_dir() and b.is_dir()
    before=int(subprocess.check_output(['du','-sk',str(ROOT)],text=True).split()[0])*1024;rows=[]
    for q in sorted(b.rglob('*')):
        rel=q.relative_to(b)
        if '.git' in rel.parts or '__pycache__' in rel.parts or not q.is_file():continue
        p=a/rel
        if not p.is_file() or p.stat().st_size!=q.stat().st_size or p.stat().st_ino==q.stat().st_ino:continue
        h=digest(p)
        if h!=digest(q):continue
        tmp=q.with_name(q.name+'.identical-snapshot-hardlink');assert not tmp.exists()
        os.link(p,tmp);os.replace(tmp,q)
        rows.append(dict(source=str(p.relative_to(ROOT)),target=str(q.relative_to(ROOT)),sha256=h,bytes=q.stat().st_size))
    after=int(subprocess.check_output(['du','-sk',str(ROOT)],text=True).split()[0])*1024
    result=dict(observed_at_utc=now(),source=source,target=target,before_allocated_bytes=before,after_allocated_bytes=after,
      files_shared=len(rows),files=rows,scope='Exact byte-identical files between two frozen self-rerun source copies only. Neither is edited; no mutable root document/code is newly shared. Git internals excluded. Every path and byte retained.')
    (ROOT/record).write_text(json.dumps(result,indent=2)+'\n')
    event('immutable_snapshot_storage_shared','Share exact duplicate bytes between immutable self-rerun source copies',[record,source,target],saved_allocated_bytes=before-after)
    print(json.dumps({k:result[k] for k in ['observed_at_utc','files_shared','before_allocated_bytes','after_allocated_bytes']}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--target',required=True);p.add_argument('--record',required=True);a=p.parse_args();run(a.source,a.target,a.record)
