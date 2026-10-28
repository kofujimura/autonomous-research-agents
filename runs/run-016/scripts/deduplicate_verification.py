"""Share only scientifically identical recomputed array containers after checks.

All computations and comparisons precede replacement. Scientific arrays are
retained at both paths; only duplicate storage/container encoding is normalized.
This is a same-session storage optimization, never independent reproduction.
"""
import argparse,hashlib,json,os
from pathlib import Path
import numpy as np
from records import ROOT,now,digest,event

def array_digest(path):
    h=hashlib.sha256()
    with np.load(path,allow_pickle=False) as data:
        for key in sorted(data.files):
            a=data[key]
            h.update(key.encode()+b'\0'+a.dtype.str.encode()+b'\0')
            h.update(json.dumps(a.shape).encode()+b'\0'+a.tobytes(order='C'))
    return h.hexdigest()

def share_file(source,target):
    before=digest(target);expected=digest(source)
    semantic=None
    if before!=expected:
        a=array_digest(source);b=array_digest(target)
        if a!=b:return dict(shared=False,reason='Arrays differ at byte level; original recomputed file retained',recomputed_sha256=before,expected_sha256=expected)
        semantic=a
    size=target.stat().st_size;temporary=target.with_name(target.name+'.verified-hardlink')
    assert not temporary.exists()
    os.link(source,temporary);os.replace(temporary,target)
    return dict(shared=True,scientific_arrays_identical=True,array_sha256=semantic,
        recomputed_container_sha256_before=before,canonical_container_sha256=expected,logical_bytes=size,
        note='If container bytes differed, scientific arrays matched exactly before canonical-container sharing')

def compact(output_path,record_path):
    out=Path(output_path).resolve();assert out.is_relative_to(ROOT/'verification-work')
    result=json.loads((out/'verification-result.json').read_text());assert result['status']=='passed'
    source_root=Path(result['source_root']).resolve();assert source_root.is_relative_to(ROOT/'verification-work')
    config=json.loads((source_root/'verification-config.json').read_text());pairs=[]
    analyses=config['analyses'] if result['mode']=='all' else [r for r in config['analyses'] if r['role']=='primary']
    for i,r in enumerate(analyses):pairs.append((source_root/r['path'],out/'inference'/str(i)))
    for task in config['supplemental_tasks']:
        target=out/'supplements'/task['name']
        if target.exists():pairs.append((source_root/task['expected_path'],target))
    rows=[]
    for source_base,target_base in pairs:
        if not target_base.exists():continue
        for target in sorted(target_base.rglob('*.npz')):
            source=source_base/target.relative_to(target_base);assert source.exists()
            row=share_file(source,target);row.update(source=str(source.relative_to(ROOT)),target=str(target.relative_to(ROOT)))
            rows.append(row)
    record=dict(observed_at_utc=now(),verification_output=str(out.relative_to(ROOT)),
        based_on='Completed numerical verification plus exact array-byte comparison before sharing',
        shared_files=sum(r['shared'] for r in rows),retained_unique_files=sum(not r['shared'] for r in rows),files=rows,
        scope='No scientific values discarded or substituted before their recomputation/check. All logical outputs remain available. Same-session storage optimization, not independent reproduction.')
    (ROOT/record_path).write_text(json.dumps(record,indent=2)+'\n')
    event('verification_storage_deduplication','After passed verification, share only exact scientific-array duplicates; retain every differing recomputed array file',
          [record_path,str(out.relative_to(ROOT))],shared_files=record['shared_files'],retained_unique_files=record['retained_unique_files'])
    print(json.dumps({k:record[k] for k in ['observed_at_utc','shared_files','retained_unique_files']}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--record',required=True);a=p.parse_args();compact(a.output,a.record)
