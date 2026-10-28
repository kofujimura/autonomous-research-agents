"""Download explicitly selected public material and retain provenance."""
import argparse, json, urllib.request, urllib.error, ssl
import certifi
from pathlib import Path
from records import ROOT, now, digest, append

def fetch(url, destination, license_note, purpose):
    path = ROOT / destination
    if path.exists():
        print('EXISTS',destination, path.stat().st_size)
        return
    path.parent.mkdir(parents=True,exist_ok=True)
    started = now()
    req=urllib.request.Request(url,headers={'User-Agent':'FreeResearch016/1.0 (public academic research; single downloads)'})
    try:
        with urllib.request.urlopen(req,timeout=90,context=ssl.create_default_context(cafile=certifi.where())) as response:
            headers=dict(response.headers)
            actual=response.url
            body=response.read(200*1024*1024+1)
            if len(body)>200*1024*1024: raise ValueError('single-download cap exceeded')
        path.write_bytes(body)
        rec=dict(url=url,resolved_url=actual,obtained_at_utc=now(),started_at_utc=started,
                 path=destination,bytes=len(body),sha256=digest(path),license=license_note,
                 purpose=purpose,headers=headers,status='success')
        append('data/downloads.jsonl',rec)
        print(json.dumps({k:rec[k] for k in ['path','bytes','sha256','status']}))
    except Exception as exc:
        append('data/downloads.jsonl',dict(url=url,started_at_utc=started,ended_at_utc=now(),
               path=destination,status='failed',error=type(exc).__name__+': '+str(exc)))
        raise

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('url');p.add_argument('destination');p.add_argument('--license',required=True)
    p.add_argument('--purpose',required=True)
    a=p.parse_args();fetch(a.url,a.destination,a.license,a.purpose)
