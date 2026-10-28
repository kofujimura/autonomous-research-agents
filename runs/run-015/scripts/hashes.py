"""SHA-256 output lists/checks. Authoritative scope is explicit, not tamper proof."""
import argparse
import hashlib
import json
import os
from pathlib import Path

from record import ROOT,now

SKIP_DIRS={'.git','.venv','.cache','__pycache__'}

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',default=str(ROOT));p.add_argument('--file',required=True)
    p.add_argument('--exclude',action='append',default=[]);p.add_argument('--scope-file');p.add_argument('--check',action='store_true');a=p.parse_args()
    root=Path(a.root).resolve();listing=Path(a.file).resolve()
    if a.check:
        checked=0
        for line in listing.read_text().splitlines():
            expected,relative=line.split('  ',1);target=root/relative
            assert target.resolve().is_relative_to(root),'Hash entry escapes source root'
            assert target.is_file() and sha(target)==expected,relative;checked+=1
        print(json.dumps({'status':'passed','files_checked':checked}));return
    prefixes=[Path(x).as_posix().rstrip('/') for x in a.exclude]
    if a.scope_file:
        Path(a.scope_file).write_text(json.dumps({'created_at_utc':now(),'root':str(root),
            'excluded_directory_names':sorted(SKIP_DIRS),'additional_excluded_prefixes':prefixes,
            'output_list_excluded':str(listing),'symlinks':'not dereferenced; generated helper link trees are caches, original data files are regular files',
            'scope':'All other regular files, including raw data, failed/partial results and logs. Verification working cache has its own auxiliary list; authoritative verification reports are included here. Hashes support consistency, not tamper-proofness or independent reproduction.'},indent=2)+'\n')
    rows=[]
    for current,dirs,files in os.walk(root,followlinks=False):
        relative_dir=Path(current).relative_to(root)
        dirs[:]=[d for d in dirs if d not in SKIP_DIRS and not (Path(current)/d).is_symlink()
                 and not any((relative_dir/d).as_posix()==x or (relative_dir/d).as_posix().startswith(x+'/') for x in prefixes)]
        for name in files:
            path=Path(current)/name;relative=path.relative_to(root).as_posix()
            if path==listing or path.is_symlink() or any(relative==x or relative.startswith(x+'/') for x in prefixes):continue
            rows.append((relative,sha(path)))
    listing.parent.mkdir(parents=True,exist_ok=True)
    listing.write_text(''.join(value+'  '+path+'\n' for path,value in sorted(rows)))
    print(json.dumps({'created_at_utc':now(),'files_hashed':len(rows),'list':str(listing)}))

if __name__=='__main__':main()
