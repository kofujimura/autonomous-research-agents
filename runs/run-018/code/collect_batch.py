"""Sequential bounded acquisition tasks within one recorded experiment."""
import argparse,json,traceback,time,hashlib
from records import ROOT,now
from collect_embeddings import aef,tessera
from collect_hydro import collect as hydro
from collect_hand import collect as hand

def main():
 p=argparse.ArgumentParser();p.add_argument('product',choices=['aef','tessera','hydro','hand']);p.add_argument('regions',nargs='+');p.add_argument('--year',type=int,default=2024);p.add_argument('--output',required=True);a=p.parse_args()
 results=[]
 for rid in a.regions:
  folder=ROOT/'data/main'/rid;stamp=now();start=time.monotonic()
  try:
   if a.product in ['hydro','hand']:globals()[a.product](rid)
   else:globals()[a.product](rid,a.year)
   error=None
  except Exception as e:error=str(e);traceback.print_exc()
  record=dict(region=rid,product=a.product,year=a.year,start_time_utc=stamp,end_time_utc=now(),elapsed_seconds=time.monotonic()-start,error=error,input_selected_sha256=hashlib.sha256((folder/'selected.geojson').read_bytes()).hexdigest() if (folder/'selected.geojson').exists() else None)
  results.append(record);(ROOT/a.output).write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(record),flush=True)
 return int(any(r['error'] for r in results))
if __name__=='__main__':raise SystemExit(main())
