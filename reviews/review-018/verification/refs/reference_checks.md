# Reference and novelty checks (reviewer; 2026-10-28 ~08:40-08:50Z)
Method: WebSearch (standard) for discovery; page content fetched with curl (no AI summarization of fetched pages); Crossref API for DOIs. Raw pages saved in this directory.

## Existence checks (sample: 8 of 17 references, prioritizing novelty-critical/2026 items)
| Reference | Check | Result |
|---|---|---|
| Qu et al. 2026 arXiv:2601.01558v2 | arXiv abs page | exists; title/authors match (Qu, Ouyang, ...), 2026-01-04; search summary: embedding similarity used to pick donor basins (consistent with paper's description) |
| Ou & Zheng 2026 GRL e2025GL121604 | Crossref | exists; title matches; GRL vol 53; 2026-04-03 |
| Liu et al. 2026 GRL e2026GL122814 | Crossref | exists; authors Liu, Shen, Yang, Ji, Lawson, Kraabel match |
| Ryan et al. 2026 Remote Sensing 18(2) 293 | Crossref | exists; title/authors match |
| Askew et al. 2025 WEM 33:58 | Crossref | exists; title/authors match; HAND + Sentinel-2 hydroperiod (consistent) |
| Heiman 2026 arXiv:2605.05547 | arXiv abs page | exists; title/author match |
| Young & Keshav 2026 arXiv:2610.32617 | arXiv abs page | exists; title/authors match; 2026-10-23 |
| Sharma et al. 2026 preprints.org 202610.0964 | search result URL listed; direct curl returned empty page | existence indicated by search index only; content not checked |
No non-existent reference found in the sample. Content-level check limited to search/abstract summaries.

## Close work not cited in paper (found within this bounded search)
- Abrahamson, J. & Stegen, J. (2026). "Mapping Wetland Inundation Regimes using Google's AlphaEarth Embeddings: A Case Study in the Florida Everglades", Society for Freshwater Science 2026 Annual Meeting poster #222 (PNNL). Random forest on AlphaEarth embeddings to map annual inundation regimes (seasonal/permanent/ephemeral) 2018-2021 with EDEN gauge-based ground truth; compared to Sentinel-2 NDWI composites; unsupervised clustering. (sfs_135001.html)
- arXiv:2602.10354 (2026) "Physically Interpretable AlphaEarth Foundation Model Embeddings ..." : 64-d AlphaEarth embeddings reconstruct 26 CONUS environmental variables incl. hydrology/terrain with high R2 (12/26 > 0.90). Relevant to redundancy between embeddings and the physical baseline. (arxiv_2602.10354.html)
- Remote-sensing mapping of wetland surface-water regimes for NWI: DeVries et al. 2017 (Remote Sensing, Landsat sub-pixel water fraction), SWaRe multi-source surface water regimes (AGU 2018 abstract, with NWI context), Lang et al. 2008 (SAR hydroperiod vs NWI). Found via search result listings only; not read in full.
"Not found within the range searched" applies to any study using embedding similarity to select wetland references with an NWI water-regime endpoint.
