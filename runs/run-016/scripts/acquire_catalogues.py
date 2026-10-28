"""Public, anonymous metadata/index acquisition; no model API or credentials."""
import json
from pathlib import Path
from fetch import fetch
from records import ROOT,now,digest

OUT=ROOT/'data/catalogues';OUT.mkdir(parents=True,exist_ok=True)
fetch('https://huggingface.co/api/datasets/EOA-team/SwissCrop25',
      'data/catalogues/swiss-repository.json','Public dataset metadata',
      'Pin original public SwissCrop25 repository revision')
meta=json.loads((OUT/'swiss-repository.json').read_text())
revision=meta['sha']
base=f'https://huggingface.co/datasets/EOA-team/SwissCrop25/resolve/{revision}/'
for name in ['metadata/tiles.parquet','metadata/crop_classes.csv',
             'metadata/swisscrop25_to_hcat4.csv']+[f'labels/{y}.tar.json' for y in range(2021,2026)]:
    fetch(base+name,'data/catalogues/'+name.replace('/','_'),'CC BY 4.0',
          'SwissCrop25 public label access index or taxonomy; no image download')
fetch('https://data.source.coop/tge-labs/aef/v1/annual/aef_index.parquet',
      'data/catalogues/aef_index.parquet','CC BY 4.0, Google/DeepMind attribution',
      'Find native-resolution public AlphaEarth files for preplanned Swiss points')
manifest=dict(observed_at_utc=now(),swiss_revision=revision,swiss_resolve_base=base,
              plan_path='protocol/plan-v1.md',catalogues_excluded_from_git=True,
              exclusion_reason='Large download/access indexes; saved numerical extracts will permit offline verification',
              files=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p),bytes=p.stat().st_size)
                     for p in sorted(OUT.iterdir()) if p.is_file()])
(ROOT/'data/catalogue-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest),flush=True)
