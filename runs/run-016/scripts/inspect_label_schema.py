import json
from records import ROOT,now,digest
from public_ranges import swiss_range

p=ROOT/'data/catalogues/labels_2021.tar.json'
index=json.loads(p.read_text())['refs']
key=next(k for k in index if k.endswith('/.zmetadata'))
raw=swiss_range(index[key],2021)
m=json.loads(raw)
out=dict(observed_at_utc=now(),index_sha256=digest(p),first_key=key,consolidated=m)
(ROOT/'data/label-schema.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
