"""Small, sequential public-data retrieval with provenance. No credentials."""
import argparse, hashlib, json, time, urllib.request, ssl
from pathlib import Path
from record import ROOT, append, now

def fetch(url, relative, license_note="not yet checked", timeout=90):
    p=ROOT/relative
    if p.exists():
        raise FileExistsError(relative)
    req=urllib.request.Request(url, headers={"User-Agent":"FreeResearch014/1.0 (public research; ordinary retrieval)"})
    started=now()
    p.parent.mkdir(parents=True,exist_ok=True)
    try:
        import certifi
        ctx=ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        ctx=ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as res:
        final=res.url
        content_type=res.headers.get("Content-Type")
        data=res.read(128*1024*1024+1)
    if len(data)>128*1024*1024:
        raise ValueError("single retrieval exceeds 128 MiB limit")
    p.write_bytes(data)
    record=dict(url=url,final_url=final,requested_at_utc=started,obtained_at_utc=now(),path=relative,
                bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),content_type=content_type,
                licence=license_note,method="ordinary HTTPS GET; no credentials",bundled=True)
    append("sources/retrievals.jsonl",record)
    print(json.dumps(record))
    return record

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("url"); p.add_argument("path"); p.add_argument("--licence",default="not yet checked")
    a=p.parse_args(); fetch(a.url,a.path,a.licence)
