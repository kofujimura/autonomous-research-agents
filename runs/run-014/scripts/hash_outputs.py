"""Hash stable trial outputs; check mode is read-only and needs no packages/network."""
import argparse,hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXCLUDED_PARTS={'.git','.venv','.cache','__pycache__','verification-work','matplotlib-cache'}
LIST_NAMES={'SHA256SUMS','SHA256SUMS.txt'}

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while block:=f.read(1024*1024):h.update(block)
    return h.hexdigest()

def paths():
    for p in sorted(ROOT.rglob('*')):
        rel=p.relative_to(ROOT)
        if p.is_symlink() or not p.is_file():continue
        if any(s in EXCLUDED_PARTS for s in rel.parts) or p.name in LIST_NAMES or p.suffix=='.pyc':continue
        yield p,rel.as_posix()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args()
    target=ROOT/'SHA256SUMS.txt'
    if a.check:
        entries={}
        for line in target.read_text().splitlines():
            sha,name=line.split('  ',1);entries[name]=sha
        current={name:digest(p) for p,name in paths()}
        missing=set(entries)-set(current);added=set(current)-set(entries)
        changed=[n for n in entries.keys()&current.keys() if entries[n]!=current[n]]
        if missing or added or changed:
            print(f'FAIL: missing={len(missing)}, added={len(added)}, changed={len(changed)}')
            for title,items in [('missing',missing),('added',added),('changed',changed)]:
                for name in sorted(items)[:20]:print(title,name)
            raise SystemExit(1)
        print(f'PASS: {len(entries)} file hashes match; no network or source writes')
    else:
        entries=[f'{digest(p)}  {name}' for p,name in paths()]
        target.write_text('\n'.join(entries)+'\n');print(f'Wrote {len(entries)} hashes')

if __name__=='__main__':main()
