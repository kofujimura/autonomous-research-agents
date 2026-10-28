"""Validate the future-year patch reader against the archived measured repair."""
from pathlib import Path
import hashlib,json
import numpy as np
from collect_embeddings import aef
from records import ROOT,now

target=ROOT/'data/main/R04/aef-2024-tile-safe-check.npz';assert not target.exists()
aef('R04',2024,suffix='-tile-safe-check')
expected=ROOT/'data/corrections/R04/aef-2024.npz';x=np.load(target);y=np.load(expected);checks={k:bool(np.array_equal(x[k],y[k],equal_nan=True)) for k in x.files};assert all(checks.values()),checks
out=ROOT/'analysis/tile-safe-reader-check';out.mkdir(exist_ok=False)
record=dict(checked_at_utc=now(),checks=checks,all_arrays_exactly_equal=True,new_reader_path=str(target.relative_to(ROOT)),corrected_archived_path=str(expected.relative_to(ROOT)),source_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),expected_sha256=hashlib.sha256(expected.read_bytes()).hexdigest(),scope='One original-panel window containing the known tile edge; not exhaustive provider validation')
(out/'result.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
