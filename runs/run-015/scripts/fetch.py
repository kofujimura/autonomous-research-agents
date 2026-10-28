"""Small, cached public-source downloads with provenance (no credentials)."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
import urllib.request
from record import ROOT, now, append

def fetch(url, relative, source_id, licence="not yet assessed", max_bytes=30_000_000):
    target=ROOT/relative
    if target.exists():
        print(json.dumps({'path':relative,'cached':True,'bytes':target.stat().st_size}))
        return
    request=urllib.request.Request(url,headers={'User-Agent':'FreeResearch015/1.0 (public scholarly research; single cached retrieval)'})
    obtained=now()
    try:
        # System curl uses the OS trust store. Python's unconfigured certificate
        # bundle failed at initialization; TLS verification is never disabled.
        response=subprocess.run(['curl','--fail','--location','--silent','--show-error',
                                 '--max-time','45','--max-filesize',str(max_bytes),
                                 '--user-agent','FreeResearch015/1.0',url],
                                capture_output=True,timeout=50,check=True)
        body=response.stdout
        if len(body)>max_bytes: raise ValueError('download size cap exceeded')
        final_url=None
        content_type=None
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(body)
        item=dict(source_id=source_id,url=url,final_url=final_url,obtained_at_utc=obtained,path=relative,bytes=len(body),sha256=hashlib.sha256(body).hexdigest(),licence=licence,access_range='downloaded; passage inspection recorded separately',content_type=content_type)
        append('sources.jsonl',item)
        print(json.dumps(item))
    except Exception as error:
        detail = error.stderr.decode(errors='replace') if isinstance(error,subprocess.CalledProcessError) else str(error)
        append('sources.jsonl',dict(source_id=source_id,url=url,obtained_at_utc=obtained,path=None,status='retrieval_failed',error=type(error).__name__+': '+detail,access_range='not accessed'))
        print(json.dumps({'source_id':source_id,'status':'failed','error':type(error).__name__+': '+detail}))
        return False

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('url');p.add_argument('path');p.add_argument('source_id');p.add_argument('--licence',default='not yet assessed')
    a=p.parse_args();fetch(a.url,a.path,a.source_id,a.licence)
