"""Bounded fallback for a known public ECMWF .index object after GET errors."""
import re
import time
import requests
from record import now

def recover(session,bases,relative,log):
    collected=b'';total=None
    for base in bases:
        url=base+relative+'.index';stamp=now();failed=False
        while total is None or len(collected)<total:
            initial_start=len(collected);end=initial_start+16383 if total is None else min(initial_start+16383,total-1)
            success=False
            for attempt in range(3):
                start=len(collected);before=len(collected)
                status=None;crange=None
                try:
                    with session.get(url,headers={'Range':f'bytes={start}-{end}'},timeout=(10,25),stream=True) as response:
                        status=response.status_code;crange=response.headers.get('Content-Range');response.raise_for_status()
                        if status!=206:raise ValueError('Index endpoint ignored Range')
                        match=re.fullmatch(r'bytes (\d+)-(\d+)/(\d+)',crange or '')
                        if not match:raise ValueError('Invalid index Content-Range')
                        lo,hi,size=map(int,match.groups())
                        if lo!=start or hi!=min(end,size-1) or not 0<size<=8_000_000:raise ValueError('Incorrect or oversized index range')
                        if total is not None and total!=size:raise ValueError('Index changed size during retrieval')
                        total=size;response.raw.enforce_content_length=False
                        for block in response.iter_content(4096):
                            if len(collected)+len(block)>hi+1:raise ValueError('Index response exceeds requested range')
                            collected+=block
                        if len(collected)!=hi+1:raise ValueError('Truncated index range')
                    success=True
                    log({'operation':'index_range','url':url,'requested_start':lo,'requested_end':hi,
                         'attempt':attempt+1,'status':'completed','http_status':status,'content_range':crange,'bytes_received':len(collected)-before})
                    break
                except (requests.RequestException,ValueError) as error:
                    log({'operation':'index_range','url':url,'requested_start':start,'requested_end':end,
                         'attempt':attempt+1,'status':'failed','http_status':status,'content_range':crange,'bytes_retained':len(collected),'error_type':type(error).__name__})
                    if status in [200,403,404]:break
                    if attempt<2:time.sleep(2**attempt)
            if not success:failed=True;break
        if not failed and total is not None and len(collected)==total:return collected,url,stamp
    raise RuntimeError('Both documented endpoints failed bounded index-range recovery')
