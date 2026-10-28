# Data and source licences

Terms checked on 2026-10-26; source copies and retrieval times are in sources.jsonl and data/downloads.jsonl. This document records the terms used; it does not replace the original licences.

## SwissCrop25

Public reference declarations and taxonomy: CC BY 4.0, Agroscope Earth Observation of Agroecosystems Team. The pinned revision is recorded in data/catalogue-manifest.json. Transformations here include fractional aggregation, largest-coverage classification, stable-support masks and numerical samples. All source attributions required by the card are retained below. They cover the complete dataset; this study downloads labels rather than the full Sentinel-2/weather collection.

When using this dataset, please cite:

- Contains modified Copernicus Sentinel-2 data 2019–2025, processed by Agroscope.
- Contains data from MeteoSwiss (Federal Office of Meteorology and Climatology), Open Government Data.
- Contains cantonal agricultural land-use data (Nutzungsflächen / Surfaces d'utilisation /
  Superfici d'utilizzazione) from all 26 Swiss cantons (AG, AI, AR, BE, BL, BS, FR, GE, GL, GR,
  JU, LU, NE, NW, OW, SG, SH, SO, SZ, TG, TI, UR, VD, VS, ZG, ZH), obtained via
  [geodienste.ch](https://www.geodienste.ch/services/lwb_nutzungsflaechen), snapshot dates
  2019–2025. Cantons with specific attribution requirements:
  - `Quelle: Nutzungsflächen, Kanton Graubünden`
  - `Fonte: Amministrazione cantonale - Canton Ticino`
  - `Source: Géodonnées Etat de Vaud`
  - `Kanton St.Gallen`
  - `Kanton Nidwalden, Amt für Landwirtschaft`
  - `Kanton Obwalden, Amt für Landwirtschaft und Umwelt`

## Annual embeddings

AlphaEarth public Source Cooperative mirror: CC BY 4.0. The AlphaEarth Foundations Satellite Embedding dataset is produced by Google and Google DeepMind. The downloaded spatial-index hash and per-extract source URLs, transformations and numerical hashes are retained in the data ledgers. Dequantization follows the mirror README.

TESSERA public v1.1-dclimate store: the official AWS public-data catalogue specifies CC-BY-SA, without a licence version. This unresolved version is recorded rather than filled in. Preserve that attribution and share-alike designation with all redistributed TESSERA numerical extracts; consult the original catalogue for applicable terms. TESSERA model-weight CC0 terms refer to a different object and are not used to relicense these embeddings. Attribution: the TESSERA authors and dClimate public store maintainers; source/model identifiers and metadata are pinned in data/tessera-zone-32-metadata.json and feature ledgers.

## Documents and code

Scholarly source copies retain their own rights and licence notices. Their inclusion for verification does not grant a new licence to those documents. Public author metadata were incidental to literature retrieval and are not analytic records. Dependencies retain their original licences. No blanket licence for third-party data or documents is implied by the local Git repository. The study is not published externally during this trial.
