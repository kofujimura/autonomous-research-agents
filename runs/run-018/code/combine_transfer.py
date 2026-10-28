"""Bundle fixed held-out windows by rotation for the common summary entry point."""
import argparse,json
from pathlib import Path
import pandas as pd
p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--expected-windows',type=int,default=12);p.add_argument('--round-trip',action='store_true');a=p.parse_args();windows=sorted(x for x in a.inputs.glob('R??') if (x/'transfer-record.json').exists());assert len(windows)==a.expected_windows
for r in range(4):
 folder=a.output/f'r{r}';folder.mkdir(parents=True,exist_ok=False)
 for name in ['predictions.csv','pools.csv']:
  x=pd.concat([pd.read_csv(w/f'r{r}'/name,float_precision='round_trip' if a.round_trip else None) for w in windows],ignore_index=True);assert not x.duplicated(['query_id','method'] if 'method' in x else ['query_id']).any();x.to_csv(folder/name,index=False,float_format='%.17g')
(a.output/'combination.json').write_text(json.dumps(dict(windows=[w.name for w in windows],source=str(a.inputs),expected_windows=a.expected_windows),indent=2)+'\n')
