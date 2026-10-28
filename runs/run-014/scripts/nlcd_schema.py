"""Read only published ZIP tabular members and metadata; no performance test."""
import io,json,hashlib,zipfile
from pathlib import Path
import pandas as pd
from remote_zip import RangeFile,URL
from record import ROOT,now,append

def main():
    dest=ROOT/'data/nlcd';prefix='Annual_NLCD_CONUSV1_Ref_Data_Release/'
    names=['NLCD2023_Full8360_AnnualAttributes.csv','Plot_Coordinates_List_Simple_and_Stratified.csv','lcnext_8360_final.shp.xml']
    summaries=[]
    with RangeFile(URL,'sources/nlcd-range-requests.jsonl') as r:
        with zipfile.ZipFile(r) as z:
            for name in names:
                data=z.read(prefix+name) # zipfile validates the published CRC32.
                item=dict(url=URL,member=prefix+name,obtained_at_utc=now(),bytes=len(data),
                          sha256=hashlib.sha256(data).hexdigest(),crc32=z.getinfo(prefix+name).CRC,
                          licence='Public domain / no restrictions',bundled=True)
                if name.endswith('.csv'):
                    df=pd.read_csv(io.BytesIO(data),low_memory=False)
                    item['columns']=df.columns.tolist();item['rows']=len(df)
                    # Do not retain a file if its schema unexpectedly contains personal fields.
                    if any(any(term in c.lower() for term in ['name','email','phone','analyst','interpreter']) for c in df.columns):
                        raise RuntimeError('Unexpected potential personal field; raw member not saved, inspect schema conservatively')
                    item['dtypes']={c:str(v) for c,v in df.dtypes.items()}
                path=dest/name
                if path.exists():raise FileExistsError(path)
                path.write_bytes(data);item['path']=str(path.relative_to(ROOT))
                append('sources/retrievals.jsonl',item);summaries.append(item)
    (dest/'schema.json').write_text(json.dumps(summaries,indent=2)+'\n');print(json.dumps(summaries,indent=2))

if __name__=='__main__':main()
