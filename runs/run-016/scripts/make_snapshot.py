"""Materialize a committed self-rerun copy without duplicating immutable inputs."""
import argparse,hashlib,json,os,subprocess
from pathlib import Path
from records import ROOT,now,event

p=argparse.ArgumentParser();p.add_argument('--destination',required=True);p.add_argument('--record',required=True);a=p.parse_args()
dest=(ROOT/a.destination).resolve()
assert dest.is_relative_to(ROOT/'verification-work') and not dest.exists()
sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
subprocess.run(['git','clone','--quiet','--shared','--no-checkout',str(ROOT),str(dest)],check=True)
tree=subprocess.check_output(['git','ls-tree','-rz',sha],cwd=ROOT).split(b'\0')
linked=[];copied=[]
for line in tree:
    if not line:continue
    meta,name=line.split(b'\t',1);mode,kind,oid=meta.decode().split();name=name.decode()
    assert kind=='blob' and mode in ['100644','100755'],('Unsupported tracked object',mode,name)
    source=ROOT/name;target=dest/name;target.parent.mkdir(parents=True,exist_ok=True)
    frozen_metadata=(name.startswith('data/') and source.suffix.lower()=='.json') or (name.startswith('results/') and name!='results/study-tallies.json' and source.suffix.lower() in ['.csv','.json','.jsonl'])
    immutable=source.suffix.lower() in ['.npz','.npy','.pdf'] or frozen_metadata
    matches=False
    if immutable and source.exists():
        size=source.stat().st_size;h=hashlib.sha1();h.update(f'blob {size}\0'.encode())
        with source.open('rb') as stream:
            for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
        matches=h.hexdigest()==oid
    if matches:
        os.link(source,target);linked.append(name)
    else:
        target.write_bytes(subprocess.check_output(['git','cat-file','blob',oid],cwd=ROOT));copied.append(name)
        if mode=='100755':target.chmod(0o755)
subprocess.run(['git','read-tree','HEAD'],cwd=dest,check=True)
record=dict(created_at_utc=now(),source_commit=sha,destination=str(dest.relative_to(ROOT)),
    method='Shared Git object store; mutable documents, ledgers, code and figures copied from commit blobs. Immutable NPZ/NPY/PDF inputs and frozen versioned data/scientific-result manifests/tables/raw-output metadata hardlinked only after their Git blob hash matched. Bookkeeping tallies are excluded from sharing. Old scientific artifacts must remain immutable; revisions use new destinations. No original inputs are written.',
    immutable_hardlinks=len(linked),copied_files=len(copied),excluded_from_git=True,
    qualification='New working location for this session self-rerun, not independent reproduction. Shared immutable bytes avoid storage duplication; all verification outputs use a different fresh path.')
(ROOT/a.record).write_text(json.dumps(record,indent=2)+'\n')
event('verification_snapshot_created','Create committed self-rerun copy using explicitly shared immutable input bytes',[a.record,a.destination],source_commit=sha)
print(json.dumps(record))
