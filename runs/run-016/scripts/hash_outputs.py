"""Create a scoped SHA-256 inventory, retaining append-only event receipts."""
import argparse,json
from records import ROOT,now,digest

EXCLUDED_TREES={'.git','.venv','.cache','__pycache__'}
def included(path,destination):
    rel=path.relative_to(ROOT)
    if any(part in EXCLUDED_TREES for part in rel.parts):return False
    if path.suffix=='.pyc':return False
    if rel==destination:return False
    return True

def run(destination):
    from pathlib import Path
    target=Path(destination)
    assert not target.is_absolute() and '..' not in target.parts
    files=[];inode_hashes={}
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file() or not included(path,target):continue
        assert not path.is_symlink(),'Do not silently follow external evidence'
        rel=path.relative_to(ROOT).as_posix()
        st=path.stat();identity=(st.st_dev,st.st_ino,st.st_size)
        if identity not in inode_hashes:inode_hashes[identity]=digest(path)
        files.append(dict(path=rel,bytes=st.st_size,sha256=inode_hashes[identity],
            mode='prefix' if rel=='events.jsonl' else 'full',
            optional_for_numerical_verification=rel.startswith(('data/catalogues/','data/labels-chunks/','verification-work/'))))
    result=dict(created_at_utc=now(),algorithm='SHA-256',files=files,
        excluded_trees=sorted(EXCLUDED_TREES),
        excluded_files=[target.as_posix()+' (current inventory; self-reference avoidance)','*.pyc'],
        later_files='The mirror copy of this inventory and its check/submission receipts are written afterwards and are not in this inventory. A later revised inventory includes earlier submission inventories and check receipts when present.',
        event_prefix_rule='events.jsonl is hashed through the recorded byte length. Later append-only commit/submission receipts are outside that prefix. All scientific artifacts use whole-file hashes.',
        git_excluded_raw_data='Original catalogue indexes, compressed label ranges and self-rerun working trees/raw outputs are included here even though excluded from Git; copy them from the original directory for a full inventory check. They are not needed by numerical verification.',
        qualification='An inventory detects differences relative to these recorded bytes. It does not establish independence, trusted timestamps or absence of tampering.')
    (ROOT/target).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(path=target.as_posix(),files=len(files),hashed_bytes=sum(r['bytes'] for r in files))))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default='SHA256SUMS.json');a=p.parse_args();run(a.output)
