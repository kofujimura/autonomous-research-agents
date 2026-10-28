"""Bounded anonymous public byte-range reads, cached with provenance."""
import hashlib,json,time
from pathlib import Path
import requests
from records import ROOT,now,digest,append

SESSION=requests.Session()
SESSION.trust_env=False  # Public reads: no implicit netrc authentication.
SESSION.headers['User-Agent']='FreeResearch016/1.0 public dataset research'

def read_range(url,offset,length,kind='labels'):
    assert url.startswith('https://') and 0<=offset and 0<length<=32*1024**2
    key=hashlib.sha256(f'{url}|{offset}|{length}'.encode()).hexdigest()
    folder=ROOT/'data'/f'{kind}-chunks';folder.mkdir(parents=True,exist_ok=True)
    p=folder/(key+'.bin')
    if p.exists():
        data=p.read_bytes()
        if len(data)==length:return data
        raise ValueError('Cached range has wrong length: '+str(p))
    for attempt in range(1,4):
        start=now()
        try:
            with SESSION.get(url,headers={'Range':f'bytes={offset}-{offset+length-1}'},
                             stream=True,timeout=(20,90)) as r:
                r.raise_for_status()
                if r.status_code!=206:raise ValueError('Server did not honor range; full response not downloaded')
                content_range=r.headers.get('Content-Range','')
                if not content_range.startswith(f'bytes {offset}-{offset+length-1}/'):
                    raise ValueError('Unexpected Content-Range: '+content_range)
                data=r.raw.read(length+1,decode_content=False)
                if len(data)!=length:raise ValueError('Range response length mismatch')
                headers={k:r.headers.get(k) for k in ['ETag','Last-Modified','Content-Range','Content-Type']}
            p.write_bytes(data)
            append('data/range_reads.jsonl',dict(requested_at_utc=start,completed_at_utc=now(),url=url,
                   offset=offset,length=length,attempt=attempt,path=str(p.relative_to(ROOT)),
                   sha256=digest(p),headers=headers,status='success',kind=kind))
            return data
        except Exception as e:
            append('data/range_reads.jsonl',dict(requested_at_utc=start,completed_at_utc=now(),url=url,
                   offset=offset,length=length,attempt=attempt,status='failed',error=repr(e),kind=kind))
            if attempt==3:raise
            time.sleep(attempt)

def swiss_range(ref,year):
    m=json.loads((ROOT/'data/catalogue-manifest.json').read_text())
    url=m['swiss_resolve_base']+f'labels/{year}.tar'
    return read_range(url,int(ref[1]),int(ref[2]))
