"""Ordinary HTTP Range reader for a publicly linked scientific ZIP archive.

Never accepts a full-body response to a range request. No authentication,
enumeration of unlinked resources, access bypass or parallel requests.
"""
import io,json,hashlib,zipfile
from pathlib import Path
import certifi,requests
from record import ROOT,now,append

URL='https://www.mrlc.gov/downloads/sciweb1/shared/mrlc/data-bundles/Annual_NLCD_CONUSV1_Ref_Data_Release.zip'

class RangeFile(io.RawIOBase):
    def __init__(self,url,log):
        self.url=url;self.log=log;self.pos=0;self.session=requests.Session()
        r=self.session.head(url,timeout=30,verify=certifi.where());r.raise_for_status()
        self.size=int(r.headers['Content-Length']);self.last_modified=r.headers.get('Last-Modified')
    def readable(self):return True
    def seekable(self):return True
    def tell(self):return self.pos
    def seek(self,offset,whence=0):
        self.pos=offset if whence==0 else (self.pos+offset if whence==1 else self.size+offset)
        if not 0<=self.pos<=self.size:raise ValueError('Seek outside ZIP')
        return self.pos
    def read(self,n=-1):
        if n<0:n=self.size-self.pos
        n=min(n,self.size-self.pos)
        if n==0:return b''
        if n>128*1024**2:raise ValueError('Single range exceeds 128 MiB')
        first=self.pos;last=first+n-1;started=now()
        with self.session.get(self.url,headers={'Range':f'bytes={first}-{last}'},stream=True,
                              timeout=60,verify=certifi.where()) as r:
            if r.status_code!=206:raise RuntimeError(f'Range unsupported: HTTP {r.status_code}; full body not read')
            data=r.raw.read(n+1)
            if len(data)!=n:raise RuntimeError(f'Range length mismatch {len(data)} != {n}')
            content_range=r.headers.get('Content-Range')
        self.pos+=n
        append(self.log,dict(url=self.url,requested_at_utc=started,obtained_at_utc=now(),
                             first=first,last=last,bytes=n,status=206,content_range=content_range,
                             sha256=hashlib.sha256(data).hexdigest()))
        return data

def main():
    p=ROOT/'data/nlcd';p.mkdir(parents=True,exist_ok=True)
    with RangeFile(URL,'sources/nlcd-range-requests.jsonl') as r:
        with zipfile.ZipFile(r) as z:
            index=[dict(filename=i.filename,uncompressed_bytes=i.file_size,compressed_bytes=i.compress_size,
                        crc32=i.CRC,compression=i.compress_type) for i in z.infolist()]
            result=dict(obtained_at_utc=now(),url=URL,archive_bytes=r.size,last_modified=r.last_modified,
                        licence='Public domain / no restrictions, official MRLC and USGS pages',members=index,
                        purpose='Access and schema feasibility only; no embedding or score evaluation')
            (p/'archive-index.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
