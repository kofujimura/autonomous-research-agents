"""Bibliographic index of passages checked by this session; no retrieval."""
import json
from records import ROOT,now,append,digest,event

entries=[
 dict(source_id='SWISSCROP25',title='SwissCrop25: A National Multi-Year Benchmark for Operational Crop Mapping',
      authors='Thomas Lauber, Mehmet Ozgur Turkoglu, Sélène Ledain and Helge Aasen',year=2026,
      doi_or_version='arXiv:2608.09497v1',url='https://arxiv.org/html/2608.09497v1',
      path='sources/swisscrop25-paper.html',range_checked='Full text sections 3.1–3.4, 4 setup, appendix A and label-coverage table; introduction and temporal-generalization discussion',
      supports='Reference-label origins, planting-intent limitation, complete 2021–2025 coverage, fractional label generation and crop hierarchy; country-limited evaluation'),
 dict(source_id='SWISSCROP25-CARD',title='SwissCrop25 official dataset card',authors='Agroscope EOA team',year=2026,
      doi_or_version='Pinned repository revision in data/catalogue-manifest.json',url='https://huggingface.co/datasets/EOA-team/SwissCrop25',
      path='sources/swisscrop25-official-readme.md',range_checked='Full card, layout, licence, attribution, no farm-identifying attributes disclaimer',
      supports='CC BY 4.0 reuse and required attribution, label-only random access'),
 dict(source_id='AEF2025',title='AlphaEarth Foundations: An embedding field model for accurate and efficient global mapping from sparse label data',
      authors='Christopher F. Brown et al.',year=2025,doi_or_version='arXiv:2507.22291v2',url='https://arxiv.org/html/2507.22291v2',
      path='sources/alphaearth-2025.html',range_checked='Training inputs and model description; production section S22.3 read in full; sparse-label mapping and production annual inference passages',
      supports='AEF is a representation with annotated training inputs; production differs from evaluated model; CDL added through 2023. Do not assert unseen pretraining or historical real-time deployment'),
 dict(source_id='AEF-MIRROR',title='AlphaEarth Foundations GCS data: public COG mirror README',authors='TGE Labs public dataset maintainers',year=2026,
      doi_or_version='v1/annual public mirror; downloaded index hash pinned',url='https://data.source.coop/tge-labs/aef/README.md',
      path='sources/aef-readme.md',range_checked='Full file: bottom-up orientation, VRTs, licence/attribution, quantization and spatial index',
      supports='CC BY 4.0, int8 dequantization and native-resolution oriented data access'),
 dict(source_id='LIPTON2018',title='Detecting and Correcting for Label Shift with Black Box Predictors',
      authors='Zachary C. Lipton, Yu-Xiang Wang and Alexander J. Smola',year=2018,doi_or_version='PMLR 80:3122–3130',
      url='https://proceedings.mlr.press/v80/lipton18a/lipton18a.pdf',path='sources/lipton-2018.pdf',
      range_checked='Full paper relevant sections 3–5, assumptions A.1–A.3, estimator equation (1), consistency and singular-value condition',
      supports='Source-confusion quantification requires stable class-conditionals and identifiable source class support; differs from target reference sampling'),
 dict(source_id='PANINSKI2003',title='Estimation of Entropy and Mutual Information',authors='Liam Paninski',year=2003,
      doi_or_version='10.1162/089976603321780272',url='https://www.cns.nyu.edu/pub/lcv/paninski-infoEst-2003.pdf',
      path='sources/paninski-2003.pdf',range_checked='Full text definitions of MLE/Miller–Madow/jackknife, section 3.1 and section 9 conclusions; section 4 asymptotic linearization',
      supports='Entropy plug-in bias and limitations of normal/resampling intervals, especially small sample or simplex boundaries; these caveats are established'),
 dict(source_id='ROTATION-SAMPLE1981',title='Development of rotation sample designs for the estimation of crop acreages',
      authors='T. G. Lycthuan-Lee',year=1981,doi_or_version='NASA-CR-167438 / JSC-17427',
      url='https://ntrs.nasa.gov/api/citations/19820013780/downloads/19820013780.pdf',path='sources/crop-rotation-sampling-1981.pdf',
      range_checked='Full report relevant introduction, sections 1.5 and 3.1 and conclusions; OCR limitations retained',
      supports='Repeated/rotating crop-acreage samples and dependence on year-to-year correlation are longstanding, not novel'),
 dict(source_id='EUROCROPS2',title='EuroCrops v2.0: multi-annual harmonized parcel level crop type data linked to European Union-wide survey, statistical, and Earth Observation products',
      authors='Martin Claverie et al.',year=2026,doi_or_version='10.5194/essd-18-4075-2026',
      url='https://essd.copernicus.org/articles/18/4075/2026/',path='sources/eurocrops-v2-2026.pdf',
      range_checked='Full text sections 2.1–2.3, 2.5 and discussion limitations; licence separately checked in source copyright.txt',
      supports='Alternative public multiannual administrative reference, code/geometry harmonization limitations; not used as primary experimental data'),
]
existing={json.loads(x)['source_id'] for x in (ROOT/'sources.jsonl').read_text().splitlines()}
downloads=[json.loads(x) for x in (ROOT/'data/downloads.jsonl').read_text().splitlines()]
for e in entries:
    if e['source_id'] in existing:continue
    p=e.pop('path');matches=[d for d in downloads if d.get('path')==p and d['status']=='success']
    e.update(obtained_at_utc=matches[-1]['obtained_at_utc'] if matches else None,
             checked_at_utc=now(),access='full_text_relevant_passages_checked',paths=[p],sha256=digest(ROOT/p),
             chronology_note='Registration is retrospective; checked passages are specified, not a claim of exhaustive reading')
    append('sources.jsonl',e)
append('sources.jsonl',dict(source_id='POLICY-DIVERSITY2025-LEAD',title='Policy relevant crop diversity monitoring based on earth observation and farmers’ declarations',
       authors='Marijn van der Velde et al.',year=2025,doi_or_version='10.1088/1748-9326/ad9d61',url='https://doi.org/10.1088/1748-9326/ad9d61',
       checked_at_utc=now(),access='search_results_and_repository_abstract_only',
       paths=['sources/policy-diversity-repository-search.json','sources/policy-diversity-jrc-record.json','sources/policy-crop-diversity-2024.pdf'],
       range_checked='Search returned extensive article text but direct full-text retrieval was blocked; JRC record was metadata only',
       supports='Prior-work lead only; do not cite as supporting evidence until relevant full text independently accessible',
       correction='The .pdf download is a saved HTML bot-check response, not the scholarly PDF; earlier successful HTTP status did not validate content'))
event('source_check','Registered independently checked main sources and corrected the non-PDF literature download status',['sources.jsonl'])
