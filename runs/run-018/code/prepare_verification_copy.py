"""Make a fresh Git snapshot inside the authorized verification workspace."""
from pathlib import Path
import argparse,hashlib,json,os,re,subprocess,tarfile
from records import ROOT,now,git

p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--reuse-identical-from',type=Path);a=p.parse_args();assert re.fullmatch(r'[a-zA-Z0-9_-]+',a.name)
reuse=a.reuse_identical_from.resolve() if a.reuse_identical_from else None
if reuse:assert reuse.is_dir() and ROOT/'verification-work' in reuse.parents
base=ROOT/'verification-work'/a.name;base.mkdir(parents=True,exist_ok=False);source=base/'source';source.mkdir();sha=git('rev-parse','HEAD');stamp=now()
proc=subprocess.Popen(['git','-C',str(ROOT),'archive','--format=tar',sha],stdout=subprocess.PIPE)
linked_n=0;linked_bytes=0;written_n=0
with tarfile.open(fileobj=proc.stdout,mode='r|') as stream:
 if reuse is None:stream.extractall(source,filter='data')
 else:
  for member in stream:
   rel=Path(member.name);assert not rel.is_absolute() and '..' not in rel.parts
   target=source/rel
   if member.isdir():target.mkdir(parents=True,exist_ok=True);continue
   assert member.isfile(),'Only regular files/directories are deduplicated'
   target.parent.mkdir(parents=True,exist_ok=True);value=stream.extractfile(member).read();old=reuse/rel
   if old.is_file() and old.stat().st_size==len(value) and hashlib.sha256(old.read_bytes()).digest()==hashlib.sha256(value).digest():
    os.link(old,target);linked_n+=1;linked_bytes+=len(value)
   else:target.write_bytes(value);target.chmod(member.mode&0o777);written_n+=1
assert proc.wait()==0
record=dict(prepared_at_utc=stamp,completed_at_utc=now(),source_commit=sha,source_copy=str(source),results_directory=str(base/'results'),excluded_from_git=True,reused_identical_files_from=str(reuse) if reuse else None,hardlinked_file_n=linked_n,hardlinked_bytes=linked_bytes,newly_written_file_n=written_n if reuse else None,reason='Fresh Git archive with optional SHA-256-checked hardlinks to unchanged immutable files; source copies are never written during verification. Counted toward allocated directory storage. Nonbundled locator index is not needed for offline verification.')
(base/'copy-record.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
