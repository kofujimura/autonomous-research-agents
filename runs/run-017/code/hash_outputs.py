"""Hash all included research outputs, including raw arrays outside Git."""
import hashlib
import json
from pathlib import Path
from records import ROOT,now

def excluded(path):
    parts=path.parts;name=path.name;value=path.as_posix()
    if any(p in ['.git','.venv','.cache','__pycache__'] for p in parts):return True
    if name.endswith('.pyc') or name=='.DS_Store' or name=='OUTPUT_SHA256.jsonl':return True
    if value.startswith('data/derived/features/') and name.endswith('.npz'):return True
    if value.startswith('verification-work/') and ('input' in parts or 'cache' in parts):return True
    return False

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while data:=f.read(1024*1024):h.update(data)
    return h.hexdigest()

def main():
    started=now();rows=[]
    for path in sorted(ROOT.rglob('*')):
        rel=path.relative_to(ROOT)
        if path.is_symlink() or not path.is_file() or excluded(rel):continue
        rows.append(dict(path=rel.as_posix(),bytes=path.stat().st_size,sha256=digest(path)))
    header=dict(type='scope',started_at_utc=started,completed_at_utc=now(),scope='HASH_SCOPE.md',
        included_files=len(rows),included_bytes=sum(x['bytes'] for x in rows),
        exclusions='See HASH_SCOPE.md; all raw self-rerun measurements and prediction arrays are included')
    (ROOT/'OUTPUT_SHA256.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in [header,*rows]))
    print(json.dumps(header))

if __name__=='__main__':main()
