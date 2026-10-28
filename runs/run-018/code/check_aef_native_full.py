"""Full archived R01 patch-set equality under native versus provider-VRT transport."""
import json,numpy as np
from collect_embeddings import aef
from records import ROOT,now

def main():
 aef('R01',2024,use_native=True,suffix='-native-check')
 folder=ROOT/'data/main/R01';old=np.load(folder/'aef-2024.npz');new=np.load(folder/'aef-2024-native-check.npz');result=dict(checked_at_utc=now(),comparisons={k:bool(np.array_equal(old[k],new[k],equal_nan=True)) for k in old.files},wetlands=len(old['objectid']),raw_vector_values=int(old['raw'].size),scope='Exact archived scientific-input equality, no matching outcome used')
 (ROOT/'analysis/native-source-check/full-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
 assert all(result['comparisons'].values())
if __name__=='__main__':main()
