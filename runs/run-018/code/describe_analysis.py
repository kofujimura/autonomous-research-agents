"""Human-readable analysis conditions; paths serve only as evidence references."""
import re

def describe(key):
 fixed={'analysis/primary-summary':'Original panel; forest; initial extraction',
 'analysis/primary-corrected-summary':'Original panel; forest; corrected extraction',
 'analysis/recent-summary':'Recent-image panel; forest; initial extraction',
 'analysis/recent-corrected-summary':'Recent-image panel; forest; corrected extraction',
 'analysis/controls/hgb-summary':'Original panel; boosted trees; initial extraction',
 'analysis/controls/hgb-corrected-summary':'Original panel; boosted trees; corrected extraction',
 'analysis/controls/full-features-summary':'All features per split; forest seed offset 0; initial extraction',
 'analysis/controls/constant-all-summary':'Constant column; all features; initial extraction',
 'analysis/controls/constant-hgb-summary':'Constant column; boosted trees; initial extraction',
 'analysis/transfer-corrected-summary':'Train on other windows; forest; corrected extraction',
 'analysis/transfer-summary':'Train on other windows; forest; initial extraction',
 'analysis/random-summary':'Exploratory geographic-frame panel; forest'}
 if key in fixed:return fixed[key]
 m=re.fullmatch(r'analysis/review-seeds/seed-(\d+)-summary',key)
 if m:return f'Post-review forest seed offset {m[1]}; corrected inputs'
 m=re.fullmatch(r'analysis/controls/constant-corrected-(seed-0|all|hgb)-summary',key)
 if m:return 'Corrected-input zero column; '+{'seed-0':'forest feature fraction 0.7; seed offset 0','all':'all-feature forest; seed offset 0','hgb':'fixed boosted trees'}[m[1]]
 m=re.fullmatch(r'analysis/transfer-strong/(rf-all-benchmark|hgb-raw|hgb-white)-summary',key)
 if m:return {'rf-all-benchmark':'Other-window training; all-feature physical forest versus original 0.7 augmented forest','hgb-raw':'Other-window training; boosted trees; raw cosine augmentation','hgb-white':'Other-window training; boosted trees; whitened cosine augmentation'}[m[1]]
 for pattern,label in [(r'analysis/controls/seed-(\d+)-summary','Forest seed offset {}; initial extraction'),(r'analysis/controls/all-corrected-seed-(\d+)-summary','All features per split; forest seed offset {}; corrected extraction'),(r'analysis/controls/constant-seed-(\d+)-summary','Constant column; forest seed offset {}; initial extraction')]:
  m=re.fullmatch(pattern,key)
  if m:return label.format(m[1])
 m=re.fullmatch(r'analysis/controls/(permute|noise|noise-all)-(\d+)-summary',key)
 if m:
  kind={'permute':'Within-window/vegetation/role embedding shuffle','noise':'Independent scalar; forest feature fraction 0.7','noise-all':'Independent scalar; all features per split'}[m[1]]
  return f'{kind}; repetition {int(m[2])+1}; initial extraction'
 m=re.fullmatch(r'analysis/polygon/([ABCD])-(rf|hgb)-summary',key)
 if m:
  condition={'A':'Contiguous patch and point covariates','B':'Dispersed up to 256 pixels and point covariates','C':'Dispersed up to 256 pixels and averaged covariates','D':'Dispersed original pixel count and point covariates'}[m[1]]
  return condition+'; common polygon cohort; '+('forest' if m[2]=='rf' else 'boosted trees')
 m=re.fullmatch(r'analysis/(boundaries|boundaries-corrected)/(.+)-summary',key)
 if m:
  condition={'reference-0':'Reference distance ≥0 km','reference-3000':'Reference distance ≥3 km','training-0':'Training exclusion 0 km','training-3000':'Training exclusion 3 km','margin-30':'Interior margin ≥30 m','within-region':'Within-window physical median/IQR scaling','no-hand':'Physical model without HAND','centre':'Centre-pixel embeddings'}[m[2]]
  return condition+'; forest; '+('corrected extraction' if m[1]=='boundaries-corrected' else 'initial extraction')
 m=re.fullmatch(r'analysis/year-(2021|2023|2024)-summary',key)
 if m:return f'{m[1]} embeddings with fixed physical covariates; forest'
 m=re.fullmatch(r'analysis/metric-whitened/(primary|polygonC)-(hgb|rf-all|raw-rf-all)-summary',key)
 if m:
  population='Original interior patches' if m[1]=='primary' else 'Dispersed embeddings and averaged physical covariates'
  learner='boosted trees' if m[2]=='hgb' else 'all-feature forest'
  return population+'; '+('raw' if m[2]=='raw-rf-all' else 'whitened')+' cosine augmentation; '+learner
 raise ValueError('Add a scientific condition description before reporting '+key)
