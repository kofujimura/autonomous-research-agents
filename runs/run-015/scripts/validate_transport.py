"""Local in-memory truncated-response fixture; never contacts a network."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import requests
import urllib3
from urllib3.response import HTTPResponse
from index_ranges import recover
from record import now

def response(body,start,end,total):
    result=requests.Response();result.status_code=206
    result.headers={'Content-Range':f'bytes {start}-{end}/{total}','Content-Length':str(end-start+1)}
    result.raw=HTTPResponse(body=io.BytesIO(body),headers=result.headers,preload_content=False,enforce_content_length=True)
    return result

class Session:
    def __init__(self,payload):self.payload=payload;self.calls=[]
    def get(self,url,headers,**kwargs):
        match=re.fullmatch(r'bytes=(\d+)-(\d+)',headers['Range']);start,end=map(int,match.groups());end=min(end,len(self.payload)-1)
        self.calls.append({'start':start,'end':end})
        body=self.payload[start:end+1]
        if len(self.calls)==1:body=body[:3677]
        return response(body,start,end,len(self.payload))

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True);payload=b'0123456789'*2000
    r=response(payload[:3677],0,16383,len(payload));old=b'';old_error=None
    try:
        for block in r.iter_content(4096):old+=block
    except requests.exceptions.ChunkedEncodingError as error:old_error=type(error).__name__
    assert old_error=='ChunkedEncodingError' and len(old)==0
    r=response(payload[:3677],0,16383,len(payload));r.raw.enforce_content_length=False
    retained=b''.join(r.iter_content(4096));assert retained==payload[:3677]
    assert len(retained)!=16384 # it must still fail the caller's complete-range check
    log=[];session=Session(payload)
    body,url,stamp=recover(session,['https://mock.invalid/'],'synthetic-index',log.append)
    assert body==payload and session.calls[1]['start']==3677
    assert any(x['status']=='failed' and x['bytes_retained']==3677 for x in log)
    report={'status':'passed','completed_at_utc':now(),'requests_version':requests.__version__,
            'urllib3_version':urllib3.__version__,'old_error':old_error,'old_retained_bytes':len(old),
            'new_retained_bytes':len(retained),'complete_bytes':len(body),'sha256':hashlib.sha256(body).hexdigest(),
            'calls':session.calls,'log':log,'network_calls':0,
            'scope':'Synthetic ingestion-code check, not weather evidence or a third-party test'}
    (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':main()
