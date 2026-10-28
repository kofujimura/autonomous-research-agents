"""Read-only check of a submitted scoped hash inventory. No network or API."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,json
from pathlib import Path
from records import ROOT,now

def check(manifest,allow_missing_optional=False):
    m=json.loads((ROOT/manifest).read_text());checked=[];missing=[]
    for row in m['files']:
        rel=Path(row['path']);assert not rel.is_absolute() and '..' not in rel.parts
        path=ROOT/rel
        if not path.exists() and allow_missing_optional and row['optional_for_numerical_verification']:
            missing.append(row['path']);continue
        assert path.is_file() and not path.is_symlink(),('Missing or unsafe inventory input',row['path'])
        size=path.stat().st_size;prefix=row['mode']=='prefix'
        assert size>=row['bytes'] if prefix else size==row['bytes'],('Byte length differs',row['path'])
        remaining=row['bytes'];h=hashlib.sha256()
        with path.open('rb') as stream:
            while remaining:
                block=stream.read(min(1024**2,remaining));assert block
                h.update(block);remaining-=len(block)
        assert h.hexdigest()==row['sha256'],('SHA-256 differs',row['path'])
        checked.append(row['path'])
    return dict(observed_at_utc=now(),status='passed',manifest=manifest,checked_files=len(checked),
        missing_optional_files=missing,complete_inventory_checked=not missing,
        event_prefix_rule=m['event_prefix_rule'],network_used=False,ai_api_called=False)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifest',default='SHA256SUMS.json')
    p.add_argument('--allow-missing-optional',action='store_true');p.add_argument('--output');a=p.parse_args()
    result=check(a.manifest,a.allow_missing_optional)
    if a.output:
        out=Path(a.output).resolve()
        assert not out.is_relative_to(ROOT) or out.relative_to(ROOT).as_posix().startswith('review/hash-verification-')
        assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
