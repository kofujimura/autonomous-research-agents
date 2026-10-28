"""Supplement a commit copy with precisely the bundled arrays its fits require.

Default copies bytes and checks SHA-256. --reuse-read-only creates links instead
and is intended for the session's storage-bounded self-check; it shares inputs
with the original bundle and is explicitly not an independent data copy.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def within(root,relative,allow_file_link=False):
    path=root/relative
    check=path.parent.resolve() if allow_file_link else path.resolve()
    if not check.is_relative_to(root.resolve()):raise ValueError('Path escapes declared bundle/copy')
    return path

def main():
    p=argparse.ArgumentParser();p.add_argument('--bundle',required=True);p.add_argument('--copy',required=True)
    p.add_argument('--reuse-read-only',action='store_true');a=p.parse_args()
    bundle=Path(a.bundle).resolve();copy=Path(a.copy).resolve()
    if bundle==copy:raise ValueError('Use a separate commit copy')
    copied=0;existing=0;total=0
    for metadata_path in sorted((copy/'data/results/fits').glob('*.json')):
        metadata=json.loads(metadata_path.read_text());relative=metadata['prediction_path']
        source=within(bundle,relative);destination=within(copy,relative,allow_file_link=a.reuse_read_only);expected=metadata['prediction_sha256']
        if destination.is_symlink() and destination.resolve()!=source.resolve():raise RuntimeError('Unexpected existing input link')
        if sha(source)!=expected:raise RuntimeError('Bundled prediction SHA mismatch: '+relative)
        total+=source.stat().st_size
        if destination.exists():
            if sha(destination)!=expected:raise RuntimeError('Existing copy differs; preserve and investigate: '+relative)
            existing+=1;continue
        destination.parent.mkdir(parents=True,exist_ok=True)
        if a.reuse_read_only:destination.symlink_to(source)
        else:shutil.copy2(source,destination)
        if sha(destination)!=expected:raise RuntimeError('Copied prediction SHA mismatch: '+relative)
        copied+=1
    if copied+existing==0:raise RuntimeError('No completed fit metadata in destination copy')
    print(json.dumps(dict(required_arrays=copied+existing,newly_prepared=copied,already_present=existing,
        required_input_bytes=total,mode='shared read-only input links' if a.reuse_read_only else 'byte copies',
        all_hashes_match=True),indent=2))

if __name__=='__main__':main()
